# Final Year Project

Computer vision countermeasure to attentional bias in video-assisted refereeing.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
ruff check src tests
```

## Demo

The `demo/` folder runs [Roboflow's soccer example](https://github.com/roboflow/sports/tree/main/examples/soccer) on a short sample clip (player boxes and a top-down pitch view).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/roboflow/sports.git
cd demo/sports/examples/soccer
pip install -r requirements.txt
./setup.sh
python main.py \
  --source_video_path data/clip8s.mp4 \
  --target_video_path output.mp4 \
  --device mps \
  --mode RADAR
```

Use `--device cpu` if MPS is not available. Weights, sample clips, and output videos are not committed.
