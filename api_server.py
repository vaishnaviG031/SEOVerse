"""Production-ready web API for SEOVerse YouTube Intelligence platform.
Powered by CrewAI, Google Gemini, YouTube Data API v3, with JWT Authentication,
user history, and CORS middleware.
"""
import os
import sys
import re
import json
import urllib.request
from pathlib import Path
from threading import Lock

# Fix Windows console encoding so emojis never cause 'charmap' codec crashes
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

from dotenv import load_dotenv
PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")

from youtube_data import search_youtube, format_youtube_section
from report_parser import parse_report_to_json
import auth
import email_service

from starlette.applications import Starlette
from starlette.requests import Request as StarletteRequest
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

WEB_DIR = PROJECT_DIR / "frontend"
REPORT_PATH = (Path("/tmp/reports") if os.getenv("VERCEL") else (PROJECT_DIR / "reports")) / "latest_report.md"
RUN_LOCK = Lock()


def clean_str(s: str) -> str:
    """Safely sanitize text to prevent console/charmap encoding issues on Windows."""
    return s.encode("ascii", "ignore").decode("ascii")


def check_ollama_status() -> bool:
    """Check if local Ollama server is running."""
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/tags", headers={"User-Agent": "TubePilot/1.0"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
        return False


def auth_cookie_response(request: StarletteRequest, result: dict) -> JSONResponse:
    token = result.pop("token", None)
    response = JSONResponse(result)
    if token:
        response.set_cookie(
            "aivora_token", token, httponly=True,
            secure=request.url.scheme == "https" or os.getenv("COOKIE_SECURE", "").lower() in {"1", "true", "yes"},
            samesite="lax", max_age=auth.JWT_EXPIRATION_HOURS * 3600, path="/",
        )
    return response


def get_current_user_from_request(request: StarletteRequest) -> dict | None:
    """Extract authenticated user from Authorization header or cookie."""
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
    elif "aivora_token" in request.cookies:
        token = request.cookies.get("aivora_token")

    if not token:
        return None

    payload = auth.decode_jwt_token(token)
    if not payload:
        return None

    return auth.get_user_by_id(payload.get("user_id"))


# -------------------------------------------------------------
# CORE API ENDPOINTS
# -------------------------------------------------------------

async def health(request: StarletteRequest):
    model = os.getenv("MODEL", "gemini/gemini-3.5-flash-lite")
    has_gemini = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    has_youtube = bool(os.getenv("YOUTUBE_API_KEY"))
    ollama_online = await run_in_threadpool(check_ollama_status)

    return JSONResponse({
        "status": "ok",
        "model": model,
        "gemini_connected": has_gemini,
        "youtube_connected": has_youtube,
        "ollama_connected": ollama_online,
        "service": "SEOVerse YouTube Intelligence Studio",
        "analysis_running": RUN_LOCK.locked()
    })


# -------------------------------------------------------------
# AUTHENTICATION ENDPOINTS
# -------------------------------------------------------------

async def auth_signup(request: StarletteRequest):
    """Handle new user sign up."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    email = str(body.get("email", "")).strip()
    password = str(body.get("password", "")).strip()
    full_name = str(body.get("full_name", "")).strip() or "Creator"

    result = await run_in_threadpool(auth.register_user, email, password, full_name)
    if not result.get("success"):
        return JSONResponse({"error": result.get("error")}, status_code=400)

    # Dispatch verification email (or simulation)
    code = result.get("verification_code")
    await run_in_threadpool(email_service.send_verification_email, email, full_name, code)

    return JSONResponse({
        "success": True,
        "email": email,
        "message": "Account created! A 6-digit verification code has been sent to your email.",
        # In local development if SMTP is not set, include code for frictionless testing:
        "dev_code": code if not os.getenv("SMTP_HOST") else None
    })


async def auth_resend_verification(request: StarletteRequest):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)
    email = str(body.get("email", "")).strip()
    result = await run_in_threadpool(auth.resend_verification_code, email)
    if not result.get("success"):
        return JSONResponse({"error": result.get("error")}, status_code=400)
    sent = await run_in_threadpool(
        email_service.send_verification_email, email, "Creator", result["verification_code"]
    )
    if os.getenv("SMTP_HOST") and not sent:
        return JSONResponse({"error": "Email delivery failed. Please try again later."}, status_code=502)
    return JSONResponse({
        "success": True,
        "message": "A new verification code was sent.",
        "dev_code": result["verification_code"] if not os.getenv("SMTP_HOST") else None,
    })


async def auth_verify_email(request: StarletteRequest):
    """Handle email verification code."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    email = str(body.get("email", "")).strip()
    code = str(body.get("code", "")).strip()

    result = await run_in_threadpool(auth.verify_user_email, email, code)
    if not result.get("success"):
        return JSONResponse({"error": result.get("error")}, status_code=400)

    return auth_cookie_response(request, result)


async def auth_login(request: StarletteRequest):
    """Handle user login with email and password."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    email = str(body.get("email", "")).strip()
    password = str(body.get("password", "")).strip()

    result = await run_in_threadpool(auth.authenticate_user, email, password)
    if not result.get("success"):
        return JSONResponse(result, status_code=401)

    return auth_cookie_response(request, result)


async def auth_forgot_password(request: StarletteRequest):
    """Initiate password reset."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    email = str(body.get("email", "")).strip()
    result = await run_in_threadpool(auth.request_password_reset, email)

    if result.get("reset_token"):
        await run_in_threadpool(email_service.send_reset_password_email, email, result["reset_token"])

    return JSONResponse({
        "success": True,
        "message": result.get("message"),
        "dev_token": result.get("reset_token") if not os.getenv("SMTP_HOST") else None
    })


async def auth_reset_password(request: StarletteRequest):
    """Finalize password reset with token."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)

    token = str(body.get("token", "")).strip()
    new_password = str(body.get("new_password", "")).strip()

    result = await run_in_threadpool(auth.reset_password, token, new_password)
    if not result.get("success"):
        return JSONResponse({"error": result.get("error")}, status_code=400)

    return JSONResponse(result)


async def auth_logout(request: StarletteRequest):
    response = JSONResponse({"success": True})
    response.delete_cookie("aivora_token", path="/", httponly=True, samesite="lax")
    return response


async def auth_me(request: StarletteRequest):
    """Return the profile of the logged-in user."""
    user = get_current_user_from_request(request)
    if not user:
        return JSONResponse({"authenticated": False}, status_code=200)

    return JSONResponse({
        "authenticated": True,
        "user": user
    })


async def get_history(request: StarletteRequest):
    """Return past analysis runs for the authenticated user."""
    user = get_current_user_from_request(request)
    if not user:
        return JSONResponse({"error": "Authentication required to view history."}, status_code=401)

    history_items = await run_in_threadpool(auth.get_user_history, user["id"])
    return JSONResponse({"history": history_items})


async def get_history_detail(request: StarletteRequest):
    """Return specific analysis item from user's history."""
    user = get_current_user_from_request(request)
    if not user:
        return JSONResponse({"error": "Authentication required."}, status_code=401)

    item_id = int(request.path_params["item_id"])
    item = await run_in_threadpool(auth.get_history_item, item_id, user["id"])
    if not item:
        return JSONResponse({"error": "Item not found."}, status_code=404)

    parsed_data = {}
    if item.get("report_data_json"):
        try:
            parsed_data = json.loads(item["report_data_json"])
        except Exception:
            pass

    return JSONResponse({
        "topic": item["topic"],
        "model": item["model"],
        "report": item["report_markdown"],
        "data": parsed_data,
        "created_at": item["created_at"]
    })


# -------------------------------------------------------------
# SEO WORKFLOW ENDPOINTS
# -------------------------------------------------------------

async def saved_report(request: StarletteRequest):
    user = get_current_user_from_request(request)
    if not user:
        return JSONResponse({"error": "Authentication required."}, status_code=401)
    history = await run_in_threadpool(auth.get_user_history, user["id"], 1)
    if not history:
        return JSONResponse({"error": "No saved report yet."}, status_code=404)
    item = await run_in_threadpool(auth.get_history_item, history[0]["id"], user["id"])
    if not item:
        return JSONResponse({"error": "Saved report not found."}, status_code=404)
    try:
        parsed_data = json.loads(item.get("report_data_json") or "{}")
    except (TypeError, json.JSONDecodeError):
        parsed_data = {}
    return JSONResponse({
        "topic": item["topic"],
        "data": parsed_data,
        "competitors": parsed_data.get("competitors", []),
        "report": item["report_markdown"],
    })


def run_crew(topic: str) -> str:
    # 1. Fetch live YouTube competitor data via YouTube Data API v3
    youtube_data = search_youtube(topic)
    
    # 2. Build live context snippet for the agents
    live_context = ""
    if youtube_data.get("connected") and youtube_data.get("videos"):
        context_items = ["\nLive Competitor Video Benchmarks from YouTube:"]
        for v in youtube_data["videos"][:6]:
            clean_title = clean_str(v.get("title", ""))
            clean_channel = clean_str(v.get("channel", ""))
            views = f"{int(v['views']):,}" if str(v.get("views", "")).isdigit() else "N/A"
            likes = f"{int(v['likes']):,}" if str(v.get("likes", "")).isdigit() else "N/A"
            context_items.append(f"- \"{clean_title}\" by {clean_channel} ({views} views, {likes} likes)")
        live_context = "\n".join(context_items)

    # 3. Kick off the 6-agent CrewAI pipeline
    from youtube_seo_agent.crew import YoutubeSeoAgentCrew
    crew_instance = YoutubeSeoAgentCrew().crew()
    result = crew_instance.kickoff(inputs={
        "topic": clean_str(topic),
        "live_context": live_context,
    })

    final_report = getattr(result, "raw", None) or ""

    # Collect individual task outputs if available for full transparency
    outputs = []
    for index, task_output in enumerate(getattr(result, "tasks_output", []) or [], start=1):
        raw = getattr(task_output, "raw", None) or str(task_output)
        name = getattr(task_output, "name", None) or f"Stage {index}"
        outputs.append(f"### Stage {index}: {name}\n\n{raw}")

    # Combine report
    if final_report.strip():
        report = final_report
        if outputs:
            report = report + "\n\n---\n\n## 📋 Agent Stage Breakdown\n\n" + "\n\n".join(outputs)
    elif outputs:
        report = "# Assembled YouTube Strategy Report\n\n" + "\n\n".join(outputs)
    else:
        report = str(result)

    # 4. Attach live YouTube search data table
    youtube_section = format_youtube_section(youtube_data)
    model_name = os.getenv("MODEL", "gemini/gemini-3.5-flash-lite")
    
    full_output = (
        f"# 🎬 SEOVerse YouTube Intelligence — SEO Strategy Blueprint\n\n"
        f"**Topic:** {topic}\n\n"
        f"**AI Engine:** {model_name}\n\n"
        f"---\n\n"
        f"{youtube_section}\n\n"
        f"---\n\n"
        f"{report}\n"
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(full_output, encoding="utf-8", errors="replace")
    return full_output


async def analyze(request: StarletteRequest):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Request body must be valid JSON."}, status_code=400)
        
    topic = str(body.get("topic", "")).strip()[:180]
    if not topic:
        return JSONResponse({"error": "Please enter a YouTube topic or niche."}, status_code=400)

    # Check for authenticated user to save history
    user = get_current_user_from_request(request)
    if not user:
        return JSONResponse({"error": "Sign in to use the research dashboard."}, status_code=401)

    if body.get("model"):
        os.environ["MODEL"] = str(body["model"]).strip()
        
    if not RUN_LOCK.acquire(blocking=False):
        return JSONResponse({
            "error": "An analysis is already running. Please wait for it to finish before starting another."
        }, status_code=409)
        
    try:
        report = await run_in_threadpool(run_crew, topic)
        parsed_data = parse_report_to_json(report, topic)
        competitors_result = await run_in_threadpool(search_youtube, topic, 8)
        parsed_data["competitors"] = competitors_result.get("videos", [])
        model_name = os.getenv("MODEL", "gemini/gemini-3.5-flash-lite")

        # Save to user history if logged in
        if user:
            try:
                score = parsed_data.get("opportunity_score")
                await run_in_threadpool(
                    auth.save_user_history,
                    user["id"],
                    topic,
                    model_name,
                    score,
                    report,
                    json.dumps(parsed_data)
                )
            except Exception as e:
                print(f"Failed to save history: {e}")

        return JSONResponse({
            "topic": topic,
            "report": report,
            "data": parsed_data,
            "competitors": competitors_result.get("videos", []),
            "model": model_name
        })
    except Exception as exc:
        print(f"Analysis failed: {type(exc).__name__}: {exc}", flush=True)
        return JSONResponse({
            "error": "The CrewAI workflow encountered an issue.",
            "detail": f"{type(exc).__name__}: {exc}"
        }, status_code=500)
    finally:
        RUN_LOCK.release()


def compute_quick_prediction(topic: str) -> dict:
    """Summarize observed public video data without inventing forecasts."""
    yt_data = search_youtube(topic, max_results=8)
    videos = yt_data.get("videos", [])
    valid_views = [int(v["views"]) for v in videos if str(v.get("views", "")).isdigit()]
    valid_likes = [int(v["likes"]) for v in videos if str(v.get("likes", "")).isdigit()]
    ordered_views = sorted(valid_views)
    median_views = None
    if ordered_views:
        middle = len(ordered_views) // 2
        median_views = ((ordered_views[middle - 1] + ordered_views[middle]) // 2
                        if len(ordered_views) % 2 == 0 else ordered_views[middle])
    return {
        "topic": topic,
        "competitors": videos,
        "stats": {
            "sample_count": len(videos),
            "views_count": len(valid_views),
            "avg_views": f"{sum(valid_views) // len(valid_views):,}" if valid_views else None,
            "median_views": f"{median_views:,}" if median_views is not None else None,
            "top_views": f"{max(valid_views):,}" if valid_views else None,
            "avg_likes": f"{sum(valid_likes) // len(valid_likes):,}" if valid_likes else None,
            "source": "Observed public YouTube search results",
        },
        "prediction_methodology": [{
            "step": "Observed data",
            "detail": (
                f"Showing counts from {len(valid_views)} of {len(videos)} returned public videos. "
                "These are current observations, not search-volume estimates or predictions of future views."
            ),
        }],
        "data_limitations": (
            "YouTube search results are a small, changing sample. Search volume, audience retention, "
            "click-through rate, and future views are not available from this public data."
        ),
    }


async def quick_predict(request: StarletteRequest):
    if not get_current_user_from_request(request):
        return JSONResponse({"error": "Sign in to use the research dashboard."}, status_code=401)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Request body must be valid JSON."}, status_code=400)
        
    topic = str(body.get("topic", "")).strip()[:180]
    if not topic:
        return JSONResponse({"error": "Please enter a topic or keyword."}, status_code=400)

    try:
        data = await run_in_threadpool(compute_quick_prediction, topic)
        return JSONResponse(data)
    except Exception as exc:
        return JSONResponse({"error": f"Prediction failed: {exc}"}, status_code=500)


async def live_competitors(request: StarletteRequest):
    if not get_current_user_from_request(request):
        return JSONResponse({"error": "Authentication required."}, status_code=401)
    query = request.query_params.get("q", "").strip() or "AI tools for college students"
    data = await run_in_threadpool(search_youtube, query, 10)
    return JSONResponse(data)


async def set_model(request: StarletteRequest):
    if not get_current_user_from_request(request):
        return JSONResponse({"error": "Authentication required."}, status_code=401)
    try:
        body = await request.json()
        model = str(body.get("model", "")).strip()
        if model:
            os.environ["MODEL"] = model
            return JSONResponse({"status": "updated", "model": model})
        return JSONResponse({"error": "No model specified."}, status_code=400)
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


# -------------------------------------------------------------
# APPLICATION CONFIGURATION & MIDDLEWARE
# -------------------------------------------------------------

_cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()]
middleware = (
    [Middleware(CORSMiddleware, allow_origins=_cors_origins, allow_credentials=True,
                allow_methods=["GET", "POST"], allow_headers=["Content-Type"])]
    if _cors_origins else []
)

routes = [
    # System & Health
    Route("/api/health", health, methods=["GET"]),
    Route("/api/model", set_model, methods=["POST"]),
    
    # Authentication
    Route("/api/auth/signup", auth_signup, methods=["POST"]),
    Route("/api/auth/verify-email", auth_verify_email, methods=["POST"]),
    Route("/api/auth/resend-verification", auth_resend_verification, methods=["POST"]),
    Route("/api/auth/login", auth_login, methods=["POST"]),
    Route("/api/auth/forgot-password", auth_forgot_password, methods=["POST"]),
    Route("/api/auth/reset-password", auth_reset_password, methods=["POST"]),
    Route("/api/auth/me", auth_me, methods=["GET"]),
    Route("/api/auth/logout", auth_logout, methods=["POST"]),

    # User History
    Route("/api/history", get_history, methods=["GET"]),
    Route("/api/history/{item_id:int}", get_history_detail, methods=["GET"]),

    # YouTube SEO & Agents
    Route("/api/report", saved_report, methods=["GET"]),
    Route("/api/analyze", analyze, methods=["POST"]),
    Route("/api/quick-predict", quick_predict, methods=["POST"]),
    Route("/api/competitors", live_competitors, methods=["GET"]),

    # Static Web App (Landing page & Studio)
    Mount("/", app=StaticFiles(directory=str(WEB_DIR), html=True), name="frontend"),
]

app = Starlette(debug=False, routes=routes, middleware=middleware)
