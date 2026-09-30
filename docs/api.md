# API Reference

Base URL: `/api/v1`

All responses follow a consistent format. Errors use the format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

## Authentication
Currently no authentication required (local-only application).

## Health & System

### GET /health
Basic health check.

**Response 200:**
```json
{
  "status": "healthy",
  "timestamp": "2026-09-30T12:00:00Z"
}
```

### GET /ready
Readiness check including database connectivity.

**Response 200:**
```json
{
  "status": "ready",
  "timestamp": "2026-09-30T12:00:00Z"
}
```

### GET /system/capabilities
Get system capabilities and available providers.

**Response 200:**
```json
{
  "product_name": "Sahayak",
  "providers": {
    "npu_available": true,
    "gpu_available": false,
    "cpu_available": true,
    "available_providers": ["QNNExecutionProvider", "CPUExecutionProvider"],
    "selected_providers": ["QNNExecutionProvider", "CPUExecutionProvider"]
  },
  "models_loaded": {
    "vad": {"provider": "QNNExecutionProvider", "simulated": false},
    "asr": {"provider": "QNNExecutionProvider", "simulated": false},
    "summarizer": {"provider": "CPU", "simulated": false}
  },
  "simulated_mode": false
}
```

## Sessions

### POST /sessions
Create a new session.

**Request:**
```json
{
  "title": "Team Meeting",
  "language": "en"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "title": "Team Meeting",
  "language": "en",
  "started_at": "2026-09-30T12:00:00Z",
  "ended_at": null,
  "status": "active"
}
```

### GET /sessions
List sessions with pagination.

**Query Parameters:**
- `limit` (int, default 50, max 100)
- `offset` (int, default 0)
- `status` (string, optional: active|completed|archived)

**Response 200:**
```json
[
  {
    "id": "uuid",
    "title": "Team Meeting",
    "language": "en",
    "started_at": "2026-09-30T12:00:00Z",
    "ended_at": "2026-09-30T13:00:00Z",
    "status": "completed"
  }
]
```

### GET /sessions/{id}
Get session with full details (transcript segments and summaries).

**Response 200:**
```json
{
  "id": "uuid",
  "title": "Team Meeting",
  "language": "en",
  "started_at": "2026-09-30T12:00:00Z",
  "ended_at": "2026-09-30T13:00:00Z",
  "status": "completed",
  "transcript_segments": [
    {
      "id": "uuid",
      "session_id": "uuid",
      "start_ms": 0,
      "end_ms": 5000,
      "text": "Hello everyone",
      "language": "en",
      "provider": "QNNExecutionProvider",
      "simulated": false
    }
  ],
  "summaries": [
    {
      "id": "uuid",
      "session_id": "uuid",
      "key_points": ["Meeting started", "Agenda discussed"],
      "action_items": ["Send follow-up email"],
      "provider": "CPU",
      "simulated": false,
      "created_at": "2026-09-30T13:05:00Z"
    }
  ]
}
```

### PATCH /sessions/{id}
Update a session.

**Request:**
```json
{
  "title": "Updated Title",
  "status": "completed"
}
```

**Response 200:**
```json
{
  "id": "uuid",
  "title": "Updated Title",
  "language": "en",
  "started_at": "2026-09-30T12:00:00Z",
  "ended_at": "2026-09-30T13:00:00Z",
  "status": "completed"
}
```

### DELETE /sessions/{id}
Delete a session.

**Response 204:** No content

### POST /sessions/{id}/summary
Generate a summary for a session.

**Response 200:**
```json
{
  "id": "uuid",
  "session_id": "uuid",
  "key_points": ["Key point 1", "Key point 2"],
  "action_items": ["Action item 1"],
  "provider": "CPU",
  "simulated": false,
  "created_at": "2026-09-30T13:05:00Z"
}
```

### GET /sessions/{id}/summary
Get the latest summary for a session.

**Response 200:** Same as POST response

### WebSocket /sessions/{id}/stream
WebSocket endpoint for live caption streaming.

**Client → Server:** Raw audio bytes (16kHz, 16-bit PCM, mono)

**Server → Client:** JSON messages
```json
{
  "type": "caption",
  "payload": {
    "text": "Transcribed text",
    "provider": "QNNExecutionProvider",
    "simulated": false,
    "latency_ms": 45
  }
}
```

```json
{
  "type": "error",
  "payload": {
    "message": "Error description"
  }
}
```

```json
{
  "type": "end",
  "payload": {}
}
```

## Benchmarks

### POST /benchmarks
Run a new benchmark.

**Request:**
```json
{
  "audio_name": "benchmark_audio.wav",
  "audio_duration_s": 30.0,
  "device_info": {}
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "audio_name": "benchmark_audio.wav",
  "audio_duration_s": 30.0,
  "started_at": "2026-09-30T12:00:00Z",
  "finished_at": "2026-09-30T12:05:00Z",
  "device_info": {},
  "results": [
    {
      "id": "uuid",
      "run_id": "uuid",
      "provider": "QNNExecutionProvider",
      "stage": "vad",
      "latency_ms": 12,
      "real_time_factor": 0.0004,
      "cpu_percent": 5.2,
      "npu_percent": 45.0,
      "battery_delta_percent": 0.1,
      "simulated": false
    }
  ]
}
```

### GET /benchmarks
List benchmark runs.

**Query Parameters:**
- `limit` (int, default 50, max 100)
- `offset` (int, default 0)

**Response 200:**
```json
[
  {
    "id": "uuid",
    "audio_name": "benchmark_audio.wav",
    "audio_duration_s": 30.0,
    "started_at": "2026-09-30T12:00:00Z",
    "finished_at": "2026-09-30T12:05:00Z",
    "device_info": {}
  }
]
```

### GET /benchmarks/{id}
Get benchmark run with all results.

**Response 200:** Same as POST response with full results array.

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| NOT_FOUND | 404 | Resource not found |
| VALIDATION_ERROR | 422 | Input validation failed |
| ENGINE_ERROR | 500 | ML engine processing error |
| PROVIDER_UNAVAILABLE | 503 | Requested execution provider not available |
| INTERNAL_ERROR | 500 | Unexpected server error |

## Rate Limiting
Not currently implemented. Recommended for production deployments.

## WebSocket Protocol

The WebSocket protocol expects raw audio data (Int16Array) sent as binary messages.
The server responds with JSON text messages for captions and errors.

Recommended audio format:
- Sample rate: 16000 Hz
- Bit depth: 16-bit
- Channels: 1 (mono)
- Chunk size: ~4096 samples (~256ms)

## Pagination
List endpoints support `limit` and `offset` query parameters.
Maximum limit is 100.