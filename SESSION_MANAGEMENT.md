# Session Management Guide

## Overview

The Telegram Media Server now supports multiple Telegram accounts! You can:
- Create new sessions directly in the web UI
- Upload existing `.session` files
- Switch between multiple accounts
- Manage all your sessions from one place

## Features

### 1. Session Bar
At the top of the web interface, you'll see your current logged-in account with:
- Avatar (first letter of name)
- Full name
- Username or phone number
- Quick access to switch or add accounts

### 2. Create New Session (In-Browser)

**Steps:**
1. Click "➕ Add Account" button
2. Enter a session name (e.g., `my_work_account`)
3. Enter your phone number with country code (e.g., `+1234567890`)
4. Click "Send Code"
5. Check your Telegram app for the verification code
6. Enter the code (and 2FA password if enabled)
7. Click "Verify Code"
8. Done! Your session is created and saved

**Session files are stored in:** `/data/session/`

### 3. Upload Existing Session

If you have a `.session` file from another device:

1. Click "🔄 Switch Account"
2. Click "📤 Upload Session File"
3. Select your `.session` file
4. Click "Upload"
5. The session will be available immediately

### 4. Switch Between Accounts

1. Click "🔄 Switch Account"
2. See all available sessions
3. Click "Switch" on the account you want to use
4. The app will reconnect with that account
5. All chats and media will be from the new account

### 5. Delete Sessions

1. Click "🔄 Switch Account"
2. Click "Delete" next to any session
3. Confirm deletion
4. The session file will be permanently removed

## Technical Details

### API Endpoints

- `GET /api/sessions` - List all sessions and current user
- `POST /api/sessions/create` - Start session creation (sends code)
- `POST /api/sessions/verify` - Verify code and complete session
- `POST /api/sessions/switch` - Switch to different session
- `POST /api/sessions/upload` - Upload session file
- `DELETE /api/sessions/{name}` - Delete session

### Session Files

Session files are SQLite databases created by Telethon that store:
- Authorization keys
- User information
- Connection state

**Location:** `/data/session/*.session`

**Format:** Binary SQLite database (not human-readable)

### Security Notes

- Session files contain sensitive authentication data
- Keep them secure and don't share them
- Each session file is tied to a specific Telegram account
- Deleting a session doesn't log you out from Telegram (you can re-login)
- Session files work across devices (you can copy them)

## Use Cases

### Multiple Personal Accounts
Switch between your personal and work Telegram accounts without logging out.

### Family Sharing
Each family member can have their own session on the same server.

### Testing
Create test accounts for development without affecting your main account.

### Migration
Upload sessions from other devices or backup/restore sessions easily.

## Troubleshooting

### "Session is not authorized"
The session file is invalid or expired. Delete it and create a new one.

### "Two-factor authentication enabled"
Enter your 2FA password in the password field when verifying the code.

### "Code expired"
Start over and request a new code. Telegram codes expire after a few minutes.

### Can't switch sessions
Make sure the session file exists and is valid. Try uploading it again.

## Example Workflow

```
1. Open web interface
2. Click "Add Account"
3. Enter: session_name="work_account", phone="+1234567890"
4. Click "Send Code"
5. Check Telegram app → receive code "12345"
6. Enter code "12345"
7. Click "Verify Code"
8. ✅ Logged in as "John Doe"
9. Click "Load Chats" to see work account chats
10. Click "Switch Account" to change to personal account
```

## Notes

- You can have unlimited sessions
- Only one session is active at a time
- Switching sessions is instant (no restart needed)
- Background downloads continue even when switching accounts
- Each account has its own database of scanned chats/media
