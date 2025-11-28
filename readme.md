To download the library used by the optimizer, run `pip3 install sqlglot`

To start the cluster, open powershell in the folder you saved the .yml file and run:
`docker-compose up -d`

You can open http://localhost:8080 in your browser to view the health of the nodes.

The init.sql file sets up the tables in the nodes (for the demo, just the tables for the books and the patrons).
So in powershell (in the same folder as the init file) run:
`Get-Content init.sql | docker exec -i downtown-library ./cockroach sql --insecure`
to initialize these tables. 

After initializing the tables, you can optionally add some dummy data by running:
`Get-Content dummydata.sql | docker exec -i downtown-library ./cockroach sql --insecure`

To make sure the dummy data worked, run:
`docker exec -it downtown-library ./cockroach sql --insecure --database=library_system`
to run a SQL session.
Then, enter a simple SQL query, such as:
`SELECT book_name FROM books_A;`.

You can also run:
`docker exec -it downtown-library ./cockroach sql --insecure`
in powershell to manually use SQL.

To start coordinator service, go to the `coordinator` directory and run `python3 main.py`.

The heartbeat service will alert the user when a node is crashed or recovered. You can also enter `STATUS;` to check node status.

Distributed Library System – README
1. Project Overview

This project implements a distributed library catalog on top of a 3-node CockroachDB cluster with:

Horizontal partitioning of tables (books_a/b/c, patrons_a/b/c)

A Python coordinator that:

Parses and routes SQL to the correct nodes

Executes distributed queries in parallel

Merges results and enforces a final LIMIT

A small Flask HTTP API (/sql, /write) to expose the coordinator for testing

Locust.io for load testing and evaluation (throughput, latency)

Manual procedures for consistency delay and fault recovery measurements

2. Prerequisites
Software

Docker and Docker Compose

Python 3.10+ (you used 3.12)

`pip`

Python dependencies

From the project root:

`pip install flask locust psycopg[binary] psycopg_pool`


(If you have a venv, activate it first.)

3. Starting the CockroachDB Cluster

From the project root (where docker-compose.yml lives):

`docker-compose up -d`


You should see 3 containers when you run:

`docker ps`


Example names (yours):

`downtown-library`

`west-library`

`north-library`

3.1. Initialize schema

Run this once to create the tables:

`Get-Content init.sql | docker exec -i downtown-library ./cockroach sql --insecure --database=library_system`

3.2. Load dummy data (optional but recommended)

`Get-Content dummydata.sql | docker exec -i downtown-library ./cockroach sql --insecure --database=library_system`

3.3. Verify tables exist
`docker exec -it downtown-library ./cockroach sql --insecure --database=library_system -e "SHOW TABLES;"`


You should see:

`books_a, books_b, books_c`

`patrons_a, patrons_b, patrons_c`

4. Coordinator CLI (manual SQL)

The CLI coordinator is in coordinator/main.py.
Run it from the project root:

`python -m coordinator.main`


You should see:

`=== Coordinator ===`
`SQL>`


Example queries:

`SELECT * FROM books LIMIT 10;
SELECT book_name, checked_out FROM books WHERE book_name ILIKE '%ring%' LIMIT 5;
exit`


Behavior:

optimizer – cleans SQL and adds a default LIMIT if missing.

router – figures out which physical tables (books_a/b/c) to query and which nodes to send them to.

parallel_db – executes the per-node SQL in parallel threads.

Results are merged and truncated to the final LIMIT.

5. HTTP API (for Locust & external clients)

The API lives in api_server.py. It wraps the coordinator logic behind HTTP.

5.1. Start the API server

From the project root:

`python api_server.py`


Flask will start on http://localhost:8000.

5.2. /sql – read queries

HTTP GET:

`GET /sql?q=<URL-encoded SQL>`


Example (in browser):

`http://localhost:8000/sql?q=SELECT%20*%20FROM%20books%20LIMIT%2010;`


You should get JSON:

`{
  "query": "SELECT ...",
  "nodes": ["node1", "node2", "node3"],
  "limit": 10,
  "count": 10,
  "rows": [ ... ]
}`

5.3. /write – test writes

HTTP POST:

`POST /write`


This endpoint:

picks a random shard (books_a/b/c)

picks a random sample ISBN

toggles checked_out = NOT checked_out for that ISBN

directly executes UPDATE on the correct node

Example (PowerShell):

`Invoke-WebRequest -Method POST http://localhost:8000/write`


Expected JSON:

`{
  "ok": true,
  "node": "node3",
  "table": "books_c",
  "isbn": "9780451524935"
}`

6. Parallel Execution Logic (summary)

You don’t need to configure anything: parallel_db.py is already wired in.

router.route_query(sql) → returns (nodes, sqls_per_node)

execute_in_parallel(nodes, sqls) uses a ThreadPoolExecutor to run executor.execute_on_node concurrently for each node.

main.py and api_server.py both use this to run distributed queries.

7. Evaluation: How to Reproduce the Metrics

This section describes exactly how to run the experiments used in the evaluation.

7.1. Read Throughput & Latency (Locust)
7.1.1. Ensure dependencies
`pip install locust`

7.1.2. locustfile

You already have locustfile.py in the project root. It defines:

READ: search_books → random SELECT * FROM books WHERE book_name ILIKE '%term%' LIMIT N

READ: hot_small → SELECT book_name FROM books LIMIT 3

WRITE: toggle_checkout → hits /write (used later for write throughput)

7.1.3. Start API & Locust

Start api_server in one terminal:

`python api_server.py`


Start Locust in another terminal:

`python -m locust -H http://localhost:8000`


Open the UI:
`→ http://localhost:8089`

In the UI:

Number of users: 100

Spawn rate: 20

Click Start Swarming

After ~1–2 minutes, open the Statistics tab.

7.1.4. What to record (Reads)

Look at rows:

READ: search_books

READ: hot_small

Aggregated

Record:

Current RPS (or total RPS) → reads/second throughput

Median (ms) (50% column) → median read latency

99%ile (ms) → 99th percentile read latency

# Fails and Failures % → should be 0 during the clean run.

These numbers give you the read throughput and latency metrics.

7.2. Write Throughput & Latency (Locust)

Use the same Locust run (same locustfile.py), but now focus on:

Row: POST WRITE: toggle_checkout

Record:

Current RPS → writes/second throughput

Median (ms) → median write latency

99%ile (ms) → 99th percentile write latency

Failures → should stay at 0.

Because the write task has a lower weight (1 vs 8+2 for reads), writes will be about ~10% of total traffic.

7.3. Consistency Delay (manual SQL)

Goal: measure how long it takes for a write on one node to be visible on the others.

7.3.1. Open SQL shells
# Node1
`docker exec -it downtown-library ./cockroach sql --insecure --database=library_system`

# Node2
`docker exec -it west-library ./cockroach sql --insecure --database=library_system`

# Node3
`docker exec -it north-library ./cockroach sql --insecure --database=library_system`

7.3.2. Choose a test row

On Node1:

`SELECT isbn, checked_out
FROM books_a
WHERE isbn = 9780451524935;`


Note current checked_out.

7.3.3. Update on Node1 and capture now()

On Node1:

`UPDATE books_a
SET checked_out = NOT checked_out
WHERE isbn = 9780451524935
RETURNING checked_out, now();
`

Record:

checked_out (new value)

now() → T_write

7.3.4. Immediately read on Node2 and Node3

On Node2:

`SELECT checked_out, now()
FROM books_a
WHERE isbn = 9780451524935;`


Record:

checked_out (should match new value)

now() → T_read_node2

On Node3:

`SELECT checked_out, now()
FROM books_a
WHERE isbn = 9780451524935;`


Record:

checked_out

now() → T_read_node3

7.3.5. Interpret

Since both Node2 and Node3 already show the updated checked_out value by the time you query them, and individual statement times are only 5–8 ms, the consistency delay is effectively on the order of a few milliseconds, negligible compared to your ~2s end-to-end latency.

7.4. Fault Recovery (Node Failure Under Load)

Goal: observe how the system behaves when a node fails and restarts.

7.4.1. Start API & Locust

Same as 7.1:

`python api_server.py`
`python -m locust -H http://localhost:8000`


Locust UI:

Users: 100

Spawn rate: 20

Start swarming and let it stabilize.

Optionally run python -m coordinator.main in another terminal if you want heartbeat alerts.

7.4.2. Kill one node

In a new terminal, stop one Cockroach container (e.g., west-library):

`docker stop west-library`


Immediately:

Watch Locust → Failures % jumps to 100%, RPS may drop or remain similar but all 500s.

`Open Cockroach UI → http://localhost:8080`
 → Nodes tab:

Node becomes Suspect then Dead after Cockroach’s failure timeout.

Record approximate times:

T_stop – when you ran docker stop

T_down_detected – when Cockroach UI marks node as suspect/dead

If you have the heartbeat running, note the >>> ALERT: nodeX just went DOWN! timestamp too.

7.4.3. Restart the node

After 20–30 seconds:

`docker start west-library`


Then:

In Cockroach UI, watch node go back to Live

Locust’s failures should drop, RPS stabilize again

Record times:

T_restart – when you started the node

T_recovered – when Cockroach shows node live again

T_stable – when Locust failures return to 0%

7.4.4. Interpretation

You can compute:

Failure detection time ≈ T_down_detected - T_stop

Recovery time ≈ T_recovered - T_restart

Outage window at the application level ≈ T_stable - T_stop

These give you the fault-tolerance metrics described in the project spec.

8. Stopping Everything

When you’re done:

Stop Locust

In the Locust UI, click Stop, then close the terminal.

Stop API

Ctrl+C in the python api_server.py terminal.

Stop coordinator CLI / heartbeat

Ctrl+C in the python -m coordinator.main terminal.

Stop Cockroach cluster

From the project root:

docker-compose down

