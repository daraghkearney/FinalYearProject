# Supervisor demo (off-the-shelf)

This is **not** the project. It is Roboflow's existing soccer example: YOLO
player boxes plus a top-down radar. Say that out loud when you show it.

Upstream: https://github.com/roboflow/sports/tree/main/examples/soccer

`demo/sports/examples/soccer/main.py` is that file. Lines marked `LOCAL FYP`
are the only edits: skip the live window when there is no display, and
do not crash on empty teams, missing tracker IDs, or a failed pitch overlay.
Detection, tracking, team colours, and radar are still Roboflow's.

## One-time setup

From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/roboflow/sports.git
cd demo/sports/examples/soccer
pip install -r requirements.txt
./setup.sh
```

`setup.sh` pulls their sample clips and football-trained weights into `data/`.
Those files stay gitignored.

## Run

Apple Silicon:

Use absolute paths for the output file. An 8-second clip is enough for the meeting.

```bash
cd demo/sports/examples/soccer
python main.py \
  --source_video_path data/clip8s.mp4 \
  --target_video_path /Users/daraghkearney/Desktop/FinalYearProject/demo/output/radar.mp4 \
  --device mps \
  --mode RADAR
```

Quicker check (boxes only, no radar):

```bash
python main.py \
  --source_video_path data/clip8s.mp4 \
  --target_video_path /Users/daraghkearney/Desktop/FinalYearProject/demo/output/players.mp4 \
  --device mps \
  --mode PLAYER_DETECTION
```

On Intel Mac or no MPS, use `--device cpu`.

Open the output video. That is the demo.
