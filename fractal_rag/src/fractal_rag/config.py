"""Runtime configuration for fractal-rag.

Settings are loaded from environment variables (FRACTAL_RAG_*) with sensible
defaults for the local K3s deployment described in the design spec.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FRACTAL_RAG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Weaviate connection
    weaviate_http_host: str = "localhost"
    weaviate_http_port: int = 30080
    weaviate_grpc_host: str = "localhost"
    weaviate_grpc_port: int = 30051
    weaviate_secure: bool = False

    # Collections
    artifact_collection: str = "FractalArtifact"
    concept_collection: str = "Concept"
    vectorizer_module: str = "text2vec-transformers"

    # Filesystem paths
    corpus_root: Path = Path("/opt/tswetnam/fractal-notebooks")
    irods_root: str = "/iplant/home/tswetnam/fractal-notebooks/"
    repo_root: Path = Path("/opt/tswetnam/github/fractal-notebooks")
    cache_dir: Path = Path.home() / ".cache" / "fractal-rag"

    # Chunking
    chunk_max_tokens: int = 500
    chunk_overlap_tokens: int = 50
    embedding_tokenizer: str = "Snowflake/snowflake-arctic-embed-l-v2.0"

    # Ingest
    batch_size: int = 100
    batch_concurrency: int = 4

    # MCP server
    mcp_default_limit: int = 10
    mcp_max_limit: int = 50

    @property
    def failed_objects_path(self) -> Path:
        return self.cache_dir / "failed_objects.jsonl"

    @property
    def state_path(self) -> Path:
        return self.cache_dir / "state.json"

    @property
    def concepts_seed_path(self) -> Path:
        return Path(__file__).parent / "concepts" / "seed.yaml"


_settings: Settings | None = None


def get_settings(refresh: bool = False) -> Settings:
    """Return the process-wide Settings singleton."""
    global _settings
    if _settings is None or refresh:
        _settings = Settings()
        _settings.cache_dir.mkdir(parents=True, exist_ok=True)
    return _settings
