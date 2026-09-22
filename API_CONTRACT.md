# Crop Disease Assistant API Contract

This contract defines the one-day hackathon interface between Person A
(image quality and disease classifier) and Person B (backend/orchestrator).

## Person A: Image and Classification

Person A is responsible for:

- Checking whether the crop image is usable.
- Classifying the crop and likely disease.
- Returning the crop, disease, and classifier confidence.

Person A must return this JSON shape:

```json
{
  "crop": "Tomato",
  "disease": "Early Blight",
  "confidence": 0.87
}
```

`confidence` must be a numeric value from `0` to `1`, inclusive.

Person A must not calculate the final treatment decision. Classifier
confidence alone must never directly authorize treatment.

## Person B: Backend and Orchestration

Person B receives:

- Person A's classifier result.
- The farmer's reported symptoms.

Person B then:

1. Matches the farmer's symptoms against the knowledge base.
2. Performs deterministic confidence gating using the classifier confidence
   and symptom match score.
3. Selects exactly one decision: `TREATMENT`, `CLARIFY`, or `REFER`.

Person B may provide a treatment only when a verified knowledge-base record
contains both a treatment and its source. Person B must not invent treatment,
source, disease information, or agricultural recommendations.

### Decision meanings

- `TREATMENT`: A verified treatment and source are available.
- `CLARIFY`: More symptom information is needed.
- `REFER`: Confidence is too low, the disease is unknown, or no verified
  treatment and source are available.

## Valid classifier output

```json
{
  "crop": "Tomato",
  "disease": "Early Blight",
  "confidence": 0.87
}
```

## Invalid classifier output

The confidence value is greater than `1`, so this payload is invalid:

```json
{
  "crop": "Tomato",
  "disease": "Early Blight",
  "confidence": 1.2
}
```
