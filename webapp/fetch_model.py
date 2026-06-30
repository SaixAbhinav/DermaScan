"""Optionally download model.keras at startup.

If the MODEL_URL environment variable is set and model.keras is not already
present, download it into the model directory. This lets you deploy without
committing the large model file to git. No-op if MODEL_URL is unset or the model
already exists, so it is always safe to run before the server starts.
"""

from __future__ import annotations

import os
import sys
import urllib.request

from backend import config


def main() -> None:
    url = os.environ.get("MODEL_URL", "").strip()
    if not url:
        print("MODEL_URL not set - skipping model download.")
        return
    if config.MODEL_PATH.exists():
        print(f"Model already present at {config.MODEL_PATH} — skipping download.")
        return

    config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading model from {url} -> {config.MODEL_PATH} ...")
    try:
        urllib.request.urlretrieve(url, config.MODEL_PATH)
        print("Download complete.")
    except Exception as exc:  # noqa: BLE001
        print(f"WARNING: model download failed: {exc}", file=sys.stderr)
        # Don't crash startup — the app serves a 503 on /predict until a model exists.


if __name__ == "__main__":
    main()
