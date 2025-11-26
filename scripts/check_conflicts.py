#!/usr/bin/env python
"""Check for transactions with conflict labels."""

from scripts.core.api_client import PocketSmithClient
from scripts.core.labels import has_review_flag
from dotenv import load_dotenv

load_dotenv()
client = PocketSmithClient()
user = client.get_user()
user_id = user["id"]

# Get all transactions with conflict labels
print("Fetching conflict transactions...", flush=True)
all_conflicts = []
page = 1
while True:
    batch = client.get_transactions(
        user_id, start_date="2025-01-01", end_date="2025-12-31", page=page, per_page=100
    )
    if not batch:
        break
    for txn in batch:
        labels = txn.get("labels", [])
        if has_review_flag(labels):
            all_conflicts.append(txn)
    if len(batch) < 100:
        break
    page += 1

print(f"\nFound {len(all_conflicts)} transactions with conflict labels")

if all_conflicts:
    # Show first few
    for i, txn in enumerate(all_conflicts[:3]):
        cat = txn.get("category", {})
        date = txn.get("date")
        payee = txn.get("payee")
        amount = abs(txn.get("amount", 0))
        cat_title = cat.get("title", "Uncategorized")
        labels = txn.get("labels", [])
        note = txn.get("note", "")

        print(f"\n{i+1}. Date: {date}")
        print(f"   Payee: {payee}")
        print(f"   Amount: ${amount}")
        print(f"   Current Category: {cat_title}")
        print(f"   Labels: {labels}")
        print(f"   Note: {note}")
