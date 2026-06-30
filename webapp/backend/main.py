"""FastAPI application: prediction API + static frontend.

Run locally from the webapp/ directory:
    uvicorn backend.main:app --reload
Then open http://127.0.0.1:8000
"""

from __future__ import annotations

import json
import io

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

from . import config
from . import lesion_info
from .model_service import service, ModelNotAvailable
from .schemas import (
    AboutResponse,
    ClassScore,
    ExampleImage,
    PredictionResponse,
)

app = FastAPI(title="Skin Lesion Classifier", version="1.0.0")


def _class_score(code: str, probability: float) -> ClassScore:
    info = lesion_info.get_info(code)
    return ClassScore(
        code=code,
        name=info["name"],
        short_name=info["short_name"],
        probability=probability,
        risk=info["risk"],
        concerning=lesion_info.is_concerning(code),
    )


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "model_available": service.available}


@app.post("/api/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)) -> PredictionResponse:
    raw = await file.read()
    try:
        img = Image.open(io.BytesIO(raw))
        img.load()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="Could not read image file.")

    try:
        probs = service.predict(img)
    except ModelNotAvailable as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    scores = sorted(
        (_class_score(code, p) for code, p in probs.items()),
        key=lambda s: s.probability,
        reverse=True,
    )
    predicted = scores[0]

    # Grad-CAM overlay for the predicted class (best-effort).
    gradcam_png = None
    try:
        from .gradcam import gradcam_base64

        class_index = service.labels.index(predicted.code)
        gradcam_png = gradcam_base64(img, class_index)
    except Exception:  # noqa: BLE001 - never let visualization break prediction
        gradcam_png = None

    return PredictionResponse(
        predicted=predicted,
        top3=scores[:3],
        all_scores=scores,
        description=lesion_info.get_info(predicted.code)["description"],
        gradcam_png=gradcam_png,
        disclaimer=lesion_info.DISCLAIMER,
    )


@app.get("/api/examples", response_model=list[ExampleImage])
def examples() -> list[ExampleImage]:
    if not config.EXAMPLES_DIR.is_dir():
        return []
    out: list[ExampleImage] = []
    for path in sorted(config.EXAMPLES_DIR.glob("*.jpg")):
        code = path.stem
        out.append(
            ExampleImage(
                code=code,
                name=lesion_info.get_info(code)["short_name"],
                url=f"/assets/examples/{path.name}",
            )
        )
    return out


@app.get("/api/about", response_model=AboutResponse)
def about() -> AboutResponse:
    accuracy = None
    labels: list[str] = []
    report = None
    if config.METRICS_PATH.exists():
        with open(config.METRICS_PATH) as f:
            data = json.load(f)
        report = data.get("report")
        labels = data.get("labels", [])
        if report and "accuracy" in report:
            accuracy = report["accuracy"]

    cm_url = (
        "/assets/confusion_matrix.png"
        if config.CONFUSION_MATRIX_PATH.exists()
        else None
    )
    return AboutResponse(
        model_available=service.available,
        accuracy=accuracy,
        labels=labels,
        report=report,
        confusion_matrix_url=cm_url,
        disclaimer=lesion_info.DISCLAIMER,
    )


# --- static files ----------------------------------------------------------
# Model artifacts (example images, confusion matrix) served read-only.
if config.MODEL_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=str(config.MODEL_DIR)), name="assets")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(config.FRONTEND_DIR / "index.html"))


# Frontend assets (style.css, app.js, ...). Mounted last so it doesn't shadow
# the /api routes above.
if config.FRONTEND_DIR.is_dir():
    app.mount(
        "/", StaticFiles(directory=str(config.FRONTEND_DIR), html=True), name="frontend"
    )
