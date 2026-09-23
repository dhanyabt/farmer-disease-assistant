# HACKMINT - Person C

Farmer-facing Streamlit interface for the HACKMINT crop disease assistance
platform. This project connects image input and farmer symptoms to the Person B
orchestrator, which can combine them with Person A's image prediction.

## Run the demo

```powershell
cd HACKMINT-PersonC
..\venv\Scripts\python.exe -m streamlit run app.py
```

The default demo mode uses deterministic fixtures, so the high-confidence,
borderline, and low-confidence paths can be shown without a running backend.
Use symptom text containing `uncertain`, `mixed`, or `borderline` for the
borderline path, and `severe`, `unknown`, `many`, or `wilting` for the low path.

## Connect the live backend

Set `HACKMINT_BACKEND_URL` to the Person B orchestrator endpoint. Person C sends
an image as multipart form data and sends `crop_name`, `plant_part`, and
`symptoms` as form fields:

```powershell
$env:HACKMINT_BACKEND_URL = "http://localhost:8000/analyze"
..\venv\Scripts\python.exe -m streamlit run app.py
```

The adapter accepts either `disease` or `diagnosis`, either `confidence` or
`image_confidence`, and either `treatment` or `recommendation`, making it easy
to connect the existing Person A/B services without rebuilding them.

## Test

```powershell
..\venv\Scripts\python.exe -m unittest discover -s . -p "test_*.py"
```
