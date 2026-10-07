import json
from pathlib import Path

from faster_whisper import WhisperModel


# ============================================================
# CONFIGURATION
# ============================================================

AUDIO_DIR = Path("projects/esp32/audio")
OUTPUT_DIR = Path("projects/esp32/subtitles")

MODEL_SIZE = "small"

# Première version : CPU
DEVICE = "cpu"
COMPUTE_TYPE = "int8"


# ============================================================
# SRT FORMAT
# ============================================================

def format_timestamp(seconds: float) -> str:

    hours = int(seconds // 3600)

    minutes = int(
        (seconds % 3600) // 60
    )

    secs = int(
        seconds % 60
    )

    milliseconds = int(
        round((seconds - int(seconds)) * 1000)
    )

    if milliseconds >= 1000:

        milliseconds = 0
        secs += 1

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d},"
        f"{milliseconds:03d}"
    )


# ============================================================
# TRANSCRIPTION
# ============================================================

def transcribe_file(
    model,
    audio_file,
    offset_seconds=0.0
):

    print()
    print(
        f"🎙️ Transcription : {audio_file.name}"
    )

    segments, info = model.transcribe(
        str(audio_file),
        language="fr",
        beam_size=5,
        vad_filter=True,
        initial_prompt=(
        "ESP32, STEM, IoT, robotique, "
        "microcontrôleur, Wi-Fi, Bluetooth, "
        "capteurs, programmation, électronique."
    )
    )

    results = []

    for segment in segments:

        start = (
            segment.start +
            offset_seconds
        )

        end = (
            segment.end +
            offset_seconds
        )

        text = segment.text.strip()

        if not text:
            continue

        results.append({
            "start": start,
            "end": end,
            "text": text
        })

        print(
            f"  {start:.2f}s → "
            f"{end:.2f}s : {text}"
        )

    return results


# ============================================================
# CREATION DU SRT
# ============================================================

def create_srt(segments):

    lines = []

    for index, segment in enumerate(
        segments,
        start=1
    ):

        lines.append(
            str(index)
        )

        lines.append(
            f"{format_timestamp(segment['start'])}"
            " --> "
            f"{format_timestamp(segment['end'])}"
        )

        lines.append(
            segment["text"]
        )

        lines.append("")

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("       AI CONTENT FACTORY")
    print("       LOCAL SUBTITLE GENERATOR")
    print("=" * 60)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print()
    print(
        f"🧠 Modèle Whisper : {MODEL_SIZE}"
    )

    print(
        f"💻 Device : {DEVICE}"
    )

    print(
        f"⚙️ Compute type : {COMPUTE_TYPE}"
    )

    print()
    print("⏳ Chargement du modèle...")

    model = WhisperModel(
        MODEL_SIZE,
        device=DEVICE,
        compute_type=COMPUTE_TYPE
    )

    print("✅ Modèle chargé.")

    audio_files = sorted(
        AUDIO_DIR.glob("scene_*.wav")
    )

    if not audio_files:

        raise FileNotFoundError(
            "Aucun fichier scene_XX.wav trouvé."
        )

    all_segments = []

    offset = 0.0

    manifest = []

    # --------------------------------------------------------
    # TRANSCRIPTION SCENE PAR SCENE
    # --------------------------------------------------------

    for audio_file in audio_files:

        segments = transcribe_file(
            model,
            audio_file,
            offset
        )

        all_segments.extend(
            segments
        )

        # ----------------------------------------------------
        # Durée audio de la scène
        # ----------------------------------------------------

        import wave

        with wave.open(
            str(audio_file),
            "rb"
        ) as wav:

            frames = wav.getnframes()
            rate = wav.getframerate()

            duration = frames / float(rate)

        manifest.append({
            "file": str(audio_file),
            "offset": offset,
            "duration": duration
        })

        offset += duration

    # --------------------------------------------------------
    # SRT FINAL
    # --------------------------------------------------------

    srt_content = create_srt(
        all_segments
    )

    srt_file = (
        OUTPUT_DIR /
        "subtitles.srt"
    )

    srt_file.write_text(
        srt_content,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    json_file = (
        OUTPUT_DIR /
        "subtitles.json"
    )

    json_file.write_text(
        json.dumps(
            all_segments,
            ensure_ascii=False,
            indent=4
        ),
        encoding="utf-8"
    )

    print()
    print("=" * 60)
    print("✅ SOUS-TITRES GÉNÉRÉS")
    print("=" * 60)

    print()
    print(
        f"📄 SRT : {srt_file}"
    )

    print(
        f"📄 JSON : {json_file}"
    )

    print(
        f"🎬 Segments : {len(all_segments)}"
    )


if __name__ == "__main__":

    main()