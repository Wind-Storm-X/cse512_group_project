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
    '''Output Formatter'''
    if not rows:
        print("(no results)")
        return

    # Convert RealDictRow to dictionaries
    rows = [dict(r) for r in rows]

    # Extract columns
    columns = list(rows[0].keys())

    # Compute max width for each column
    col_widths = {col: max(len(col), *(len(str(r[col])) for r in rows)) for col in columns}

    # Header
    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    print(header)
    print("-" * len(header))

    # Rows
    for r in rows:
        line = " | ".join(str(r[col]).ljust(col_widths[col]) for col in columns)
        print(line)

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
        nodes, sqls = route_query(optimized_sql)
        print(f"→ Routed to nodes: {nodes}")

        # Optimize queries after routing
        for q in sqls:
            q = optimize(q)

        # Execute on each node
        results = []
        for node, actual_sql in zip(nodes, sqls):
            try:
                res = execute_on_node(node, actual_sql)
                results.extend(res)  # merge row lists
            except Exception as e:
                print(f"→ Execution error on {node}: {e}")

        # Enforce final LIMIT at Coordinator level
        user_limit = extract_limit(optimized_sql) or 100  # default LIMIT if missing
        final_results = results[:user_limit]

        # Print final merged result
        print("→ Merged Result:")
        print_table(final_results)

if __name__ == "__main__":
    main()
