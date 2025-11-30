# coordinator/router.py
from coordinator.parser import extract_table
from coordinator.heartbeat import node_status

BRANCH_MAP = {
    "_a": ["node1"],
    "_b": ["node2"],
    "_c": ["node3"],
}

ALL_NODES = ["node1", "node2", "node3"]

# Logical global tables
LOGICAL_TO_PHYSICAL = {
    "patrons": ["patrons_A", "patrons_B", "patrons_C"],
    "books": ["books_A", "books_B", "books_C"],
}


def _alive_nodes(nodes):
    """Return only nodes that are alive according to heartbeat."""
    return [n for n in nodes if node_status.get(n, {}).get("alive", False)]


def route_query(sql: str):
    """
    Returns:
        (nodes, rewritten_sqls)
        - nodes: list of target nodes
        - rewritten_sql_list: same length as nodes
    """
    table = extract_table(sql)
    if not table:
        alive = _alive_nodes(ALL_NODES)
        return alive, [sql] * len(alive)

    table_lower = table.lower()

    # --- Case 1: explicit table patrons_A, books_B ---
    for suffix, nodes in BRANCH_MAP.items():
        if table_lower.endswith(suffix):
            alive = _alive_nodes(nodes)
            return alive, [sql] * len(alive)

    # --- Case 2: logical table patrons / books ---
    if table_lower in LOGICAL_TO_PHYSICAL:
        physical_tables = LOGICAL_TO_PHYSICAL[table_lower]

        # 1-to-1 physical table mapping: node1 -> _A, node2 -> _B, node3 -> _C
        alive = _alive_nodes(ALL_NODES)

        rewritten_sqls = []
        for node in alive:
            idx = ALL_NODES.index(node)
            physical_table = physical_tables[idx]
            rewritten_sqls.append(sql.replace(table, physical_table))

        return alive, rewritten_sqls

    # --- Case 3: unknown table, broadcast but only to alive nodes ---
    alive = _alive_nodes(ALL_NODES)
    return alive, [sql] * len(alive)
