import requests
import json
import os
import time


def send_request_to_api(prompt, max_retries=10):
    """
    Send a request to the Gemini API with a given prompt, retrying if the request fails due to a 429 error.

    Parameters:
    - prompt (str): The specific prompt to include in the request.
    - max_retries (int): Maximum number of retries for the request.

    Returns:
    - str: The response text or an error message.
    """
    url = os.getenv("GOOGLE_MODEL")
    api_key = os.getenv("API_KEY")

    model_config = {
        "temperature": 0,
    }

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "generation_config": model_config,
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    retries = 0
    while retries <= max_retries:
        try:
            response = requests.post(f"{url}?key={api_key}", headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                result = response.json()
                try:
                    return result['candidates'][0]['content']['parts'][0]['text'].replace("*", "")
                except (KeyError, IndexError):
                    raise Exception("Error: Unexpected response structure.")
            elif response.status_code == 429:
                retries += 1
                time.sleep(1)
            else:
                raise Exception(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            raise Exception(e)
    raise Exception("Error: Maximum retries exceeded. Could not complete the request.")
