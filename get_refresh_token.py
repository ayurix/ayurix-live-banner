"""Run ONCE locally. Needs client_secret.json (OAuth client type: Desktop app). Prints CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN."""
import json
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", ["https://www.googleapis.com/auth/youtube"])
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
print("CLIENT_ID     =", creds.client_id)
print("CLIENT_SECRET =", creds.client_secret)
print("REFRESH_TOKEN =", creds.refresh_token)
