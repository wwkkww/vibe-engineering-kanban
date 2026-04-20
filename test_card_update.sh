#!/bin/bash

echo "=== Testing Card Update Feature ==="

# Test data
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlciIsImV4cCI6OTk5OTk5OTk5OX0.DjKqL7SWw23SBcALx6K-BQJcPf-3BQDWArmAb9gXjuU"
BASE_URL="http://localhost:8000"

echo ""
echo "1️⃣  Fetching board..."
BOARD=$(curl -s -X GET "$BASE_URL/api/board" \
  -H "Cookie: auth_token=$TOKEN")

# Extract first card ID
CARD_ID=$(echo "$BOARD" | jq -r '.cards | keys[0]')
ORIGINAL_TITLE=$(echo "$BOARD" | jq -r ".cards[\"$CARD_ID\"].title")
ORIGINAL_DETAILS=$(echo "$BOARD" | jq -r ".cards[\"$CARD_ID\"].details")

echo "✓ Found card: $CARD_ID"
echo "  Title: $ORIGINAL_TITLE"
echo "  Details: $ORIGINAL_DETAILS"

echo ""
echo "2️⃣  Updating card..."
UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/api/board/cards/$CARD_ID" \
  -H "Cookie: auth_token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"UPDATED: $ORIGINAL_TITLE\",\"details\":\"Updated via API test\"}")

echo "✓ Update response received"

echo ""
echo "3️⃣  Verifying update..."
BOARD2=$(curl -s -X GET "$BASE_URL/api/board" \
  -H "Cookie: auth_token=$TOKEN")

UPDATED_TITLE=$(echo "$BOARD2" | jq -r ".cards[\"$CARD_ID\"].title")
UPDATED_DETAILS=$(echo "$BOARD2" | jq -r ".cards[\"$CARD_ID\"].details")

echo "✓ New title: $UPDATED_TITLE"
echo "✓ New details: $UPDATED_DETAILS"

echo ""
if [[ "$UPDATED_TITLE" == "UPDATED: $ORIGINAL_TITLE" ]] && [[ "$UPDATED_DETAILS" == "Updated via API test" ]]; then
  echo "✅ SUCCESS! Card update feature is working correctly"
  exit 0
else
  echo "❌ FAILED! Card was not updated properly"
  echo "  Expected title: UPDATED: $ORIGINAL_TITLE"
  echo "  Got: $UPDATED_TITLE"
  exit 1
fi
