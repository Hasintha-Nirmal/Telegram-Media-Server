# Privacy Fix: Per-Account Database Isolation

## Problem

When switching between accounts, users could see chats and media from other accounts because all accounts shared the same database. This is a serious privacy issue.

## Solution

Implemented **per-account database isolation**. Each Telegram account now has its own separate database file.

## How It Works

### Database Structure

Before:
```
/data/database/
  └── media.db  (shared by all accounts)
```

After:
```
/data/database/
  ├── account.db      (Hasintha's data)
  ├── flagtous.db     (Flagtous's data)
  └── mywork.db       (Work account's data)
```

### Automatic Switching

When you switch accounts:
1. The app connects to the new Telegram session
2. Automatically switches to that account's database
3. All queries (chats, media, messages) only see that account's data
4. Background workers (auto-sync, downloads) use the current account's database

### Complete Isolation

Each account has completely separate:
- ✅ Chat lists
- ✅ Media indexes
- ✅ Message history
- ✅ Download queues
- ✅ Sync states

**No data leakage between accounts!**

## Technical Implementation

### New Components

1. **DatabaseManager** (`database/manager.py`)
   - Manages multiple database connections
   - Creates separate database per account
   - Tracks current active account

2. **Updated telegram_client.py**
   - Sets current account when connecting
   - Ensures database isolation on account switch

3. **Updated background workers**
   - Auto-sync only processes current account
   - Download queue only processes current account's downloads

### Database Naming

Database files are named after the session file:
- `account.session` → `account.db`
- `flagtous.session` → `flagtous.db`
- `my_work_account.session` → `my_work_account.db`

## Benefits

### Privacy
- ✅ Complete data isolation between accounts
- ✅ No cross-account data leakage
- ✅ Each account's data is private

### Performance
- ✅ Smaller databases (only one account's data)
- ✅ Faster queries
- ✅ Better scalability

### Organization
- ✅ Clear separation of data
- ✅ Easy to backup individual accounts
- ✅ Easy to delete an account's data

## Migration

### Existing Data

If you already have data in the old `media.db`:
1. It will remain as-is (not deleted)
2. New accounts will get fresh databases
3. You can manually migrate if needed

### Fresh Start

For most users, this is a fresh start:
- Each account starts with an empty database
- Click "Load Chats" to populate
- Scan media as needed

## Testing

After rebuilding:

1. **Switch to Account 1**
   - Click "Load Chats"
   - See Account 1's chats only

2. **Switch to Account 2**
   - Click "Load Chats"
   - See Account 2's chats only
   - Account 1's chats are NOT visible ✅

3. **Verify Isolation**
   - Scan media in Account 1
   - Switch to Account 2
   - Account 1's media is NOT visible ✅

## Rebuild Required

```bash
# Stop container
docker-compose down

# Rebuild with new code
docker-compose build --no-cache

# Start fresh
docker-compose up
```

## Files Changed

- `database/manager.py` - NEW: Database manager
- `database/__init__.py` - Updated to use manager
- `app/telegram_client.py` - Sets current account
- `app/downloader.py` - Uses per-account database
- `main.py` - Background workers use per-account database

## Security Notes

- Each account's database is completely isolated
- No shared data between accounts
- Session files remain separate (as before)
- Download files are still organized by chat (not by account)

## Future Enhancements

Possible improvements:
- Add account selector in UI to see which account is active
- Show database size per account
- Export/import account data
- Merge accounts (if needed)
