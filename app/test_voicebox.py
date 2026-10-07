import requests
from pathlib import Path

VOICEBOX_URL = "http://127.0.0.1:17493"

text = """
Bonjour et bienvenue dans cette vidéo.
Aujourd'hui, nous allons découvrir comment fonctionne un ESP32.
"""

payload = {
    "text": text.strip(),
    "profile_id": "TON_PROFILE_ID"
}

print("🎙️ Génération de la voix...")

response = requests.post(
    f"{VOICEBOX_URL}/generate",
    json=payload,
    timeout=300
)

response.raise_for_status()

output = Path("output/test_voice.wav")

output.parent.mkdir(
    parents=True,
    exist_ok=True
)

output.write_bytes(response.content)

print("✅ Audio généré :")
print(output)