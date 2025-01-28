import asyncio
import json
import logging
import warnings
from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from fastapi_plugins import RedisSettings, RedisPlugin, depends_redis
from core1 import make_prompt
from models1 import OllamaChat
from fastapi import FastAPI, UploadFile, File, Form, Depends
from agents1 import PdfReader
from fastapi.responses import StreamingResponse


# Suppress warnings and set logging level
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Initialize Redis plugin
redis_plugin = RedisPlugin()


# App startup and shutdown events
@app.on_event("startup")
async def on_startup() -> None:
    await redis_plugin.init_app(app, config=RedisSettings(redis_host="redis"))
    await redis_plugin.init()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await redis_plugin.terminate()


# FastAPI endpoint to handle chat workflow
@app.post("/chat")
async def chat_endpoint(
    user_input: str = Form(...),
    uploaded_file: UploadFile = File(None),
    redis=Depends(depends_redis),  # Dependency injection for Redis
):
    llm = OllamaChat(model="llama3.1:8b", base_url="http://ollama:11434")
    pdf_agent = PdfReader(llm, temperature=0.2)

    # Generate a unique user ID (in practice, replace this with actual user authentication)
    user_id = "89"  # Replace with a real user ID mechanism

    # Retrieve existing chat history from Redis
    chat_history_key = f"chat_history:{user_id}"
    chat_history_json = await redis.get(chat_history_key)
    chat_history = json.loads(chat_history_json) if chat_history_json else []

    pdf_file_path = None
    file_content = b""  # Initialize as empty bytes

    # Only process the file if it is uploaded
    if uploaded_file:
        file_content = await uploaded_file.read()

    if len(file_content) > 0:
        try:
            pdf_file_path = uploaded_file.filename
            with open(pdf_file_path, "wb") as f:
                f.write(file_content)

            # Only save the document if save_to_memory is True
        except Exception as e:
            logging.error(f"Error handling file: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to process the uploaded file"},
            )

    chat_history.append(make_prompt("user", user_input))

    resp_generator = None
    try:
        if pdf_file_path:
            resp_generator = pdf_agent.ask(
                user_input, [pdf_file_path], history=chat_history
            )

    except Exception as e:
        logging.error(f"Error during chat processing: {e}")
        return JSONResponse(
            status_code=500, content={"error": "Failed to process the chat"}
        )

    # Streaming response function
    async def event_stream():
        response_text = ""
        nonlocal chat_history
        try:
            if resp_generator:
                # Stream each chunk individually
                for chunk in resp_generator:
                    if chunk:
                        if response_text[-len(chunk) :] != chunk:
                            response_text += chunk
                            yield chunk  # Stream each chunk immediately
                            await asyncio.sleep(
                                0.02
                            )  # Optional: simulate typing effect
                    else:
                        # If the chunk is empty, just yield the current response
                        yield f"data: {response_text}\n"
                chat_history.append(make_prompt("assistant", response_text))

            else:
                yield f"data: Error: No response generated\n\n"

            chat_history = chat_history[-10:]  # Keep last 5 messages
            await redis.set(chat_history_key, json.dumps(chat_history), ex=864000)

        except Exception as e:
            yield f"data: Error occurred in the response generation: {str(e)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
