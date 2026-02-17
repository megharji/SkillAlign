import os
import requests

HF_TOKEN_HR = os.getenv("HF_TOKEN_HR")

API_URL = os.getenv("HF_URL_HR")

headers = {
    "Authorization": f"Bearer {HF_TOKEN_HR}",
    "Content-Type": "application/json",
}

def get_similarity(source_sentence: str, sentences: list[str]) -> list[float]:
    payload = {
        "inputs": {
            "source_sentence": source_sentence,
            "sentences": sentences
        }
    }

    r = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    if r.status_code != 200:
        raise Exception(f"HF API error: {r.text}")
    return r.json()  # list of floats
