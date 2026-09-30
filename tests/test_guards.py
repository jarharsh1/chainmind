"""Tests for the read-only Cypher guard."""

import pytest

from pipeline.guards import UnsafeCypherError, assert_read_only, check_read_only

READ_ONLY_QUERIES = [
    "MATCH (s:Supplier) RETURN s.name",
    "MATCH (s:Supplier)-[:SUPPLIES]->(c:Component) RETURN c.name, s.name",
    "MATCH (c:Component) WITH c, count(*) AS n WHERE n = 1 RETURN c.name",
    'MATCH (p:Product) WHERE toLower(p.name) CONTAINS "iphone" RETURN p.name',
    "OPTIONAL MATCH (n)-[r]-(m) RETURN n, m ORDER BY n.name LIMIT 10",
    # 'SUPPLIES' contains no standalone 'SET'/'USE'; 'OFFSET' contains 'SET' but not as a word.
    "MATCH (w:Warehouse)-[:SHIPS_TO]->(r:Retailer) RETURN r.name SKIP 5 LIMIT 5",
]

WRITE_QUERIES = [
    "MATCH (s:Supplier) DETACH DELETE s",
    "CREATE (x:Evil {name: 'boom'})",
    "MATCH (n) SET n.hacked = true RETURN n",
    "MERGE (s:Supplier {id: 'x'})",
    "MATCH (n) REMOVE n.name",
    "DROP CONSTRAINT foo",
    "MATCH (n) DELETE n",
    "CALL db.labels()",
    "CALL apoc.create.node(['X'], {})",
    "LOAD CSV FROM 'file:///x.csv' AS row RETURN row",
    "FOREACH (x IN [1,2] | CREATE (:N))",
]


@pytest.mark.parametrize("cypher", READ_ONLY_QUERIES)
def test_read_only_queries_pass(cypher):
    assert check_read_only(cypher)[0] is True
    assert assert_read_only(cypher) == cypher


@pytest.mark.parametrize("cypher", WRITE_QUERIES)
def test_write_queries_blocked(cypher):
    is_safe, reason = check_read_only(cypher)
    assert is_safe is False
    assert reason
    with pytest.raises(UnsafeCypherError):
        assert_read_only(cypher)


def test_empty_query_blocked():
    assert check_read_only("")[0] is False
    assert check_read_only("   ")[0] is False


def test_keyword_inside_string_literal_is_safe():
    # A supplier literally named "Create Corp" must not look like a CREATE clause.
    cypher = 'MATCH (s:Supplier {name: "Create Corp"}) RETURN s.name'
    assert check_read_only(cypher)[0] is True


def test_keyword_inside_comment_is_safe():
    cypher = "MATCH (s:Supplier) RETURN s.name // TODO: DELETE later"
    assert check_read_only(cypher)[0] is True


def test_write_hidden_after_read_is_blocked():
    # A trailing write clause must still be caught.
    cypher = "MATCH (s:Supplier) WITH s LIMIT 1 DETACH DELETE s"
    assert check_read_only(cypher)[0] is False
