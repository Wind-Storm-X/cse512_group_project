# coordinator/router.py

from coordinator.parser import extract_logical_tables, contains_join
from coordinator.heartbeat import node_status
import re

DEBUG = False

ALL_NODES = ["node1", "node2", "node3"]

LOGICAL_TO_PHYSICAL = {
    "patrons": ["patrons_A", "patrons_B", "patrons_C"],
    "books":   ["books_A", "books_B", "books_C"],
}

def pick_alive_node():
    """
    Return the first alive CockroachDB node.
    If none are alive, fallback to the first node for error reporting.
    """
    for n in ALL_NODES:
        if node_status[n]["alive"]:
            return n
    return ALL_NODES[0]

def route_query(sql: str):
    """
    Route SQL queries to CockroachDB nodes with logical table awareness.

    Rules:
    - SELECT + logical table → split into multiple queries against physical tables
      (A/B/C), each sent to an alive node.
    - DELETE + logical table → split into multiple queries against physical tables.
    - INSERT + logical table → go to primary node (first physical table only)
    - UPDATE + logical table → split to all physical tables
    - JOIN involving logical table → forbidden (raise error)
    - All other queries → sent to a single alive node
    """

    sql = sql.strip()
    logicals = extract_logical_tables(sql)
    if DEBUG:
        print("route_query:", sql, "=> logicals:", logicals)

    # remove quotes from loucst input
    for t in logicals:
        # match optional quotes and optional dot after table
        sql = re.sub(rf'["\']?{t}["\']?(?=\.)?', t, sql, flags=re.IGNORECASE)

    sql_upper = sql.upper()
    # print("refined route_query:", sql)

    # Forbidden: JOINs on logical tables
    if contains_join(sql) and logicals:
        raise ValueError("JOINs on logical tables are not allowed.")

    # Case: INSERT on logical table → primary node only
    if sql_upper.startswith("INSERT") and logicals:
        if DEBUG:
            print("INSERT with logical table: insert to primary node")
        logical = logicals[0]
        physicals = LOGICAL_TO_PHYSICAL[logical]
        primary_node = ALL_NODES[0]  # primary node
        primary_table = physicals[0]
        new_sql = re.sub(rf"\b{logical}\b", primary_table, sql, flags=re.IGNORECASE)
        if DEBUG:
            print("refined route_query:", new_sql)
        return [primary_node], [new_sql]

    # Case: UPDATE on logical table → split to all physical tables
    if sql_upper.startswith("UPDATE") and logicals:
        if DEBUG:
            print("UPDATE with logical table: global update")
        logical = logicals[0]
        physicals = LOGICAL_TO_PHYSICAL[logical]
        nodes = []
        sqls = []
        for phy in physicals:
            new_sql = re.sub(rf"\b{logical}\b", phy, sql, flags=re.IGNORECASE)
            if DEBUG:
                print("refined route_query:", new_sql)
            sqls.append(new_sql)
            nodes.append(pick_alive_node())  # choose alive node for each table
        return nodes, sqls

    # Case: SELECT + logical table → split into physical tables
    if sql_upper.startswith("SELECT") and logicals:
        if DEBUG:
            print("SELECT with logical table: global search")
        logical = logicals[0]
        physicals = LOGICAL_TO_PHYSICAL[logical]
        nodes = []
        sqls = []
        for phy in physicals:
            new_sql = re.sub(rf"\b{logical}\b", phy, sql, flags=re.IGNORECASE)
            if DEBUG:
                print("refined route_query:", new_sql)
            sqls.append(new_sql)
            nodes.append(pick_alive_node())
        return nodes, sqls

    # Case: DELETE + logical table → split into physical tables
    if sql_upper.startswith("DELETE") and logicals:
        if DEBUG:
            print("DELETE with logical table: global delete")
        logical = logicals[0]
        physicals = LOGICAL_TO_PHYSICAL[logical]
        nodes = []
        sqls = []
        for phy in physicals:
            new_sql = re.sub(rf"\b{logical}\b", phy, sql, flags=re.IGNORECASE)
            if DEBUG:
                print("refined route_query:", new_sql)
            sqls.append(new_sql)
            nodes.append(pick_alive_node())
        return nodes, sqls

    # All other queries → single alive node
    if DEBUG:
        print("query without logical table:", sql)
    node = pick_alive_node()
    return [node], [sql]