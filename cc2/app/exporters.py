from pathlib import Path
from uuid import uuid4

from fpdf import FPDF

from app.config import get_settings


def get_local_image_path(
    image_url: str
) -> Path:

    """
    Convert:

        /static/panels/example.png

    into:

        static/panels/example.png
    """

    clean_path = image_url.lstrip("/")

    return Path(clean_path)


def save_pdf(
    title: str,
    layout: list[dict]
) -> str:

    settings = get_settings()

    filename = (
        f"comic_{uuid4().hex}.pdf"
    )

    pdf_path = (
        Path(settings.exports_dir)
        / filename
    )

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    for panel in layout:

        pdf.add_page()

        # Panel heading
        pdf.set_font(
            "Helvetica",
            "B",
            18
        )

        pdf.multi_cell(
            0,
            10,
            f"Panel {panel['panel_number']}: "
            f"{panel['title']}"
        )

        pdf.ln(3)

        # Image
        image_path = get_local_image_path(
            panel["image"]
        )

        if image_path.exists():

            from PIL import Image

            with Image.open(image_path) as image:

                width, height = image.size

            max_width = 180
            max_height = 105

            scale = min(
                max_width / width,
                max_height / height
            )

            display_width = width * scale
            display_height = height * scale

            pdf.image(
                str(image_path),
                x=15,
                y=35,
                w=display_width,
                h=display_height
            )

            pdf.set_y(
                35 + display_height + 8
            )

        # Scene description
        pdf.set_font(
            "Helvetica",
            "I",
            11
        )

        pdf.multi_cell(
            0,
            7,
            panel["scene_description"]
        )

        pdf.ln(2)

        # Caption
        pdf.set_font(
            "Helvetica",
            "B",
            11
        )

        pdf.multi_cell(
            0,
            7,
            f"Caption: {panel['caption']}"
        )

        pdf.ln(1)

        # Narration
        pdf.set_font(
            "Helvetica",
            "",
            11
        )

        pdf.multi_cell(
            0,
            7,
            f"Narration: {panel['narration']}"
        )

        pdf.ln(1)

        # Dialogue
        pdf.multi_cell(
            0,
            7,
            f"Dialogue: {panel['dialogue']}"
        )

    pdf.output(
        str(pdf_path)
    )

    return (
        f"/static/exports/"
        f"{filename}"
    )