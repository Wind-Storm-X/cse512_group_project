# coordinator/router.py
import re
from .parser import extract_table

# Which node owns which shard table (by suffix)
BRANCH_MAP = {
    "_a": ["node1"],
    "_b": ["node2"],
    "_c": ["node3"],
}

ALL_NODES = ["node1", "node2", "node3"]

# physical shard tables (all lowercase to match Cockroach)
LOGICAL_TO_PHYSICAL = {
    "books":   ["books_a",   "books_b",   "books_c"],
    "patrons": ["patrons_a", "patrons_b", "patrons_c"],
}


def _rewrite_from(sql: str, old_table: str, new_table: str) -> str:
    """
    Replace only the table name in the FROM clause.

    Handles:
        FROM books
        FROM "books"
    but does NOT touch aliases like AS "books".
    """
    pattern = re.compile(
        r'(from\s+)"?' + re.escape(old_table) + r'"?',
        re.IGNORECASE
    )
    # replace only the first match (the FROM)
    return pattern.sub(rf'\1{new_table}', sql, count=1)


def route_query(sql: str):
    """
    Returns (nodes, rewritten_sql_list)

    - nodes: list of node names
    - rewritten_sql_list: same length as nodes; SQL for each node
    """
    table = extract_table(sql)
    if not table:
        # Broadcast original SQL everywhere
        return ALL_NODES, [sql] * len(ALL_NODES)

    table_original = table           
    table_lower = table_original.lower()

    # User already targeted a shard table
    for suffix, nodes in BRANCH_MAP.items():
        if table_lower.endswith(suffix):
            # already a physical shard table; send only to its node
            return nodes, [sql]

    # Logical table 
    if table_lower in LOGICAL_TO_PHYSICAL:
        physical_tables = LOGICAL_TO_PHYSICAL[table_lower]

        rewritten_sqls = []
        for phys in physical_tables:
            s = _rewrite_from(sql, table_original, phys)
            rewritten_sqls.append(s)

        return ALL_NODES, rewritten_sqls

    # Unknown table, just broadcast the original 
    return ALL_NODES, [sql] * len(ALL_NODES)
