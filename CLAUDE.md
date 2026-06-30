# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A deep-learning project that classifies skin lesion dermoscopy images from the HAM10000 dataset into 7 diagnostic classes (akiec, bcc, bkl, df, mel, nv, vasc) using a MobileNet-based transfer-learning CNN in TensorFlow/Keras.

The repository currently consists of two Jupyter notebooks and a README — there is no installable package, build system, test suite, or CLI. Work happens by editing/running notebook cells in Jupyter.

## Repository Structure

- [Skin lesion Analyizer.ipynb](Skin%20lesion%20Analyizer.ipynb) — the main pipeline: prepares train/val directories from `HAM10000_metadata.csv`, deduplicates images by `lesion_id`, splits the held-out validation set *before* augmentation (to avoid leaking augmented duplicates of val images into train), augments minority classes up to ~6000 images each via `ImageDataGenerator`, builds a model from `MobileNet` (drops the last 5 layers, adds `Flatten` → `Dropout` → `Dense(7, softmax)`, fine-tunes only the last 23 layers), trains with class weights that up-weight melanoma (class index 4), and evaluates with a confusion matrix and classification report.
- [skin_cancer_process.ipynb](skin_cancer_process.ipynb) — exploratory data analysis on the HAM10000 metadata (null handling/imputation on `age`, column renames, and seaborn plots of diagnosis distribution by age bin, sex, and lesion localization). Written for a Google Colab environment (paths under `/content/drive/MyDrive/Datasets/...`).
- [README.md](README.md) — project description, dataset/tooling overview.

## Important Environment Notes

- File paths are hardcoded and environment-specific, not portable:
  - `Skin lesion Analyizer.ipynb` assumes a local Windows path: `C:/Windows/System32/Data Analytics/...` for the HAM10000 CSV, image folders (`HAM10000_images_part_1`/`_2`), and the `base_dir` train/val split it creates on disk.
  - `skin_cancer_process.ipynb` assumes a Google Colab path: `/content/drive/MyDrive/Datasets/HAM10000_metadata.csv`.
  - When reusing these notebooks elsewhere, update these path constants first.
- The dataset (HAM10000, from Kaggle) is not included in the repo and must be downloaded separately.
- Running the full pipeline mutates the filesystem: it creates a `base_dir/` with per-class `train_dir`/`val_dir` subfolders and writes thousands of augmented images to disk. This is a one-time data-prep step, not something to redo per notebook run.
- Saved model artifacts (`model.keras`, `model.json`, `model.weights.h5`) are written next to/under the hardcoded data path, not into the repo.

## Working in This Repo

- There is no `requirements.txt`/`environment.yml`. Dependencies (inferred from notebook imports): `tensorflow`/`keras`, `numpy`, `pandas`, `scikit-learn`, `opencv`/`PIL`, `matplotlib`, `seaborn`.
- There are no automated tests or lint config — validate notebook changes by re-running the relevant cells and checking that `model.evaluate` / `classification_report` output still makes sense.
- Custom Keras metrics `top_2_accuracy`/`top_3_accuracy` (wrapping `top_k_categorical_accuracy`) are redefined in multiple cells and must be registered via `tf.keras.utils.get_custom_objects()` before loading a saved model that used them.
