import psycopg2
import json
import os
from tqdm import tqdm

# ======== Setup ========
DB_NAME = "library_system"
DB_USER = "root"
DB_HOST = "localhost"
DB_PORT = 26257
BATCH_SIZE = 5000

# JSONL files (one JSON object per line)
JSONL_FILES = [
    "patrons_A.jsonl",
    "patrons_B.jsonl",
    "patrons_C.jsonl",
    "books_A.jsonl",
    "books_B.jsonl",
    "books_C.jsonl"
]
# ========================


def connect_db():
    """Connect to CockroachDB"""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password="",
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = False
    return conn


def insert_batch(cur, table, rows):
    """Insert a batch of rows into the specified table"""
    if not rows:
        return

    first = rows[0]
    cols = list(first.keys())
    placeholders = ", ".join(["%s"] * len(cols))
    colnames = ", ".join(cols)

    sql = f"INSERT INTO {table} ({colnames}) VALUES ({placeholders})"
    data = [tuple(row.get(col) for col in cols) for row in rows]
    cur.executemany(sql, data)


def import_jsonl_to_db(jsonl_file, conn):
    """Import a JSONL file to the database"""
    table_name = os.path.splitext(os.path.basename(jsonl_file))[0]
    print(f"\n📘 Importing {jsonl_file} → Table {table_name} ...")

    cur = conn.cursor()

    print(f"🧹 Truncating table {table_name} ...")
    cur.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
    conn.commit()
    
    batch = []
    total_inserted = 0

    with open(jsonl_file, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc=table_name, unit="lines"):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            batch.append(row)

            if len(batch) >= BATCH_SIZE:
                insert_batch(cur, table_name, batch)
                conn.commit()
                total_inserted += len(batch)
                batch.clear()

    # Insert remaining records
    if batch:
        insert_batch(cur, table_name, batch)
        conn.commit()
        total_inserted += len(batch)

    cur.close()
    print(f"✅ {table_name}: imported {total_inserted:,} records.")


def main():
    conn = connect_db()
    try:
        for f in JSONL_FILES:
            if not os.path.exists(f):
                print(f"⚠️ File not found: {f}")
                continue
            import_jsonl_to_db(f, conn)
    except Exception as e:
        print("❌ Error:", e)
        conn.rollback()
    finally:
        conn.close()
        print("\n🚀 Completed!")


if __name__ == "__main__":
    main()
