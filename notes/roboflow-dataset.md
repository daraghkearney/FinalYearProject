# Roboflow dataset — Amateur Match Detection

Label Staydia/Suncroft frames here. Roboflow is the **dataset hub**. Real YOLOv8 training is in **Google Colab** (`notebooks/train_suncroft_yolov8.ipynb`), not Roboflow’s hosted train as the main path.

## Project

- Workspace: `daraghs-workspace-oiqly`
- Project: `amateur-match-detection`
- Classes: `player`, `ball`, `referee`
- **v1** — Soccer detection baseline (~600 images)
- **v2** — Soccer detection with test1 frames (612 images); Colab train + BotSort done → `weights/best_v2.pt` (gitignored)

Export for Colab: **Download Dataset** → format **YOLOv8** → **Show download code**.

Do not put API keys in the repo. Use Colab secrets or a local `.env` (gitignored).

## Annotation rules

- **player** — full body box when you can tell it is a player. Include far/small players if you are sure.
- **ball** — only when clearly visible.
- **referee** — separate from players (kit usually different).
- Skip blobs you cannot identify.
- One box per person; do not merge two players into one box.
- Prefer consistency over perfect edges.

Team colours (home vs away) are **not** YOLO classes. HSV / kit split comes after tracking.

## New versions (v3+)

Batch ~50–100 new or fixed images (hard cases, referee/ball misses), then **Generate** a Version. In Colab bump `VERSION` and the run name, re-train, save `weights/best_vN.pt`.

## Progress log

| Date | Version | Images | Notes |
|------|---------|--------|-------|
| Nov 2026 | v1 | ~600 | Baseline labelled set |
| Nov 2026 | v2 | 612 | + reviewed test1 frames; Colab yolov8s imgsz 960 → best_v2; BotSort on short clip OK; player↔referee flicker / ID fragmentation expected |

## After labelling / train

1. Create a Version in Roboflow.
2. Colab: download as YOLOv8, train `yolov8s.pt`, imgsz 960, ~50 epochs.
3. Keep `best_vN.pt` under `weights/` locally (gitignored).
