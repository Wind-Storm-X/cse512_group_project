# coordinator/executor.py
import psycopg2
from psycopg2.extras import RealDictCursor
from coordinator.config import NODES

def execute_on_node(node_key, sql):
    conn = None
    try:
        conn = psycopg2.connect(NODES[node_key])
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            if cur.description:
                return cur.fetchall()
            else:
                conn.commit()
                return None
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()