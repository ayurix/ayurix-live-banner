"""Poll sub count; if changed, render banner and upload it to YouTube. Env: CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN. Optional: FORCE=1, DRY_RUN=1, FAKE_COUNT=N"""
import os, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from render import render_banner

COUNT_FILE = "count.txt"
SCOPES = ["https://www.googleapis.com/auth/youtube"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


def yt_client():
    creds = Credentials(None, refresh_token=os.environ["REFRESH_TOKEN"], token_uri=TOKEN_URI,
                        client_id=os.environ["CLIENT_ID"], client_secret=os.environ["CLIENT_SECRET"], scopes=SCOPES)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def last_count():
    try:
        return int(open(COUNT_FILE).read().strip())
    except Exception:
        return -1


def main():
    if os.environ.get("DRY_RUN") and os.environ.get("FAKE_COUNT"):
        print("dry run ->", render_banner(int(os.environ["FAKE_COUNT"]))); return
    yt = yt_client()
    ch = yt.channels().list(part="statistics", mine=True).execute()["items"][0]
    stats = ch["statistics"]
    if stats.get("hiddenSubscriberCount"):
        sys.exit("Subscriber count is hidden on the channel; make it public in YouTube Studio.")
    count = int(stats["subscriberCount"])
    print("subs:", count, "last:", last_count())
    if count == last_count() and not os.environ.get("FORCE"):
        print("no change"); return
    path = render_banner(count)
    if os.environ.get("DRY_RUN"):
        print("dry run, rendered", path); return
    # 1) upload image -> URL hosted by YouTube
    url = yt.channelBanners().insert(media_body=MediaFileUpload(path, mimetype="image/jpeg")).execute()["url"]
    # 2) set it as the banner, resending existing branding so nothing else is wiped
    cur = yt.channels().list(part="brandingSettings", mine=True).execute()["items"][0]
    cur["brandingSettings"].setdefault("image", {})["bannerExternalUrl"] = url
    yt.channels().update(part="brandingSettings", body={"id": cur["id"], "brandingSettings": cur["brandingSettings"]}).execute()
    open(COUNT_FILE, "w").write(str(count))      # only after success
    print("banner updated ->", count)


if __name__ == "__main__":
    main()
