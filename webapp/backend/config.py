"""Configuration and artifact paths for the web app.

The model artifacts produced by the training notebook's export cell live in
MODEL_DIR. Override with the MODEL_DIR environment variable when deploying.

Expected files in MODEL_DIR:
    model.keras           - the trained Keras model
    class_indices.json    - {"akiec": 0, ..., "vasc": 6}
    metrics.json          - accuracy + classification report (for the About page)
    confusion_matrix.png  - confusion matrix image (for the About page)
    examples/<class>.jpg  - one sample image per class (demo gallery)
"""

from __future__ import annotations

import os
from pathlib import Path

# webapp/ root (parent of this backend/ package)
BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = Path(os.environ.get("MODEL_DIR", BASE_DIR / "model"))

MODEL_PATH = MODEL_DIR / "model.keras"
CLASS_INDICES_PATH = MODEL_DIR / "class_indices.json"
METRICS_PATH = MODEL_DIR / "metrics.json"
CONFUSION_MATRIX_PATH = MODEL_DIR / "confusion_matrix.png"
EXAMPLES_DIR = MODEL_DIR / "examples"

FRONTEND_DIR = BASE_DIR / "frontend"

# Model input size (MobileNet, as used in training).
IMAGE_SIZE = 224

# Fallback class order if class_indices.json is missing. Matches the alphabetical
# folder order ImageDataGenerator produces (akiec=0 ... vasc=6).
DEFAULT_CLASS_ORDER = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]
