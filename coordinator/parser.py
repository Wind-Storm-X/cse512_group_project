# coordinator/parser.py
import re

def extract_table(sql: str):
    if not sql:
        return None
    # allow optional double quotes around table name in FROM
    m = re.search(r'from\s+"?([a-zA-Z0-9_]+)"?', sql, re.IGNORECASE)
    if not m:
        return None
    return m.group(1)
