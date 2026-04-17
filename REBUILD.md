# Rebuild Instructions

## Changes Made

### 1. Fixed Session File Permissions
- Updated Dockerfile to set proper permissions on `/data` directory
- Fixes "readonly database" error

### 2. Improved Session Creation Flow
- Now a clear 3-step process:
  1. Enter phone number → Send code
  2. Enter verification code → Verify
  3. If 2FA enabled → Enter password (only shown if needed)

### 3. Better Error Handling
- Clear, actionable error messages
- Detects expired codes, invalid codes, 2FA requirements
- Automatic cleanup of failed sessions

## How to Rebuild

```bash
# Stop current container
docker-compose down

# Rebuild with new changes
docker-compose build --no-cache

# Start fresh
docker-compose up
```

## Testing Session Creation

1. Open http://localhost:8080
2. Click "Add Account"
3. Enter session name (e.g., `test_account`)
4. Enter phone with country code (e.g., `+1234567890`)
5. Click "Send Code"
6. Check Telegram app for code
7. Enter code and click "Verify Code"
8. If 2FA enabled, you'll see password screen automatically
9. Enter password and click "Verify Password"
10. Done! ✅

## What's Different Now

**Before:**
- Single form with all fields
- Confusing when to enter what
- Poor error messages
- Session permission issues

**After:**
- Step-by-step wizard
- Clear instructions at each step
- Only shows 2FA field if actually needed
- Helpful error messages
- Proper file permissions

## Troubleshooting

If you still see "readonly database":
```bash
# Fix permissions on existing data
chmod -R 777 telegram-media-server/data/

# Then rebuild
docker-compose build --no-cache
docker-compose up
```

If session creation fails:
- Make sure you enter the code within 2 minutes
- Don't refresh the page during creation
- If it fails, close modal and start completely over
- Check Docker logs for specific errors
