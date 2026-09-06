

from ollama import Client


class OllamaChat:
    def __init__(self, host: str = "http://localhost:11434", model: str = "llama3.1:8b-instruct-q8_0"):
        if model is None:
            raise ValueError('You must provide a model to use OllamaChat. Example: OllamaChat(model="llama3:instruct")')

        self._host = host
        self._model = model
        self._ollama = Client(host=host)

    def ask(self, prompts: list, format: str = "text", temperature: float = 0.1):
        """
        Ask a question to the LLM (non-streaming mode).

        Args:
            prompts (list): A list of prompts to ask.
            format (str, optional): The format of the response. Use "json" for JSON. Defaults to "text".
            temperature (float, optional): The temperature of the LLM. Defaults to 0.8.

        Returns:
            str: The full response from the LLM.
        """
        try:
            response = self._ollama.chat(
                model=self._model, messages=prompts, format=format,
                options={"temperature": temperature, "top_k": 5, "top_p": 0.9}, stream=False
            )
            return response["message"]["content"]
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def ask_stream(self, prompts: list, format: str = "text", temperature: float = 0.1):
        """
        Ask a question to the LLM in streaming mode.

        Args:
            prompts (list): A list of prompts to ask.
            format (str, optional): The format of the response. Use "json" for JSON. Defaults to "text".
            temperature (float, optional): The temperature of the LLM. Defaults to 0.8.

        Yields:
            str: Chunks of the response as they arrive.
        """
        try:
            for response_chunk in self._ollama.chat(
                    model=self._model, messages=prompts, format=format, options={"temperature": temperature,"top_k": 5, "top_p": 0.9},
                    stream=True
            ):
                content = response_chunk.get("message", {}).get("content", "")
                if content:
                    yield content
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
