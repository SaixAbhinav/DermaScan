"""Model loading, preprocessing, and prediction.

The preprocessing here MUST match what the training notebook used:
    - load image as RGB
    - resize to 224x224
    - apply tensorflow.keras.applications.mobilenet.preprocess_input  (scales to [-1, 1])

Using a different normalization (e.g. dividing by 255) silently produces garbage
predictions, so this is centralized in one place.

The model is loaded lazily on first use so the web server can still start (and
serve the frontend / examples / About page) before the model has been trained.
"""

from __future__ import annotations

import json
import threading

import numpy as np
from PIL import Image

from . import config


class ModelNotAvailable(RuntimeError):
    """Raised when a prediction is requested but model artifacts are missing."""


class ModelService:
    def __init__(self) -> None:
        self._model = None
        self._labels: list[str] | None = None
        self._preprocess = None
        self._lock = threading.Lock()

    # ----- loading -------------------------------------------------------
    @property
    def available(self) -> bool:
        return config.MODEL_PATH.exists()

    def _load(self) -> None:
        """Load the model + labels once (thread-safe)."""
        if self._model is not None:
            return
        with self._lock:
            if self._model is not None:
                return
            if not config.MODEL_PATH.exists():
                raise ModelNotAvailable(
                    f"model.keras not found at {config.MODEL_PATH}. "
                    "Train the model (see the training notebook) and place the "
                    "exported artifacts in the model/ directory."
                )

            # Imported here so the server can boot without TensorFlow installed
            # or before a model exists.
            import tensorflow as tf
            from tensorflow.keras.applications.mobilenet import preprocess_input

            def top_2_accuracy(y_true, y_pred):
                return tf.keras.metrics.top_k_categorical_accuracy(y_true, y_pred, k=2)

            def top_3_accuracy(y_true, y_pred):
                return tf.keras.metrics.top_k_categorical_accuracy(y_true, y_pred, k=3)

            self._model = tf.keras.models.load_model(
                config.MODEL_PATH,
                custom_objects={
                    "top_2_accuracy": top_2_accuracy,
                    "top_3_accuracy": top_3_accuracy,
                },
            )
            self._preprocess = preprocess_input
            self._labels = self._load_labels()

    def _load_labels(self) -> list[str]:
        if config.CLASS_INDICES_PATH.exists():
            with open(config.CLASS_INDICES_PATH) as f:
                class_indices = json.load(f)
            # sort class names by their integer index -> authoritative output order
            return [c for c, _ in sorted(class_indices.items(), key=lambda kv: kv[1])]
        return list(config.DEFAULT_CLASS_ORDER)

    @property
    def labels(self) -> list[str]:
        self._load()
        return self._labels  # type: ignore[return-value]

    @property
    def model(self):
        self._load()
        return self._model

    # ----- preprocessing & prediction ------------------------------------
    def preprocess(self, img: Image.Image) -> np.ndarray:
        """RGB -> 224x224 -> mobilenet.preprocess_input -> (1, 224, 224, 3)."""
        self._load()
        img = img.convert("RGB").resize((config.IMAGE_SIZE, config.IMAGE_SIZE))
        arr = np.asarray(img, dtype=np.float32)
        arr = self._preprocess(arr)  # type: ignore[misc]
        return np.expand_dims(arr, axis=0)

    def predict(self, img: Image.Image) -> dict[str, float]:
        """Return {class_code: probability} for all classes."""
        batch = self.preprocess(img)
        probs = self.model.predict(batch, verbose=0)[0]
        return {label: float(p) for label, p in zip(self.labels, probs)}


# Singleton used across the app.
service = ModelService()
