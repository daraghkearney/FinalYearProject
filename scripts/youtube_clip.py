"""Pull a few seconds from a YouTube URL. Delete the file when you are done analysing it."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import imageio_ffmpeg
from yt_dlp import YoutubeDL
from yt_dlp.utils import download_range_func


def _ffmpeg_dir() -> Path:
    bundled = Path(imageio_ffmpeg.get_ffmpeg_exe())
    # yt-dlp looks for a binary named "ffmpeg", not the imageio filename.
    shim_dir = Path(__file__).resolve().parents[1] / "data" / "bin"
    shim_dir.mkdir(parents=True, exist_ok=True)
    shim = shim_dir / "ffmpeg"
    if not shim.exists():
        shim.symlink_to(bundled)
    os.environ["PATH"] = str(shim_dir) + os.pathsep + os.environ.get("PATH", "")
    return shim_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a short window from YouTube. Do not commit the mp4."
    )
    parser.add_argument("url")
    parser.add_argument("--start", type=float, default=0, help="start time in seconds")
    parser.add_argument("--seconds", type=float, default=8, help="how many seconds to keep")
    parser.add_argument(
        "--out",
        default="data/youtube/clip.mp4",
        help="output path (under data/, which is gitignored)",
    )
    args = parser.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    start = max(args.start, 0)
    end = start + max(args.seconds, 1)

    ydl_opts = {
        "outtmpl": str(out.with_suffix("")),
        "merge_output_format": "mp4",
        "format": "bv*[height<=720]+ba/b[height<=720]/b",
        "download_ranges": download_range_func(None, [(start, end)]),
        "force_keyframes_at_cuts": True,
        "ffmpeg_location": str(_ffmpeg_dir()),
        "overwrites": True,
        "noprogress": False,
        "quiet": False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([args.url])

    print(f"wrote clip. analyse it, then delete {out.parent}")


if __name__ == "__main__":
    main()
