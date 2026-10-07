import subprocess
import json
from pathlib import Path
import wave
import shutil


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_DIR = Path("projects/esp32")

AUDIO_DIR = PROJECT_DIR / "audio"
IMAGE_DIR = PROJECT_DIR / "images"
SUBTITLE_DIR = PROJECT_DIR / "subtitles"

WORK_DIR = PROJECT_DIR / "video_work"
SCENE_DIR = WORK_DIR / "scenes"

OUTPUT_DIR = PROJECT_DIR / "output"

FINAL_VIDEO = OUTPUT_DIR / "esp32_video.mp4"

SUBTITLE_FILE = SUBTITLE_DIR / "subtitles.srt"


VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

FPS = 30


# ============================================================
# UTILITAIRES
# ============================================================

def run_command(command):

    print()
    print("▶", " ".join(str(x) for x in command))

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode != 0:

        print(result.stdout)

        raise RuntimeError(
            f"FFmpeg a échoué avec le code "
            f"{result.returncode}"
        )

    return result.stdout


def audio_duration(audio_file):

    with wave.open(
        str(audio_file),
        "rb"
    ) as wav:

        frames = wav.getnframes()
        rate = wav.getframerate()

        return frames / float(rate)


# ============================================================
# CREER UNE SCENE VIDEO
# ============================================================

def create_scene_video(
    scene_id
):

    image_file = (
        IMAGE_DIR /
        f"scene_{scene_id:02d}.png"
    )

    audio_file = (
        AUDIO_DIR /
        f"scene_{scene_id:02d}.wav"
    )

    output_file = (
        SCENE_DIR /
        f"scene_{scene_id:02d}.mp4"
    )

    if not image_file.exists():

        raise FileNotFoundError(
            f"Image absente : {image_file}"
        )

    if not audio_file.exists():

        raise FileNotFoundError(
            f"Audio absent : {audio_file}"
        )

    duration = audio_duration(
        audio_file
    )

    print()
    print(
        f"🎬 Scène {scene_id}"
    )

    print(
        f"   Image : {image_file}"
    )

    print(
        f"   Audio : {audio_file}"
    )

    print(
        f"   Durée : {duration:.2f} s"
    )

    command = [
        "ffmpeg",
        "-y",

        "-loop",
        "1",

        "-i",
        str(image_file),

        "-i",
        str(audio_file),

        "-t",
        f"{duration:.3f}",

        "-vf",
        (
            f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:"
            "force_original_aspect_ratio=decrease,"
            f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:"
            "(ow-iw)/2:(oh-ih)/2"
        ),

        "-r",
        str(FPS),

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "23",

        "-pix_fmt",
        "yuv420p",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-shortest",

        str(output_file)
    ]

    run_command(command)

    print(
        f"   ✅ {output_file}"
    )

    return output_file


# ============================================================
# CONCATENER LES SCENES
# ============================================================

def concatenate_scenes(
    scene_files
):

    concat_file = (
        WORK_DIR /
        "concat.txt"
    )

    with open(
        concat_file,
        "w",
        encoding="utf-8"
    ) as file:

        for scene_file in scene_files:

            absolute_path = scene_file.resolve()

            # Pour FFmpeg sous Windows
            path_string = (
                str(absolute_path)
                .replace("\\", "/")
                .replace("'", "'\\''")
            )

            file.write(
                f"file '{path_string}'\n"
            )

    intermediate = (
        WORK_DIR /
        "video_without_subtitles.mp4"
    )

    command = [
        "ffmpeg",
        "-y",

        "-f",
        "concat",

        "-safe",
        "0",

        "-i",
        str(concat_file),

        "-c",
        "copy",

        str(intermediate)
    ]

    run_command(command)

    print()
    print(
        f"✅ Vidéo assemblée : {intermediate}"
    )

    return intermediate


# ============================================================
# AJOUT DES SOUS-TITRES
# ============================================================

def add_subtitles(
    input_video
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not SUBTITLE_FILE.exists():

        print(
            "⚠️ subtitles.srt absent."
        )

        print(
            "La vidéo sera produite sans "
            "sous-titres intégrés."
        )

        shutil.copy2(
            input_video,
            FINAL_VIDEO
        )

        return FINAL_VIDEO

    # FFmpeg accepte un chemin relatif ici
    # puisque nous travaillons depuis le projet racine.

    subtitle_path = (
        str(SUBTITLE_FILE)
        .replace("\\", "/")
    )

    subtitle_filter = (
        f"subtitles='{subtitle_path}':"
        "force_style="
        "'FontName=Arial,"
        "FontSize=18,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "Outline=3,"
        "Shadow=1,"
        "Alignment=2,"
        "MarginV=120'"
    )

    command = [
        "ffmpeg",
        "-y",

        "-i",
        str(input_video),

        "-vf",
        subtitle_filter,

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "22",

        "-c:a",
        "copy",

        str(FINAL_VIDEO)
    ]

    run_command(command)

    return FINAL_VIDEO


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("        AI CONTENT FACTORY")
    print("        VIDEO BUILDER")
    print("=" * 60)

    WORK_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    SCENE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Lister les scènes
    # --------------------------------------------------------

    audio_files = sorted(
        AUDIO_DIR.glob("scene_*.wav")
    )

    if not audio_files:

        raise FileNotFoundError(
            "Aucun fichier WAV trouvé."
        )

    print()
    print(
        f"🎬 {len(audio_files)} scènes détectées."
    )

    # --------------------------------------------------------
    # Génération des scènes vidéo
    # --------------------------------------------------------

    scene_files = []

    for audio_file in audio_files:

        # scene_01.wav → 01

        scene_id = int(
            audio_file.stem.split("_")[1]
        )

        video_file = create_scene_video(
            scene_id
        )

        scene_files.append(
            video_file
        )

    # --------------------------------------------------------
    # Concaténation
    # --------------------------------------------------------

    intermediate = concatenate_scenes(
        scene_files
    )

    # --------------------------------------------------------
    # Sous-titres
    # --------------------------------------------------------

    final_video = add_subtitles(
        intermediate
    )

    print()
    print("=" * 60)
    print("✅ VIDÉO FINALE CRÉÉE")
    print("=" * 60)

    print()
    print(
        f"🎬 {final_video}"
    )


if __name__ == "__main__":

    main()