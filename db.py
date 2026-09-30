"""
Neo4j connection management for ChainMind.

A single shared driver (previously three separate ones lived across the
codebase) plus a read-only session helper. Use `read_session()` for anything
driven by user/LLM input — combined with the Cypher guard it is defense in
depth: even if a write query slipped past the guard, the session is opened with
READ access.
"""

from collections.abc import Iterator
from contextlib import contextmanager

from neo4j import READ_ACCESS, Driver, GraphDatabase, Session

from config import get_settings

_driver: Driver | None = None


def get_driver() -> Driver:
    """Return the shared Neo4j driver, creating it on first use."""
    global _driver
    if _driver is None:
        s = get_settings()
        _driver = GraphDatabase.driver(s.neo4j_uri, auth=s.read_auth)
    return _driver


def close_driver() -> None:
    """Close the shared driver (call on application shutdown)."""
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


@contextmanager
def read_session() -> Iterator[Session]:
    """Yield a Neo4j session opened with READ access."""
    driver = get_driver()
    session = driver.session(default_access_mode=READ_ACCESS)
    try:
        yield session
    finally:
        session.close()
