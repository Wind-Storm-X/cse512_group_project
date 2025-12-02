# coordinator/main.py
from coordinator.router import route_query
from coordinator.executor import execute_on_node
from coordinator.optimizer import optimize
from coordinator.heartbeat import start_heartbeat, node_status
import re
from sqlglot.errors import ParseError

def read_sql(prompt="SQL> "):
    print(prompt, end="")
    lines = []
    while True:
        line = input()
        if line.strip().endswith(";"):
            lines.append(line.strip()[:-1])
            break
        lines.append(line)
    return " ".join(lines)

def extract_limit(sql: str) -> int:
    m = re.search(r"limit\s+(\d+)", sql, re.IGNORECASE)
    return int(m.group(1)) if m else None

def print_table(rows):
    '''Output Formatter'''
    if not rows:
        print("(no results)")
        return

    rows = [dict(r) for r in rows]
    columns = list(rows[0].keys())
    col_widths = {col: max(len(col), *(len(str(r[col])) for r in rows)) for col in columns}
    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    print(header)
    print("-" * len(header))
    for r in rows:
        line = " | ".join(str(r[col]).ljust(col_widths[col]) for col in columns)
        print(line)

def merge_and_dedup_rows(list_of_rowlists):
    """
    Merge multiple lists of rows (each row is dict-like) and deduplicate.
    Deduplication done by tuple of values in column order (stable).
    """
    merged = []
    seen = set()
    for rows in list_of_rowlists:
        if not rows:
            continue
        for r in rows:
            # convert RealDictRow -> dict if needed
            rd = dict(r)
            key = tuple(rd.items())  # use full row content as identity
            if key not in seen:
                seen.add(key)
                merged.append(rd)
    return merged

def main():
    print("=== Coordinator ===")
    print("Note: Enter \"STATUS;\" to check each node's status.")
    start_heartbeat()

    while True:
        sql = read_sql()
        if sql.lower() == "exit":
            break
        if sql.lower() == "status":
            print("\nNode Status")
            print("-----------------------------------")
            for node, s in node_status.items():
                status = "ALIVE" if s["alive"] else "DEAD"
                latency = f"{s['latency']:.1f} ms" if s['latency'] else "-"
                last_ok = s['last_ok'] if s['last_ok'] else "-"
                err = s['error'].strip().split("\n")[0] if s['error'] else "-"
                print(f"Node: {node}")
                print(f"  Status  : {status}")
                print(f"  Latency : {latency}")
                print(f"  Last OK : {last_ok}")
                print(f"  Error   : {err}")
                print(f"  Trend   : {s['trend']}")
                print(f"  Fail#   : {s['fail_count']}")
                print(f"  Success#: {s['success_count']}")
                print()
            continue

        if not sql:
            continue

        # Optimize SQL (if you still want optimizer)
        # optimized_sql = optimize(sql)

        # Route (this returns nodes list and sql list; nodes may be equal length >1)
        try:
            nodes, sqls = route_query(sql)
            optimized_sqls = []
            for q in sqls:
                try:
                    optimized_sqls.append(optimize(q))
                except ParseError as pe:
                    print(f"→ SQL syntax error (optimizer): {pe}")
                    optimized_sqls.append(q)
        except ValueError as e:
            print(f"→ Query error: {e}")
            continue  # skip this query, allow user to continue

        # Ensure nodes and sqls pair up: if nodes length is 1 but many sqls, expand
        if len(nodes) == 1 and len(sqls) > 1:
            nodes = [nodes[0]] * len(sqls)

        print(f"→ Routed to nodes: {nodes}")

        # Execute each (pairwise)
        select_results_collector = []  # collect SELECT results (lists)
        for node, actual_sql in zip(nodes, optimized_sqls):
            try:
                res = execute_on_node(node, actual_sql)
                # If the executor returns a list, it's SELECT or INSERT ... RETURNING
                if isinstance(res, list):
                    select_results_collector.append(res)
                # If res is None (INSERT without RETURNING), there's nothing to merge
            except Exception as e:
                print(f"→ Execution error on {node}: {e}")

        # If we have multiple SELECT result sets, merge & dedup
        merged = []
        if select_results_collector:
            merged = merge_and_dedup_rows(select_results_collector)

        # Apply LIMIT at coordinator level if present in original SQL
        user_limit = extract_limit(sql) or 100
        if user_limit is not None:
            merged = merged[:user_limit]

        print("→ Merged Result:")
        print_table(merged)

if __name__ == "__main__":
    main()