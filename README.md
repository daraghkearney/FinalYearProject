# Final year project

A computer-vision countermeasure to attentional bias in video-assisted refereeing.

This repository is the judged artefact. Off-the-shelf detection (YOLO, ByteTrack, Roboflow sports) is used as-is. The work that is mine lives in the rules engine, the error model, and the web app.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ruff check src tests
```

CI runs `ruff check` on every push to `main`.
