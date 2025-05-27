import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import pandas as pd
import os
import json
from utils import send_request_to_api


def calculate_and_save_embeddings(jobs_file, output_file):
    """
    Generate embeddings for job descriptions, required skills, and titles using a pre-trained SentenceTransformer model,
    then save the embeddings to a specified file.

    Parameters:
    - jobs_file (str): Path to the Excel file containing job information.
    - output_file (str): Path to save the calculated embeddings.

    Returns:
    - None
    """
    model = SentenceTransformer(os.getenv("MODEL_EMBEDDINGS"))
    column_names = os.getenv("COLUMNS_EXCEL_EMBEDDINGS")
    column_names = json.loads(column_names)
    try:
        jobs_df = pd.read_excel(jobs_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"The jobs file {jobs_file} was not found.")
    except Exception as e:
        raise RuntimeError(f"Error reading jobs file: {str(e)}") from e
    missing_columns = [col for col in column_names if col not in jobs_df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in the dataset for COLUMNS_EXCEL_EMBEDDINGS: {missing_columns}")
    texts = jobs_df[column_names].agg(" ".join, axis=1).tolist()
    embeddings = model.encode(texts)
    np.save(output_file, embeddings)



def load_embeddings(output_file):
    """
    A function that loads embeddings from a specified file.

    Parameters:
    output_file (str): The path to the file containing the embeddings.

    Returns:
    numpy array: The loaded embeddings.
    """
    embeddings = np.load(output_file)
    return embeddings


def generate_opinion_details(cv_text, best_job):
    """
    Generate an opinion based on the CV and best job using GEMINI 1.5 Flash.

    Parameters:
    - cv_text (str): The text of the CV.
    - best_job (str): The text of the matched job.

    Returns:
    - str: The opinion on the job based on the CV.
    """
    prompt = (f"Based on the following CV text and the match job role: {cv_text} {best_job}. "
              f"Is this person good for this job? What is the similarity (always in percentage)? "
              f"Only a few lines (not a lot of phrases).")
    try:
        response = send_request_to_api(prompt)
        if "Error:" in response:
            return f"API Error: {response}"
        return response
    except Exception as e:
        raise RuntimeError(f"Error in generate_opinion_details: {str(e)}") from e


def predict_job(cv_text):
    """
    Extract the predicted job based on a CV text using an external API.

    Parameters:
    - cv_text (str): The text of the CV.

    Returns:
    - str: The predicted job or an error message.
    """
    prompt = (f"Based on the following CV text, predict the most suitable job "
              f"(describe it with a list of words, like skills and job title)"
              f"(not a complete sentence): {cv_text}")
    try:
        response = send_request_to_api(prompt)
        if "Error:" in response:
            return f"API Error: {response}"
        return response
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e


def check_predicted_job_similarity(cv_text, jobs_file, embeddings):
    """
    Check the similarity between the predicted job and job embeddings from a file.

    Parameters:
    - predicted_job (str): The predicted job title or description.
    - jobs_file (str): Path to the Excel file containing job offers.
    - embeddings (list): Precomputed embeddings for the job offers.

    Returns:
    - str: The most similar job's details and similarity score.
    """
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    model = SentenceTransformer(os.getenv("MODEL_EMBEDDINGS"))
    try:
        jobs_df = pd.read_excel(jobs_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"The jobs file {jobs_file} was not found.")
    except Exception as e:
        raise RuntimeError(f"Error reading jobs file: {str(e)}") from e
    predicted_job = predict_job(cv_text)
    predicted_job_embedding = model.encode([predicted_job])
    jobs_df["Similarity"] = cosine_similarity(predicted_job_embedding, embeddings)[0]
    best_match = jobs_df.sort_values(by="Similarity", ascending=False).iloc[0]
    # similarity_score = best_match["Similarity"] * 100

    column_names = os.getenv("COLUMNS_EXCEL_BEST_JOB")
    column_names = json.loads(column_names)
    missing_columns = [col for col in column_names if col not in jobs_df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in the dataset for COLUMNS_EXCEL_BEST_JOB: {missing_columns}")
    best_job_details = "\n".join(
        [f"{col}: {best_match[col]}" for col in column_names]
    )

    column_names = os.getenv("COLUMNS_EXCEL_GENERATE_OPINION")
    column_names = json.loads(column_names)
    missing_columns = [col for col in column_names if col not in jobs_df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in the dataset for COLUMNS_EXCEL_GENERATE_OPINION: {missing_columns}")
    best_match_details = "\n".join(
        [f"{col}: {best_match[col]}" for col in column_names]
    )

    additional_details = generate_opinion_details(cv_text, best_match_details)

    best_job_details += f"\n\nOpinion on matched job:\n{additional_details}"
    return best_job_details
