# # coordinator/parser.py
# import re

# def extract_table(sql: str):
#     """
#     Extract the table name from an SQL query.
#     Example:
#         SELECT * FROM books_A LIMIT 3;
#     Returns:
#         "books_a"
#     """
#     if not sql:
#         return None
#     m = re.search(r"from\s+([a-zA-Z0-9_]+)", sql, re.IGNORECASE)
#     if not m:
#         return None
#     return m.group(1).lower()


# coordinator/parser.py
import re

def extract_table(sql: str) -> str:
    """
    Extract the table name from SQL.
    Handles:
      - INSERT INTO table_name ...
      - SELECT ... FROM table_name ...
      - DELETE FROM table_name ...
    Returns table name as it appears in SQL, including suffix (_A/_B/_C)
    """
    sql = sql.strip().rstrip(";")
    pattern = r"(?:INSERT\s+INTO|DELETE\s+FROM|FROM)\s+([a-zA-Z_][a-zA-Z0-9_]*)"
    match = re.search(pattern, sql, re.IGNORECASE)
    if match:
        return match.group(1)
    return None