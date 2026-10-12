"""Builds the public privacy-policy site from each game's docs/PRIVACY_POLICY.md.

Run from anywhere:  python privacy-site/build.py
Writes the site into this repo's root (GitHub Pages serves it as can-albayrak.github.io):
index.html, tilt-grid/, fuse-chain/, cuddle-pop/ (each an index.html).
The game repos must sit next to this repo (same parent folder), each on the branch that
is live in Play (e.g. play-release); it refuses to run while a policy has an unfilled
[placeholder].
Only the subset of Markdown the policies use is supported: # headings, paragraphs,
"- " lists, **bold**, `code` and bare https:// links.
"""
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ROOT = os.path.dirname(REPO)  # the folder that holds the game repos
OUT = REPO
GAMES = [
    ("tilt-grid", "Tilt Grid", "tild-grid"),
    ("fuse-chain", "Fuse Chain", "fuse-chain"),
    ("cuddle-pop", "Cuddle Pop", "cuddle-pop"),
]

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{ font: 17px/1.6 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color: #1f2430;
         background: #f7f8fb; margin: 0; padding: 32px 16px; }}
  main {{ max-width: 720px; margin: 0 auto; background: #fff; padding: 32px; border-radius: 12px;
          box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  h1 {{ font-size: 1.8em; margin-top: 0; }}
  h2 {{ font-size: 1.2em; margin-top: 1.6em; }}
  a {{ color: #2450c4; }}
  code {{ background: #eef0f5; padding: 0 4px; border-radius: 4px; }}
</style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"(https://[^\s<)]+)", r'<a href="\1">\1</a>', text)
    return text


def to_html(md: str) -> str:
    out, para, items = [], [], []

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()
        if items:
            out.append("<ul>" + "".join("<li>" + inline(i) + "</li>" for i in items) + "</ul>")
            items.clear()

    for line in md.splitlines():
        s = line.strip()
        if not s:
            flush()
        elif s.startswith("#"):
            flush()
            level = len(s) - len(s.lstrip("#"))
            out.append(f"<h{level}>{inline(s[level:].strip())}</h{level}>")
        elif s.startswith("- "):
            if para:
                flush()
            items.append(s[2:])
        else:
            if items:
                flush()
            para.append(s)
    flush()
    return "\n".join(out)


def main() -> None:
    links = []
    for slug, name, repo in GAMES:
        with open(os.path.join(ROOT, repo, "docs", "PRIVACY_POLICY.md"), encoding="utf-8") as f:
            md = f.read()
        # A placeholder like "[date version 1.1 is released]" means the policy is not final,
        # or the game repo is on a branch whose policy is not live yet: stop.
        left = re.findall(r"\[[^\]\n]+\](?!\()", md)
        if left:
            sys.exit(f"{repo}/docs/PRIVACY_POLICY.md has unfilled placeholders {left}: fill them, "
                     f"or check out the branch that is live in Play (git -C {repo} branch --show-current).")
        os.makedirs(os.path.join(OUT, slug), exist_ok=True)
        with open(os.path.join(OUT, slug, "index.html"), "w", encoding="utf-8") as f:
            f.write(PAGE.format(title=f"{name} Privacy Policy", body=to_html(md)))
        links.append(f'<li><a href="{slug}/">{html.escape(name)}</a></li>')
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(PAGE.format(title="Privacy Policies",
                            body="<h1>Privacy Policies</h1>\n<p>Games by Can Albayrak.</p>\n<ul>" + "".join(links) + "</ul>"))
    # GitHub Pages: serve files as they are (no Jekyll processing).
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    print("site written to", OUT)


if __name__ == "__main__":
    main()
