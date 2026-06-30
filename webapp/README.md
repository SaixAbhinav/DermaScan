# DermaScan — Skin Lesion Classifier Web App

A deployable FastAPI + vanilla-JS web app that serves the HAM10000 MobileNet
model. Upload a dermoscopy image and get a prediction with top-3 / all-7
probability bars, a Grad-CAM heatmap, plain-language lesion info with a
benign/malignant risk flag, built-in example images, and an About page with the
model's accuracy and confusion matrix.

> ⚠️ **Educational demo only — not a medical device.**

## Architecture

```
webapp/
├── backend/
│   ├── main.py           FastAPI app: /api/predict, /api/examples, /api/about + static
│   ├── model_service.py  loads model.keras, preprocessing (224 + mobilenet.preprocess_input)
│   ├── gradcam.py        Grad-CAM overlay (last conv layer), returns base64 PNG
│   ├── lesion_info.py    per-class names, descriptions, risk levels, disclaimer
│   ├── schemas.py        Pydantic response models
│   └── config.py         artifact paths (override with MODEL_DIR)
├── frontend/             index.html · style.css · app.js (single page)
├── model/                trained artifacts (gitignored — see model/README.md)
├── requirements.txt
├── render.yaml / Procfile / fetch_model.py   deployment
```

The API and model are decoupled: the server **starts without a trained model**
(frontend + About page still load); `/api/predict` returns HTTP 503 until
`model/model.keras` exists.

## 1. Train the model (prerequisite)

The app needs artifacts produced by the export cell in
[`../Skin lesion Analyizer.ipynb`](../Skin%20lesion%20Analyizer.ipynb). Training
is GPU-heavy — use Google Colab or Kaggle (free GPU):

1. Download HAM10000 from Kaggle.
2. Open the notebook and set the data location (the first config cell):
   - Colab:  `DATA_ROOT=/content/drive/MyDrive/Datasets/HAM10000`
   - Kaggle: `INPUT_DIR=/kaggle/input/skin-cancer-mnist-ham10000` and a writable
     `BASE_DIR`/`OUTPUT_DIR` (e.g. `/kaggle/working`)
   These are read from environment variables, so set them before launching
   Jupyter, or just edit the defaults in that cell.
3. Run all cells. The final **export cell** writes to `OUTPUT_DIR`:
   `model.keras`, `class_indices.json`, `metrics.json`, `confusion_matrix.png`,
   and `examples/<class>.jpg`.
4. Copy those into `webapp/model/` (or point `MODEL_DIR` at them).

## 2. Run locally

```bash
cd skin_cancer_prediction/webapp
python -m venv .venv && . .venv/Scripts/activate   # Windows; use bin/activate on macOS/Linux
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Open <http://127.0.0.1:8000>. Interactive API docs at `/docs`.

## 3. Deploy (Render)

1. Push the repo to GitHub.
2. Render → **New → Blueprint**, select the repo (`render.yaml` sets root dir to
   `skin_cancer_prediction/webapp`).
3. Provide the model one of two ways:
   - **git-LFS:** track `model/model.keras` (+ the json/png) with LFS and commit.
   - **URL download:** host `model.keras` somewhere with a direct link and set the
     `MODEL_URL` env var; `fetch_model.py` downloads it at startup.

Notes:
- `tensorflow-cpu` keeps the build small. The free tier (512 MB RAM) is tight for
  TensorFlow — if it OOMs, use the **starter** instance (already set in
  `render.yaml`) or deploy to Hugging Face Spaces instead.
- Set `MODEL_DIR` if your artifacts live outside `webapp/model/`.

## API reference

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/predict` | multipart `file` → predicted class, top-3, all-7 scores, lesion info, Grad-CAM PNG |
| GET | `/api/examples` | bundled example images (one per class) |
| GET | `/api/about` | accuracy + per-class metrics + confusion-matrix URL |
| GET | `/api/health` | liveness + whether a model is loaded |
