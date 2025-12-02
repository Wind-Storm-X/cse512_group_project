# coordinator/executor.py
import psycopg2
from psycopg2.extras import RealDictCursor
from coordinator.config import NODES

def execute_on_node(node_key, sql):
    """
    Execute given SQL on the target node.
    - For SELECT/RETURNING: fetch rows and COMMIT the transaction so results are visible to others.
    - For non-RETURNING writes: commit and return None.
    Exceptions are propagated to caller so coordinator can decide what to do.
    """
    if not node_key:
        raise ValueError("Invalid node_key: None")
    if node_key not in NODES:
        raise ValueError(f"Unknown node_key: {node_key}")

    dsn = NODES[node_key]
    conn = None
    try:
        # open connection per-call (simple, matches current design)
        conn = psycopg2.connect(dsn)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)

            # If the statement returns rows (SELECT or INSERT ... RETURNING)
            if cur.description is not None:
                rows = cur.fetchall()
                # IMPORTANT: commit so the insert/returning becomes durable and visible
                # to other connections (otherwise only this transaction sees it).
                conn.commit()
                return rows
            else:
                # Non-returning write / DDL: commit and return None
                conn.commit()
                return None

    except Exception:
        # On error, rollback if possible then re-raise for caller logging/handling
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass