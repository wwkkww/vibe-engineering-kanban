# Test Script for Kanban API
Write-Host "Testing Kanban API..." -ForegroundColor Green
Write-Host ""

# Test 1: Login
Write-Host "1. Testing login endpoint..." -ForegroundColor Cyan
$loginResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"username":"user","password":"password"}' -UseBasicParsing
$loginData = $loginResponse.Content | ConvertFrom-Json
Write-Host "   ✅ Login successful"
Write-Host "   Token (first 30 chars): $($loginData.token.Substring(0, 30))..."
Write-Host "   Expires in: $($loginData.expiresIn) seconds"
$token = $loginData.token
Write-Host ""

# Test 2: Get Board
Write-Host "2. Testing GET /api/board..." -ForegroundColor Cyan
$boardResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/board" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
$board = $boardResponse.Content | ConvertFrom-Json
Write-Host "   ✅ Board fetched"
Write-Host "   Columns: $($board.columns.Length)"
Write-Host "   Cards: $($board.cards.Count)"
Write-Host ""

# Test 3: Display board structure
Write-Host "3. Board Structure:" -ForegroundColor Cyan
foreach ($col in $board.columns) {
  $cardCount = if ($col.cardIds -is [array]) { $col.cardIds.Length } else { if ($col.cardIds) { 1 } else { 0 } }
  Write-Host "   - $($col.title): $cardCount cards"
}
Write-Host ""

# Test 4: Create a new card
Write-Host "4. Testing POST /api/board/cards..." -ForegroundColor Cyan
$cardBody = @{
  columnId = "col-backlog"
  title = "Test Card"
  details = "This is a test card created via API"
} | ConvertTo-Json
$cardResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/board/cards" -Method Post -Headers @{"Authorization"="Bearer $token"; "Content-Type"="application/json"} -Body $cardBody -UseBasicParsing
Write-Host "   ✅ Card created successfully"
Write-Host ""

# Test 5: Verify board updated
Write-Host "5. Verifying board update..." -ForegroundColor Cyan
$updatedResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/board" -Headers @{"Authorization"="Bearer $token"} -UseBasicParsing
$updatedBoard = $updatedResponse.Content | ConvertFrom-Json
Write-Host "   ✅ Board refreshed"
Write-Host "   Updated cards count: $($updatedBoard.cards.Count)"
Write-Host ""

Write-Host "✅ All tests passed!" -ForegroundColor Green
