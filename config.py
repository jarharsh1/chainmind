"""
Centralized configuration for ChainMind.

All environment access lives here — no ad-hoc os.getenv scattered across the
codebase. Import `get_settings()` anywhere you need config; it is cached so the
.env file is read once per process.

Provider is pure configuration: point LLM_BASE_URL / LLM_MODEL / LLM_API_KEY at
any OpenAI-compatible endpoint (Groq by default, or NVIDIA NIM, Ollama, vLLM,
LM Studio, OpenAI ...). No code changes needed to switch providers.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- Neo4j ----
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "graphrag123"
    # Optional dedicated read-only user (defense in depth). Falls back to the
    # main credentials when unset.
    neo4j_read_username: str | None = None
    neo4j_read_password: str | None = None

    # ---- LLM (OpenAI-compatible; defaults to Groq) ----
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"
    llm_timeout_seconds: float = 30.0
    llm_max_retries: int = 3

    # ---- Query / API ----
    query_timeout_seconds: float = 15.0
    graph_node_limit: int = 500
    # Comma-separated list of allowed CORS origins, or "*" for all.
    cors_origins: str = "*"

    @property
    def read_auth(self) -> tuple[str, str]:
        """Read-only Neo4j credentials, falling back to the main user."""
        username = self.neo4j_read_username or self.neo4j_username
        password = self.neo4j_read_password or self.neo4j_password
        return (username, password)

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS origins as a list. '*' stays a single wildcard entry."""
        raw = self.cors_origins.strip()
        if raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return the cached Settings instance."""
    return Settings()
