from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request
)

from fastapi.responses import (
    HTMLResponse
)

from fastapi.templating import (
    Jinja2Templates
)

from app.schemas import (
    PromptRequest,
    ComicResponse
)

from app.gemini_flash import (
    generate_outline
)

from app.gemini_pro import (
    generate_story
)

from app.image_generator import (
    generate_image
)

from app.layout_builder import (
    build_comic_layout
)

from app.exporters import (
    save_pdf
)


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


# ---------------------------------------
# COMPLETE COMIC GENERATION
# ---------------------------------------

def generate_complete_comic(
    data: PromptRequest
):

    # Step 1
    outline = generate_outline(
        data
    )

    # Step 2
    story = generate_story(
        data,
        outline
    )

    # Step 3
    images = []

    for panel in story.panels:

        image = generate_image(
            panel.image_prompt
        )

        images.append(image)

    # Step 4
    layout = build_comic_layout(
        story,
        images
    )

    # Step 5
    title = (
        f"{data.character_name}'s "
        "Comic Adventure"
    )

    # Step 6
    pdf_url = save_pdf(
        title,
        layout
    )

    return (
        title,
        layout,
        pdf_url
    )


# ---------------------------------------
# HOME
# ---------------------------------------

@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": None
        }
    )


# ---------------------------------------
# HTML FORM GENERATION
# ---------------------------------------

@router.post(
    "/generate",
    response_class=HTMLResponse
)
async def generate(
    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...)
):

    try:

        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style
        )

        (
            title,
            layout,
            pdf_url
        ) = generate_complete_comic(
            data
        )

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "title": title,
                "layout": layout,
                "pdf_url": pdf_url
            }
        )

    except Exception as error:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(error)
            },
            status_code=500
        )


# ---------------------------------------
# JSON API
# ---------------------------------------

@router.post(
    "/generate-comic/json",
    response_model=ComicResponse
)
async def generate_json(
    payload: PromptRequest
):

    try:

        (
            title,
            layout,
            pdf_url
        ) = generate_complete_comic(
            payload
        )

        return ComicResponse(
            title=title,
            panels=layout,
            pdf_url=pdf_url
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ---------------------------------------
# IMAGE TEST
# ---------------------------------------

@router.post(
    "/test-image"
)
async def test_image(
    request: Request
):

    body = await request.json()

    prompt = str(
        body.get("prompt", "")
    ).strip()

    if not prompt:

        raise HTTPException(
            status_code=400,
            detail="prompt is required"
        )

    try:

        image_url = generate_image(
            prompt
        )

        return {
            "success": True,
            "image_url": image_url
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ---------------------------------------
# EXPORT SUCCESS
# ---------------------------------------

@router.get(
    "/export-success",
    response_class=HTMLResponse
)
async def export_success(
    request: Request,
    pdf_url: str = ""
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "pdf_url": pdf_url
        }
    )