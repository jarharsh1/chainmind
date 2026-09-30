"""Tests for question classification and schema pruning."""

import pytest

from pipeline.schema_pruner import (
    CATEGORY_SCHEMA_MAP,
    classify_question,
    get_pruned_schema,
)


@pytest.mark.parametrize(
    "question,expected",
    [
        ("Which suppliers are from China?", "supplier"),
        ("What components are used in Galaxy Ultra X?", "product"),
        ("How much stock is in the Dubai warehouse?", "inventory"),
        ("What is the cheapest shipping route to Flipkart?", "shipping"),
        ("Show the full chain from supplier to retailer", "full_chain"),
    ],
)
def test_classify_question(question, expected):
    assert classify_question(question) == expected


def test_unknown_question_falls_back_to_full_chain():
    assert classify_question("zxcvbnm qwerty asdf") == "full_chain"


def test_every_category_has_schema():
    categories = {
        classify_question(q)
        for q in [
            "supplier delivery",
            "product component",
            "warehouse stock",
            "shipping route cost",
            "risk single source",
            "full chain end to end",
        ]
    }
    for category in categories:
        assert category in CATEGORY_SCHEMA_MAP


def test_pruned_schema_contains_relevant_nodes():
    schema = get_pruned_schema("Which suppliers are from China?")
    assert "Category: supplier" in schema
    assert "Supplier" in schema
    assert "SUPPLIES" in schema


def test_pruned_schema_full_chain_contains_all_nodes():
    schema = get_pruned_schema("Show the full end to end chain")
    for node in ["Supplier", "Component", "Product", "Warehouse", "Retailer"]:
        assert node in schema
