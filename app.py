import json
import logging
import os
import tempfile
import warnings

from fastapi import Depends, FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi_plugins import RedisPlugin, RedisSettings, depends_redis

from agents1 import PdfReader
from core1 import make_prompt
from models1 import OllamaChat

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
logging.basicConfig(level=logging.INFO)

app = FastAPI()
redis_plugin = RedisPlugin()


@app.on_event("startup")
async def on_startup() -> None:
    redis_host = os.getenv("REDIS_HOST", "redis")
    await redis_plugin.init_app(app, config=RedisSettings(redis_host=redis_host))
    await redis_plugin.init()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await redis_plugin.terminate()


@app.post("/chat")
async def chat_endpoint(
    user_input: str = Form(...),
    uploaded_file: UploadFile = File(None),
    user_id: str = Form("local"),
    redis=Depends(depends_redis),
):
    ollama_host = os.getenv("OLLAMA_HOST", "ollama")
    ollama_port = os.getenv("OLLAMA_PORT", "11434")
    llm = OllamaChat(model="llama3.1:8b", host=f"http://{ollama_host}:{ollama_port}")
    pdf_agent = PdfReader(llm, temperature=0.2)

    chat_history_key = f"chat_history:{user_id}"
    chat_history_json = await redis.get(chat_history_key)
    chat_history = json.loads(chat_history_json) if chat_history_json else []

    pdf_file_path = None
    try:
        if uploaded_file is not None:
            file_content = await uploaded_file.read()
            if file_content:
                suffix = os.path.splitext(uploaded_file.filename or "upload.pdf")[1] or ".pdf"
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                    tmp.write(file_content)
                    pdf_file_path = tmp.name

        chat_history.append(make_prompt("user", user_input))
        pdfs = [pdf_file_path] if pdf_file_path else []
        answer = pdf_agent.ask(user_input, pdfs, history=chat_history)
        if not answer:
            return JSONResponse(status_code=502, content={"error": "The model returned no response"})

        async def event_stream():
            yield answer
            chat_history.append(make_prompt("assistant", answer))
            await redis.set(chat_history_key, json.dumps(chat_history[-10:]), ex=864000)

        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except Exception as exc:
        logging.error("Error during chat processing: %s", exc)
        return JSONResponse(status_code=500, content={"error": "Failed to process the chat"})
    finally:
        if pdf_file_path and os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
