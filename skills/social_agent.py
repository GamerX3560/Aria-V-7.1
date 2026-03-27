#!/usr/bin/env python3
import sys
import json
import argparse
import requests
import os

ENV_PATH = os.path.expanduser("~/aria/.env")

def get_telegram_creds():
    token, chat_id = None, None
    try:
        with open(ENV_PATH, 'r') as f:
            for line in f:
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    token = line.split("=", 1)[1].strip().strip('"\'')
                elif line.startswith("TELEGRAM_USER_ID="):
                    chat_id = line.split("=", 1)[1].strip().strip('"\'')
    except Exception:
        pass
    
    if not token and "TELEGRAM_BOT_TOKEN" in os.environ:
        token = os.environ["TELEGRAM_BOT_TOKEN"]
    if not chat_id and "TELEGRAM_USER_ID" in os.environ:
        chat_id = os.environ["TELEGRAM_USER_ID"]
        
    return token, chat_id

def send_telegram_message(message):
    token, chat_id = get_telegram_creds()
    if not token or not chat_id:
        print("ERROR: Telegram Bot Token or User ID not configured in ~/aria/.env")
        sys.exit(1)
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        print("SUCCESS: Message sent to Telegram Saved Messages.")
    except Exception as e:
        print(f"ERROR: Failed to send Telegram message: {e}")

def post_tweet(content):
    print(json.dumps({"status": "error", "message": "Twitter API not yet integrated"}))

def post_linkedin(content):
    print(json.dumps({"status": "error", "message": "LinkedIn API not yet integrated"}))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARIA Social Agent Skill")
    parser.add_argument("action", choices=["tweet", "linkedin", "telegram"])
    parser.add_argument("--message", type=str, help="Content to post/send")
    
    args = parser.parse_args()
    if args.action == "telegram":
        if not args.message:
            print("ERROR: Missing --message")
            sys.exit(1)
        send_telegram_message(args.message)
    elif args.action == "tweet":
        post_tweet(args.message)
    elif args.action == "linkedin":
        post_linkedin(args.message)
