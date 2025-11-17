# coordinator/main.py
from router import route_query
from executor import execute_on_node
from optimizer import optimize

def main():
    print("=== Coordinator V0.1 ===")

    while True:
        sql = input("\nSQL> ").strip()
        if sql.lower() == "exit":
            break
        if not sql:
            continue

        # 1. Optimize SQL (currently no-op)
        optimized_sql = optimize(sql)

        # 2. Decide which node to send the query to
        node = route_query(optimized_sql)
        if node is None:
            print("→ Error: cannot determine target node from SQL (unknown or unsupported table).")
            continue
        print(f"→ Routed to: {node}")

        # 3. Execute SQL with error handling
        try:
            result = execute_on_node(node, optimized_sql)
            print("→ Result:")
            print(result)
        except Exception as e:
            print("→ Execution error (caught):", e)
            # keep loop alive for next command

if __name__ == "__main__":
    main()
