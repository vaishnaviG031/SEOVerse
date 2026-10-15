import os
import sys
from pathlib import Path

# Add project root to sys.path so all imports work seamlessly on Vercel
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import the main Starlette ASGI application
from api_server import app
