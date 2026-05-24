"""Thin wrapper around the Weaviate v4 Python client.

Centralizes connection configuration so the rest of the package never has to
think about hosts, ports, or context-manager semantics.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import weaviate
from weaviate.client import WeaviateClient

from .config import Settings, get_settings


def connect(settings: Settings | None = None) -> WeaviateClient:
    """Connect to the Weaviate instance described in Settings.

    Caller is responsible for closing the client (use `client_session` for
    automatic cleanup).
    """
    s = settings or get_settings()
    return weaviate.connect_to_custom(
        http_host=s.weaviate_http_host,
        http_port=s.weaviate_http_port,
        http_secure=s.weaviate_secure,
        grpc_host=s.weaviate_grpc_host,
        grpc_port=s.weaviate_grpc_port,
        grpc_secure=s.weaviate_secure,
    )


@contextmanager
def client_session(settings: Settings | None = None) -> Iterator[WeaviateClient]:
    """Context-managed Weaviate client; guarantees close()."""
    client = connect(settings)
    try:
        yield client
    finally:
        client.close()
