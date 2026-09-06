import os

from core1 import get_yaml_prompt, read_pdf, \
    make_prompt


class PdfReader():
    """
    An Agent used to answer questions based on information from given PDF files.
    """

    def __init__(self, llm: object, additional_system_instructions: str = "", custom_system_prompt: str = None,
                 temperature: float = 0.6):
        """
        Initializes a new PdfReader.
        Args:
            llm (object): An object that implements the ask() method.
            additional_system_instructions (str, optional): Additional instructions to include in the system prompt.
            custom_system_prompt (str, optional): Custom system prompt. Defaults to None.
            temperature (float, optional): The temperature of the LLM. Defaults to 0.8.
        """
        self.chat_history = []
        self.llm = llm
        self.additional_instructions = additional_system_instructions
        self.system_prompt = get_yaml_prompt("system_prompts.yaml", "DocumentReader")
        self.custom_system_prompt = custom_system_prompt
        self.temperature = temperature

    def ask(self, question: str, pdf_files: list, history: list = None):
        """
        Ask a question based on the given PDF files.
        Args:
            question (str): The question to ask.
            pdf_files (list): A list of PDF files to read. Each file should be a string representing the path to the PDF file.
            history (list): A list of previous chat messages in openai format.
        """
        if self.llm is None:
            raise ValueError("No LLM object provided.")

        prompts = []
        question_prompts = self.get_prompt(question, pdf_files)
        prompts.append(question_prompts[0])

        if history is not None:
            prompts.extend(history)

        prompts.append(question_prompts[1])
        response = self.llm.ask(prompts, temperature=self.temperature)

        self.chat_history.append(question_prompts[1])  # dont include the system prompt
        self.chat_history.append(make_prompt("assistant", response))
        return response

    def get_prompt(self, question, pdf_files: list = None):
        """
        Generates the prompt for the LLM.
        args:
            question (str): The question to ask.
            pdf_files (list): A list of PDF files to read. Each file should be a string path to the PDF file.
        """
        pdf_text = ""
        for pdf_file in pdf_files or []:
            pdf_text += f"Contents of document {os.path.basename(pdf_file)} :\n"
            pdf_text += read_pdf(pdf_file) + "\n\n"
        if self.custom_system_prompt is None:
            self.system_prompt = get_yaml_prompt("system_prompts.yaml", "DocumentReader")
        else:
            self.system_prompt = self.custom_system_prompt

        self.system_prompt = make_prompt("system", self.system_prompt.format(documents=pdf_text, question=question,
                                                                             additional_instructions=self.additional_instructions))

        user_prompt = make_prompt("user", question)
        prompts = [self.system_prompt, user_prompt]

        return prompts
