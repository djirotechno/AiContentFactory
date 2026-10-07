import requests
import time

url = "http://localhost:11434/api/generate"

data = {
    "model": "qwen3:8b",
    "prompt": "Écris une phrase sur l'ESP32.",
    "stream": False,
    "think": False,
    "options": {
        "num_predict": 50
    }
}

print("Test Qwen3 sans thinking...")

start = time.time()

response = requests.post(
    url,
    json=data,
    timeout=180
)

elapsed = time.time() - start

response.raise_for_status()

print(f"Temps : {elapsed:.2f} secondes")
print("Réponse :")
print(response.json()["response"])