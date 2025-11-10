from faker import Faker
import random
import json
from tqdm import tqdm
import uuid

fake = Faker()
Faker.seed(42)
random.seed(42)

# Configuration
TARGET_BOOKS = 1_000_000
PATRONS_PER_NODE = 12_000
NODES = ["A", "B", "C"]

# Helper: controlled random copy count
def sample_copy_count():
    r = random.random()
    if r < 0.05:
        return random.randint(1, 2)     # rare
    elif r < 0.20:
        return random.randint(9, 20)    # popular
    else:
        return random.randint(3, 8)     # normal

# 1. Generate patrons
patrons_by_node = {}
all_patrons = []

for node in NODES:
    patrons = []
    for _ in range(PATRONS_PER_NODE):
        patrons.append({
            "card_id": str(uuid.uuid4()),
            "first_name": fake.first_name(),
            "last_name": fake.last_name()
        })
    patrons_by_node[node] = patrons
    all_patrons.extend(patrons)

# Add shared patrons across nodes (cross-library accounts)
shared_accounts = random.sample(all_patrons, 1000)
for patron in shared_accounts:
    nodes_for_share = random.sample(NODES, k=random.randint(2, 3))
    for node in nodes_for_share:
        # only add if not already in node
        if not any(p["card_id"] == patron["card_id"] for p in patrons_by_node[node]):
            patrons_by_node[node].append({
                "card_id": patron["card_id"],
                "first_name": patron["first_name"],
                "last_name": patron["last_name"]
            })

# 2. Generate books
books_by_node = {node: [] for node in NODES}
total_books = 0
book_isbn_counter = 10_000_000_000

with tqdm(total=TARGET_BOOKS, desc="Generating books") as pbar:
    while total_books < TARGET_BOOKS:
        isbn = book_isbn_counter
        book_isbn_counter += 1
        title = fake.sentence(nb_words=4).rstrip(".")
        author_fn = fake.first_name()
        author_ln = fake.last_name()
        copy_count = sample_copy_count()

        # Decide which nodes will have copies
        assigned_nodes = random.sample(NODES, k=random.randint(1, min(3, copy_count)))

        # Distribute copies across nodes
        for _ in range(copy_count):
            if total_books >= TARGET_BOOKS:
                break
            node = random.choice(assigned_nodes)
            checked_out = random.random() < 0.2
            patron_checked_out = None
            if checked_out and patrons_by_node[node]:
                patron_checked_out = random.choice(patrons_by_node[node])["card_id"]

            books_by_node[node].append({
                "library_id": str(uuid.uuid4()),
                "isbn": isbn,
                "book_name": title,
                "book_author_fn": author_fn,
                "book_author_ln": author_ln,
                "checked_out": checked_out,
                "patron_checked_out": patron_checked_out
            })
            total_books += 1
            pbar.update(1)

# 3. Write out to JSONL files
for node in NODES:
    with open(f"patrons_{node}.jsonl", "w", encoding="utf-8") as f:
        for p in patrons_by_node[node]:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    with open(f"books_{node}.jsonl", "w", encoding="utf-8") as f:
        for b in books_by_node[node]:
            f.write(json.dumps(b, ensure_ascii=False) + "\n")

print(f"✅ Done! Total books generated: {total_books:,}")
