"""Extract still frames from a Staydia/Suncroft clip for Roboflow labelling.

Example:
  python scripts/extract_frames.py data/suncroft/suncroft1.mp4 --every 1
  python scripts/extract_frames.py data/suncroft/ --every 2 --max-frames 600

Frames land under data/frames/<clip_stem>/ (gitignored). Upload those JPEGs
to Roboflow. Do not commit them.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "frames"


def iter_videos(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    vids = sorted(
        p
        for p in path.iterdir()
        if p.suffix.lower() in {".mp4", ".mov", ".mkv", ".avi"}
    )
    if not vids:
        raise SystemExit(f"no videos found under {path}")
    return vids


def extract_one(
    video: Path,
    out_dir: Path,
    every_s: float,
    max_frames: int | None,
    jpeg_quality: int,
) -> int:
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise SystemExit(f"could not open {video}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(int(round(fps * every_s)), 1)
    stem = video.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    frame_i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_i % step == 0:
            t = frame_i / fps
            name = f"{stem}_t{t:07.2f}_f{frame_i:06d}.jpg"
            dest = out_dir / name
            cv2.imwrite(
                str(dest),
                frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality],
            )
            written += 1
            if max_frames is not None and written >= max_frames:
                break
        frame_i += 1

    cap.release()
    print(
        f"{video.name}: fps={fps:.2f} frames={total} "
        f"every={every_s}s step={step} wrote={written} -> {out_dir}"
    )
    return written


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract 1 frame every N seconds for Roboflow annotation."
    )
    parser.add_argument(
        "source",
        type=Path,
        help="video file or directory of videos (e.g. data/suncroft/)",
    )
    parser.add_argument(
        "--every",
        type=float,
        default=1.0,
        help="seconds between frames (default 1). Use 2 if you have long halves.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="output root (default data/frames)",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="stop after this many frames across all clips (aim ~500-600 total)",
    )
    parser.add_argument(
        "--jpeg-quality",
        type=int,
        default=92,
        help="JPEG quality 1-100 (default 92)",
    )
    args = parser.parse_args()

    source = args.source
    if not source.is_absolute():
        source = (ROOT / source).resolve()
    out_root = args.out if args.out.is_absolute() else (ROOT / args.out).resolve()

    videos = iter_videos(source)
    remaining = args.max_frames
    total_written = 0
    for video in videos:
        clip_out = out_root / video.stem
        limit = remaining
        n = extract_one(
            video=video,
            out_dir=clip_out,
            every_s=max(args.every, 0.2),
            max_frames=limit,
            jpeg_quality=min(max(args.jpeg_quality, 1), 100),
        )
        total_written += n
        if remaining is not None:
            remaining -= n
            if remaining <= 0:
                break

    print(f"total frames written: {total_written}")
    print(f"upload JPEGs under {out_root} to Roboflow, then delete if disk is tight")


if __name__ == "__main__":
    main()
