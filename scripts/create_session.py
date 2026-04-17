#!/usr/bin/env python3
"""
Script to create a Telegram session file
Run this before starting the server for the first time
"""

from telethon import TelegramClient
import asyncio
import os
import sys

async def create_session(api_id, api_hash, session_name):
    """Create Telegram session"""
    client = TelegramClient(session_name, api_id, api_hash)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            phone = input("Enter your phone number (with country code, e.g., +1234567890): ").strip()
            await client.send_code_request(phone)
            code = input("Enter the code you received: ").strip()
            
            try:
                await client.sign_in(phone, code)
            except Exception as e:
                if "password" in str(e).lower():
                    password = input("Two-factor authentication enabled. Enter your password: ").strip()
                    await client.sign_in(password=password)
                else:
                    raise
        
        me = await client.get_me()
        print(f"\n✅ Session created successfully!")
        print(f"Logged in as: {me.first_name} (@{me.username})")
        print(f"Session file: {session_name}.session")
        print(f"\nMove this file to: ./data/session/{session_name}.session")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        await client.disconnect()


def main():
    print("=== Telegram Session Creator ===\n")
    
    # Get credentials
    api_id = input("Enter your API_ID: ").strip()
    api_hash = input("Enter your API_HASH: ").strip()
    session_name = input("Enter session name (default: account): ").strip() or "account"
    
    if not api_id or not api_hash:
        print("Error: API_ID and API_HASH are required")
        sys.exit(1)
    
    try:
        api_id = int(api_id)
    except ValueError:
        print("Error: API_ID must be a number")
        sys.exit(1)
    
    # Run async function
    asyncio.run(create_session(api_id, api_hash, session_name))


if __name__ == "__main__":
    main()
