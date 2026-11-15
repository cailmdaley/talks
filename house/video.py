# /// script
# dependencies = ["imageio-ffmpeg"]
# ///
"""Encode a clip for a house deck, plus its required poster.

    uv run house/video.py SRC OUT.mp4 [--width 1920] [--crf 26] [--fps 30]
        [--start S] [--duration S] [--speed X] [--poster-at S] [--vf FILTERS]

Writes OUT.mp4 (H.264, no audio, yuv420p, faststart) and OUT.jpg.
Aim for a few MB per clip; the offline deck inlines both files.
"""

import argparse
import os
import subprocess

import imageio_ffmpeg


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src")
    parser.add_argument("out")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--crf", type=int, default=26)
    parser.add_argument("--fps", type=float, default=30)
    parser.add_argument("--start", type=float, default=0)
    parser.add_argument("--duration", type=float)
    parser.add_argument("--speed", type=float, default=1.0,
                        help="playback speed-up factor")
    parser.add_argument("--vf", default="", help="extra ffmpeg filters applied first")
    parser.add_argument("--poster-at", type=float, default=0.0,
                        help="seconds into the output clip")
    args = parser.parse_args()
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cut = ["-ss", str(args.start)]
    if args.duration:
        cut += ["-t", str(args.duration)]
    filters = (args.vf + "," if args.vf else "") + (
        f"setpts=PTS/{args.speed},fps={args.fps},"
        f"scale={args.width}:-2:flags=lanczos,format=yuv420p"
    )
    subprocess.run([
        ffmpeg, "-y", "-loglevel", "error", *cut, "-i", args.src,
        "-an", "-vf", filters, "-c:v", "libx264", "-preset", "slow",
        "-crf", str(args.crf), "-profile:v", "high",
        "-movflags", "+faststart", args.out,
    ], check=True)
    poster = os.path.splitext(args.out)[0] + ".jpg"
    subprocess.run([
        ffmpeg, "-y", "-loglevel", "error", "-ss", str(args.poster_at),
        "-i", args.out, "-frames:v", "1", "-q:v", "3", poster,
    ], check=True)
    print(f"{args.out}: {os.path.getsize(args.out) / 1e6:.1f} MB; poster {poster}")


if __name__ == "__main__":
    main()
