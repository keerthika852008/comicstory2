from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont

from app.config import get_settings


def get_output_path() -> Path:

    settings = get_settings()

    filename = (
        f"panel_{uuid4().hex}.png"
    )

    return (
        Path(settings.panels_dir)
        / filename
    )


# ---------------------------------------
# MOCK IMAGE
# ---------------------------------------

def create_mock_image(
    prompt: str,
    path: Path
):

    settings = get_settings()

    image = Image.new(
        "RGB",
        (
            settings.image_width,
            settings.image_height
        ),
        "white"
    )

    draw = ImageDraw.Draw(image)

    try:

        title_font = ImageFont.truetype(
            "DejaVuSans.ttf",
            30
        )

        text_font = ImageFont.truetype(
            "DejaVuSans.ttf",
            18
        )

    except OSError:

        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    draw.rectangle(
        (
            20,
            20,
            settings.image_width - 20,
            settings.image_height - 20
        ),
        outline="black",
        width=5
    )

    draw.text(
        (50, 50),
        "ComicCraft Demo Panel",
        fill="black",
        font=title_font
    )

    draw.multiline_text(
        (50, 130),
        prompt[:500],
        fill="black",
        font=text_font,
        spacing=8
    )

    image.save(path)


# ---------------------------------------
# HUGGING FACE IMAGE GENERATION
# ---------------------------------------

def generate_huggingface_image(
    prompt: str,
    path: Path
):

    from huggingface_hub import InferenceClient

    settings = get_settings()

    if not settings.hf_token:

        raise RuntimeError(
            "HF_TOKEN is not configured. "
            "Add it to your .env file."
        )

    client = InferenceClient(
        api_key=settings.hf_token
    )

    image = client.text_to_image(
        prompt=prompt,
        model=settings.image_model
    )

    image.save(path)


# ---------------------------------------
# LOCAL DIFFUSERS IMAGE GENERATION
# ---------------------------------------

def generate_local_image(
    prompt: str,
    path: Path
):

    import torch

    from diffusers import (
        AutoPipelineForText2Image
    )

    settings = get_settings()

    if torch.cuda.is_available():

        device = "cuda"
        dtype = torch.float16

    else:

        device = "cpu"
        dtype = torch.float32

    pipeline = (
        AutoPipelineForText2Image
        .from_pretrained(
            settings.local_image_model,
            torch_dtype=dtype
        )
    )

    pipeline = pipeline.to(device)

    result = pipeline(
        prompt,
        num_inference_steps=settings.image_steps,
        width=settings.image_width,
        height=settings.image_height
    )

    result.images[0].save(path)


# ---------------------------------------
# MAIN FUNCTION
# ---------------------------------------

def generate_image(
    prompt: str
) -> str:

    settings = get_settings()

    output_path = get_output_path()

    # Mock mode
    if settings.mock_ai:

        create_mock_image(
            prompt,
            output_path
        )

    # Local Diffusers
    elif settings.image_backend.lower() == "local":

        generate_local_image(
            prompt,
            output_path
        )

    # Hugging Face
    else:

        generate_huggingface_image(
            prompt,
            output_path
        )

    return (
        f"/static/panels/"
        f"{output_path.name}"
    )