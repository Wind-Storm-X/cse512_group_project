# locustfile.py
import random
from locust import HttpUser, task, between

WORDS = [
    "the", "lord", "rings", "mockingbird", "code", "harry",
    "data", "network", "war", "peace", "hobbit", "ai"
]

def rand_term():
    return random.choice(WORDS)

class CoordinatorUser(HttpUser):
    wait_time = between(0.05, 0.2)

    @task(8)
    def search_books(self):
        term = rand_term()
        limit = random.choice([10, 25, 50])
        q = f"SELECT * FROM books WHERE book_name ILIKE '%{term}%' LIMIT {limit};"
        self.client.get("/sql", params={"q": q}, name="READ: search_books")

    @task(2)
    def hot_read(self):
        q = "SELECT book_name FROM books LIMIT 3;"
        self.client.get("/sql", params={"q": q}, name="READ: hot_small")

    @task(1)  # NEW: write traffic (~10% of requests)
    def toggle_checkout(self):
        self.client.post("/write", name="WRITE: toggle_checkout")

    @task(2)  # 20% = small read for latency baseline
    def hot_read(self):
        q = "SELECT book_name FROM books LIMIT 3;"
        self.client.get(
            "/sql",
            params={"q": q},
            name="READ: hot_small"
        )
