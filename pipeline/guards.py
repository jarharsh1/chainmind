"""
Read-only Cypher guard.

The LLM generates Cypher from natural language. A prompt-injected or simply
mis-generated query could contain a write/DDL clause (CREATE, DELETE, MERGE,
DROP, ...). This module rejects any such query *before* it is executed, so the
database can never be mutated through the chat path. Combined with the
READ_ACCESS session in `db.py` this is defense in depth.
"""

import re

# Clauses that write data, change schema, or run administrative commands.
# Matched case-insensitively as whole words.
_WRITE_KEYWORDS = (
    "CREATE",
    "DELETE",
    "DETACH",
    "MERGE",
    "SET",
    "REMOVE",
    "DROP",
    "FOREACH",
    "LOAD CSV",
    "CALL DB.",
    "CALL DBMS.",
    "CALL APOC.CREATE",
    "CALL APOC.MERGE",
    "CALL APOC.REFACTOR",
    "CALL APOC.PERIODIC",
    "GRANT",
    "REVOKE",
    "DENY",
    "START",
    "USE",
    "TERMINATE",
)


class UnsafeCypherError(ValueError):
    """Raised when a Cypher query contains a write, DDL, or admin clause."""


def _strip_string_literals(cypher: str) -> str:
    """Remove quoted string literals so keywords inside data don't false-trip.

    e.g. a supplier literally named "Create Corp" should not look like a CREATE.
    """
    # Remove double- and single-quoted literals (handling escaped quotes).
    without_double = re.sub(r'"(?:[^"\\]|\\.)*"', '""', cypher)
    without_single = re.sub(r"'(?:[^'\\]|\\.)*'", "''", without_double)
    # Remove line and block comments.
    without_line = re.sub(r"//[^\n]*", " ", without_single)
    without_block = re.sub(r"/\*.*?\*/", " ", without_line, flags=re.DOTALL)
    return without_block


def check_read_only(cypher: str) -> tuple[bool, str | None]:
    """Return (is_safe, reason). reason is None when safe."""
    if not cypher or not cypher.strip():
        return False, "Empty query."

    sanitized = _strip_string_literals(cypher).upper()

    for keyword in _WRITE_KEYWORDS:
        if " " in keyword or "." in keyword:
            # Multi-token keyword (e.g. "LOAD CSV", "CALL DB.") — substring match
            # on a normalized (single-spaced) form.
            normalized = re.sub(r"\s+", " ", sanitized)
            if keyword in normalized:
                return False, f"Query contains a disallowed clause: {keyword.title()}."
        else:
            # Single word — require word boundaries so SUPPLIES != SET, etc.
            if re.search(rf"\b{keyword}\b", sanitized):
                return False, f"Query contains a disallowed clause: {keyword.title()}."

    return True, None


def assert_read_only(cypher: str) -> str:
    """Return the query if read-only, else raise UnsafeCypherError."""
    is_safe, reason = check_read_only(cypher)
    if not is_safe:
        raise UnsafeCypherError(reason or "Query is not read-only.")
    return cypher
