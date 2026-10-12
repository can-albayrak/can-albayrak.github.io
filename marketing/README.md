# Marketing kit: Tilt Grid, Fuse Chain, Cuddle Pop

Lives in the `can-albayrak.github.io` repo. The scripts expect the three game repos (`tild-grid`, `fuse-chain`, `cuddle-pop`) in the same parent folder as this repo.

## What is here

| File | What it does |
|------|--------------|
| `promo_shots.py` | Play Store screenshots with a caption band, en + tr, for all three games -> `<repo>/store/listing/promo/<lang>/` |
| `make_videos.py` | Encodes recorded gameplay frames into 1080x1920 MP4 clips -> `marketing/videos/` (needs ffmpeg: `winget install Gyan.FFmpeg`) |

## Recording new clips

Godot is `Godot_v4.7.2-stable_win64_console.exe` (on this PC in the parent folder). Out dirs must not contain spaces, so they are `res://...` paths.

```
# Tilt Grid (in tild-grid/): hook 0..2, any seed; frames have the hook text built in
godot --path . --resolution 270x480 --fixed-fps 30 -s res://tools/dev/video_driver.gd -- res://build/video/tg_en_0 lang=en hook=0 seed=6

# Fuse Chain (in fuse-chain/)
godot --path . --resolution 270x480 --fixed-fps 30 -s res://tools/dev/video_driver.gd -- res://build/video/fc_tr_1 lang=tr hook=1 seed=18

# Cuddle Pop (in cuddle-pop/): Godot Movie Maker, one folder per toy, with sound
godot --path . --resolution 594x1056 --fixed-fps 30 --write-movie res://build/video/cp_bubbles/f.png -- --shot=bubbles res://build/vshots
```

Then `python marketing/make_videos.py`. Change the seed to get a different game; look at a few frames before posting.

## Posting plan (first 3 weeks)

Same clip on **TikTok, YouTube Shorts and Instagram Reels**. One clip a day, every day.

- **Week 1 (closed test running):** "I made my first games" story. Day 1: talk to the camera for 10 s, then the Tilt Grid clip. Then one gameplay clip a day, rotating the three games. Bio: "Coming soon to Google Play".
- **Week 2:** the clip that got the most views in week 1, again with a new hook and seed. Reply to every comment, ideally with a new clip ("You asked which way to tilt: here").
- **Week 3 (store pages live):** Play links in the bio (one link page if the platform allows only one). Keep posting; put the best performer into Google Ads as the video asset.

Rules that matter:
- The first second must already move: no logo intro, no menu.
- A question on screen gets comments, and comments spread the clip.
- Music: these clips promote your own apps, which TikTok and Instagram treat as commercial content. Use only their **Commercial Music Library** (TikTok: "Commercial sounds"; Instagram: sounds marked for business use) or the game's own sounds. Popular chart songs can get a promotional clip muted or taken down. Cuddle Pop clips already have the game sounds.
- Cuddle Pop is for kids: post it as content for parents ("a calm app for toddlers"), never target children, and no "download now" aimed at kids.
- Never buy views or followers.
