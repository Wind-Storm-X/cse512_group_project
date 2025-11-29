# coordinator/executor.py
import psycopg2
from psycopg2.extras import RealDictCursor
from .config import NODES

def execute_on_node(node_key, sql):
    if not node_key:
        raise ValueError("Invalid node_key: None")

    if node_key not in NODES:
        raise ValueError(f"Unknown node_key: {node_key}")

    dsn = NODES[node_key]

    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)

            if cur.description is not None:
                # SELECT-like query
                rows = cur.fetchall()
                return rows
            else:
                # INSERT/UPDATE/DDL
                conn.commit()
                return {"rows_affected": cur.rowcount}
    finally:
        conn.close()