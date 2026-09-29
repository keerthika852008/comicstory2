from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import (
    ComicOutline,
    PanelOutline,
    PromptRequest
)


def get_client():

    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Add it to your .env file."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_outline(
    request: PromptRequest
) -> ComicOutline:

    settings = get_settings()

    # -----------------------------
    # MOCK MODE
    # -----------------------------

    if settings.mock_ai:

        titles = [
            "The Beginning",
            "The Journey",
            "The Challenge",
            "The Turning Point",
            "The New Beginning"
        ]

        panels = []

        for number in range(1, 6):

            panels.append(
                PanelOutline(
                    panel_number=number,
                    title=titles[number - 1],
                    scene_description=(
                        f"{request.character_name} explores "
                        f"{request.setting} as the adventure develops."
                    ),
                    image_prompt=(
                        f"{request.character_name} in "
                        f"{request.setting}, panel {number}, "
                        f"{request.art_style}, "
                        f"{request.tone}, "
                        "cinematic comic illustration, "
                        "expressive character, "
                        "detailed environment, "
                        "no text, no letters, no speech bubbles"
                    )
                )
            )

        return ComicOutline(panels=panels)

    # -----------------------------
    # REAL GEMINI MODE
    # -----------------------------

    prompt = f"""
Create a coherent five-panel comic outline.

Story idea:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Requirements:

1. Generate exactly five panels.
2. The panels must form one continuous story.
3. Keep the same main character throughout.
4. Give every panel a short title.
5. Give every panel a scene description.
6. Give every panel an image-generation prompt.
7. Image prompts must not contain written text.
8. Do not include speech bubbles in image prompts.
9. Make the ending feel complete.
"""

    client = get_client()

    response = client.models.generate_content(

        model=settings.gemini_flash_model,

        contents=prompt,

        config=types.GenerateContentConfig(

            response_mime_type="application/json",

            response_schema=ComicOutline,

            temperature=0.8,
        ),
    )

    return ComicOutline.model_validate_json(
        response.text
    )