# Staydia / Suncroft footage

Grassroots detection trains on **Suncroft clips from Staydia**, not SoccerNet broadcast.

## On disk (gitignored under `data/`)

| Path | What it is |
|------|------------|
| `data/suncroft/clip1.mp4` … `clip10.mp4` | ~1 min Staydia clips used for the ~600-frame extract |
| `data/frames/clip1/` … `clip10/` | JPEGs from `scripts/extract_frames.py` (uploaded to Roboflow) |

Do **not** commit Staydia videos or frames (`data/` is gitignored).

## Frame extract

```bash
python scripts/extract_frames.py data/suncroft/ --every 1 --max-frames 600
# or --every 2 on longer clips
```

## Why this footage

Broadcast YOLO weights miss far/small players on this high-wide Staydia view. The custom dataset is so detection works on the camera teams actually have.
