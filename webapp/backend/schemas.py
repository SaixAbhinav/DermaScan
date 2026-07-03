"""Pydantic response models for the API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ClassScore(BaseModel):
    code: str            # e.g. "mel"
    name: str            # full diagnosis name
    short_name: str
    probability: float   # 0..1
    risk: str            # benign | premalignant | malignant | unknown
    concerning: bool


class PredictionResponse(BaseModel):
    predicted: ClassScore           # top-1
    top3: list[ClassScore]          # top-3 by probability
    all_scores: list[ClassScore]    # all 7, sorted by probability desc
    description: str                 # description of the predicted class
    gradcam_png: str | None = None  # base64-encoded PNG overlay, if available
    disclaimer: str
    weak_match: bool = False        # top match strength is low / distribution is flat


class ExampleImage(BaseModel):
    code: str
    name: str
    url: str


class AboutResponse(BaseModel):
    # `model_available` would otherwise collide with pydantic's protected
    # "model_" namespace; disable that check for this response.
    model_config = ConfigDict(protected_namespaces=())

    model_available: bool
    accuracy: float | None = None
    labels: list[str] = []
    report: dict | None = None      # full per-class precision/recall/f1
    confusion_matrix_url: str | None = None
    disclaimer: str
