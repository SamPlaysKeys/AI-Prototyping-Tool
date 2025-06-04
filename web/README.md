# AI Prototyping Tool - Web Application

A FastAPI-based web interface for the AI Prototyping Tool with **LM Studio integration**, real-time status updates, and markdown rendering.

## Features

✅ **LM Studio Integration** - Automatically detects and uses local LM Studio models
✅ **POST endpoint `/generate`** - Accepts JSON with `prompt` and options
✅ **Simple HTML frontend** - Served at `/` with an intuitive form interface
✅ **Client-side Markdown rendering** - Uses Marked.js for beautiful content display
✅ **Live status updates** - WebSocket-based real-time progress notifications
✅ **Model detection** - Shows currently loaded LM Studio model in real-time
✅ **Containerized deployment** - Docker support for easy local deployment

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Build and run the application
cd web
docker-compose up --build

# Access the application
open http://localhost:8000
```

### Option 2: Direct Python Execution

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
cd web
python app.py

# Access the application
open http://localhost:8000
```

## API Endpoints

### `POST /generate`
Generate content based on a prompt and options.

**Request Body:**
```json
{
  "prompt": "Write a story about AI",
  "options": {
    "model": "gpt-3.5-turbo",
    "max_tokens": 1000,
    "temperature": 0.7,
    "format": "markdown"
  }
}
```

**Response:**
```json
{
  "id": "uuid-task-id",
  "content": "",
  "status": "processing",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### `GET /`
Serves the HTML frontend with form interface.

### `WS /ws`
WebSocket endpoint for real-time status updates.

### `GET /tasks/{task_id}`
Get the status of a specific generation task.

### `GET /health`
Health check endpoint.

## LM Studio Integration

The application automatically integrates with LM Studio running on your local machine:

### Prerequisites
1. **Install LM Studio** - Download from [lmstudio.ai](https://lmstudio.ai)
2. **Load a Model** - Use LM Studio to download and load any compatible model
3. **Start Local Server** - Enable the local server in LM Studio (default port 1234)

### Features
- **Automatic Detection** - Checks LM Studio connection status every 30 seconds
- **Model Display** - Shows currently loaded model name in the interface
- **Fallback Mode** - Uses mock responses when LM Studio is not available
- **Real-time Status** - Live connection indicator with refresh button

### Setup Steps
1. Start LM Studio application
2. Go to "Local Server" tab in LM Studio
3. Click "Start Server" (usually on port 1234)
4. Load any model you want to use
5. Open the web application - it will automatically detect the loaded model

## Web Interface

The web interface includes:

- **LM Studio Status Panel** - Shows connection status and current model
- **Prompt input** - Large textarea for entering prompts
- **Model selection** - Automatically populated with LM Studio model
- **Parameter controls** - Adjust max tokens, temperature, output format
- **Real-time status** - Live updates via WebSocket
- **Markdown rendering** - Beautiful display of generated content
- **Loading indicators** - Visual feedback during processing

## Configuration Options

| Option | Description | Default |
|--------|-------------|----------|
| `model` | AI model to use | `gpt-3.5-turbo` |
| `max_tokens` | Maximum tokens to generate | `1000` |
| `temperature` | Randomness (0.0-2.0) | `0.7` |
| `format` | Output format | `markdown` |

## Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn web.app:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

- `PYTHONPATH` - Python path (set to `/app` in Docker)
- `ENV` - Environment mode (`development`, `production`)

## Docker Deployment

### Build Image

```bash
docker build -t ai-prototyping-tool-web -f web/Dockerfile .
```

### Run Container

```bash
docker run -p 8000:8000 ai-prototyping-tool-web
```

### Health Check

The container includes a health check that verifies the `/health` endpoint every 30 seconds.

## Architecture

- **FastAPI** - Asynchronous web framework
- **WebSockets** - Real-time bidirectional communication
- **Marked.js** - Client-side markdown rendering
- **Responsive Design** - Mobile-friendly interface
- **Task Management** - Background processing with status tracking

## Integration Notes

This is a demonstration application. To integrate with actual AI services:

1. Replace the mock `process_generation()` function with real AI API calls
2. Add proper error handling and rate limiting
3. Implement authentication if needed
4. Add persistent storage for task history

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in docker-compose.yml or when running directly
2. **WebSocket connection fails**: Check firewall settings and ensure WebSocket support
3. **Container won't start**: Check logs with `docker-compose logs ai-prototyping-web`

### LM Studio Issues

1. **LM Studio not connecting**:
   - Ensure LM Studio is running and server is started
   - Check that LM Studio is using port 1234 (default)
   - Verify a model is loaded in LM Studio
   - Click the "Refresh" button in the status panel

2. **Model not detected**:
   - Make sure a model is fully loaded (not just downloaded)
   - Restart LM Studio if the model appears stuck
   - Check LM Studio logs for any errors

3. **Generation timeouts**:
   - Large models may take longer to respond
   - Current timeout is set to 2 minutes
   - Consider using a smaller/faster model for testing

4. **Mock responses instead of real AI**:
   - This means LM Studio is not accessible
   - Follow the setup steps in the LM Studio Integration section
   - Check the status panel for connection details

### Logs

```bash
# View container logs
docker-compose logs -f ai-prototyping-web

# Check health status
docker-compose ps
```
