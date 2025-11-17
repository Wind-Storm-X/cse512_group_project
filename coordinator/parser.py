# coordinator/parser.py
import re

def extract_table(sql: str):
    """
    Extract the table name from an SQL query.
    Example:
        SELECT * FROM books_A LIMIT 3;
    Returns:
        "books_a"
    """
    if not sql:
        return None
    m = re.search(r"from\s+([a-zA-Z0-9_]+)", sql, re.IGNORECASE)
    if not m:
        return None
    return m.group(1).lower()
