# API Documentation

Base URL: `http://localhost:8080`

## Endpoints

### Chats

#### Get All Chats
```
GET /api/chats?limit=100&offset=0
```

Response:
```json
[
  {
    "id": 123456789,
    "name": "My Channel",
    "username": "mychannel",
    "chat_type": "channel",
    "member_count": 1000,
    "last_activity": "2024-01-01T12:00:00"
  }
]
```

#### Scan Chats
```
POST /api/scan/chats
```

Response:
```json
{
  "count": 42
}
```

### Media

#### Get Media
```
GET /api/media?chat_id=123&media_type=video&limit=100&offset=0
```

Query Parameters:
- `chat_id` (optional): Filter by chat
- `media_type` (optional): Filter by type (video, photo, audio, document, voice, gif)
- `limit` (optional): Results per page (default: 100, max: 1000)
- `offset` (optional): Pagination offset (default: 0)

Response:
```json
[
  {
    "id": 1,
    "message_id": 123,
    "chat_id": 456,
    "chat_name": "My Channel",
    "file_name": "video.mp4",
    "file_size": 10485760,
    "media_type": "video",
    "duration": 120,
    "upload_date": "2024-01-01T12:00:00"
  }
]
```

#### Get Media by ID
```
GET /api/media/{media_id}
```

Response:
```json
{
  "id": 1,
  "message_id": 123,
  "chat_id": 456,
  "file_name": "video.mp4",
  "file_size": 10485760,
  "media_type": "video",
  "duration": 120,
  "width": 1920,
  "height": 1080,
  "mime_type": "video/mp4",
  "upload_date": "2024-01-01T12:00:00"
}
```

#### Scan Media
```
POST /api/scan/media
```

Scan all chats for media.

Response:
```json
{
  "count": 1234
}
```

#### Scan Chat Media
```
POST /api/scan/chat/{chat_id}
```

Scan specific chat for media.

Response:
```json
{
  "count": 56
}
```

### Search

#### Search Media
```
GET /api/search?q=video&media_type=video&chat_id=123&min_size=1000000&max_size=100000000&limit=100&offset=0
```

Query Parameters:
- `q` (optional): Search query (searches filename and chat name)
- `media_type` (optional): Filter by media type
- `chat_id` (optional): Filter by chat
- `min_size` (optional): Minimum file size in bytes
- `max_size` (optional): Maximum file size in bytes
- `limit` (optional): Results per page
- `offset` (optional): Pagination offset

Response: Same as Get Media

### Statistics

#### Get Stats
```
GET /api/stats
```

Response:
```json
{
  "total_chats": 42,
  "total_media": 1234,
  "total_storage": 10737418240,
  "media_by_type": {
    "video": 500,
    "photo": 600,
    "audio": 100,
    "document": 34
  }
}
```

### Downloads

#### Queue Download
```
POST /api/download/{media_id}
```

Response:
```json
{
  "queue_id": 1,
  "status": "queued"
}
```

#### Get Download Queue
```
GET /api/queue
```

Response:
```json
[
  {
    "id": 1,
    "media_id": 123,
    "status": "downloading",
    "progress": 45.5,
    "error_message": null,
    "created_at": "2024-01-01T12:00:00"
  }
]
```

### Streaming

#### Stream Media
```
GET /stream/{media_id}
```

Streams media with HTTP range request support for video playback.

Headers:
- `Range: bytes=0-1023` (optional): Request specific byte range

Response:
- Status: 200 (full content) or 206 (partial content)
- Headers:
  - `Content-Type`: Media MIME type
  - `Content-Length`: Content size
  - `Content-Range`: Byte range (for partial content)
  - `Accept-Ranges: bytes`

## Usage Examples

### Python

```python
import requests

# Get all videos
response = requests.get('http://localhost:8080/api/media?media_type=video')
videos = response.json()

# Search for media
response = requests.get('http://localhost:8080/api/search?q=funny&media_type=video')
results = response.json()

# Queue download
response = requests.post('http://localhost:8080/api/download/123')
queue_info = response.json()

# Stream video
video_url = 'http://localhost:8080/stream/123'
# Use in HTML5 video player or download with range requests
```

### JavaScript

```javascript
// Get stats
fetch('/api/stats')
  .then(r => r.json())
  .then(data => console.log(data));

// Search media
fetch('/api/search?q=video&media_type=video')
  .then(r => r.json())
  .then(media => console.log(media));

// Stream video in HTML5 player
const video = document.createElement('video');
video.src = '/stream/123';
video.controls = true;
document.body.appendChild(video);
```

### cURL

```bash
# Get chats
curl http://localhost:8080/api/chats

# Search media
curl "http://localhost:8080/api/search?q=video&media_type=video"

# Queue download
curl -X POST http://localhost:8080/api/download/123

# Stream with range request
curl -H "Range: bytes=0-1023" http://localhost:8080/stream/123
```

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `206 Partial Content`: Successful range request
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message"
}
```
