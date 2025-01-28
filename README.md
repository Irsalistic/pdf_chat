# AI Chat Application with Ollama and FastAPI

A full-stack chat application that combines Ollama's language models with FastAPI for advanced features like PDF processing and chat history persistence. The application includes both a direct chat interface via Ollama WebUI and a custom API interface with additional capabilities.

## Features

- 🤖 Ollama language model integration
- 📄 PDF document processing and analysis
- 💾 Chat history persistence with Redis
- ⚡ Real-time streaming responses
- 🌐 Web interface via Ollama WebUI
- 🔄 Custom FastAPI endpoints for advanced features
- 🎮 NVIDIA GPU support for faster inference

## Prerequisites

- Docker and Docker Compose
- NVIDIA GPU (optional but recommended)
- NVIDIA Container Toolkit (if using GPU)

## System Requirements

- Minimum 16GB RAM
- 50GB disk space
- CPU with AVX512 support (recommended)
- NVIDIA GPU (optional)

## Project Structure

```
.
├── app.py              # FastAPI application
├── Dockerfile          # FastAPI service Dockerfile
├── docker-compose.yml  # Main compose file
├── requirements.txt    # Python dependencies
└── ollama/            # Ollama related files
    ├── Dockerfile     # Ollama service Dockerfile
    └── ollama-webui/  # WebUI data directory
```

## Installation & Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Create a `requirements.txt` file with necessary dependencies:
```
fastapi
uvicorn
python-multipart
redis
fastapi-plugins
```

3. Configure environment variables (optional):
```bash
cp .env.example .env
```

4. Start the services:
```bash
docker-compose up --build
```

## Available Services

- FastAPI Chat Service: `http://localhost:8003`
- Ollama WebUI: `http://localhost:8081`
- Ollama API: `http://localhost:11434`
- Redis: `localhost:6379`

## Using the Chat Application

### Via Ollama WebUI

1. Access the WebUI at `http://localhost:8081`
2. Create an admin account on first login
3. Download required models through the admin panel
4. Start chatting!

### Via FastAPI Endpoint

The FastAPI service provides a POST endpoint at `/chat` that accepts:
- User input text
- Optional PDF file upload
- Maintains chat history in Redis

Example API usage:
```python
import requests

files = {
    'uploaded_file': ('document.pdf', open('document.pdf', 'rb')),
    'user_input': (None, 'Please analyze this document')
}

response = requests.post('http://localhost:8003/chat', files=files)
```

## Configuration

### Docker Compose Environment Variables

```yaml
REDIS_HOST: Redis server hostname
REDIS_PORT: Redis server port
OLLAMA_HOST: Ollama service hostname
OLLAMA_PORT: Ollama service port
WEBUI_AUTH: Enable/disable WebUI authentication
WEBUI_SECRET_KEY: Secret key for WebUI
```

### GPU Support

The application is configured to use NVIDIA GPUs if available. Make sure you have:
1. NVIDIA drivers installed
2. NVIDIA Container Toolkit installed
3. Docker configured to use NVIDIA runtime

## Troubleshooting

1. If Ollama fails to start:
   - Check GPU drivers and NVIDIA Container Toolkit installation
   - Verify port 11434 is not in use

2. If WebUI can't connect to Ollama:
   - Check if Ollama service is running
   - Verify network connectivity in Docker

3. If Redis connection fails:
   - Ensure Redis service is running
   - Check Redis connection parameters

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues and feature requests, please create an issue in the repository.