import random                          

from flask import Flask, request, jsonify

from coordinator.optimizer import optimize
from coordinator.router import route_query
from coordinator.main import extract_limit
from coordinator.parallel_db import execute_in_parallel
from coordinator.executor import execute_on_node   

SAMPLE_ISBNS = [
    "9780451524935",  # 1984
    "9780061120084",  # To Kill a Mockingbird
    "9780544003415",  # The Lord of the Rings
    "9780141439518",  # Pride and Prejudice
]

ALIAS_TO_NODE = {
    "a": "node1",
    "b": "node2",
    "c": "node3",
}

app = Flask(__name__)

@app.get("/sql")
def sql_endpoint():
    # ?q=SELECT * FROM books LIMIT 10;
    q = request.args.get("q")
    if not q:
        return jsonify({"error": "missing q parameter"}), 400

    # 1) optimize
    optimized = optimize(q)

    # 2) routing to nodes
    nodes, sqls = route_query(optimized)

    # 3) parallel execution
    rows = execute_in_parallel(nodes, sqls)

    # 4) enforce LIMIT at coordinator level
    limit = extract_limit(optimized) or 100
    rows = rows[:limit]

    return jsonify({
        "query": optimized,
        "nodes": nodes,
        "limit": limit,
        "count": len(rows),
        "rows": rows,
    })

@app.post("/write")
def write_endpoint():
    """
    Simple write used for load testing:
    pick a random shard (books_a/b/c) and flip the checked_out flag
    for a random ISBN on that shard.
    """
    branch = random.choice(["a", "b", "c"])       # choose a shard
    table = f"books_{branch}"                     # books_a / books_b / books_c
    node  = ALIAS_TO_NODE[branch]                 # node1 / node2 / node3

    isbn = random.choice(SAMPLE_ISBNS)

    sql = f"UPDATE {table} SET checked_out = NOT checked_out WHERE isbn = '{isbn}'"

    # direct write to the correct node 
    execute_on_node(node, sql)

    return jsonify({
        "ok": True,
        "node": node,
        "table": table,
        "isbn": isbn,
    })

if __name__ == "__main__":
    # run on http://localhost:8000
    app.run(host="0.0.0.0", port=8000, debug=True)
