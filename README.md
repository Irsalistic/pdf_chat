# PDF Chat

Self-hosted chat over PDFs using **Ollama**, **FastAPI**, and **Redis** for conversation history. Run it with Docker Compose.

## Features

- Talk to a local Ollama model
- Upload a PDF and ask questions about it
- Redis-backed chat history
- Streaming responses
- Optional NVIDIA GPU for faster inference

## Requirements

- Docker and Docker Compose
- About 16 GB RAM (models are large)
- NVIDIA GPU + Container Toolkit if you want GPU inference

## Setup

```bash
git clone https://github.com/Irsalistic/pdf_chat.git
cd pdf_chat
docker compose -f compose.yml up --build
```

This repo uses `compose.yml` (not `docker-compose.yml`). `requirements.txt` is already in the repo.

## Services

| Service | URL |
|---------|-----|
| FastAPI chat | http://localhost:8003 |
| Ollama WebUI | http://localhost:8081 |
| Ollama API | http://localhost:11434 |
| Redis | localhost:6379 |

On first WebUI visit, create an admin account and pull a model.

### FastAPI `/chat`

```python
import requests

files = {"uploaded_file": ("document.pdf", open("document.pdf", "rb"))}
data = {"user_input": "Summarize this document"}
response = requests.post("http://localhost:8003/chat", files=files, data=data)
```

## Layout

```
app.py                 # FastAPI app
agents1.py
core1.py
models1.py
utils1.py
system_prompts.yaml
compose.yml
Dockerfile
ollama/                # Ollama image + WebUI
llama2.pdf, oscar.pdf  # Sample PDFs
```

## Troubleshooting

- Ollama will not start: check GPU drivers / NVIDIA Container Toolkit, and that port 11434 is free.
- WebUI cannot reach Ollama: confirm the `ollama` service is up.
- Redis errors: confirm the `redis` service is up.
