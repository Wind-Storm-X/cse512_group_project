# coordinator/parser.py
import re

LOGICAL_TABLES = ("patrons", "books")

def extract_logical_tables(sql: str, logicals=LOGICAL_TABLES):
    """
    Return all logical tables (patrons / books) that appear in the SQL.
    Does NOT match physical tables like patrons_A or books_C.
    """
    sql_low = sql.lower()
    found = []

    for t in logicals:
        # Match only word boundaries to avoid false positives
        if re.search(rf"\b{t}\b", sql_low):
            found.append(t)

    return found


def contains_join(sql: str):
    """
    Returns True if the SQL contains a JOIN clause.
    """
    return re.search(r"\bJOIN\b", sql, re.IGNORECASE) is not None