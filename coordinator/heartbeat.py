# coordinator/heartbeat.py
import time
import threading
import sys
from .executor import execute_on_node  # ← relative import

HEARTBEAT_INTERVAL = 5  # seconds
WARMUP_CYCLES = 3       # Number of heartbeat cycles before printing alerts

node_status = {
    "node1": {"alive": False, "latency": None, "last_ok": None, "error": None,
              "fail_count": 0, "success_count": 0, "trend": "UNKNOWN"},
    "node2": {"alive": False, "latency": None, "last_ok": None, "error": None,
              "fail_count": 0, "success_count": 0, "trend": "UNKNOWN"},
    "node3": {"alive": False, "latency": None, "last_ok": None, "error": None,
              "fail_count": 0, "success_count": 0, "trend": "UNKNOWN"},
}

def safe_alert(text):
    # best effort to keep the SQL prompt tidy
    sys.stdout.write("\033[2K")
    sys.stdout.write("\033[1A")
    sys.stdout.write("\033[2K")
    print(f">>> ALERT: {text}")
    sys.stdout.write("SQL> ")
    sys.stdout.flush()

def heartbeat_loop():
    previous_state = {node: False for node in node_status.keys()}
    heartbeat_counter = 0
    initialized = False

    while True:
        heartbeat_counter += 1
        if heartbeat_counter >= WARMUP_CYCLES:
            initialized = True

        for node in node_status.keys():
            t0 = time.time()
            try:
                execute_on_node(node, "SELECT 1")
                latency = (time.time() - t0) * 1000

                node_status[node].update({
                    "alive": True,
                    "latency": latency,
                    "last_ok": time.strftime("%H:%M:%S"),
                    "error": None
                })

                # DEAD → ALIVE transition
                if previous_state[node] is False and initialized:
                    safe_alert(f"{node} has RECOVERED at {node_status[node]['last_ok']} "
                               f"(latency={latency:.1f} ms)")

                previous_state[node] = True
                node_status[node]["success_count"] += 1
                node_status[node]["fail_count"] = 0
                node_status[node]["trend"] = "UP" if node_status[node]["success_count"] >= 3 else "STABLE"

            except Exception as e:
                err = str(e)
                node_status[node].update({
                    "alive": False,
                    "latency": None,
                    "error": err,
                })

                # ALIVE → DEAD transition
                if previous_state[node] is True and initialized:
                    safe_alert(f"{node} just went DOWN! error={err}")  # ← fixed

                previous_state[node] = False
                node_status[node]["fail_count"] += 1
                node_status[node]["success_count"] = 0
                node_status[node]["trend"] = "DOWN" if node_status[node]["fail_count"] >= 3 else "STABLE"

        time.sleep(HEARTBEAT_INTERVAL)

def start_heartbeat():
    t = threading.Thread(target=heartbeat_loop, daemon=True)
    t.start()
