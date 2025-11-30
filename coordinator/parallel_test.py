from coordinator.parallel_db import execute_in_parallel
import time

def main():
    # You can use A/B/C aliases OR node1/node2/node3
    nodes = ["A", "B", "C"]
    sql = "SELECT now()"
    sqls = [sql] * len(nodes)

    t0 = time.perf_counter()
    results = execute_in_parallel(nodes, sqls)
    dt = time.perf_counter() - t0

    print("Parallel results:")
    for row in results:
        print(row)
    print(f"Elapsed: {dt:.3f}s")

if __name__ == "__main__":
    main()
