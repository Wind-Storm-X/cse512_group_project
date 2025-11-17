# coordinator/router.py
from parser import extract_table

def route_query(sql: str):
    sql_lower = sql.lower()

    table = extract_table(sql)
    if not table:
        return None

    table = table.lower()
    if table.endswith("_a"):
        return "node1"
    if table.endswith("_b"):
        return "node2"
    if table.endswith("_c"):
        return "node3"
    return None
