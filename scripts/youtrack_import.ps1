# YouTrack import helper (PowerShell)
# Usage: Update variables below, run to delete demo issues and import CSV
# Requires: YouTrack REST API token with admin permissions

$youtrackUrl = "https://your-youtrack.example.com"  # set to your instance
$apiToken = "<YOU_TRACK_TOKEN>"                    # set securely (do NOT commit token)
$projectId = "EMBEDNET"                            # target project
$csvPath = "docs\youtrack_import.csv"

# 1) Backup existing issues (optional): export via YouTrack API (not implemented here)
# 2) Delete demo issues: requires caution. This filters by summary containing 'demo' or 'sample'
$headers = @{ Authorization = "Bearer $apiToken"; Accept = 'application/json' }
$searchUrl = "$youtrackUrl/api/issues?query=project:%20$projectId%20%22demo%22&fields=id,summary";
# Fetch matching issues
try {
  $issues = Invoke-RestMethod -Uri $searchUrl -Headers $headers -Method Get
} catch { Write-Error "Failed to query YouTrack: $_"; exit 1 }

foreach ($i in $issues) {
  $id = $i.id
  Write-Output "Deleting issue $id: $($i.summary)"
  Invoke-RestMethod -Uri "$youtrackUrl/api/issues/$id" -Headers $headers -Method Delete
}

# 3) Import CSV: create issues from CSV rows
$rows = Import-Csv -Path $csvPath
foreach ($r in $rows) {
  $body = @{ project = $projectId; summary = $r.Summary; description = $r.Description; priority = $r.Priority } | ConvertTo-Json
  Invoke-RestMethod -Uri "$youtrackUrl/api/issues?fields=id,summary" -Headers $headers -Method Post -Body $body -ContentType 'application/json'
  Start-Sleep -Seconds 1
}

Write-Output "Import finished (or attempted). Check YouTrack UI for results."