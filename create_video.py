import sys
import subprocess
import shutil
import re
import unicodedata
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent

APP_DIR = ROOT_DIR / "app"

WORK_PROJECT = ROOT_DIR / "projects" / "esp32"

PROJECTS_DIR = ROOT_DIR / "projects"



PIPELINE = [
    (
        "🧠 Génération du script",
        APP_DIR / "script_generator.py"
    ),
    (
        "🎙️ Génération des voix",
        APP_DIR / "voicebox_client.py"
    ),
    (
        "📝 Génération des sous-titres",
        APP_DIR / "subtitle_generator.py"
    ),
    (
        "🖼️ Génération des visuels",
        APP_DIR / "visual_generator.py"
    ),
    (
        "🎬 Construction de la vidéo",
        APP_DIR / "video_builder.py"
    ),
]


# ============================================================
# SLUG
# ============================================================

def slugify(text):

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = text.encode(
        "ascii",
        "ignore"
    ).decode(
        "ascii"
    )

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9]+",
        "_",
        text
    )

    text = text.strip("_")

    return text[:80]


# ============================================================
# NETTOYAGE
# ============================================================

def clean_workspace():

    if not WORK_PROJECT.exists():
        return

    print()
    print("🧹 Nettoyage du projet précédent...")

    shutil.rmtree(
        WORK_PROJECT
    )

    print("✅ Workspace nettoyé.")


# ============================================================
# EXECUTION D'UNE ETAPE
# ============================================================

def run_step(
    title,
    script,
    args=None
):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

    command = [
        sys.executable,
        "-u",
        str(script)
    ]

    if args:
        command.extend(args)

    result = subprocess.run(
        command,
        cwd=ROOT_DIR
    )

    if result.returncode != 0:

        print()
        print(
            f"❌ ÉCHEC : {title}"
        )

        print(
            f"Code retour : {result.returncode}"
        )

        raise RuntimeError(
            f"L'étape a échoué : {title}"
        )

    print()
    print(
        f"✅ Étape terminée : {title}"
    )


# ============================================================
# DETERMINER LE NOM FINAL
# ============================================================

def get_final_project_path(topic):

    base_name = slugify(topic)

    if not base_name:
        base_name = "video"

    candidate = (
        PROJECTS_DIR /
        base_name
    )

    counter = 2

    while candidate.exists():

        candidate = (
            PROJECTS_DIR /
            f"{base_name}_{counter}"
        )

        counter += 1

    return candidate


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Sujet obligatoire
    # --------------------------------------------------------

    if len(sys.argv) < 2:

        print()
        print(
            "❌ Vous devez fournir un sujet."
        )

        print()
        print(
            "Exemple :"
        )

        print(
            'python create_video.py '
            '"Comment fonctionne un ESP32 ?"'
        )

        sys.exit(1)

    topic = " ".join(
        sys.argv[1:]
    )

    print()
    print("=" * 70)
    print("             AI CONTENT FACTORY")
    print("=" * 70)

    print()
    print(
        f"🎯 Sujet : {topic}"
    )

    print()
    print(
        "🚀 Démarrage du pipeline..."
    )

    try:

        # ----------------------------------------------------
        # Nettoyage
        # ----------------------------------------------------

        clean_workspace()

        # ----------------------------------------------------
        # ETAPE 1
        # ----------------------------------------------------

        run_step(
            "🧠 ÉTAPE 1 — SCRIPT + STORYBOARD",
            PIPELINE[0][1],
            [topic]
        )

        # ----------------------------------------------------
        # ETAPE 2
        # ----------------------------------------------------

        run_step(
            "🎙️ ÉTAPE 2 — VOIX TTS",
            PIPELINE[1][1]
        )

        # ----------------------------------------------------
        # ETAPE 3
        # ----------------------------------------------------

        run_step(
            "📝 ÉTAPE 3 — SOUS-TITRES",
            PIPELINE[2][1]
        )

        # ----------------------------------------------------
        # ETAPE 4
        # ----------------------------------------------------

        run_step(
            "🖼️ ÉTAPE 4 — VISUELS",
            PIPELINE[3][1]
        )

        # ----------------------------------------------------
        # ETAPE 5
        # ----------------------------------------------------

        run_step(
            "🎬 ÉTAPE 5 — VIDÉO",
            PIPELINE[4][1]
        )

        # ----------------------------------------------------
        # Vérification vidéo
        # ----------------------------------------------------

        final_video = (
            WORK_PROJECT /
            "output" /
            "esp32_video.mp4"
        )

        if not final_video.exists():

            raise FileNotFoundError(
                f"Vidéo finale absente : {final_video}"
            )

        # ----------------------------------------------------
        # Déplacement vers un dossier propre
        # ----------------------------------------------------

        final_project = get_final_project_path(
            topic
        )

        print()
        print(
            "📦 Organisation du projet final..."
        )

        shutil.move(
            str(WORK_PROJECT),
            str(final_project)
        )

        final_video = (
            final_project /
            "output" /
            "esp32_video.mp4"
        )

        # ----------------------------------------------------
        # FIN
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("       ✅ PIPELINE TERMINÉ AVEC SUCCÈS")
        print("=" * 70)

        print()
        print(
            f"🎯 Sujet : {topic}"
        )

        print(
            f"📁 Projet : {final_project}"
        )

        print(
            f"🎬 Vidéo : {final_video}"
        )

        print()

    except Exception as error:

        print()
        print("=" * 70)
        print("                ❌ PIPELINE ARRÊTÉ")
        print("=" * 70)

        print()
        print(
            f"Erreur : {error}"
        )

        sys.exit(1)


if __name__ == "__main__":
    main()