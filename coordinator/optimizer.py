# coordinator/optimizer.py
import re
from sqlglot.optimizer import optimize as sqlglot_optimize

library_schema = {
    "patrons_A": {
        "card_id": "UUID",
        "first_name": "STRING",
        "last_name": "STRING",
    },
    "patrons_B": {
        "card_id": "UUID",
        "first_name": "STRING",
        "last_name": "STRING",
    },
    "patrons_C": {
        "card_id": "UUID",
        "first_name": "STRING",
        "last_name": "STRING",
    },
    "books_A": {
        "library_id": "UUID",
        "isbn": "INT",
        "book_name": "STRING",
        "book_author_fn": "STRING",
        "book_author_ln": "STRING",
        "checked_out": "BOOLEAN",
        "patron_checked_out": "UUID",
    },
    "books_B": {
        "library_id": "UUID",
        "isbn": "INT",
        "book_name": "STRING",
        "book_author_fn": "STRING",
        "book_author_ln": "STRING",
        "checked_out": "BOOLEAN",
        "patron_checked_out": "UUID",
    },
    "books_C": {
        "library_id": "UUID",
        "isbn": "INT",
        "book_name": "STRING",
        "book_author_fn": "STRING",
        "book_author_ln": "STRING",
        "checked_out": "BOOLEAN",
        "patron_checked_out": "UUID",
    },
}

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

    # sqlglot doesn't have a cockroachdb dialect, but cockroachdb is highly compatible with postgres
    optimized_expression = sqlglot_optimize(sql, schema=library_schema, dialect="postgres")
    optimized_sql = optimized_expression.sql(pretty=True)

    # SELECT * FROM books_C;
    return optimized_sql
