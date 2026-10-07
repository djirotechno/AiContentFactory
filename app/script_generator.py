import requests
import json
from pathlib import Path
import time
import sys

# ============================================================
# CONFIGURATION
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:8b"


# ============================================================
# SCHEMA JSON DU STORYBOARD
# ============================================================

STORYBOARD_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string"
        },
        "duration": {
            "type": "integer"
        },
        "format": {
            "type": "string"
        },
        "language": {
            "type": "string"
        },
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer"
                    },
                    "duration": {
                        "type": "integer"
                    },
                    "voice": {
                        "type": "string"
                    },
                    "visual": {
                        "type": "string"
                    }
                },
                "required": [
                    "id",
                    "duration",
                    "voice",
                    "visual"
                ]
            }
        }
    },
    "required": [
        "title",
        "duration",
        "format",
        "language",
        "scenes"
    ]
}


# ============================================================
# GENERATION DU STORYBOARD
# ============================================================

def generate_script(topic, duration=30):

    prompt = f"""
Tu es un scénariste spécialisé dans la vulgarisation
scientifique, la robotique, l'IoT et les STEM.

Crée une vidéo courte destinée à YouTube Shorts,
TikTok ou Instagram Reels.

SUJET :
{topic}

DUREE :
{duration} secondes

PUBLIC :
Débutants, élèves et étudiants.

LANGUE :
Français.

Crée exactement 4 scènes.

Pour chaque scène :

- id = numéro de la scène
- duration = durée en secondes
- voice = texte parlé par la voix off
- visual = description du visuel à afficher

Le texte doit être simple, naturel et pédagogique.

IMPORTANT :
Respecte exactement la structure JSON demandée.
Ne supprime aucune propriété.
Ne rajoute aucune propriété.

Les identifiants des scènes doivent être :

1
2
3
4
"""

    print("🧠 Génération du storyboard avec Qwen3...")

    start = time.time()

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,

            # Désactivation du raisonnement pour accélérer
            "think": False,

            # JSON Schema imposé à Ollama
            "format": STORYBOARD_SCHEMA,

            "options": {
                "temperature": 0,
                "num_predict": 600
            }
        },
        timeout=300
    )

    response.raise_for_status()

    elapsed = time.time() - start

    print(
        f"✅ Génération terminée en {elapsed:.2f} secondes"
    )

    result = response.json()["response"]

    # Conversion JSON
    data = json.loads(result)

    return data


# ============================================================
# VALIDATION / NORMALISATION
# ============================================================

def validate_storyboard(data):

    required_top_level = [
        "title",
        "duration",
        "format",
        "language",
        "scenes"
    ]

    for field in required_top_level:

        if field not in data:

            raise ValueError(
                f"❌ Propriété manquante : {field}"
            )

    scenes = data["scenes"]

    if not isinstance(scenes, list):

        raise ValueError(
            "❌ 'scenes' doit être une liste"
        )

    if len(scenes) != 4:

        print(
            f"⚠️ {len(scenes)} scènes reçues "
            f"(4 attendues)"
        )

    # Sécurité : compléter les IDs si nécessaires
    for index, scene in enumerate(scenes, start=1):

        if "id" not in scene:

            print(
                f"⚠️ ID manquant pour la scène {index}"
            )

            scene["id"] = index

        if "duration" not in scene:

            scene["duration"] = 7

        if "voice" not in scene:

            scene["voice"] = ""

        if "visual" not in scene:

            scene["visual"] = ""

    return data


# ============================================================
# SAUVEGARDE DU PROJET
# ============================================================

def save_project(data):

    project_name = "esp32"

    project_dir = (
        Path("projects") /
        project_name
    )

    project_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # STORYBOARD JSON
    # --------------------------------------------------------

    storyboard_file = (
        project_dir /
        "storyboard.json"
    )

    with open(
        storyboard_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

    # --------------------------------------------------------
    # SCRIPT TEXTE
    # --------------------------------------------------------

    script_file = (
        project_dir /
        "script.txt"
    )

    with open(
        script_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            data["title"] + "\n"
        )

        f.write(
            "=" * len(data["title"])
            + "\n\n"
        )

        for scene in data["scenes"]:

            scene_id = scene.get(
                "id",
                0
            )

            duration = scene.get(
                "duration",
                0
            )

            voice = scene.get(
                "voice",
                ""
            )

            visual = scene.get(
                "visual",
                ""
            )

            f.write(
                f"SCÈNE {scene_id} "
                f"({duration} secondes)\n"
            )

            f.write(
                f"VOIX : {voice}\n"
            )

            f.write(
                f"VISUEL : {visual}\n\n"
            )

    return project_dir


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================


if __name__ == "__main__":

    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "Comment fonctionne un ESP32 ?"

    print()
    print("=" * 50)
    print("       AI CONTENT FACTORY")
    print("=" * 50)
    print()

    print(f"🎯 Sujet : {topic}")
    print()

    try:

        data = generate_script(topic)

        data = validate_storyboard(data)

        project_dir = save_project(data)

        print()
        print("✅ PROJET CRÉÉ AVEC SUCCÈS")
        print(f"📁 {project_dir}")
        print()

        print("🎬 SCÈNES :")

        for scene in data["scenes"]:
            print(
                f"   Scene {scene['id']} "
                f"→ {scene['duration']} s"
            )

    except requests.exceptions.Timeout:

        print(
            "❌ Ollama a dépassé le délai d'attente."
        )

        sys.exit(1)

    except json.JSONDecodeError:

        print(
            "❌ Ollama a retourné un JSON invalide."
        )

        sys.exit(1)

    except Exception as error:

        print(
            f"❌ Erreur : {error}"
        )

        sys.exit(1)