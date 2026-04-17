# Session Creation Troubleshooting

## Common Errors and Solutions

### Error: "The key is not registered in the system"

**What it means:** The verification session expired or the code was entered too late.

**Solutions:**
1. **Start fresh**: Close the modal and click "Add Account" again
2. **Be quick**: Enter the code within 2-3 minutes of receiving it
3. **Don't refresh**: Keep the browser tab open during the process
4. **One attempt**: Don't try multiple times with the same code

**Step-by-step fix:**
```
1. Click "Add Account"
2. Enter session name and phone
3. Click "Send Code"
4. IMMEDIATELY check Telegram app
5. Enter code within 1-2 minutes
6. Click "Verify Code"
```

---

### Error: "Verification code expired or invalid"

**Cause:** You waited too long or entered the wrong code.

**Solution:**
1. Close the modal
2. Click "Add Account" again
3. Request a new code
4. Enter it quickly (within 2 minutes)

---

### Error: "Two-factor authentication is enabled"

**Cause:** Your account has 2FA (Cloud Password) enabled.

**Solution:**
1. Enter the verification code first
2. Then enter your 2FA password in the password field
3. Click "Verify Code"

**Note:** This is your Telegram Cloud Password, NOT your phone lock code.

---

### Error: "Session expired. Please start over"

**Cause:** Too much time passed between requesting code and verifying.

**Solution:**
1. Close the modal completely
2. Click "Add Account" again
3. Complete the entire process quickly (under 3 minutes)

---

## Best Practices for Session Creation

### ✅ DO:
- Have your phone ready before starting
- Complete the process in one go (under 3 minutes)
- Keep the browser tab open
- Use the exact code from Telegram (no spaces)
- Enter 2FA password if you have it enabled

### ❌ DON'T:
- Refresh the page during creation
- Wait more than 2-3 minutes to enter code
- Try the same code multiple times
- Close the modal and reopen it
- Use old codes from previous attempts

---

## Alternative: Upload Session File

If you keep having issues creating sessions in the browser, you can create them using the command line script and then upload:

### Method 1: Using the Script

```bash
# On your local machine (not in Docker)
cd telegram-media-server
python scripts/create_session.py
```

This will:
1. Ask for your phone number
2. Send you a code
3. Ask for the code
4. Ask for 2FA password (if enabled)
5. Create a `.session` file

### Method 2: Upload to Web UI

1. Find the created `.session` file in `data/session/`
2. In the web UI, click "Switch Account"
3. Click "Upload Session File"
4. Select your `.session` file
5. Done!

---

## Understanding Telegram Session Flow

```
1. Request Code
   ↓
   [Telegram sends code to your app]
   ↓
2. Enter Code (within 2-3 minutes)
   ↓
3. If 2FA enabled → Enter Password
   ↓
4. Session Created ✅
```

**Important:** Each "Request Code" creates a NEW session attempt. You can't reuse codes from previous attempts.

---

## Why Sessions Expire

Telegram's security measures:
- Codes expire after 2-3 minutes
- Each code is tied to a specific session attempt
- Can't reuse codes
- Connection must stay open during verification

This is normal Telegram behavior, not a bug in the app.

---

## Quick Checklist

Before creating a session:

- [ ] Phone is nearby and unlocked
- [ ] Telegram app is open
- [ ] Browser tab will stay open
- [ ] You have 3-5 minutes of uninterrupted time
- [ ] You know your 2FA password (if enabled)
- [ ] Internet connection is stable

---

## Still Having Issues?

### Option 1: Use Command Line
The `scripts/create_session.py` script is more reliable because it maintains the connection throughout the process.

### Option 2: Upload Existing Session
If you have a working session from another device, just upload it.

### Option 3: Check Logs
Look at Docker logs for specific error messages:
```bash
docker-compose logs -f telegram-media-server
```

---

## Success Tips

**Fastest method:**
1. Have Telegram app open on another device
2. Click "Add Account" in web UI
3. Enter details and click "Send Code"
4. Immediately switch to Telegram app
5. Copy code
6. Paste in web UI
7. Click "Verify Code"
8. Total time: under 30 seconds ✅

**Most reliable method:**
1. Use `scripts/create_session.py` on command line
2. Upload the created `.session` file
3. No time pressure, no browser issues
