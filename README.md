# Ayurix banner bot — sub progress bar (N / goal) on the YouTube banner

## STATUS (for any AI continuing this)
DONE and tested locally: render.py (banner renderer), prepare_track.py (built assets/track.png), update_banner.py (poll + upload), get_refresh_token.py, workflow.
NOT TESTED: the live YouTube upload (needs the user's OAuth credentials). Everything else was verified by rendering 54/55/100 and comparing against the user's original AE export.

## How it works
1. Every 5 min GitHub Actions runs update_banner.py.
2. It reads statistics.subscriberCount (exact below 1,000 subs). If equal to count.txt -> exit.
3. render.py: bar PNG space (2171x724) -> empty track + gradient fill CROPPED to count/goal (not stretched)
   + ragged pixel edge + number (Press Start 2P, blue/magenta chromatic edge) + additive multi-blur glow (Deep Glow look-alike)
   -> scaled 0.3325, placed at (71,612) on assets/bg.png at 88% opacity (matches the AE layer) -> banner.jpg (JPEG, <6 MB).
4. channelBanners.insert uploads it -> URL; channels.update(brandingSettings) sets image.bannerExternalUrl,
   re-sending the existing brandingSettings so nothing else is wiped.
5. count.txt is written only after success and committed by the workflow.

## Files
assets/bg.png banner without the bar | assets/track.png empty bar (made by prepare_track.py from bar_original.png)
assets/fill.png user's full noisy gradient | assets/PressStart2P-Regular.ttf (SIL OFL)
render.py constants at top: SCALE, OFFSET, FILL_BOX, NUM_XY, NUM_SIZE, glow strengths, GOALS

## YOUR SETUP (one time)
1. console.cloud.google.com -> new project -> enable "YouTube Data API v3".
2. OAuth consent screen: External. Add yourself as a test user, then PUBLISH the app ("In production").
   If it stays in "Testing", the refresh token dies after 7 days and the bot silently stops.
3. Credentials -> Create OAuth client ID -> type "Desktop app" -> download as client_secret.json into this folder.
4. pip install -r requirements.txt ; python get_refresh_token.py -> log in with the CHANNEL's Google account
   (click through the "unverified app" warning) -> copy the 3 printed values.
5. GitHub: create a PUBLIC repo (see warning below), push this folder, then Settings -> Secrets -> Actions:
   CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN.
6. Actions tab -> update-banner -> Run workflow once to test.

## Local tests
DRY_RUN=1 FAKE_COUNT=54 python update_banner.py   # renders banner.jpg only, no API calls
python render.py 73                                # quick preview

## Known limits (be realistic)
- Not instant: GitHub cron is delayed 5-20 min, and YouTube's count and banner caching add more.
- Private repo + 5-min cron burns the free 2,000 Actions minutes/month. Use a public repo, or change cron to */15.
- GitHub disables scheduled workflows after 60 days without repo activity; commits of count.txt keep it alive while subs change.
- At count >= goal the goal auto-advances (100 -> 250 -> 500 -> 1000...) per GOALS in render.py. 4-digit numbers are wider; check the look.
- Quota: poll = 1 unit, banner update ~100 units; default 10,000/day is plenty.
- If the sub count is hidden in Studio, the API returns no number and the script exits with a message.
- Glow is an approximation of After Effects Deep Glow, not identical.

## LOOK TUNING (top of render.py) — v3, tested against the user's AE export
Bar: OPACITY, SOFTEN, TINT/DESAT/GAIN, BAR_SHADOW (soft drop shadow), DG_THRESHOLD=80 + DG_RADII (Deep Glow look-alike), DG_WARM.
Number: NUM_COLOR (muted indigo so it reads on bright areas), NUM_SHADOW, NUM_GLOW (light halo, weaker than the bar's glow).
assets/track.png is built by prepare_track.py: spike removed, dark track turned into a pale glassy strip, dark blurry fringe faded out.
Known gap vs AE: the AE version has a stronger pink haze and orange heart rim. Raise DG_RADII exposures / DG_WARM to push closer.

## v6 (FINAL look) — render.py
One slow wave drives track, fill, number baseline, heart position + tilt: WAVE_AMP (19), WAVE_FLOOR, WAVE_X0/X1, HEART_TILT, WAVE_SEED; wavelengths are set in _wave_dy (long = low frequency).
Scattered stars (banner px): random layout every render (STAR_SEED=None; set an int to freeze). Mix of tapered sparkles, thin crosses, dots with random thickness + glow;
sparser (STAR_MIN0/STAR_MINK) and dimmer (STAR_FADE) farther from the bar. They do NOT follow the wave; the sparkles baked into track.png DO.
Number: NUM_X/NUM_Y/NUM_H/NUM_CW/NUM_GAP, NUM_COLOR, NUM_SHADOW (dark, bottom-right), NUM_LIGHT (white, top-left), NUM_GLOW. Shadows are applied after the glow.
Needs scipy (requirements.txt). Test: python render.py 54

## CONTINUATION PROMPT (paste into another AI together with this folder)
"I have a Python project (banner-bot) that renders my YouTube banner with a subscriber progress bar (render.py) and uploads it via YouTube Data API v3 (update_banner.py) from a GitHub Actions cron. Read README.md first. Rendering is done and visually tuned; the live upload is untested. Help me: (1) finish Google Cloud OAuth setup and get the refresh token, (2) push to a public GitHub repo with the 3 secrets and run the workflow once, (3) fix any API errors I paste, (4) optionally tune the look in render.py (constants at top). Do not rewrite the renderer from scratch. Keep answers short."
