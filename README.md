# can-albayrak.github.io

Public site of Peak Studios, served by GitHub Pages. Generated, do not edit the HTML by hand:

    python marketing/site_build.py        # run in the Wildcat-studios repo next to this one

- `/`, `/tr/`: studio page (EN, TR).
- `/<game>/`, `/tr/<game>/`: one canonical page per game (positioning, how to play, screenshots, FAQ, JSON-LD).
- `/<game>/privacy/`: the privacy policy from the game repo's `docs/PRIVACY_POLICY.md` (was `/<game>/` before 2026-11-03).
- `/<game>/img/`: icon and store screenshots, resized.
- `robots.txt`, `sitemap.xml`, `llms.txt`: generated too. `app-ads.txt` is kept by hand.
- `marketing/`: older copies of the store screenshot and video tools; the live versions are in the Wildcat-studios repo.
- `privacy-site/build.py`: the old privacy-only generator, superseded by `site_build.py`.

Sources: `games.toml` (name, package, status, positioning sentence), each game's `docs/STORE_LISTING.md`
and `docs/PRIVACY_POLICY.md`, `store/listing/icon_512.png` and `store/listing/promo/<lang>/`.
