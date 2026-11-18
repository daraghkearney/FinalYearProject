"""Compare Roboflow/YOLO boxes to SoccerNet Mask R-CNN boxes on the 8s clip.

SoccerNet tracking GT is not on this United-Arsenal game. The public player
boxes for this match are Mask R-CNN features at 2 fps. This script lines those
up with YOLO on the same 8 seconds (10:00-10:08 of the first half).
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]
GAME = (
    ROOT
    / "data/soccernet/england_epl/2014-2015"
    / "2015-05-17 - 18-00 Manchester United 1 - 1 Arsenal"
)
CLIP = ROOT / "data/soccernet/united_arsenal_8s.mp4"
WEIGHTS = ROOT / "demo/sports/examples/soccer/data/football-player-detection.pt"
OUT_JSON = ROOT / "data/soccernet/box_compare.json"
OUT_JPG = ROOT / "demo/output/soccernet_box_compare.jpg"

CLIP_START_S = 600.0  # 10:00, same trim as FIN-10
# OpenCV trim is ~10 frames behind the 2 fps Mask R-CNN clock (checked by IoU sweep).
FRAME_OFFSET = 10
SN_FPS = 2.0
PERSON_CLASS_IDS = {1, 2, 3}  # goalkeeper, player, referee
IOU_HIT = 0.5


def iou(a: np.ndarray, b: np.ndarray) -> float:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    if inter <= 0:
        return 0.0
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def centre(box: np.ndarray) -> np.ndarray:
    return np.array([(box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0])


def feet(box: np.ndarray) -> np.ndarray:
    # bottom-centre: the point that matters for an offside line
    return np.array([(box[0] + box[2]) / 2.0, box[3]])


def homography_matrix(calib_preds: list, sn_i: int) -> tuple[np.ndarray | None, float]:
    rec = calib_preds[sn_i]
    item = rec[0] if isinstance(rec, list) else rec
    conf = float(item.get("confidence") or 0.0)
    H = np.array(item["homography"], dtype=np.float64).reshape(3, 3)
    try:
        Hi = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        return None, conf
    return Hi, conf


def image_to_pitch(Hi: np.ndarray, xy: np.ndarray) -> np.ndarray | None:
    p = np.array([xy[0], xy[1], 1.0], dtype=np.float64)
    q = Hi @ p
    if abs(q[2]) < 1e-8:
        return None
    return q[:2] / q[2]


def greedy_match(yolo_boxes: np.ndarray, sn_boxes: np.ndarray) -> list[tuple[int, int, float]]:
    pairs: list[tuple[int, int, float]] = []
    if len(yolo_boxes) == 0 or len(sn_boxes) == 0:
        return pairs
    scores = []
    for i, yb in enumerate(yolo_boxes):
        for j, sb in enumerate(sn_boxes):
            scores.append((iou(yb, sb), i, j))
    used_y: set[int] = set()
    used_s: set[int] = set()
    for score, i, j in sorted(scores, reverse=True):
        if i in used_y or j in used_s:
            continue
        if score < IOU_HIT:
            break
        used_y.add(i)
        used_s.add(j)
        pairs.append((i, j, score))
    return pairs


def yolo_person_boxes(model: YOLO, frame: np.ndarray, device: str) -> np.ndarray:
    result = model(frame, imgsz=1280, verbose=False, device=device)[0]
    if result.boxes is None or len(result.boxes) == 0:
        return np.zeros((0, 4), dtype=np.float32)
    xyxy = result.boxes.xyxy.cpu().numpy()
    cls = result.boxes.cls.cpu().numpy().astype(int)
    keep = np.array([c in PERSON_CLASS_IDS for c in cls])
    return xyxy[keep] if keep.any() else np.zeros((0, 4), dtype=np.float32)


def main() -> None:
    sn = json.loads((GAME / "1_player_boundingbox_maskrcnn.json").read_text())
    preds = sn["predictions"]
    calib = json.loads((GAME / "1_field_calib_ccbv.json").read_text())
    calib_preds = calib["predictions"]

    cap = cv2.VideoCapture(str(CLIP))
    clip_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    n_clip = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    device = "mps"

    start_i = int(CLIP_START_S * SN_FPS)
    end_s = CLIP_START_S + n_clip / clip_fps
    end_i = min(len(preds), int(end_s * SN_FPS))

    model = YOLO(str(WEIGHTS)).to(device=device)

    per_frame = []
    all_metre: list[float] = []
    overlay_frame = None
    overlay_yolo = None
    overlay_sn = None
    overlay_pairs = None

    for sn_i in range(start_i, end_i):
        t = sn_i / SN_FPS
        clip_f = int(round((t - CLIP_START_S) * clip_fps)) + FRAME_OFFSET
        clip_f = min(max(clip_f, 0), n_clip - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, clip_f)
        ok, frame = cap.read()
        if not ok:
            continue

        rec = preds[sn_i]
        sn_boxes = np.array(rec["bboxes"], dtype=np.float32).reshape(-1, 4)
        onfield = np.array(rec.get("onfield") or [1] * len(sn_boxes), dtype=int)
        sn_boxes = sn_boxes[onfield == 1] if len(sn_boxes) else sn_boxes

        yolo_boxes = yolo_person_boxes(model, frame, device)
        pairs = greedy_match(yolo_boxes, sn_boxes)
        hit_y = {i for i, _, _ in pairs}
        hit_s = {j for _, j, _ in pairs}
        dists = [
            float(np.linalg.norm(centre(yolo_boxes[i]) - centre(sn_boxes[j])))
            for i, j, _ in pairs
        ]
        Hi, calib_conf = homography_matrix(calib_preds, sn_i)
        metre_gaps = []
        if Hi is not None:
            for i, j, _ in pairs:
                py = image_to_pitch(Hi, feet(yolo_boxes[i]))
                ps = image_to_pitch(Hi, feet(sn_boxes[j]))
                if py is None or ps is None:
                    continue
                metre_gaps.append(float(np.linalg.norm(py - ps)))
                all_metre.append(metre_gaps[-1])
        row = {
            "t": t,
            "sn_frame": sn_i,
            "clip_frame": clip_f,
            "n_yolo": int(len(yolo_boxes)),
            "n_sn": int(len(sn_boxes)),
            "hits": len(pairs),
            "misses": int(len(sn_boxes) - len(hit_s)),
            "extras": int(len(yolo_boxes) - len(hit_y)),
            "mean_iou": float(np.mean([p[2] for p in pairs])) if pairs else 0.0,
            "mean_centre_px": float(np.mean(dists)) if dists else None,
            "calib_conf": calib_conf,
            "mean_feet_m": float(np.mean(metre_gaps)) if metre_gaps else None,
            "median_feet_m": float(np.median(metre_gaps)) if metre_gaps else None,
            "n_metre_hits": len(metre_gaps),
        }
        per_frame.append(row)

        if overlay_frame is None and sn_i == start_i + (end_i - start_i) // 2:
            overlay_frame = frame.copy()
            overlay_yolo = yolo_boxes
            overlay_sn = sn_boxes
            overlay_pairs = pairs

    cap.release()

    hits = sum(r["hits"] for r in per_frame)
    misses = sum(r["misses"] for r in per_frame)
    extras = sum(r["extras"] for r in per_frame)
    ious = [r["mean_iou"] for r in per_frame if r["hits"]]
    dists = [r["mean_centre_px"] for r in per_frame if r["mean_centre_px"] is not None]
    summary = {
        "clip": str(CLIP.relative_to(ROOT)),
        "clip_start_s": CLIP_START_S,
        "frame_offset": FRAME_OFFSET,
        "n_sn_frames": len(per_frame),
        "iou_hit": IOU_HIT,
        "hits": hits,
        "misses": misses,
        "extras": extras,
        "hit_rate_on_sn": hits / (hits + misses) if (hits + misses) else 0.0,
        "mean_iou": float(np.mean(ious)) if ious else 0.0,
        "mean_centre_px": float(np.mean(dists)) if dists else None,
        "n_metre_hits": len(all_metre),
        "mean_feet_m": float(np.mean(all_metre)) if all_metre else None,
        "median_feet_m": float(np.median(all_metre)) if all_metre else None,
        "p90_feet_m": float(np.percentile(all_metre, 90)) if all_metre else None,
        "frames": per_frame,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, indent=2))

    if overlay_frame is not None:
        vis = overlay_frame.copy()
        for box in overlay_sn:
            x1, y1, x2, y2 = box.astype(int)
            cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 255), 2)  # SN yellow
        for box in overlay_yolo:
            x1, y1, x2, y2 = box.astype(int)
            cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 0), 2)  # YOLO green
        OUT_JPG.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(OUT_JPG), vis)

    print(json.dumps({k: v for k, v in summary.items() if k != "frames"}, indent=2))
    print("per frame:")
    for r in per_frame:
        print(
            f"  t={r['t']:.1f}s  sn={r['n_sn']:2d} yolo={r['n_yolo']:2d} "
            f"hits={r['hits']:2d} misses={r['misses']:2d} extras={r['extras']:2d} "
            f"iou={r['mean_iou']:.2f} centre_px={r['mean_centre_px']} "
            f"feet_m={r['mean_feet_m']}"
        )
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_JPG} (yellow=SoccerNet, green=YOLO)")


if __name__ == "__main__":
    main()
