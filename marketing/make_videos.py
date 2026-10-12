"""Encodes the recorded gameplay frames into vertical MP4 clips for TikTok / Shorts / Reels.

Needs ffmpeg on PATH (winget install Gyan.FFmpeg).
Run from anywhere:  python marketing/make_videos.py
Writes marketing/videos/*.mp4 (1080x1920, 30 fps, H.264).

Frames come from each game's recorder (see the commands in marketing/README.md):
- tild-grid/build/video/tg_<lang>_<n>/0000.jpg ...   (hook text already in the frames)
- fuse-chain/build/video/fc_<lang>_<n>/0000.jpg ...
- cuddle-pop/build/video/cp_<toy>/f00000000.png + f.wav   (Godot Movie Maker, 594x1056;
  joined into one montage with sound, and the hook band is added here)
"""
import glob
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # the folder that holds the game repos
OUT = os.path.join(HERE, "videos")
FPS = 30
CUDDLE_TOYS = ["bubbles", "fireworks", "monster", "band", "paint"]
CUDDLE_HOOKS = {
    "en": ["Tap, pop, giggle!", "Made for little hands\n(ages 2–6)"],
    "tr": ["Dokun, patlat, kıkırda!", "Küçük eller için\n(2–6 yaş)"],
}
HOOK_SECONDS = 3.5


def ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe is None:
        # winget installs it here; the PATH alias only appears in a new shell.
        found = glob.glob(os.path.expandvars(
            r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg*\*\bin\ffmpeg.exe"))
        exe = found[0] if found else None
    if exe is None:
        sys.exit("ffmpeg not found. Install it with: winget install Gyan.FFmpeg")
    return exe


def run(args: list) -> None:
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error"] + args, check=True)


ENCODE = ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]


def encode_jpg_clips(repo: str, prefix: str, name: str) -> None:
    for d in sorted(glob.glob(os.path.join(ROOT, repo, "build", "video", prefix + "_*"))):
        tag = os.path.basename(d)[len(prefix) + 1:]
        out = os.path.join(OUT, f"{name}_{tag}.mp4")
        run(["-framerate", str(FPS), "-i", os.path.join(d, "%04d.jpg"), *ENCODE, out])
        print("wrote", os.path.relpath(out, ROOT))


def hook_png(text: str, path: str) -> None:
    """A 1080x1920 transparent overlay: the hook on a dark rounded band at the top."""
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, 120, 1040, 420], radius=40, fill=(56, 41, 74, 225))
    font = ImageFont.truetype(os.path.join(ROOT, "cuddle-pop", "store", "fonts", "BalooBhaijaan2.ttf"), 92)
    font.set_variation_by_axes([700])
    d.multiline_text((540, 270), text, font=font, fill="white", anchor="mm", align="center", spacing=8,
                     stroke_width=4, stroke_fill=(56, 41, 74))
    img.save(path)


def encode_cuddle() -> None:
    base = os.path.join(ROOT, "cuddle-pop", "build", "video")
    tmp = os.path.join(base, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    parts = []
    for toy in CUDDLE_TOYS:
        d = os.path.join(base, "cp_" + toy)
        part = os.path.join(tmp, toy + ".mp4")
        run(["-framerate", str(FPS), "-i", os.path.join(d, "f%08d.png"), "-i", os.path.join(d, "f.wav"),
             "-vf", "scale=1080:1920:flags=lanczos", *ENCODE, "-c:a", "aac", "-b:a", "160k", "-shortest", part])
        parts.append(part)
    listing = os.path.join(tmp, "parts.txt")
    with open(listing, "w") as f:
        f.writelines(f"file '{p.replace(os.sep, '/')}'\n" for p in parts)
    montage = os.path.join(tmp, "montage.mp4")
    run(["-f", "concat", "-safe", "0", "-i", listing, "-c", "copy", montage])
    for lang, hooks in CUDDLE_HOOKS.items():
        for n, text in enumerate(hooks):
            png = os.path.join(tmp, f"hook_{lang}_{n}.png")
            hook_png(text, png)
            out = os.path.join(OUT, f"cuddle-pop_{lang}_{n}.mp4")
            run(["-i", montage, "-i", png, "-filter_complex",
                 f"[0:v][1:v]overlay=0:0:enable='lt(t,{HOOK_SECONDS})'", *ENCODE, "-c:a", "copy", out])
            print("wrote", os.path.relpath(out, ROOT))
    shutil.rmtree(tmp)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    encode_jpg_clips("tild-grid", "tg", "tilt-grid")
    encode_jpg_clips("fuse-chain", "fc", "fuse-chain")
    encode_cuddle()
