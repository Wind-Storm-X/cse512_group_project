# coordinator/router.py
from coordinator.parser import extract_table
from coordinator.heartbeat import node_status

BRANCH_MAP = {
    "_a": ["node1"],
    "_b": ["node2"],
    "_c": ["node3"],
}

ALL_NODES = ["node1", "node2", "node3"]

LOGICAL_TO_PHYSICAL = {
    "patrons": ["patrons_A", "patrons_B", "patrons_C"],
    "books": ["books_A", "books_B", "books_C"],
}

def _alive_nodes(nodes, allow_fallback=False):
    if allow_fallback:
        return nodes
    return [n for n in nodes if node_status.get(n, {}).get("alive", False)]

def route_query(sql: str):
    table = extract_table(sql)
    if not table:
        return ALL_NODES, [sql] * len(ALL_NODES)

    table_lower = table.lower()
    sql_upper = sql.strip().upper()
    is_insert = sql_upper.startswith("INSERT")
    is_delete_or_select = sql_upper.startswith("DELETE") or sql_upper.startswith("SELECT")

    # 1. Explicit shard
    for suffix, nodes in BRANCH_MAP.items():
        if table_lower.endswith(suffix):
            if is_insert:
                # INSERT goes to primary node only
                return [nodes[0]], [sql]
            else:
                # SELECT / DELETE can fallback to alive nodes
                alive = _alive_nodes(nodes, allow_fallback=True)
                return alive, [sql] * len(alive)

    # 2. Logical table
    if table_lower in LOGICAL_TO_PHYSICAL:
        physical_tables = LOGICAL_TO_PHYSICAL[table_lower]
        if is_insert:
            # INSERT → primary node only
            primary_node = ALL_NODES[0]
            primary_table = physical_tables[0]
            sql_rewritten = sql.replace(table, primary_table)
            return [primary_node], [sql_rewritten]
        elif is_delete_or_select:
            # SELECT/DELETE → all alive nodes
            target_nodes = []
            rewritten_sqls = []
            for idx, physical_table in enumerate(physical_tables):
                primary_node = ALL_NODES[idx]
                if node_status.get(primary_node, {}).get("alive", False):
                    target_nodes.append(primary_node)
                    rewritten_sqls.append(sql.replace(table, physical_table))
            # Remove duplicates
            seen = set()
            unique_nodes = []
            unique_sqls = []
            for n, s in zip(target_nodes, rewritten_sqls):
                if n not in seen:
                    unique_nodes.append(n)
                    unique_sqls.append(s)
                    seen.add(n)
            return unique_nodes, unique_sqls

    # 3. Unknown table → broadcast to all nodes
    return ALL_NODES, [sql] * len(ALL_NODES)