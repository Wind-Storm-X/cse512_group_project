from concurrent.futures import ThreadPoolExecutor, as_completed
from .executor import execute_on_node 

# Map aliases (A/B/C) to actual config node keys
ALIAS = {
    "A": "node1",
    "B": "node2",
    "C": "node3"
}

def execute_in_parallel(nodes, sqls):
    """
    Run SQL commands on multiple nodes concurrently.
    Supports node aliases A/B/C or full names node1/node2/node3.
    nodes: list[str] - node identifiers or aliases
    sqls: list[str]  - SQL statements for each node
    Returns a merged list of results.
    """
    if not nodes:
        return []

    # Translate A/B/C to node1/node2/node3
    normalized_nodes = [ALIAS.get(n, n) for n in nodes]

    results = []
    with ThreadPoolExecutor(max_workers=len(normalized_nodes)) as pool:
        futures = [
            pool.submit(execute_on_node, node, sql)
            for node, sql in zip(normalized_nodes, sqls)
        ]
        for fut in as_completed(futures):
            try:
                res = fut.result()
                if isinstance(res, list):
                    results.extend(res)
                elif res is not None:
                    results.append(res)
            except Exception as e:
                print(f"[Parallel Error] {e}")
    return results