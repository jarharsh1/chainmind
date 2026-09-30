"""Pydantic request/response models for the ChainMind API."""

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    question: str
    category: str
    cypher: str
    results: list[dict[str, Any]]
    answer: str


class HealthResponse(BaseModel):
    status: str
    neo4j: str


class GraphResponse(BaseModel):
    nodes: list[dict[str, Any]]
    links: list[dict[str, Any]]
    # True when the node cap trimmed the result set.
    truncated: bool = False
