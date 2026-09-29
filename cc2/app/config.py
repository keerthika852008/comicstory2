from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "ComicCraft"

    # API keys
    gemini_api_key: str = ""
    hf_token: str = ""

    # Gemini models
    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"

    # Image generation
    image_backend: str = "hf"
    image_model: str = "black-forest-labs/FLUX.1-schnell"

    # Optional local Diffusers model
    local_image_model: str = "runwayml/stable-diffusion-v1-5"

    # Development testing
    mock_ai: bool = False

    # Image size
    image_width: int = 768
    image_height: int = 768
    image_steps: int = 4

    # Directories
    output_dir: str = "static"
    panels_dir: str = "static/panels"
    exports_dir: str = "static/exports"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:

    settings = Settings()

    Path(settings.panels_dir).mkdir(
        parents=True,
        exist_ok=True
    )

    Path(settings.exports_dir).mkdir(
        parents=True,
        exist_ok=True
    )

    return settings