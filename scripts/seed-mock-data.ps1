# Warm the API with mock metrics + recommendation refresh (PowerShell)
param(
    [string]$Api = "http://localhost:8000/api/v1",
    [string]$Scenario = "wasteful"
)

$ErrorActionPreference = "Stop"
Write-Host "==> POST $Api/metrics/collect?scenario=$Scenario"
Invoke-RestMethod -Uri "$Api/metrics/collect?scenario=$Scenario" -Method Post | Out-Null
Write-Host "==> POST $Api/recommendations/refresh?scenario=$Scenario"
Invoke-RestMethod -Uri "$Api/recommendations/refresh?scenario=$Scenario" -Method Post | Out-Null
Write-Host "==> Done."
