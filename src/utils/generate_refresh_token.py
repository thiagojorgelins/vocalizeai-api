from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def main():
    client_secret_file = "client_secret.json"

    flow = InstalledAppFlow.from_client_secrets_file(
        client_secret_file, SCOPES
    )

    creds = flow.run_local_server(port=0)

    print(f"GMAIL_CLIENT_ID={creds.client_id}")
    print(f"GMAIL_CLIENT_SECRET={creds.client_secret}")
    print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")

if __name__ == "__main__":
    main()
