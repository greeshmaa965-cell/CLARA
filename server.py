"""CLARA Unified Backend API & Web Server.
Exposes REST endpoints for Normalization, Recommendation, Diffing, and Compilation,
and serves the static Configuration Studio frontend.
"""

import os
import sys
import tempfile
import subprocess
from typing import Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

# Ensure repository root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.normalization.normalizer import normalize_request
from src.recommendations.engine import generate_alternatives, DEFAULT_CATALOG_PATH, load_catalog
from src.config_diff.diff_engine import compute_explainable_diff

CLARA_EXE = BASE_DIR / "clara.exe"
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="CLARA API Server",
    description="Backend API for CLARA (Cloud Language, Analysis, and Resource Architecture)",
    version="0.2.0-dev"
)

# Enable CORS for external frontend instances or dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://clara-frontend-zeta.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
@app.get("/health")
def health_check():
    """Health check endpoint providing runtime and compiler status."""
    return {
        "status": "healthy",
        "app": "CLARA (Cloud Language, Analysis, and Resource Architecture)",
        "version": "0.2.0-dev",
        "compiler_available": CLARA_EXE.is_file(),
        "services": {
            "normalization": "active",
            "recommendations": "active",
            "diff_engine": "active",
            "c_compiler": "active" if CLARA_EXE.is_file() else "unavailable"
        }
    }


@app.get("/api/catalog")
def get_catalog():
    """Returns the loaded hardware pricing and instance catalogue snapshot."""
    try:
        return load_catalog(str(DEFAULT_CATALOG_PATH))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load catalogue: {str(e)}")


@app.post("/api/normalize")
def api_normalize(payload: dict[str, Any] = Body(...)):
    """Normalizes natural language or structured form input into canonical JSON and CLARA DSL."""
    try:
        result = normalize_request(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Normalization failed: {str(e)}")


@app.post("/api/recommend")
def api_recommend(payload: dict[str, Any] = Body(...)):
    """Generates constraint-aware alternatives (Cost, Balanced, Performance) from canonical request."""
    try:
        # Check if wrapped in canonical_request key or top-level
        req = payload.get("canonical_request", payload)
        if "normalized_request" in req:
            req = req["normalized_request"]
        result = generate_alternatives(req)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Recommendation generation failed: {str(e)}")


@app.post("/api/diff")
def api_diff(payload: dict[str, Any] = Body(...)):
    """Computes explainable diff between user input requirements and a candidate architecture."""
    try:
        orig = payload.get("original_request")
        if not orig:
            orig = payload.get("original")
        cand = payload.get("candidate")
        include_unchanged = payload.get("include_unchanged", True)

        if not orig or not cand:
            raise HTTPException(status_code=422, detail="Both 'original_request' and 'candidate' must be supplied.")

        # If wrapped in normalized_request
        if "normalized_request" in orig:
            orig = orig["normalized_request"]

        diff = compute_explainable_diff(orig, cand, include_unchanged=include_unchanged)
        return diff
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Diff generation failed: {str(e)}")


@app.post("/api/compile")
def api_compile(payload: dict[str, Any] = Body(...)):
    """Compiles CLARA DSL code using the native clara.exe compiler driver."""
    if not CLARA_EXE.is_file():
        raise HTTPException(status_code=503, detail="CLARA C compiler binary (clara.exe) not found.")

    source_code = payload.get("source", "").strip()
    target = payload.get("target", "ir").lower()  # ir, terraform, ast, check, tokens

    if not source_code:
        raise HTTPException(status_code=422, detail="Missing or empty 'source' DSL code.")

    flag_map = {
        "ir": "--ir",
        "terraform": "--terraform",
        "ast": "--ast",
        "tokens": "--tokens",
        "check": "--check"
    }
    flag = flag_map.get(target, "--ir")

    # Write source to a temporary .clara file
    with tempfile.NamedTemporaryFile(suffix=".clara", delete=False, mode="w", encoding="utf-8") as tmp:
        tmp.write(source_code)
        tmp_path = tmp.name

    try:
        proc = subprocess.run(
            [str(CLARA_EXE), flag, tmp_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        status = "SUCCESS" if proc.returncode == 0 else "ERROR"
        return {
            "status": status,
            "target": target,
            "exit_code": proc.returncode,
            "output": proc.stdout,
            "error": proc.stderr if proc.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Compiler process timed out.")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# Serve static frontend files if frontend directory exists
if FRONTEND_DIR.is_dir():
    app.mount("/styles", StaticFiles(directory=str(FRONTEND_DIR / "styles")), name="styles")
    app.mount("/src", StaticFiles(directory=str(FRONTEND_DIR / "src")), name="src")
    if (FRONTEND_DIR / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")

    @app.get("/")
    def serve_frontend_index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))


def run():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 60)
    print("CLARA Unified Server Starting...")
    print("   Backend API:  http://127.0.0.1:8000/api")
    print("   API Docs:     http://127.0.0.1:8000/docs")
    print("   Web Frontend: http://127.0.0.1:8000/")
    print("=" * 60)
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    run()
