"""
AI Response Generation Module (Section 4.14).

Supports two interchangeable Large Language Model backends, matching the
"Integration with Large Language Models" section of the dissertation:
    - Ollama (local models such as Llama 3) for privacy-sensitive deployments
    - OpenAI (cloud models such as GPT-4o-mini) for higher-capacity deployments

The active backend is selected using the LLM_PROVIDER setting so that the
rest of the application does not need to know which model is in use.
"""
from config import settings


def _generate_with_ollama(prompt: str) -> str:
    import ollama

    client = ollama.Client(host=settings.OLLAMA_BASE_URL)
    response = client.chat(
        model=settings.OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"].strip()


def _generate_with_openai(prompt: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def generate_response(prompt: str) -> str:
    """
    Generate a response from the currently configured LLM provider.
    Falls back to a safe message if the model call fails, instead of
    raising an unhandled error back to the customer (Section 4.18 Error
    Handling and Logging).
    """
    try:
        if settings.LLM_PROVIDER == "openai":
            return _generate_with_openai(prompt)
        return _generate_with_ollama(prompt)
    except Exception as exc:  # noqa: BLE001 - deliberately broad for graceful fallback
        print(f"[ai_service] LLM generation failed: {exc}")
        return (
            "I'm sorry, I'm having trouble generating a response right now. "
            "Please try again in a moment, or contact support if the issue continues."
        )


def post_process_response(text: str) -> str:
    """
    Basic response post-processing (Section 4.14.6): trims whitespace and
    removes any leaked prompt scaffolding the model may have echoed back.
    """
    cleaned = text.strip()
    for marker in ("Answer:", "Customer question:"):
        if cleaned.startswith(marker):
            cleaned = cleaned[len(marker):].strip()
    return cleaned
