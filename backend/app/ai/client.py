from openai import OpenAI

from app.config import settings

# Google's OpenAI-compatible endpoint for the Gemini API.
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def get_ai_client() -> tuple[OpenAI | None, str | None]:
    """Return (client, model) for the configured AI provider.

    Gemini is preferred when both keys are set because its free tier makes it
    the deliberate choice for users avoiding paid OpenAI usage.
    """
    if settings.GEMINI_API_KEY:
        client = OpenAI(api_key=settings.GEMINI_API_KEY, base_url=GEMINI_BASE_URL)
        return client, settings.GEMINI_MODEL
    if settings.OPENAI_API_KEY:
        return OpenAI(api_key=settings.OPENAI_API_KEY), settings.OPENAI_MODEL
    return None, None


def ai_configured() -> bool:
    return bool(settings.GEMINI_API_KEY or settings.OPENAI_API_KEY)


def ai_provider_name() -> str:
    if settings.GEMINI_API_KEY:
        return "gemini"
    if settings.OPENAI_API_KEY:
        return "openai"
    return "none"
