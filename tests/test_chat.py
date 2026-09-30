"""
End-to-end tests for the /api/chat pipeline.

The LLM and the database are mocked, so these run with no live services. The
key security guarantee under test: a prompt-injected write request is refused by
the guard and never reaches the database.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import api.main as main


@pytest.fixture
def client():
    return TestClient(main.app)


def _fake_llm(*outputs):
    """A fake LLM client whose .complete() returns the given outputs in order."""
    fake = MagicMock()
    fake.complete.side_effect = list(outputs)
    return fake


def test_write_request_is_refused_and_never_reaches_db(client):
    """A 'delete all suppliers' prompt where the LLM emits DELETE both times."""
    delete_cypher = "MATCH (s:Supplier) DETACH DELETE s"
    fake = _fake_llm(delete_cypher, delete_cypher)  # original + repair both bad

    with patch("pipeline.cypher_chain.get_llm_client", return_value=fake), patch(
        "pipeline.cypher_chain.execute_cypher"
    ) as exec_spy:
        resp = client.post("/api/chat", json={"question": "delete all suppliers"})

    assert resp.status_code == 200
    body = resp.json()
    assert "read-only" in body["answer"].lower()
    assert body["results"] == []
    # The critical assertion: the write query never touched the database.
    exec_spy.assert_not_called()


def test_read_question_returns_answer(client):
    fake = _fake_llm(
        'MATCH (s:Supplier) WHERE toLower(s.country) = "china" RETURN s.name',
        "There are 2 suppliers in China: ShenZhen MicroTech and Dongguan Power.",
    )
    rows = [{"s.name": "ShenZhen MicroTech"}, {"s.name": "Dongguan Power"}]

    with patch("pipeline.cypher_chain.get_llm_client", return_value=fake), patch(
        "pipeline.cypher_chain.execute_cypher", return_value=(rows, None)
    ):
        resp = client.post(
            "/api/chat", json={"question": "which suppliers are from China?"}
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["category"] == "supplier"
    assert body["cypher"].startswith("MATCH")
    assert body["results"] == rows
    assert "China" in body["answer"]


def test_write_then_repaired_query_executes(client):
    """First attempt is a write; the repair is read-only and does run."""
    fake = _fake_llm(
        "MATCH (s:Supplier) DELETE s",  # rejected
        "MATCH (s:Supplier) RETURN s.name",  # repaired -> safe
        "Here are the suppliers.",  # answer
    )

    with patch("pipeline.cypher_chain.get_llm_client", return_value=fake), patch(
        "pipeline.cypher_chain.execute_cypher", return_value=([{"s.name": "A"}], None)
    ) as exec_spy:
        resp = client.post("/api/chat", json={"question": "list suppliers"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["cypher"] == "MATCH (s:Supplier) RETURN s.name"
    exec_spy.assert_called_once()


def test_db_error_returns_clean_message(client):
    fake = _fake_llm("MATCH (s:Supplier) RETURN s.name")

    with patch("pipeline.cypher_chain.get_llm_client", return_value=fake), patch(
        "pipeline.cypher_chain.execute_cypher",
        return_value=([], "ServiceUnavailable: connection refused"),
    ):
        resp = client.post("/api/chat", json={"question": "list suppliers"})

    assert resp.status_code == 200
    assert "could not be completed" in resp.json()["answer"].lower()


def test_greeting_short_circuits_without_llm(client):
    """Greetings never call the LLM or the DB."""
    with patch("pipeline.cypher_chain.get_llm_client") as llm_spy, patch(
        "pipeline.cypher_chain.execute_cypher"
    ) as exec_spy:
        resp = client.post("/api/chat", json={"question": "hello"})

    assert resp.status_code == 200
    assert resp.json()["category"] == "greeting"
    llm_spy.assert_not_called()
    exec_spy.assert_not_called()


def test_empty_question_is_rejected(client):
    resp = client.post("/api/chat", json={"question": ""})
    assert resp.status_code == 422


def test_missing_question_is_rejected(client):
    resp = client.post("/api/chat", json={})
    assert resp.status_code == 422
