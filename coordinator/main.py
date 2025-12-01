# coordinator/main.py
from coordinator.router import route_query
from coordinator.executor import execute_on_node
from coordinator.optimizer import optimize
from coordinator.heartbeat import start_heartbeat, node_status
import re

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
    # Extract LIMIT from SQL, return None if not present
    m = re.search(r"limit\s+(\d+)", sql, re.IGNORECASE)
    return int(m.group(1)) if m else None

def print_table(rows):
    """Output Formatter"""
    if not rows:
        print("(no results)")
        return

    # Filter out None or non-dict results
    dict_rows = []
    for r in rows:
        if r is None:
            continue
        # If r is already a dict, keep it; else try converting
        if isinstance(r, dict):
            dict_rows.append(r)
        else:
            try:
                dict_rows.append(dict(r))
            except (ValueError, TypeError):
                # Skip non-row results (e.g., DELETE/INSERT returns)
                continue

    if not dict_rows:
        print("(no results)")
        return

    # Extract columns
    columns = list(dict_rows[0].keys())

    # Compute max width for each column
    col_widths = {col: max(len(col), *(len(str(r.get(col, ""))) for r in dict_rows)) for col in columns}

    # Header
    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    print(header)
    print("-" * len(header))

    # Rows
    for r in dict_rows:
        line = " | ".join(str(r.get(col, "")).ljust(col_widths[col]) for col in columns)
        print(line)

def main():
    print("=== Library Management System ===")
    print("Welcome to Library Management System!")
    print("Note: Enter \"STATUS;\" to check each node's status, and enter \"EXIT;\" to exit.")
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
                latency = f"{s['latency']:.1f} ms" if s["latency"] else "-"
                last_ok = s["last_ok"] if s["last_ok"] else "-"
                
                # Simplify error message
                err = s["error"]
                if err:
                    err = err.strip().split("\n")[0]  # Keep the first line
                else:
                    err = "-"

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

        # Optimize SQL
        # optimized_sql = optimize(sql)

        # Determine target nodes and possibly modified SQL for each node
        nodes, sqls = route_query(sql)
        print(f"→ Routed to nodes: {nodes}")

        # Optimize queries after routing
        optimized_sqls = [optimize(q) for q in sqls]

        # Execute on each node
        results = []
        for node, actual_sql in zip(nodes, optimized_sqls):
            try:
                res = execute_on_node(node, actual_sql)
                if res:
                    results.extend(res)
            except Exception as e:
                print(f"→ Execution error on {node}: {e}")

        # Enforce final LIMIT at Coordinator level
        user_limit = extract_limit(sql) or 100  # default LIMIT if missing
        final_results = results[:user_limit]

        # Print final merged result
        print("→ Merged Result:")
        print_table(final_results)

if __name__ == "__main__":
    main()
