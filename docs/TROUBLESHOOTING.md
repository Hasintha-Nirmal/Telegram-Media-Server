# Troubleshooting Guide

Common issues and solutions for Telegram Media Server.

## Connection Issues

### "Session is not authorized"

**Problem**: The session file is invalid or expired.

**Solutions**:
1. Create a new session file:
   ```bash
   python scripts/create_session.py
   ```
2. Ensure the session file is in the correct location: `./data/session/account.session`
3. Check file permissions: `chmod 600 data/session/account.session`
4. Verify the session was created with the same API_ID and API_HASH

### "Connection refused" or "Cannot connect to Telegram"

**Problem**: Network or firewall issues.

**Solutions**:
1. Check internet connection
2. Verify Telegram is not blocked in your region
3. Try using a VPN
4. Check Docker network: `docker network ls`
5. Restart Docker: `docker-compose restart`

### "FloodWaitError"

**Problem**: Too many requests to Telegram API.

**Solutions**:
1. Wait for the specified time (usually 1-60 seconds)
2. Reduce `SYNC_INTERVAL` in .env
3. Reduce `MAX_PARALLEL_DOWNLOADS`
4. The system automatically handles this, just wait

## Database Issues

### "Database is locked"

**Problem**: SQLite doesn't handle concurrent writes well.

**Solutions**:
1. Use PostgreSQL for production:
   ```bash
   docker-compose -f docker-compose.postgres.yml up -d
   ```
2. Reduce concurrent operations
3. Restart the server: `docker-compose restart`

### "No such table"

**Problem**: Database not initialized.

**Solutions**:
1. Delete database and restart:
   ```bash
   rm data/database/media.db
   docker-compose restart
   ```
2. Check logs: `docker-compose logs -f`

### "Database migration needed"

**Problem**: Database schema changed.

**Solutions**:
1. Backup current database:
   ```bash
   cp data/database/media.db data/database/media.db.backup
   ```
2. Delete and recreate:
   ```bash
   rm data/database/media.db
   docker-compose restart
   ```

## Scanning Issues

### "No media found after scanning"

**Problem**: Chats have no media or scanning failed.

**Solutions**:
1. Check if you actually have media in your chats
2. Verify chat access permissions
3. Check logs for errors: `docker-compose logs -f`
4. Try scanning a specific chat first
5. Ensure session has proper permissions

### "Scanning is very slow"

**Problem**: Large number of messages to process.

**Solutions**:
1. This is normal for first scan
2. Subsequent scans are incremental and faster
3. Scan specific chats instead of all at once
4. Increase system resources (CPU/RAM)
5. Use PostgreSQL instead of SQLite

### "Scanning stopped/interrupted"

**Problem**: Process crashed or was killed.

**Solutions**:
1. Check logs: `docker-compose logs -f`
2. Restart server: `docker-compose restart`
3. Scanning will resume from last checkpoint
4. Check disk space: `df -h`
5. Check memory: `docker stats`

## Streaming Issues

### "Video won't play"

**Problem**: Browser compatibility or media format.

**Solutions**:
1. Try a different browser (Chrome recommended)
2. Check if media still exists in Telegram
3. Verify MIME type is correct
4. Check browser console for errors (F12)
5. Try downloading instead of streaming

### "Buffering/stuttering during playback"

**Problem**: Network speed or server performance.

**Solutions**:
1. Check internet speed
2. Reduce video quality (if possible)
3. Download for offline viewing
4. Check server CPU/RAM usage
5. Ensure Docker has enough resources

### "Range requests not working"

**Problem**: Seeking doesn't work in video.

**Solutions**:
1. Check browser supports range requests
2. Verify media size is available
3. Check server logs for errors
4. Try a different video player

## Download Issues

### "Downloads stuck in queue"

**Problem**: Download worker not running or failed.

**Solutions**:
1. Check logs: `docker-compose logs -f`
2. Restart server: `docker-compose restart`
3. Check `MAX_PARALLEL_DOWNLOADS` setting
4. Verify disk space: `df -h`
5. Check download queue status: `GET /api/queue`

### "Download failed"

**Problem**: Network error or file no longer available.

**Solutions**:
1. Check if media still exists in Telegram
2. Retry the download
3. Check disk space
4. Check file permissions on download directory
5. Review error message in queue status

### "Downloaded files not organized correctly"

**Problem**: File organization logic issue.

**Solutions**:
1. Check chat name has valid characters
2. Verify download path permissions
3. Check logs for errors
4. Manually organize if needed

## Docker Issues

### "Container won't start"

**Problem**: Configuration or dependency issue.

**Solutions**:
1. Check logs: `docker-compose logs`
2. Verify .env file exists and is correct
3. Check port 8080 is not in use: `lsof -i :8080`
4. Rebuild image: `docker-compose build --no-cache`
5. Remove and recreate: `docker-compose down && docker-compose up -d`

### "Permission denied" errors

**Problem**: File permission issues.

**Solutions**:
1. Fix data directory permissions:
   ```bash
   sudo chown -R $USER:$USER data/
   chmod -R 755 data/
   ```
2. Check Docker has access to volumes
3. Run with proper user in docker-compose.yml

### "Out of disk space"

**Problem**: Downloads filled up disk.

**Solutions**:
1. Check disk usage: `df -h`
2. Clean up old downloads
3. Increase disk space
4. Use external storage volume
5. Set up automatic cleanup

## Performance Issues

### "Web interface is slow"

**Problem**: Database queries or large result sets.

**Solutions**:
1. Use PostgreSQL instead of SQLite
2. Reduce page size (limit parameter)
3. Add more database indexes
4. Increase server resources
5. Enable caching (future feature)

### "High CPU usage"

**Problem**: Scanning or processing intensive tasks.

**Solutions**:
1. This is normal during scanning
2. Reduce `MAX_PARALLEL_DOWNLOADS`
3. Increase `SYNC_INTERVAL`
4. Limit concurrent API requests
5. Add more CPU cores

### "High memory usage"

**Problem**: Large data sets or memory leaks.

**Solutions**:
1. Restart server periodically
2. Reduce batch sizes
3. Use pagination
4. Increase Docker memory limit
5. Monitor with `docker stats`

## API Issues

### "404 Not Found"

**Problem**: Endpoint doesn't exist or media not found.

**Solutions**:
1. Check API documentation
2. Verify media ID is correct
3. Ensure media was indexed
4. Check URL spelling

### "500 Internal Server Error"

**Problem**: Server-side error.

**Solutions**:
1. Check logs: `docker-compose logs -f`
2. Verify database connection
3. Check Telegram connection
4. Restart server
5. Report bug with logs

### "Timeout errors"

**Problem**: Request taking too long.

**Solutions**:
1. Reduce result set size
2. Use pagination
3. Optimize database queries
4. Increase timeout settings
5. Check server resources

## Search Issues

### "Search returns no results"

**Problem**: Query doesn't match or no data indexed.

**Solutions**:
1. Verify media is indexed
2. Try simpler search terms
3. Check spelling
4. Use filters to narrow down
5. Try browsing instead

### "Search is slow"

**Problem**: Large database or missing indexes.

**Solutions**:
1. Use PostgreSQL
2. Add database indexes
3. Reduce search scope with filters
4. Use pagination
5. Optimize queries

## Configuration Issues

### "Environment variables not loaded"

**Problem**: .env file not read or incorrect format.

**Solutions**:
1. Verify .env file exists
2. Check file format (no spaces around =)
3. Restart Docker: `docker-compose down && docker-compose up -d`
4. Check docker-compose.yml env_file setting
5. Set variables directly in docker-compose.yml

### "Invalid API credentials"

**Problem**: Wrong API_ID or API_HASH.

**Solutions**:
1. Verify credentials at https://my.telegram.org
2. Check for extra spaces or quotes
3. Ensure API_ID is a number
4. Recreate session with correct credentials

## Debugging Tips

### Enable Debug Logging

Edit `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Check Docker Logs
```bash
docker-compose logs -f
```

### Check Container Status
```bash
docker-compose ps
```

### Check Resource Usage
```bash
docker stats telegram-media-server
```

### Access Container Shell
```bash
docker-compose exec telegram-media-server bash
```

### Test Database Connection
```bash
docker-compose exec telegram-media-server python -c "
from database import init_db
import asyncio
asyncio.run(init_db())
print('Database OK')
"
```

### Test Telegram Connection
```bash
docker-compose exec telegram-media-server python -c "
from app.telegram_client import telegram_client
import asyncio
asyncio.run(telegram_client.connect())
print('Telegram OK')
"
```

## Getting Help

If you're still stuck:

1. **Check logs**: Most issues show up in logs
2. **Search issues**: Check GitHub issues for similar problems
3. **Provide details**: When asking for help, include:
   - Error messages
   - Logs (sanitize sensitive info)
   - System info (OS, Docker version)
   - Steps to reproduce
4. **Create issue**: Open a GitHub issue with details

## Common Error Messages

### "RuntimeError: Event loop is closed"
- Restart the server
- Check for async/await issues

### "OperationalError: database is locked"
- Use PostgreSQL
- Reduce concurrent operations

### "TimeoutError"
- Increase timeout settings
- Check network connection

### "PermissionError"
- Fix file permissions
- Check Docker volume mounts

### "ImportError: No module named"
- Rebuild Docker image
- Check requirements.txt

## Prevention Tips

1. **Regular backups**: Backup session and database
2. **Monitor resources**: Watch CPU, RAM, disk usage
3. **Update regularly**: Keep dependencies updated
4. **Use PostgreSQL**: For production deployments
5. **Set up monitoring**: Use logging and metrics
6. **Test changes**: Test in development first
7. **Read logs**: Check logs regularly for warnings

## Emergency Recovery

If everything is broken:

```bash
# Stop everything
docker-compose down

# Backup data
cp -r data data.backup

# Clean slate
rm -rf data/database/*

# Restart
docker-compose up -d

# Re-scan
# Access http://localhost:8080 and click "Scan Chats" then "Scan Media"
```

Your session file and downloads are preserved, only the index is rebuilt.
