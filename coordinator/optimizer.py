# coordinator/optimizer.py
import re

DEFAULT_LIMIT = 100

def optimize(sql: str) -> str:
    """
    Simple optimizer:
    - strips trailing semicolon
    - ensures a LIMIT clause exists (default 100)
    """
    if not isinstance(sql, str):
        return ""

    sql = sql.strip()

    # Remove trailing ';'
    if sql.endswith(";"):
        sql = sql[:-1]

    # Add a default LIMIT if not provided
    if not re.search(r"\blimit\b", sql, re.IGNORECASE):
        sql += f" LIMIT {DEFAULT_LIMIT}"

    return sql
