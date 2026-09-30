"""
Provider-agnostic LLM client.

A thin wrapper over the OpenAI client pointed at any OpenAI-compatible endpoint
(Groq by default; also NVIDIA NIM, Ollama, vLLM, LM Studio, OpenAI ...). The
provider is pure configuration — nothing downstream in the pipeline knows or
cares which endpoint is used.

Timeouts and retries are centralized here: a slow or flaky endpoint fails fast
with a bounded number of exponential-backoff retries rather than hanging.
"""

from openai import (
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
    OpenAI,
    RateLimitError,
)
from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config import get_settings

# Transient failures worth retrying. Bad requests / auth errors are not here —
# retrying those just wastes time.
_RETRYABLE = (
    APITimeoutError,
    APIConnectionError,
    RateLimitError,
    InternalServerError,
)


class LLMClient:
    """Minimal chat-completion client with timeout + retry."""

    def __init__(self) -> None:
        s = get_settings()
        # max_retries=0: tenacity below is the single source of retry truth.
        self._client = OpenAI(
            base_url=s.llm_base_url,
            api_key=s.llm_api_key or "not-needed",
            max_retries=0,
        )
        self._model = s.llm_model
        self._timeout = s.llm_timeout_seconds
        self._max_retries = max(1, s.llm_max_retries)

    def complete(
        self,
        prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 500,
    ) -> str:
        """Send a single-turn prompt and return the assistant's text reply."""
        retryer = Retrying(
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=0.5, max=8),
            retry=retry_if_exception_type(_RETRYABLE),
            reraise=True,
        )

        def _call() -> str:
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self._timeout,
            )
            return (resp.choices[0].message.content or "").strip()

        return retryer(_call)


_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Return a lazily-created shared LLM client."""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
