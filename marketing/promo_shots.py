"""Play Store screenshots with a caption band, for all three games, in English and Turkish.

Run from anywhere:  python marketing/promo_shots.py [tilt|fuse|cuddle ...]
Reads each game's plain screenshots from store/listing/screenshots/<lang>/ and writes
store/listing/promo/<lang>/<n>.png (1080 x 1920), numbered in the order to upload them.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # the folder that holds the game repos
W, H = 1080, 1920
BAND = 400  # caption area at the top
SHOT_W = 860

GAMES = {
    "tilt": {
        "repo": "tild-grid",
        "font": "fonts/Fredoka.ttf",
        "font_tr": "fonts/BalooBhaijaan2.ttf",  # Fredoka has no Ş/Ğ/İ
        "top": "#2b3fa3", "bottom": "#141a52", "text": "#ffd32a", "outline": "#0d1240",
        "langs": {"en": "en", "tr": "tr"},
        "shots": [
            ("4_chain", "Tilt the board,\nwatch it all clear!", "Tahtayı çevir,\nhepsi patlasın!"),
            ("3_preview", "See the result\nbefore you tilt", "Çevirmeden önce\nsonucu gör"),
            ("2_play", "Place the blocks,\nfill the lines", "Blokları yerleştir,\nsatırları doldur"),
            ("6_level", "Break the\ngray blocks", "Gri blokları\nkır"),
            ("5_levels", "100 levels\n+ endless mode", "100 bölüm\n+ sonsuz mod"),
            ("1_menu", "Play offline,\nno ads", "İnternetsiz oyna,\nreklam yok"),
        ],
    },
    "fuse": {
        "repo": "fuse-chain",
        "font": "fonts/Fredoka.ttf",
        "font_tr": "fonts/BalooBhaijaan2.ttf",
        "top": "#2a1f5c", "bottom": "#0e0b24", "text": "#ffd32a", "outline": "#7a1f00",
        "langs": {"en": "en", "tr": "tr"},
        "shots": [
            ("2_chain", "Light the fuse,\nwatch it spread!", "Fitili ateşle,\nyayılışını izle!"),
            ("6_tutorial", "Draw a path\nthrough the gems", "Taşların üzerinden\nfitil çiz"),
            ("3_level", "100 levels\nwith goals", "Hedefli\n100 bölüm"),
            ("4_win", "Earn up to\n3 stars", "3 yıldıza kadar\ntopla"),
            ("5_levels", "Short levels,\nquick fun", "Kısa bölümler,\nhızlı eğlence"),
            ("1_menu", "Endless mode,\nplays offline", "Sonsuz mod,\ninternetsiz oyna"),
        ],
    },
    "cuddle": {
        "repo": "cuddle-pop",
        "font": "store/fonts/BalooBhaijaan2.ttf",
        "font_tr": "store/fonts/BalooBhaijaan2.ttf",
        "top": "#78c8ff", "bottom": "#ffdcea", "text": "#ffffff", "outline": "#38294a",
        # Kids' screens have no text, so both languages use the same pictures.
        "langs": {"en": "", "tr": ""},
        "shots": [
            ("2_bubbles", "Pop bubbles full\nof animal friends", "Hayvan dostlarla\ndolu baloncuklar"),
            ("4_monster", "Feed the silly\nmonster", "Komik canavarı\nbesle"),
            ("3_fireworks", "Draw with\nfireworks", "Havai fişekle\nçiz"),
            ("5_band", "Play music with\nthe animal band", "Hayvan orkestrasıyla\nmüzik yap"),
            ("6_paint", "Finger painting,\n24 pages", "Parmakla boyama,\n24 sayfa"),
            ("7_celebration", "A big party\nfor every win", "Her başarıya\nkocaman kutlama"),
            ("1_home", "7 toys in one,\nmade for ages 2–6", "Bir arada 7 oyuncak,\n2–6 yaş için"),
        ],
    },
}


def gradient(top: str, bottom: str) -> Image.Image:
    a = Image.new("RGB", (1, 2))
    a.putpixel((0, 0), Image.new("RGB", (1, 1), top).getpixel((0, 0)))
    a.putpixel((0, 1), Image.new("RGB", (1, 1), bottom).getpixel((0, 0)))
    return a.resize((W, H), Image.BILINEAR)


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(path, size)
    try:
        font.set_variation_by_axes([700] + [a["default"] for a in font.get_variation_axes()[1:]])
    except OSError:
        pass  # not a variable font
    return font


def caption(draw: ImageDraw.ImageDraw, text: str, font_path: str, cfg: dict) -> None:
    size = 118
    while True:
        font = load_font(font_path, size)
        box = draw.multiline_textbbox((0, 0), text, font=font, spacing=10, align="center", stroke_width=7)
        if box[2] - box[0] <= W - 100 and box[3] - box[1] <= BAND - 90 or size <= 60:
            break
        size -= 4
    x = (W - (box[2] - box[0])) / 2 - box[0]
    y = (BAND - (box[3] - box[1])) / 2 - box[1] + 20
    draw.multiline_text((x, y), text, font=font, fill=cfg["text"], spacing=10, align="center",
                        stroke_width=7, stroke_fill=cfg["outline"])


def phone(shot: Image.Image) -> Image.Image:
    """The screenshot scaled to SHOT_W, with rounded corners and a soft shadow."""
    h = round(shot.height * SHOT_W / shot.width)
    shot = shot.convert("RGB").resize((SHOT_W, h), Image.LANCZOS)
    mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, SHOT_W - 1, h - 1], radius=44, fill=255)
    pad = 40
    layer = Image.new("RGBA", (SHOT_W + pad * 2, h + pad * 2), (0, 0, 0, 0))
    shadow = Image.new("L", layer.size, 0)
    ImageDraw.Draw(shadow).rounded_rectangle([pad, pad + 12, pad + SHOT_W, pad + h + 12], radius=44, fill=140)
    layer.putalpha(shadow.filter(ImageFilter.GaussianBlur(18)))
    layer.paste(shot, (pad, pad), mask)
    return layer


def build(key: str) -> None:
    cfg = GAMES[key]
    repo = os.path.join(ROOT, cfg["repo"])
    for lang, sub in cfg["langs"].items():
        src = os.path.join(repo, "store", "listing", "screenshots", sub)
        out = os.path.join(repo, "store", "listing", "promo", lang)
        os.makedirs(out, exist_ok=True)
        font_path = os.path.join(repo, cfg["font_tr" if lang == "tr" else "font"])
        for n, (name, en, tr) in enumerate(cfg["shots"], 1):
            img = gradient(cfg["top"], cfg["bottom"]).convert("RGBA")
            caption(ImageDraw.Draw(img), tr if lang == "tr" else en, font_path, cfg)
            ph = phone(Image.open(os.path.join(src, name + ".png")))
            img.alpha_composite(ph, ((W - ph.width) // 2, BAND - 30))
            img.convert("RGB").save(os.path.join(out, f"{n}_{name.split('_', 1)[1]}.png"))
        print(f"{cfg['repo']}: {len(cfg['shots'])} promo shots -> store/listing/promo/{lang}/")


if __name__ == "__main__":
    for k in sys.argv[1:] or list(GAMES):
        build(k)
