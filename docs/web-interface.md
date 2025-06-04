# Web Interface Documentation

Comprehensive guide to using the AI Prototyping Tool's web interface built with FastAPI.

## 🌐 Overview

The web interface provides an intuitive, browser-based way to generate AI-powered documentation with real-time updates and interactive features.

### Key Features

- **Interactive Form Interface**: Easy-to-use web forms for prompt input
- **Real-time Updates**: WebSocket-based progress notifications
- **Markdown Rendering**: Beautiful client-side markdown display with syntax highlighting
- **Model Management**: Real-time model detection and selection
- **Download Options**: Export generated content in multiple formats
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 🚀 Getting Started

### Quick Start

```bash
# Option 1: Using Docker (Recommended)
cd web
docker-compose up --build

# Option 2: Direct Python execution
cd web
python app.py

# Access the application
open http://localhost:8000
```

### Prerequisites

- **LM Studio**: Running with loaded model
- **Python 3.8+**: For direct execution
- **Docker**: For containerized deployment
- **Modern Browser**: Chrome, Firefox, Safari, or Edge

## 📝 User Interface Guide

### Main Interface

The web interface consists of several key sections:

#### 1. Header Section
- **Title**: AI Prototyping Tool branding
- **Status Indicator**: Shows LM Studio connection status
- **Model Information**: Displays currently loaded model

#### 2. Input Form

**Prompt Input**:
- Large text area for entering project description
- Support for multiline prompts
- Character count indicator
- Clear button for quick reset

**Deliverable Selection**:
- Checkboxes for each deliverable type
- "Select All" / "Deselect All" options
- Tooltips with deliverable descriptions

**Generation Parameters**:
- **Max Tokens**: Slider control (512-8192)
- **Temperature**: Slider control (0.1-1.0)
- **Top-p**: Slider control (0.1-1.0)
- **Output Format**: Radio buttons (Markdown/JSON)
- **Merge**: Checkbox to combine deliverables

#### 3. Generation Controls

- **Generate Button**: Primary action to start generation
- **Clear Form**: Reset all inputs to defaults
- **Load Example**: Populate form with sample data

#### 4. Progress Section

- **Progress Bar**: Visual progress indicator
- **Status Messages**: Real-time generation updates
- **Current Step**: Shows which deliverable is being generated
- **Estimated Time**: Remaining time estimate

#### 5. Results Section

- **Tabbed Interface**: Switch between generated deliverables
- **Markdown Preview**: Rendered markdown with syntax highlighting
- **Raw Content**: Plain text view for copying
- **Download Options**: Save individual files or complete package

### Step-by-Step Usage

#### Step 1: Enter Your Prompt

1. **Click in the prompt text area**
2. **Type your project description**, for example:
   ```
   Create a mobile application for fitness tracking that helps users
   monitor their daily activities, set goals, and track progress over time.
   The app should include social features for motivation and challenges.
   ```
3. **Review the character count** (recommended: 100-1000 characters)

#### Step 2: Select Deliverables

1. **Choose deliverable types** by checking boxes:
   - ✅ Problem Statement - Executive summary and problem analysis
   - ✅ Personas - User profiles and characteristics
   - ✅ Use Cases - Detailed user interaction scenarios
   - ✅ Tool Outline - Technical architecture overview
   - ⬜ Implementation Instructions - Development guide
   - ⬜ Effectiveness Assessment - Success metrics

2. **Use "Select All"** for comprehensive documentation

#### Step 3: Configure Parameters

1. **Adjust Max Tokens** (default: 2048)
   - Fewer tokens = faster generation, shorter content
   - More tokens = slower generation, more detailed content

2. **Set Temperature** (default: 0.7)
   - Lower (0.1-0.4) = more focused, consistent output
   - Higher (0.7-1.0) = more creative, diverse output

3. **Choose Output Format**
   - Markdown: Human-readable with formatting
   - JSON: Structured data for programmatic use

#### Step 4: Generate Content

1. **Click "Generate Documentation"**
2. **Watch the progress bar** and status messages
3. **Wait for completion** (typically 30 seconds to 2 minutes)

#### Step 5: Review and Download

1. **Switch between tabs** to review each deliverable
2. **Use the preview** to see formatted markdown
3. **Download individual files** or the complete package
4. **Copy content** directly from the raw text view

## 🔧 Configuration Options

### Application Settings

The web interface can be configured through environment variables:

```bash
# Server Configuration
export HOST="0.0.0.0"                    # Bind address
export PORT="8000"                        # Port number
export DEBUG="false"                      # Debug mode

# LM Studio Configuration
export LM_STUDIO_URL="http://localhost:1234/v1"
export LM_STUDIO_TIMEOUT="30"             # Connection timeout

# Generation Defaults
export DEFAULT_MAX_TOKENS="2048"
export DEFAULT_TEMPERATURE="0.7"
export DEFAULT_TOP_P="0.9"
export DEFAULT_OUTPUT_FORMAT="markdown"

# UI Configuration
export ENABLE_ANALYTICS="false"          # Usage analytics
export MAX_PROMPT_LENGTH="5000"          # Prompt character limit
export WEBSOCKET_TIMEOUT="300"           # WebSocket timeout
```

### CORS Configuration

For cross-origin requests (if hosting separately):

```python
# In app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📱 API Integration

### REST API Endpoints

The web interface exposes these API endpoints:

#### POST `/generate`

Generate documentation programmatically:

```javascript
fetch('http://localhost:8000/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    prompt: 'Create a task management app',
    deliverable_types: ['problem_statement', 'personas'],
    max_tokens: 2048,
    temperature: 0.7,
    output_format: 'markdown'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Generated content:', data.content);
})
.catch(error => {
  console.error('Error:', error);
});
```

#### WebSocket `/ws`

Real-time updates during generation:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function(event) {
  console.log('WebSocket connected');
};

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);

  switch(data.type) {
    case 'status':
      console.log('Status:', data.data.status);
      break;
    case 'progress':
      console.log('Progress:', data.data.progress * 100 + '%');
      break;
    case 'complete':
      console.log('Generation complete!', data.data);
      break;
    case 'error':
      console.error('Error:', data.data.message);
      break;
  }
};

ws.onerror = function(error) {
  console.error('WebSocket error:', error);
};
```

## 🐎 Docker Deployment

### Using Docker Compose

The recommended deployment method:

```yaml
# docker-compose.yml
version: '3.8'
services:
  ai-prototyping-tool:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LM_STUDIO_URL=http://host.docker.internal:1234/v1
      - DEBUG=false
    volumes:
      - ./output:/app/output
    restart: unless-stopped
```

```bash
# Deploy
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Custom Docker Build

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "app.py"]
```

## 📊 Advanced Features

### Batch Processing

The web interface supports batch processing through the API:

```javascript
async function batchGenerate(prompts) {
  const results = [];

  for (const prompt of prompts) {
    try {
      const response = await fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt.text,
          deliverable_types: prompt.deliverables,
          max_tokens: 1500
        })
      });

      const result = await response.json();
      results.push({ prompt: prompt.name, result });

    } catch (error) {
      console.error(`Failed to generate for ${prompt.name}:`, error);
    }
  }

  return results;
}

// Usage
const prompts = [
  { name: 'Project A', text: 'E-commerce platform', deliverables: ['problem_statement'] },
  { name: 'Project B', text: 'Social media app', deliverables: ['personas', 'use_cases'] }
];

batchGenerate(prompts).then(results => {
  console.log('Batch generation complete:', results);
});
```

### Custom Templates

Modify the web interface templates:

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{{ title }}</h1>
            <div class="status-indicator" id="status">{{ status }}</div>
        </header>

        <main>
            <form id="generation-form">
                <!-- Form content -->
            </form>

            <div id="results" class="hidden">
                <!-- Results content -->
            </div>
        </main>
    </div>

    <script src="/static/app.js"></script>
</body>
</html>
```

### Analytics and Monitoring

Add usage analytics:

```javascript
// static/analytics.js
class Analytics {
    track(event, data) {
        fetch('/analytics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event, data, timestamp: Date.now() })
        });
    }
}

const analytics = new Analytics();

// Track events
analytics.track('generation_started', { deliverables: selectedTypes });
analytics.track('generation_completed', { duration: elapsed, tokens: tokensUsed });
```

## 🔒 Security Considerations

### Input Validation

- **Prompt Length**: Limited to prevent abuse
- **Parameter Ranges**: Enforced min/max values
- **File Upload**: Sanitized file names and content
- **XSS Protection**: Input sanitization and output escaping

### Rate Limiting

```python
# app.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/generate")
@limiter.limit("10/minute")
async def generate_endpoint(request: Request, ...):
    # Generation logic
    pass
```

### HTTPS Configuration

```bash
# For production deployment
uvicorn app:app \
  --host 0.0.0.0 \
  --port 443 \
  --ssl-keyfile /path/to/private.key \
  --ssl-certfile /path/to/certificate.crt
```

## 🔧 Troubleshooting

### Common Issues

**Issue**: Web interface won't start
```bash
# Check port availability
lsof -i :8000

# Try different port
cd web
uvicorn app:app --port 8080
```

**Issue**: WebSocket connection fails
```javascript
// Check WebSocket URL
const wsUrl = window.location.protocol === 'https:'
  ? 'wss://localhost:8000/ws'
  : 'ws://localhost:8000/ws';
```

**Issue**: Generation takes too long
- Reduce max_tokens parameter
- Check LM Studio model performance
- Monitor server resources

### Debug Mode

```bash
# Enable debug mode
export DEBUG=true
cd web
python app.py
```

### Logging

```python
# Enable detailed logging
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 📚 Browser Compatibility

### Supported Browsers

| Browser | Version | WebSocket | Markdown | File Download |
|---------|---------|-----------|----------|--------------|
| Chrome | 70+ | ✅ | ✅ | ✅ |
| Firefox | 65+ | ✅ | ✅ | ✅ |
| Safari | 12+ | ✅ | ✅ | ✅ |
| Edge | 79+ | ✅ | ✅ | ✅ |

### Progressive Enhancement

The interface degrades gracefully for older browsers:
- WebSocket fallback to polling
- Basic markdown rendering
- Standard file download

---

*For API details, see the [API Reference](api-reference.md). For deployment guidance, see [Deployment](deployment.md).*
