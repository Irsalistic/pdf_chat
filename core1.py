
import logging
import os
import warnings
import fitz
import yaml
from enum import Enum
from bs4 import BeautifulSoup
from pptx import Presentation  # For handling .pptx files
from docx import Document
import chardet  # to detect text file encoding
from striprtf.striprtf import rtf_to_text  # for RTF text extraction
import csv
import pandas as pd


class AgentType(Enum):
    """
    Enum for agent types
    See documentation for explanation of Agents
    """
    PLANNER = "Planner"
    SUMMARIZER = "Summarizer"
    GENERIC_RESPONDER = "GenericResponder"
    VALIDATOR = "Validator"


def llm_has_ask(llm):
    """
    Checks if the llm object has an ask function
    Args:
        llm (object): The object to check
    Returns:
        bool: True if the llm object has an ask function, False otherwise
    """
    if not hasattr(llm, "ask"):
        warnings.warn("llm object must have an ask function! See OllamaChat class in models.py for an example.")
        return False
    return True


def make_prompt(role: str, content: str, images: list = None):
    """
    Creates a prompt in OpenAI format
    Args:
        role (str): The role of the prompt
        content (str): The content of the prompt
        images (list, optional): A list of images to include in the prompt. Defaults to None.
    Returns:
        dict: The prompt in OpenAI format
    """
    args = {
        "role": role,
        "content": content
    }
    if images is not None:
        args["images"] = images

    return {**args}


def extract_text_from_pdf(file_path):
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
    except Exception as e:
        logging.error(f"Error reading PDF file: {e}")
    if not text.strip():
        logging.warning("Extracted text from PDF is empty.")
    return text


def extract_text_from_docx(docx_file_path):
    try:
        doc = Document(docx_file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        logging.error(f"Error extracting text from DOCX1: {e}")
        return ""


# Function to extract text from PPTX
def extract_text_from_pptx(pptx_file_path):
    try:
        presentation = Presentation(pptx_file_path)
        text = ""
        for slide in presentation.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PPTX: {e}")
        return ""


# TXT text extraction function
# TXT text extraction function
def extract_text_from_txt(txt_file_path):
    try:
        with open(txt_file_path, 'rb') as f:
            raw_data = f.read()
        encoding = chardet.detect(raw_data)['encoding']  # Detect file encoding
        with open(txt_file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error extracting text from TXT: {e}")
        return ""


# HTML text extraction function
def extract_text_from_html(html_file_path):
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        return soup.get_text(separator='\n')
    except Exception as e:
        logging.error(f"Error extracting text from HTML: {e}")
        return ""


# RTF text extraction function
def extract_text_from_rtf(rtf_file_path):
    try:
        with open(rtf_file_path, 'r', encoding='utf-8') as f:
            return rtf_to_text(f.read())
    except Exception as e:
        logging.error(f"Error extracting text from RTF: {e}")
        return ""


# CSV text extraction function
def extract_text_from_csv(csv_file_path):
    text = ""
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                text += " ".join(row) + "\n"
        return text
    except Exception as e:
        logging.error(f"Error extracting text from CSV: {e}")
        return ""


def extract_text_from_xlsx(xlsx_file_path):
    try:
        df = pd.read_excel(xlsx_file_path, sheet_name=None)
        text = ""
        for sheet_name, sheet_df in df.items():
            text += sheet_df.to_string(index=False) + "\n"
        return text
    except Exception as e:
        logging.error(f"Error extracting text from XLSX: {e}")
        return ""


# Function to extract text from XLS
def extract_text_from_xls(xls_file_path):
    try:
        df = pd.read_excel(xls_file_path, sheet_name=None, engine='xlrd')
        text = ""
        for sheet_name, sheet_df in df.items():
            text += sheet_df.to_string(index=False) + "\n"
        return text
    except Exception as e:
        logging.error(f"Error extracting text from XLS: {e}")
        return ""


# Function to determine file type
def get_file_extension(file_path):
    # Extract the file extension from the file path
    base, ext = os.path.splitext(file_path)
    if ext:
        return ext[1:].lower()  # Remove the dot and convert to lower case
    return None


def read_pdf(file_path):

    if isinstance(file_path, str) and not os.path.exists(file_path):

        return file_path
    else:
        if not os.path.exists(file_path):
            logging.error(f"File not found: ")
            return ""
        result = None
        file_extension = get_file_extension(file_path)

        if file_extension == 'pdf':
            result = extract_text_from_pdf(file_path)
        elif file_extension == 'docx':
            result = extract_text_from_docx(file_path)
        elif file_extension == 'pptx':
            result = extract_text_from_pptx(file_path)
        elif file_extension == 'txt':
            result = extract_text_from_txt(file_path)
        elif file_extension == 'html':
            result = extract_text_from_html(file_path)
        elif file_extension == 'csv':
            result = extract_text_from_csv(file_path)
        elif file_extension == 'xlsx':
            result = extract_text_from_xlsx(file_path)
        elif file_extension == 'xls':
            result = extract_text_from_xls(file_path)
        else:
            logging.error(f"Unsupported file format: {file_extension}")
            return ""


        return result


def get_yaml_prompt(yaml_file_name: str, prompt_name: str):
    """
    Reads a prompt from a yaml file.
    See system_prompts.yaml for a list of prompts.
    Args:
        yaml_file_name (str): The name of the yaml file to load.
        prompt_name (str): The name of the prompt to load.
    """
    dir_of_file = os.path.dirname(os.path.realpath(__file__))
    yaml_path = os.path.join(dir_of_file, yaml_file_name)
    file = open(yaml_path)
    loaded = yaml.safe_load(file)[prompt_name]["prompt"]
    file.close()
    return loaded





