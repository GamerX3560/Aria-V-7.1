#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes needed: Gmail (send/read), Drive (full), Photos (readonly), YouTube, Personal Info, Calendar, Tasks
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/photoslibrary.readonly',
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/contacts.readonly',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/tasks'
]

VAULT_DIR = Path.home() / "aria" / "vault"

def authenticate_account(email):
    """Run the OAuth 2.0 flow to get a refresh token for a specific email."""
    if not VAULT_DIR.exists():
        VAULT_DIR.mkdir(parents=True)
        os.chmod(VAULT_DIR, 0o700)
    
    creds_file = VAULT_DIR / "credentials.json"
    token_file = VAULT_DIR / f"token_{email}.json"
    
    if not creds_file.exists():
        print(f"\n[ERROR] Missing credentials.json in {VAULT_DIR}")
        print("Please download it from Google Cloud Console (Desktop App) and place it there.")
        sys.exit(1)
        
    creds = None
    if token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        except Exception:
            pass
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print(f"Token refreshed successfully for {email}")
            except Exception as e:
                print(f"Error refreshing token for {email}: {e}")
                creds = None
        
        if not creds:
            print(f"\n[AUTH REQUIRED] Starting web flow for {email}...")
            print("Your browser should open. Please login ONLY with the account:")
            print(f" -> {email}")
            try:
                # Add 'localhost' to the authorized redirect URIs in Cloud Console for this to work
                flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
                creds = flow.run_local_server(port=0, prompt='consent')
            except Exception as e:
                print(f"Error during OAuth flow: {e}")
                sys.exit(1)
                
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
        os.chmod(token_file, 0o600)
        
    print(f"\n[SUCCESS] Authentication complete. ARIA now has permanent access to {email}.")
    print(f"Token saved securely at: {token_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ARIA Google OAuth Manager")
    parser.add_argument("email", type=str, help="The Gmail address to authenticate (e.g. mangeshchoudhary35@gmail.com)")
    
    args = parser.parse_args()
    authenticate_account(args.email)
