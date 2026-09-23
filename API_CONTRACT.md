# Crop Disease Assistant API Contract

This contract defines the one-day hackathon interface between Person A
(image quality and disease classifier) and Person B (backend/orchestrator).

## Person A: Image Analysis

### `POST /analyze`

Person A accepts a crop or leaf image and returns image-quality results,
classifier output, and an image-analysis decision.

The response has this JSON shape:

```json
{
  "quality": {
    "accepted": true,
    "blur_score": 641.85,
    "width": 345,
    "height": 490,
    "message": "Image quality is acceptable."
  },
  "prediction": {
    "crop": "Tomato",
    "disease": "Uncertain",
    "confidence": 0.4841
  },
  "decision": "REFER_TO_EXPERT",
  "message": "Insufficient confidence for automated diagnosis."
}
```

The `quality` object describes whether the image is usable for analysis.
`blur_score` is the returned image-quality score, and `width` and `height`
are the analyzed image dimensions.

The `prediction` object contains the detected crop, likely disease, and
classifier confidence. `confidence` is a numeric value from `0` to `1`,
inclusive.

Person A's `decision` is only the classifier/image-analysis decision. Valid
values are:

- `PROCEED`: Image analysis can proceed.
- `REFER_TO_EXPERT`: Image analysis does not provide sufficient confidence
  for automated diagnosis.
- `REJECT_IMAGE`: The image is not acceptable for analysis.

Person A must not calculate or authorize the final application treatment
decision. Person A's confidence and decision are inputs to Person B, not
permission to provide treatment.

## Person B: Backend and Orchestration

Person B receives:

- Person A's image-analysis response, including the prediction confidence.
- The farmer's reported symptoms.

Person B then:

1. Matches the farmer's symptoms against the verified knowledge base.
2. Performs deterministic confidence gating using the classifier confidence
   and symptom match score.
3. Selects exactly one final application decision: `TREATMENT`, `CLARIFY`, or
   `REFER`.

Person B may provide a treatment only when a verified knowledge-base record
contains both a treatment and its source. Person B must not invent treatment,
source, disease information, or agricultural recommendations.

### Final application decision meanings

- `TREATMENT`: A verified treatment and source are available.
- `CLARIFY`: More symptom information is needed.
- `REFER`: Confidence is too low, the disease is unknown, or no verified
  treatment and source are available.
