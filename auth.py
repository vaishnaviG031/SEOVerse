"""Database and Authentication module for Aivora YouTube Intelligence platform.
Provides secure password hashing (bcrypt), JWT sessions, email verification,
password reset, and user analysis history via SQLite.
"""
import os
import sqlite3
from contextlib import contextmanager
import secrets
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import bcrypt
import jwt
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
DB_DIR = Path("/tmp/database") if os.getenv("VERCEL") else (PROJECT_DIR / "database")
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "aivora.db"

load_dotenv(PROJECT_DIR / ".env")

JWT_SECRET = os.getenv("JWT_SECRET") or secrets.token_urlsafe(48)
if os.getenv("ENVIRONMENT", "development").lower() == "production" and len(JWT_SECRET) < 32:
    raise RuntimeError("Set JWT_SECRET to a random value of at least 32 characters in production.")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 168  # 7 days


@contextmanager
def get_db_connection():
    """Yield a SQLite connection and always close it after the transaction."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database tables for users and analysis history."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                is_verified INTEGER DEFAULT 0,
                verification_code TEXT,
                reset_token TEXT,
                reset_token_expiry INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User Analysis History table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                model TEXT NOT NULL,
                opportunity_score REAL,
                report_markdown TEXT NOT NULL,
                report_data_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.commit()


# Initialize database upon import
init_db()


def hash_password(password: str) -> str:
    """Securely hash a password with bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_jwt_token(user_id: int, email: str) -> str:
    """Generate a signed JWT token valid for 7 days."""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": int(time.time()) + (JWT_EXPIRATION_HOURS * 3600),
        "iat": int(time.time()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception:
        return None


def register_user(email: str, password: str, full_name: str) -> Dict[str, Any]:
    """Register a new user account and generate a 6-digit verification code."""
    email = email.strip().lower()
    full_name = full_name.strip()
    
    if len(password) < 8:
        return {"success": False, "error": "Password must be at least 6 characters long."}
    if "@" not in email or "." not in email:
        return {"success": False, "error": "Please provide a valid email address."}

    # Generate 6-digit verification code
    verification_code = f"{secrets.randbelow(900000) + 100000}"
    password_hash = hash_password(password)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (email, password_hash, full_name, is_verified, verification_code)
                VALUES (?, ?, ?, 0, ?)
            """, (email, password_hash, full_name, verification_code))
            conn.commit()
            user_id = cursor.lastrowid
            
        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "verification_code": verification_code,
            "message": "Account created! Please verify your email."
        }
    except sqlite3.IntegrityError:
        return {"success": False, "error": "An account with this email already exists."}
    except Exception as e:
        return {"success": False, "error": f"Registration failed: {str(e)}"}


def resend_verification_code(email: str) -> Dict[str, Any]:
    email = email.strip().lower()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, is_verified FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if not user:
            return {"success": False, "error": "Account not found. Check the address or create an account."}
        if user["is_verified"]:
            return {"success": False, "error": "This account is already verified. Please sign in."}
        code = f"{secrets.randbelow(900000) + 100000}"
        cursor.execute("UPDATE users SET verification_code = ? WHERE id = ?", (code, user["id"]))
        conn.commit()
        return {"success": True, "email": email, "verification_code": code}


def verify_user_email(email: str, code: str) -> Dict[str, Any]:
    """Verify user account with the 6-digit code."""
    email = email.strip().lower()
    code = code.strip()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user:
            return {"success": False, "error": "User account not found."}

        if user["is_verified"]:
            token = create_jwt_token(user["id"], user["email"])
            return {
                "success": True,
                "token": token,
                "user": {"id": user["id"], "email": user["email"], "full_name": user["full_name"]},
                "message": "Account is already verified."
            }

        if str(user["verification_code"]) == str(code):
            cursor.execute("UPDATE users SET is_verified = 1, verification_code = NULL WHERE id = ?", (user["id"],))
            conn.commit()
            token = create_jwt_token(user["id"], user["email"])
            return {
                "success": True,
                "token": token,
                "user": {"id": user["id"], "email": user["email"], "full_name": user["full_name"]},
                "message": "Email verified successfully!"
            }
        else:
            return {"success": False, "error": "Invalid verification code. Please check your code."}


def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    """Authenticate user with email and password."""
    email = email.strip().lower()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user or not verify_password(password, user["password_hash"]):
            return {"success": False, "error": "Invalid email or password."}

        if not user["is_verified"]:
            return {
                "success": False,
                "needs_verification": True,
                "email": user["email"],
                "error": "Please verify your email before logging in."
            }

        token = create_jwt_token(user["id"], user["email"])
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
            }
        }


def request_password_reset(email: str) -> Dict[str, Any]:
    """Create a reset token valid for 1 hour."""
    email = email.strip().lower()
    reset_token = secrets.token_hex(16)
    expiry = int(time.time()) + 3600  # 1 hour

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if not user:
            # Prevent email enumeration while returning clean notice
            return {"success": True, "message": "If this email is registered, a reset code has been sent."}

        cursor.execute("UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE id = ?", (reset_token, expiry, user["id"]))
        conn.commit()

        return {
            "success": True,
            "reset_token": reset_token,
            "email": email,
            "message": "Password reset instructions generated."
        }


def reset_password(token: str, new_password: str) -> Dict[str, Any]:
    """Reset password using valid reset token."""
    if len(new_password) < 8:
        return {"success": False, "error": "Password must be at least 6 characters long."}

    now = int(time.time())
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE reset_token = ? AND reset_token_expiry > ?", (token, now))
        user = cursor.fetchone()

        if not user:
            return {"success": False, "error": "Password reset token is invalid or has expired."}

        new_hash = hash_password(new_password)
        cursor.execute("UPDATE users SET password_hash = ?, reset_token = NULL, reset_token_expiry = NULL WHERE id = ?", (new_hash, user["id"]))
        conn.commit()

        return {"success": True, "message": "Password updated successfully! You can now log in."}


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve user details by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, full_name, is_verified, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def save_user_history(user_id: int, topic: str, model: str, score: float, report_md: str, report_data_json: str) -> int:
    """Save an analysis report to the user's history."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_history (user_id, topic, model, opportunity_score, report_markdown, report_data_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, topic, model, score, report_md, report_data_json))
        conn.commit()
        return cursor.lastrowid


def get_user_history(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve past reports for a user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, topic, model, opportunity_score, created_at
            FROM user_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def get_history_item(item_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve full data for a specific history item."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM user_history WHERE id = ? AND user_id = ?
        """, (item_id, user_id))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
