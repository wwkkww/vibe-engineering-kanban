#!/usr/bin/env python3
"""Test card update feature end-to-end."""

import requests
import json

BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlciIsImV4cCI6OTk5OTk5OTk5OX0.DjKqL7SWw23SBcALx6K-BQJcPf-3BQDWArmAb9gXjuU"

headers = {
    "Cookie": f"auth_token={TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 60)
print("TESTING CARD UPDATE FEATURE")
print("=" * 60)

# Step 1: Get the board
print("\n1️⃣  Fetching board...")
response = requests.get(f"{BASE_URL}/api/board", headers=headers)
board = response.json()

# Get first card
card_id = list(board["cards"].keys())[0]
card = board["cards"][card_id]
original_title = card["title"]
original_details = card["details"]

print(f"✓ Found card: {card_id}")
print(f"  Title: {original_title}")
print(f"  Details: {original_details}")

# Step 2: Update the card
print("\n2️⃣  Updating card...")
new_title = f"UPDATED: {original_title}"
new_details = "Updated via test script"

update_data = {
    "title": new_title,
    "details": new_details
}

update_response = requests.put(
    f"{BASE_URL}/api/board/cards/{card_id}",
    headers=headers,
    json=update_data
)

if update_response.status_code == 200:
    print(f"✓ Update successful (status: {update_response.status_code})")
else:
    print(f"✗ Update failed (status: {update_response.status_code})")
    print(f"  Response: {update_response.text}")
    exit(1)

# Step 3: Verify the update
print("\n3️⃣  Verifying update...")
verify_response = requests.get(f"{BASE_URL}/api/board", headers=headers)
board2 = verify_response.json()
updated_card = board2["cards"][card_id]

print(f"✓ New title: {updated_card['title']}")
print(f"✓ New details: {updated_card['details']}")

# Step 4: Validate
print("\n4️⃣  Validation...")
if updated_card["title"] == new_title and updated_card["details"] == new_details:
    print("✅ SUCCESS! Card update feature is fully working!")
    print("\nTest Results:")
    print(f"  - API endpoint responds: ✓")
    print(f"  - Update saves to database: ✓")
    print(f"  - Data persists on retrieval: ✓")
else:
    print("❌ FAILED! Data mismatch")
    print(f"  Expected title: {new_title}")
    print(f"  Got: {updated_card['title']}")
    exit(1)
