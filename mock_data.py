from faker import Faker
import random
import json
from tqdm import tqdm

fake = Faker()
Faker.seed(42)

# library sites
libraries = [
    {"library_id": f"LIB_{i:03}", "library_name": fake.company(), "city": fake.city(), "state": fake.state()}
    for i in range(1, 2001)
]

genres = ["Fiction", "Fantasy", "Science", "History", "Biography", "Romance", "Mystery", "Philosophy", "Poetry"]

N = 1_000_001  # number of records
output_file = "distributed_library_books.jsonl"  # use JSON Lines for large data amount

with open(output_file, "w", encoding="utf-8") as f:
    for i in tqdm(range(N), desc="Generating books"):
        lib = random.choice(libraries)
        status = random.choices(["available", "checked_out", "missing"], weights=[0.8, 0.18, 0.02])[0]
        borrower_id = None
        if status == "checked_out":
            borrower_id = f"USR_{random.randint(1, 50000):05}"

        record = {
            "library_id": lib["library_id"],
            "library_name": lib["library_name"],
            "city": lib["city"],
            "state": lib["state"],
            "book_id": f"BK_{i+1:07}",
            "title": fake.sentence(nb_words=4).rstrip("."),
            "author": fake.name(),
            "genre": random.choice(genres),
            "publication_year": random.randint(1950, 2025),
            "status": status,
            "borrower_id": borrower_id
        }

        # write JSON
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print(f"✅ Done! File saved as {output_file}")
