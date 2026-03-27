#!/usr/bin/env python3
import sys
import argparse
import yaml
import os
import base64
from pathlib import Path
from email.mime.text import MIMEText
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

IDENTITY_PATH = Path.home() / "aria" / "identity.yaml"
VAULT_DIR = Path.home() / "aria" / "vault"

def get_account_for_purpose(purpose_hint):
    """Find the best email account from identity.yaml based on the purpose."""
    try:
        if not IDENTITY_PATH.exists():
            return None
            
        with open(IDENTITY_PATH, 'r') as f:
            identity = yaml.safe_load(f)
            
        emails = identity.get("emails", [])
        if not emails:
            return None
            
        purpose_hint = purpose_hint.lower()
        
        # 1. Exact purpose match
        for e in emails:
            purposes = [p.lower() for p in e.get("purpose", [])]
            if purpose_hint in purposes:
                return e.get("address")
                
        # 2. Fallback to primary
        for e in emails:
            purposes = [p.lower() for p in e.get("purpose", [])]
            if "primary" in purposes:
                return e.get("address")
                
        # 3. Ultimate fallback
        return emails[0].get("address")
        
    except Exception as e:
        print(f"Error loading identity: {e}")
        return None

def get_gmail_service(email_address):
    """Load the OAuth refresh token for the specific email and build the Gmail API service."""
    token_file = VAULT_DIR / f"token_{email_address}.json"
    
    if not token_file.exists():
        print(f"ERROR: No OAuth token found for {email_address}.")
        print(f"Please run: python3 ~/aria/skills/google_auth.py {email_address}")
        sys.exit(1)
        
    try:
        # Load the permanent refresh token
        creds = Credentials.from_authorized_user_file(str(token_file), ['https://www.googleapis.com/auth/gmail.modify'])
        
        # Auto-refresh if expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save the new token seamlessly
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
                
        return build('gmail', 'v1', credentials=creds)
    except Exception as e:
        print(f"ERROR: Failed to authorize Gmail API for {email_address} - {e}")
        sys.exit(1)

def send_email(purpose, to_addr, subject, body):
    from_addr = get_account_for_purpose(purpose)
    
    if not from_addr:
        print("ERROR: Could not find suitable email account in identity.yaml")
        sys.exit(1)
        
    service = get_gmail_service(from_addr)
    
    try:
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to_addr
        message['From'] = from_addr
        message['Subject'] = subject

        # Encode the message for the Gmail API
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}

        # Send via official API
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        
        print(f"SUCCESS: Email sent via Google API from {from_addr} to {to_addr}")
        print(f"Message Id: {send_message['id']}")
        
    except HttpError as error:
        print(f"API ERROR: Failed to send email: {error}")
    except Exception as e:
        print(f"ERROR: Unexpected failure: {e}")

def check_gmail(purpose, max_results=5):
    email_addr = get_account_for_purpose(purpose)
    if not email_addr:
        print("ERROR: Could not find suitable email account.")
        sys.exit(1)
        
    service = get_gmail_service(email_addr)
    
    try:
        # Exclude Google security alerts and automated no-reply receipts
        query = 'label:inbox label:unread -from:no-reply -from:noreply -subject:"Security alert"'
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("No new unread messages.")
            return

        print(f"--- Top {len(messages)} Unread Messages for {email_addr} ---")
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['Subject', 'From']).execute()
            headers = msg_data.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            snippet = msg_data.get('snippet', '')
            
            print(f"\n[From: {sender}]")
            print(f"Subject: {subject}")
            print(f"Snippet: {snippet}")
            
    except HttpError as error:
        print(f"API ERROR: Failed to retrieve emails: {error}")
    except Exception as e:
        print(f"ERROR: Unexpected failure: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARIA Email Agent Skill (OAuth 2.0 Edition)")
    parser.add_argument("action", choices=["send", "check"])
    parser.add_argument("--purpose", type=str, default="primary", help="Purpose hint (e.g. college, github-main, primary)")
    parser.add_argument("--to", type=str, help="Recipient email")
    parser.add_argument("--subject", type=str, help="Email subject")
    parser.add_argument("--body", type=str, help="Email body content")
    
    args = parser.parse_args()
    if args.action == "send":
        if not getattr(args, 'to', None) or not getattr(args, 'subject', None) or not getattr(args, 'body', None):
            print("ERROR: Missing --to, --subject, or --body")
            sys.exit(1)
        send_email(args.purpose, args.to, args.subject, args.body)
    elif args.action == "check":
        check_gmail(args.purpose)
