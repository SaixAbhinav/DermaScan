# DermaScan — Ubiquitous Language

Glossary for the DermaScan educational demo. Terms here are the canonical
vocabulary for the UI copy, code, and design discussions. This file is a
glossary only — no implementation details, no specs.

## Audience & framing

- **Public educational demo** — DermaScan's product category. The audience is a
  non-clinician visitor (recruiter, layperson, the author) whose only intended
  action is to *understand what the model does*, never to act medically on the
  output. Register matches the author's Smart Signal project: portfolio-grade,
  technical-but-approachable, demo-first, honest about limitations.

- **Visitor** — the person using the demo. Explicitly *not* a patient and not a
  clinician. Design must actively suppress any reading of the page as diagnosis.

## The result

- **Best match** — the model's top-1 class for an image, framed as *the model's
  guess*, not a diagnosis or verdict. The result headline names the best match
  as a guess ("Best match: Melanoma"), never as a finding about the visitor.

- **Match strength** — the canonical term for a class's probability (softmax
  output), shown as a percentage ("87% match"). Framed as *how strongly the
  image matches this class*, i.e. image-to-class similarity — deliberately not a
  diagnostic probability. Replaces the banned word [[Confidence]].

- **Guess** — canonical framing for any model output shown to the visitor. The
  page presents *how the model classifies an image and how sure it is of its own
  guess*, not a claim about the visitor's skin.

## Risk

- **Risk category** — the benign / premalignant / malignant classification of a
  *lesion type* (akiec, bcc, mel, …). It is a fact about the category ("melanoma
  is a type of skin cancer"), never a finding about the visitor's image. On the
  result page it is presented as calm, neutral category-education — no alarm-red
  verdict styling. Emotional prominence belongs to the "this is a guess — see a
  dermatologist" message, not to the malignancy tag.

- **In-result caveat** — a single calm sentence placed inside the result card,
  directly under the [[Best match]] headline, reminding the visitor the result is
  a [[Guess]] about an example image and not a diagnosis. It is the *timed
  intervention* at the moment of possible misreading; the top-of-page banner is
  *arrival context*. Both exist; neither uses alarm styling (over-disclaiming
  makes the demo feel more like a real medical tool, not less).

## Input & model limits

- **Dermoscopy image** — the only input the model understands: a magnified,
  specialist image of a lesion (the HAM10000 domain). Phone photos, selfies, and
  non-skin images are **out of domain** and produce meaningless [[Match
  strength]] by design. Copy must scope every result to dermoscopy example
  images and say so plainly.

- **Weak match** — the state where the top [[Match strength]] is low / the
  distribution across classes is flat, i.e. the model is effectively guessing
  (often because the input is out of domain). Surfaced as an honest "the model
  isn't matching this strongly to any class — it may not be a dermoscopy image"
  hint, turning an out-of-domain failure into an educational moment. Detected
  cheaply from the existing scores; DermaScan deliberately does **not** build a
  real "is this a valid dermoscopy image?" detector.

- **Example gallery** — the *primary* input path, celebrated and led-with (as
  Smart Signal leads with its live demo). Uploading your own image is the
  *secondary* "bring your own dermoscopy image" path.

- **Grad-CAM** — an opt-in "look inside the model" overlay, framed as *where the
  model looked* (which pixels most influenced its [[Guess]]), never as a medical
  finding. Banned verbs in its copy: "detected", "located", "found the lesion" —
  it highlights influential pixels, and on a [[Weak match]] it will happily
  highlight a cat's ear. Shows the original image first; the visitor opts in.

## Banned terms

- **"Confidence"** — BANNED in visitor-facing copy. A layperson reads
  "87% confidence" as *"you have an 87%-likely melanoma"* (diagnostic
  probability), when it only means the model's certainty in its own guess. Use a
  replacement that clearly scopes certainty to the model. Use [[Match strength]].

- **"Diagnosis" / "verdict" / diagnosis-style styling** — the result is a
  [[Guess]], not a diagnosis. Avoid copy or visual grammar (verdict headlines,
  red alert verdict badges) that reads as a medical finding.
