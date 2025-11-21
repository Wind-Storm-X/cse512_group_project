# coordinator/optimizer.py
import re

DEFAULT_LIMIT = 100

def optimize(sql: str) -> str:
    if not isinstance(sql, str):
        return ""
    
    sql = sql.strip()

    # Delete ";""
    if sql.endswith(";"):
        sql = sql[:-1]

    # Add a default LIMIT if not provided
    if not re.search(r'\blimit\b', sql, re.IGNORECASE):
        sql += f" LIMIT {DEFAULT_LIMIT}"

    return sql
