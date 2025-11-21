# coordinator/router.py
from parser import extract_table

BRANCH_MAP = {
    "_a": ["node1"],
    "_b": ["node2"],
    "_c": ["node3"]
}

ALL_NODES = ["node1", "node2", "node3"]

# These are your logical global tables
GLOBAL_TABLES = {"patrons", "books"}

def route_query(sql: str):
    """
    Returns (nodes, rewritten_sql_list)
    - nodes: list of node names
    - rewritten_sql: SQL rewritten per node (same length as nodes)
    """

    table = extract_table(sql)
    if not table:
        return ALL_NODES, [sql] * 3

    table_lower = table.lower()

    # Case 1: explicit table (patrons_A)
    for suffix, nodes in BRANCH_MAP.items():
        if table_lower.endswith(suffix):
            return nodes, [sql]

    # Case 2: logical table (patrons, books)
    logical_to_physical = {
        "patrons": ["patrons_A", "patrons_B", "patrons_C"],
        "books": ["books_A", "books_B", "books_C"]
    }

    if table_lower in logical_to_physical:
        physical_tables = logical_to_physical[table_lower]
        rewritten_sqls = [
            sql.replace(table, physical_tables[i]) for i in range(3)
        ]
        return ALL_NODES, rewritten_sqls

    # Unknown table → treat as cross-branch but no rewrite
    return ALL_NODES, [sql] * 3

