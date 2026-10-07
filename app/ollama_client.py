
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:8b"


def generate_text(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    return response.json()["response"]


if __name__ == "__main__":

    prompt = """
    Explique simplement ce qu'est un ESP32
    pour un élève de collège en 5 phrases.
    """

    result = generate_text(prompt)

    print(result)