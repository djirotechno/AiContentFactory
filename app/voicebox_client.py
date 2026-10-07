import json
import time
from pathlib import Path

import requests


# ============================================================
# CONFIGURATION
# ============================================================

VOICEBOX_URL = "http://127.0.0.1:17493"

PROFILE_ID = "46c660d0-68b9-44ef-94bb-62a7ecf6308c"

MODEL_SIZE = "0.6B"

# IMPORTANT :
# Le schéma API de ta version de Voicebox accepte actuellement
# uniquement "en" ou "zh" pour le champ language.
# Nous commençons donc avec "en" pour rester compatible avec l'API.
LANGUAGE = "en"

STORYBOARD_FILE = Path("projects/esp32/storyboard.json")

AUDIO_DIR = Path("projects/esp32/audio")

POLL_INTERVAL = 3

MAX_WAIT_SECONDS = 1200  # 20 minutes par scène


# ============================================================
# CHARGER LE STORYBOARD
# ============================================================

def load_storyboard():

    if not STORYBOARD_FILE.exists():

        raise FileNotFoundError(
            f"Storyboard introuvable : {STORYBOARD_FILE}"
        )

    with open(
        STORYBOARD_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# GENERER UNE SCENE
# ============================================================

def generate_scene(text, scene_id):

    payload = {
        "profile_id": PROFILE_ID,
        "text": text,
        "language": LANGUAGE,
        "model_size": MODEL_SIZE
    }

    print()
    print("=" * 60)
    print(f"🎙️ SCÈNE {scene_id}")
    print("=" * 60)
    print(f"Texte : {text}")
    print()

    response = requests.post(
        f"{VOICEBOX_URL}/generate",
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    generation = response.json()

    generation_id = generation["id"]

    print(f"🆔 Generation ID : {generation_id}")
    print(f"🧠 Modèle        : {generation.get('model_size')}")
    print(f"⚙️ Engine         : {generation.get('engine')}")
    print(f"📌 Status         : {generation.get('status')}")

    return generation_id


# ============================================================
# LIRE LE STATUS
# ============================================================

def get_generation_status(generation_id):

    try:
        response = requests.get(
            f"{VOICEBOX_URL}/generate/{generation_id}/status",
            timeout=30
        )

        response.raise_for_status()

        raw_text = response.text.strip()

        # ----------------------------------------------------
        # Voicebox peut retourner un flux SSE :
        #
        # data: {...}
        #
        # data: {...}
        #
        # On ne doit décoder qu'un événement à la fois.
        # ----------------------------------------------------

        data_lines = []

        for line in raw_text.splitlines():

            line = line.strip()

            if line.startswith("data:"):

                json_part = line[5:].strip()

                if json_part:
                    data_lines.append(json_part)

        # ----------------------------------------------------
        # Prendre le dernier événement reçu
        # ----------------------------------------------------

        if data_lines:

            latest_event = data_lines[-1]

            return json.loads(latest_event)

        # ----------------------------------------------------
        # Fallback : réponse JSON classique
        # ----------------------------------------------------

        return response.json()

    except requests.RequestException as error:

        print(
            f"⚠️ Erreur communication Voicebox : {error}"
        )

        return None

    except json.JSONDecodeError as error:

        print(
            f"⚠️ JSON Voicebox invalide : {error}"
        )

        print(
            "Réponse reçue :"
        )

        print(
            response.text
        )

        return None
# ============================================================
# ATTENDRE LA FIN DE GENERATION
# ============================================================

def wait_for_generation(generation_id):

    print("⏳ Attente de la génération...")

    start = time.time()

    last_status = None

    while True:

        elapsed = time.time() - start

        if elapsed > MAX_WAIT_SECONDS:

            raise TimeoutError(
                f"La génération {generation_id} "
                f"a dépassé {MAX_WAIT_SECONDS} secondes."
            )

        status_data = get_generation_status(
            generation_id
        )

        if status_data:

            status = status_data.get(
                "status"
            )

            if status != last_status:

                print(
                    f"   Status : {status}"
                )

                last_status = status

            if status == "completed":

                duration = status_data.get(
                    "duration"
                )

                print(
                    f"✅ Génération terminée "
                    f"({duration} s)"
                )

                return status_data

            if status in (
                "failed",
                "error",
                "cancelled"
            ):

                error = status_data.get(
                    "error"
                )

                raise RuntimeError(
                    f"Génération échouée : {error}"
                )

        else:

            print(
                "   En attente de Voicebox..."
            )

        time.sleep(
            POLL_INTERVAL
        )


# ============================================================
# TELECHARGER LE WAV
# ============================================================

def download_audio(
    generation_id,
    scene_id
):

    AUDIO_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        AUDIO_DIR /
        f"scene_{scene_id:02d}.wav"
    )

    print(
        f"⬇️ Téléchargement : {output_file}"
    )

    response = requests.get(
        f"{VOICEBOX_URL}/audio/{generation_id}",
        timeout=300
    )

    response.raise_for_status()

    output_file.write_bytes(
        response.content
    )

    file_size = output_file.stat().st_size

    print(
        f"✅ Audio sauvegardé : "
        f"{output_file}"
    )

    print(
        f"📦 Taille : {file_size:,} octets"
    )

    return output_file


# ============================================================
# SAUVEGARDE DU MANIFEST
# ============================================================

def save_manifest(results):

    manifest_file = (
        AUDIO_DIR /
        "manifest.json"
    )

    with open(
        manifest_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=4
        )

    print()
    print(
        f"📄 Manifest : {manifest_file}"
    )


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

def main():

    print()
    print("=" * 60)
    print("        AI CONTENT FACTORY")
    print("        VOICEBOX TTS PIPELINE")
    print("=" * 60)

    # --------------------------------------------------------
    # STORYBOARD
    # --------------------------------------------------------

    storyboard = load_storyboard()

    scenes = storyboard.get(
        "scenes",
        []
    )

    if not scenes:

        raise ValueError(
            "Aucune scène trouvée dans storyboard.json"
        )

    print()
    print(
        f"🎬 Vidéo : {storyboard.get('title')}"
    )

    print(
        f"📌 Nombre de scènes : {len(scenes)}"
    )

    print(
        f"🧠 Modèle TTS : Qwen {MODEL_SIZE}"
    )

    print(
        f"🎤 Profil : {PROFILE_ID}"
    )

    print(
        f"🌍 Language API : {LANGUAGE}"
    )

    results = []

    # --------------------------------------------------------
    # TRAITEMENT SCENE PAR SCENE
    # --------------------------------------------------------

    for scene in scenes:

        scene_id = scene.get(
            "id"
        )

        voice_text = scene.get(
            "voice",
            ""
        ).strip()

        if not voice_text:

            print(
                f"⚠️ Scène {scene_id} "
                f"ignorée : texte vide."
            )

            continue

        output_file = (
            AUDIO_DIR /
            f"scene_{scene_id:02d}.wav"
        )

        # ----------------------------------------------------
        # Eviter de régénérer un fichier existant
        # ----------------------------------------------------

        if output_file.exists():

            print()
            print(
                f"⏭️ Scène {scene_id} "
                f"déjà générée."
            )

            results.append({
                "scene_id": scene_id,
                "status": "already_exists",
                "file": str(output_file)
            })

            continue

        # ----------------------------------------------------
        # GENERATION
        # ----------------------------------------------------

        generation_id = generate_scene(
            voice_text,
            scene_id
        )

        # ----------------------------------------------------
        # ATTENTE
        # ----------------------------------------------------

        status = wait_for_generation(
            generation_id
        )

        # ----------------------------------------------------
        # TELECHARGEMENT
        # ----------------------------------------------------

        audio_file = download_audio(
            generation_id,
            scene_id
        )

        results.append({
            "scene_id": scene_id,
            "generation_id": generation_id,
            "status": "completed",
            "duration": status.get(
                "duration"
            ),
            "file": str(audio_file)
        })

    # --------------------------------------------------------
    # MANIFEST
    # --------------------------------------------------------

    save_manifest(results)

    print()
    print("=" * 60)
    print("✅ PIPELINE VOICEBOX TERMINÉ")
    print("=" * 60)

    print()
    print("📁 Fichiers audio :")

    for result in results:

        print(
            f"   {result.get('file')}"
        )


if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print()
        print(
            "🛑 Arrêt demandé par l'utilisateur."
        )

    except Exception as error:

        print()
        print(
            f"❌ ERREUR : {error}"
        )