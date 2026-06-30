"""Static, human-readable information for each of the 7 HAM10000 classes.

This is the single source of truth for the full diagnosis name, a plain-language
description, and a benign/malignant risk indicator shown in the UI. Keyed by the
short class code used by the model (akiec, bcc, bkl, df, mel, nv, vasc).

NOTE: This is educational decision-support content, not medical advice. The risk
levels are coarse categories intended to convey relative concern, not a diagnosis.
"""

from __future__ import annotations

# risk levels, ordered from least to most concerning
RISK_BENIGN = "benign"
RISK_PREMALIGNANT = "premalignant"
RISK_MALIGNANT = "malignant"

LESION_INFO: dict[str, dict] = {
    "akiec": {
        "code": "akiec",
        "name": "Actinic keratoses / intraepithelial carcinoma",
        "short_name": "Actinic keratosis (Bowen's)",
        "risk": RISK_PREMALIGNANT,
        "description": (
            "Rough, scaly patches caused by years of sun exposure. Considered "
            "pre-cancerous (and Bowen's disease is an early, in-situ carcinoma) "
            "because they can progress to squamous cell carcinoma if untreated."
        ),
    },
    "bcc": {
        "code": "bcc",
        "name": "Basal cell carcinoma",
        "short_name": "Basal cell carcinoma",
        "risk": RISK_MALIGNANT,
        "description": (
            "The most common form of skin cancer. It grows slowly and rarely "
            "spreads, but should be treated because it can invade and damage "
            "surrounding tissue."
        ),
    },
    "bkl": {
        "code": "bkl",
        "name": "Benign keratosis-like lesions",
        "short_name": "Benign keratosis",
        "risk": RISK_BENIGN,
        "description": (
            "A group of harmless lesions (seborrheic keratoses, solar lentigines, "
            "lichen-planus-like keratoses). Non-cancerous, though they can "
            "visually resemble more serious lesions."
        ),
    },
    "df": {
        "code": "df",
        "name": "Dermatofibroma",
        "short_name": "Dermatofibroma",
        "risk": RISK_BENIGN,
        "description": (
            "A common benign fibrous skin nodule, often on the legs. Harmless and "
            "usually requires no treatment."
        ),
    },
    "mel": {
        "code": "mel",
        "name": "Melanoma",
        "short_name": "Melanoma",
        "risk": RISK_MALIGNANT,
        "description": (
            "The most dangerous form of skin cancer. It can spread to other organs "
            "if not caught early, so a suspected melanoma warrants prompt "
            "evaluation by a dermatologist."
        ),
    },
    "nv": {
        "code": "nv",
        "name": "Melanocytic nevi",
        "short_name": "Mole (nevus)",
        "risk": RISK_BENIGN,
        "description": (
            "Ordinary moles. Benign collections of pigment cells. Very common and "
            "usually harmless, but changes in size, shape, or colour are worth "
            "checking."
        ),
    },
    "vasc": {
        "code": "vasc",
        "name": "Vascular lesions",
        "short_name": "Vascular lesion",
        "risk": RISK_BENIGN,
        "description": (
            "Lesions made of blood vessels (angiomas, angiokeratomas, pyogenic "
            "granulomas, haemorrhage). Almost always benign."
        ),
    },
}

# Classes the UI should flag as needing attention (not benign).
CONCERNING = {RISK_PREMALIGNANT, RISK_MALIGNANT}


def get_info(code: str) -> dict:
    """Return the info dict for a class code, or a safe fallback."""
    return LESION_INFO.get(
        code,
        {
            "code": code,
            "name": code,
            "short_name": code,
            "risk": "unknown",
            "description": "No information available for this class.",
        },
    )


def is_concerning(code: str) -> bool:
    """True if the class is pre-malignant or malignant."""
    return get_info(code).get("risk") in CONCERNING


DISCLAIMER = (
    "This tool is a machine-learning demo for educational purposes only. "
    "It is NOT a medical device and must not be used for diagnosis. "
    "Always consult a qualified dermatologist about any skin concern."
)
