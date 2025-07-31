#!/usr/bin/env python3
"""
Telegram Session Manager

This script helps manage Telegram sessions for the Docker container.
It can be used to set up a new session or reset an existing one.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# Load environment variables
load_dotenv()

def get_credentials():
    """Get Telegram credentials from environment variables"""
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    
    if not all([api_id, api_hash, phone]):
        print("Error: Missing Telegram credentials in environment variables")
        print("Please set TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_PHONE")
        sys.exit(1)
    
    return api_id, api_hash, phone

async def setup_session(session_path: str = None):
    """Set up a new Telegram session"""
    api_id, api_hash, phone = get_credentials()
    
    if session_path:
        session_file = os.path.join(session_path, 'news_session')
    else:
        session_file = 'news_session'
    
    print(f"Setting up Telegram session at: {session_file}")
    
    # Create session directory if it doesn't exist
    if session_path and not os.path.exists(session_path):
        os.makedirs(session_path, exist_ok=True)
        print(f"Created session directory: {session_path}")
    
    client = TelegramClient(session_file, api_id, api_hash)
    
    try:
        await client.start(phone=phone)
        print("✅ Session setup successful!")
        print("You can now run the API server.")
        
    except SessionPasswordNeededError:
        print("⚠️  Two-factor authentication is enabled.")
        print("Please enter your 2FA password when prompted.")
        await client.start(phone=phone)
        print("✅ Session setup successful with 2FA!")
        
    except Exception as e:
        print(f"❌ Session setup failed: {str(e)}")
        sys.exit(1)
    
    finally:
        await client.disconnect()

async def reset_session(session_path: str = None):
    """Reset/remove existing Telegram session"""
    if session_path:
        session_file = os.path.join(session_path, 'news_session')
    else:
        session_file = 'news_session'
    
    session_files = [
        session_file,
        f"{session_file}.session",
        f"{session_file}.session-journal"
    ]
    
    removed_files = []
    for file_path in session_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                removed_files.append(file_path)
                print(f"Removed: {file_path}")
            except Exception as e:
                print(f"Failed to remove {file_path}: {str(e)}")
    
    if removed_files:
        print(f"✅ Reset {len(removed_files)} session files")
    else:
        print("ℹ️  No session files found to reset")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python session_manager.py setup [session_path]")
        print("  python session_manager.py reset [session_path]")
        print("\nExamples:")
        print("  python session_manager.py setup")
        print("  python session_manager.py setup /app/sessions")
        print("  python session_manager.py reset")
        print("  python session_manager.py reset /app/sessions")
        sys.exit(1)
    
    command = sys.argv[1]
    session_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if command == "setup":
        asyncio.run(setup_session(session_path))
    elif command == "reset":
        asyncio.run(reset_session(session_path))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main() 