"""Grad-CAM heatmap generation.

Produces a class-activation heatmap overlay showing which regions of the image
most influenced the prediction. Returned as a base64-encoded PNG so it can be
embedded directly in the JSON response and rendered in the browser.

We target the last 4-D (convolutional) layer of the model. For the MobileNet
backbone used here that is ``conv_pw_13_relu``, but we locate it dynamically so
the code keeps working if the architecture changes.
"""

from __future__ import annotations

import base64
import io

import numpy as np
from PIL import Image

from . import config
from .model_service import service


def _find_last_conv_layer(model):
    """Return the name of the last layer with a 4-D output (a feature map)."""
    for layer in reversed(model.layers):
        try:
            shape = layer.output.shape
        except AttributeError:
            continue
        if len(shape) == 4:
            return layer.name
    raise ValueError("No 4-D convolutional layer found for Grad-CAM.")


def _compute_heatmap(batch: np.ndarray, class_index: int) -> np.ndarray:
    """Grad-CAM heatmap in [0,1], shaped like the target conv feature map."""
    import tensorflow as tf

    model = service.model
    last_conv = _find_last_conv_layer(model)
    grad_model = tf.keras.models.Model(
        model.inputs, [model.get_layer(last_conv).output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_out, preds = grad_model(batch)
        loss = preds[:, class_index]

    grads = tape.gradient(loss, conv_out)
    pooled = tf.reduce_mean(grads, axis=(0, 1, 2))          # per-channel weights
    conv_out = conv_out[0]
    heatmap = conv_out @ pooled[..., tf.newaxis]            # weighted sum
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0)                        # ReLU
    max_val = tf.reduce_max(heatmap)
    if max_val > 0:
        heatmap = heatmap / max_val
    return heatmap.numpy()


def _overlay(img: Image.Image, heatmap: np.ndarray, alpha: float = 0.4) -> Image.Image:
    """Blend a 'jet'-coloured heatmap over the original (resized) image."""
    from matplotlib import cm

    size = (config.IMAGE_SIZE, config.IMAGE_SIZE)
    base = img.convert("RGB").resize(size)

    # Upscale heatmap to image size and colourize with the jet colormap.
    hm_img = Image.fromarray(np.uint8(heatmap * 255)).resize(size, Image.BILINEAR)
    hm = np.asarray(hm_img, dtype=np.float32) / 255.0
    colored = cm.jet(hm)[:, :, :3]                          # drop alpha channel
    colored = Image.fromarray(np.uint8(colored * 255))

    return Image.blend(base, colored, alpha)


def gradcam_base64(img: Image.Image, class_index: int) -> str:
    """Return a base64 'data:image/png' string of the Grad-CAM overlay."""
    batch = service.preprocess(img)
    heatmap = _compute_heatmap(batch, class_index)
    overlay = _overlay(img, heatmap)

    buf = io.BytesIO()
    overlay.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
