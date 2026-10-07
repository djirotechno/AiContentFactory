import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# CHEMINS ABSOLUS DU PROJET
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

PROJECT_DIR = ROOT_DIR / "projects" / "esp32"

STORYBOARD_FILE = PROJECT_DIR / "storyboard.json"

OUTPUT_DIR = PROJECT_DIR / "images"

WIDTH = 1080
HEIGHT = 1920


# ============================================================
# POLICES
# ============================================================

def load_font(size, bold=False):

    candidates = []

    if bold:
        candidates = [
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\calibrib.ttf",
        ]
    else:
        candidates = [
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\calibri.ttf",
        ]

    for path in candidates:

        if Path(path).exists():
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


TITLE_FONT = load_font(64, bold=True)
SCENE_FONT = load_font(38, bold=True)
BODY_FONT = load_font(34)
SMALL_FONT = load_font(26, bold=True)


# ============================================================
# UTILITAIRES TEXTE
# ============================================================

def wrap_text(draw, text, font, max_width):

    words = text.split()

    lines = []
    current = ""

    for word in words:

        candidate = (
            current + " " + word
        ).strip()

        bbox = draw.textbbox(
            (0, 0),
            candidate,
            font=font
        )

        if bbox[2] - bbox[0] <= max_width:

            current = candidate

        else:

            if current:
                lines.append(current)

            current = word

    if current:
        lines.append(current)

    return lines


def draw_wrapped(
    draw,
    text,
    x,
    y,
    max_width,
    font,
    fill=(240, 240, 240),
    spacing=12
):

    lines = wrap_text(
        draw,
        text,
        font,
        max_width
    )

    current_y = y

    for line in lines:

        draw.text(
            (x, current_y),
            line,
            font=font,
            fill=fill
        )

        bbox = draw.textbbox(
            (x, current_y),
            line,
            font=font
        )

        current_y += (
            bbox[3] -
            bbox[1] +
            spacing
        )

    return current_y


def rounded_box(
    draw,
    box,
    fill=(35, 45, 60),
    outline=(100, 130, 160),
    radius=25,
    width=3
):

    draw.rounded_rectangle(
        box,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width
    )


def center_text(
    draw,
    text,
    center_x,
    y,
    font,
    fill=(255, 255, 255)
):

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    width = bbox[2] - bbox[0]

    draw.text(
        (
            center_x - width / 2,
            y
        ),
        text,
        font=font,
        fill=fill
    )


# ============================================================
# VISUEL CAPTEUR ULTRASONIQUE
# ============================================================

def draw_ultrasonic(
    draw
):

    # Capteur HC-SR04
    x = 390
    y = 650

    rounded_box(
        draw,
        (x, y, x + 300, y + 190),
        fill=(35, 55, 75),
        outline=(100, 210, 240),
        radius=25,
        width=5
    )

    # Deux transducteurs
    draw.ellipse(
        (x + 45, y + 35, x + 125, y + 115),
        fill=(15, 25, 35),
        outline=(140, 180, 200),
        width=4
    )

    draw.ellipse(
        (x + 175, y + 35, x + 255, y + 115),
        fill=(15, 25, 35),
        outline=(140, 180, 200),
        width=4
    )

    center_text(
        draw,
        "ULTRASON",
        x + 150,
        y + 125,
        SMALL_FONT
    )

    # Ondes ultrasoniques
    for radius in [100, 160, 220]:

        draw.arc(
            (
                x + 150 - radius,
                y - radius + 80,
                x + 150 + radius,
                y + radius + 80
            ),
            200,
            340,
            fill=(100, 210, 255),
            width=6
        )

    # Objet mesuré
    object_x = 760

    draw.rectangle(
        (
            object_x,
            610,
            object_x + 80,
            880
        ),
        fill=(90, 100, 115)
    )

    draw.line(
        (
            x + 300,
            745,
            object_x,
            745
        ),
        fill=(120, 220, 255),
        width=6
    )

    center_text(
        draw,
        "DISTANCE",
        820,
        900,
        SMALL_FONT
    )


# ============================================================
# VISUEL ESP32
# ============================================================

def draw_esp32(
    draw
):

    x = 330
    y = 620

    rounded_box(
        draw,
        (x, y, x + 420, y + 280),
        fill=(30, 70, 85),
        outline=(100, 210, 230),
        radius=25,
        width=5
    )

    rounded_box(
        draw,
        (x + 120, y + 70, x + 300, y + 210),
        fill=(20, 28, 38),
        outline=(150, 170, 180),
        radius=12,
        width=3
    )

    center_text(
        draw,
        "ESP32",
        x + 210,
        y + 110,
        SCENE_FONT
    )

    # Antenne
    draw.arc(
        (x + 305, y + 30, x + 405, y + 130),
        210,
        330,
        fill=(120, 220, 255),
        width=5
    )

    draw.arc(
        (x + 320, y + 45, x + 390, y + 115),
        210,
        330,
        fill=(120, 220, 255),
        width=4
    )


# ============================================================
# VISUEL IOT
# ============================================================

def draw_iot(
    draw
):

    # Objet central
    rounded_box(
        draw,
        (390, 650, 690, 900),
        fill=(35, 60, 80),
        outline=(100, 210, 230),
        radius=30,
        width=5
    )

    center_text(
        draw,
        "IoT",
        540,
        720,
        TITLE_FONT
    )

    # Capteurs
    nodes = [
        ("CAPTEUR", 100, 500),
        ("MOBILE", 760, 500),
        ("CLOUD", 110, 1000),
        ("ACTION", 760, 1000)
    ]

    for label, x, y in nodes:

        rounded_box(
            draw,
            (x, y, x + 220, y + 100),
            fill=(40, 50, 65),
            outline=(90, 160, 190),
            radius=20,
            width=3
        )

        center_text(
            draw,
            label,
            x + 110,
            y + 33,
            SMALL_FONT
        )

        draw.line(
            (
                540,
                775,
                x + 110,
                y + 50
            ),
            fill=(100, 190, 220),
            width=4
        )


# ============================================================
# VISUEL ROBOTIQUE
# ============================================================

def draw_robotics(
    draw
):

    # Corps
    rounded_box(
        draw,
        (350, 700, 730, 990),
        fill=(45, 60, 80),
        outline=(100, 200, 220),
        radius=35,
        width=5
    )

    # Tête
    draw.ellipse(
        (430, 500, 650, 720),
        fill=(55, 75, 95),
        outline=(100, 200, 220),
        width=5
    )

    # Yeux
    draw.ellipse(
        (475, 575, 520, 620),
        fill=(100, 220, 255)
    )

    draw.ellipse(
        (560, 575, 605, 620),
        fill=(100, 220, 255)
    )

    center_text(
        draw,
        "ROBOTIQUE",
        540,
        815,
        SCENE_FONT
    )


# ============================================================
# VISUEL GENERIQUE
# ============================================================

def draw_generic(
    draw,
    visual_text
):

    rounded_box(
        draw,
        (110, 560, 970, 1030),
        fill=(30, 45, 65),
        outline=(100, 190, 220),
        radius=35,
        width=4
    )

    center_text(
        draw,
        "VISUEL STEM",
        540,
        630,
        SCENE_FONT,
        fill=(120, 220, 255)
    )

    draw_wrapped(
        draw,
        visual_text,
        170,
        760,
        740,
        BODY_FONT,
        fill=(235, 240, 245),
        spacing=18
    )


# ============================================================
# CHOIX DU VISUEL
# ============================================================

def draw_visual(
    draw,
    title,
    visual_text
):

    text = (
        title + " " +
        visual_text
    ).lower()

    if any(
        keyword in text
        for keyword in [
            "ultrason",
            "hc-sr04",
            "distance",
            "echo"
        ]
    ):

        draw_ultrasonic(draw)

    elif any(
        keyword in text
        for keyword in [
            "esp32",
            "microcontrôleur",
            "microcontroleur"
        ]
    ):

        draw_esp32(draw)

    elif any(
        keyword in text
        for keyword in [
            "iot",
            "internet",
            "wifi",
            "wi-fi",
            "bluetooth"
        ]
    ):

        draw_iot(draw)

    elif any(
        keyword in text
        for keyword in [
            "robot",
            "robotique"
        ]
    ):

        draw_robotics(draw)

    else:

        draw_generic(
            draw,
            visual_text
        )


# ============================================================
# CREER UNE IMAGE
# ============================================================

def create_scene(
    title,
    scene,
    index
):

    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        (12, 18, 28)
    )

    draw = ImageDraw.Draw(
        image
    )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    draw.rectangle(
        (0, 0, WIDTH, 220),
        fill=(18, 35, 52)
    )

    draw.text(
        (60, 40),
        "AI CONTENT FACTORY",
        font=SMALL_FONT,
        fill=(120, 220, 255)
    )

    draw_wrapped(
        draw,
        title,
        60,
        85,
        960,
        TITLE_FONT
    )

    # --------------------------------------------------------
    # SCENE
    # --------------------------------------------------------

    draw.text(
        (60, 260),
        f"SCÈNE {index}",
        font=SCENE_FONT,
        fill=(120, 220, 255)
    )

    # --------------------------------------------------------
    # VISUEL
    # --------------------------------------------------------

    visual_text = scene.get(
        "visual",
        ""
    )

    draw_visual(
        draw,
        title,
        visual_text
    )

    # --------------------------------------------------------
    # DESCRIPTION VISUELLE
    # --------------------------------------------------------

    rounded_box(
        draw,
        (60, 1120, WIDTH - 60, 1450),
        fill=(25, 34, 48),
        outline=(75, 105, 130),
        radius=30,
        width=3
    )

    draw.text(
        (100, 1160),
        "VISUEL",
        font=SMALL_FONT,
        fill=(120, 220, 255)
    )

    draw_wrapped(
        draw,
        visual_text,
        100,
        1225,
        WIDTH - 200,
        BODY_FONT
    )

    # --------------------------------------------------------
    # VOIX OFF
    # --------------------------------------------------------

    voice_text = scene.get(
        "voice",
        ""
    )

    rounded_box(
        draw,
        (60, 1490, WIDTH - 60, 1770),
        fill=(24, 32, 45),
        outline=(75, 105, 130),
        radius=30,
        width=3
    )

    draw.text(
        (100, 1530),
        "VOIX OFF",
        font=SMALL_FONT,
        fill=(120, 220, 255)
    )

    draw_wrapped(
        draw,
        voice_text,
        100,
        1590,
        WIDTH - 200,
        BODY_FONT
    )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    draw.text(
        (60, 1830),
        "STEM • ROBOTIQUE • IoT • SCIENCES",
        font=SMALL_FONT,
        fill=(150, 160, 175)
    )

    return image


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("       AI CONTENT FACTORY")
    print("       DYNAMIC VISUAL GENERATOR")
    print("=" * 60)

    if not STORYBOARD_FILE.exists():

        raise FileNotFoundError(
            f"Storyboard introuvable : {STORYBOARD_FILE}"
        )

    with open(
        STORYBOARD_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        storyboard = json.load(file)

    title = storyboard.get(
        "title",
        "Projet STEM"
    )

    scenes = storyboard.get(
        "scenes",
        []
    )

    if not scenes:

        raise ValueError(
            "Aucune scène trouvée."
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print()
    print(f"🎯 Sujet : {title}")
    print(f"🎬 {len(scenes)} scènes")

    # Supprime les anciens PNG
    for old_file in OUTPUT_DIR.glob(
        "scene_*.png"
    ):
        old_file.unlink()

    for index, scene in enumerate(
        scenes,
        start=1
    ):

        print(
            f"🖼️ Génération scène {index}..."
        )

        image = create_scene(
            title,
            scene,
            index
        )

        output_file = (
            OUTPUT_DIR /
            f"scene_{index:02d}.png"
        )

        image.save(
            output_file,
            "PNG"
        )

        print(
            f"   ✅ {output_file}"
        )

    print()
    print("=" * 60)
    print("✅ VISUELS DYNAMIQUES GÉNÉRÉS")
    print("=" * 60)


if __name__ == "__main__":
    main()