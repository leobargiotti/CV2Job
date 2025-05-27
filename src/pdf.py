import PyPDF2
from utils import send_request_to_api


def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.

    Parameters:
    pdf_path (str): The path to the PDF file.

    Returns:
    str: The extracted text from the PDF.
    """
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
    return text


def summarize_text(text):
    """
    Summarizes text using Gemini 1.5-Flash.

    Parameters:
    text (str): The text to summarize.

    Returns:
    str: The summarized text.
    """
    return send_request_to_api(f"Please summarize the following text: {text}")
