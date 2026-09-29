from google import genai
from google.genai import types

from app.config import get_settings

from app.schemas import (
    ComicOutline,
    ComicStory,
    PromptRequest
)


def get_client():

    settings = get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_story(
    request: PromptRequest,
    outline: ComicOutline
) -> ComicStory:

    settings = get_settings()

    # -----------------------------
    # MOCK MODE
    # -----------------------------

    if settings.mock_ai:

        panels = []

        for panel in outline.panels:

            panels.append(
                {
                    "panel_number": panel.panel_number,
                    "title": panel.title,
                    "scene_description": panel.scene_description,
                    "caption": (
                        f"The adventure continues in "
                        f"{request.setting}."
                    ),
                    "narration": (
                        f"{request.character_name} moves forward "
                        f"through {request.setting}, following "
                        f"the mysterious adventure."
                    ),
                    "dialogue": (
                        f"{request.character_name}: "
                        "I won't give up!"
                    ),
                    "image_prompt": panel.image_prompt,
                }
            )

        return ComicStory(
            panels=panels
        )

    # -----------------------------
    # REAL GEMINI MODE
    # -----------------------------

    prompt = f"""
Write the final story for a five-panel comic.

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

Use this outline:

{outline.model_dump_json(indent=2)}

Requirements:

- Return exactly five panels.
- Keep the same panel numbers.
- Preserve story continuity.
- Give each panel a short caption.
- Give each panel narration.
- Give each panel dialogue.
- Keep the text suitable for a comic panel.
- Dialogue should sound natural.
- Keep the requested tone.
- Keep image prompts visually consistent.
- Do not put written text into image prompts.
"""

    client = get_client()

    response = client.models.generate_content(

        model=settings.gemini_pro_model,

        contents=prompt,

        config=types.GenerateContentConfig(

            response_mime_type="application/json",

            response_schema=ComicStory,

            temperature=0.9,
        ),
    )

    return ComicStory.model_validate_json(
        response.text
    )