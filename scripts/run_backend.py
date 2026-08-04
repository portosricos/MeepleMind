import sys
import uvicorn
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def start_server():
    print("Starting MeepleMind FastAPI Backend Server on http://localhost:8000...")
    print("OpenAPI Swagger Documentation available at http://localhost:8000/docs")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    start_server()
