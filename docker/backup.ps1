Write-Host ""
Write-Host "======================================="
Write-Host " Dashboard Inteligente - Backup"
Write-Host "======================================="
Write-Host ""

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = "docker/backups/$timestamp"

New-Item -ItemType Directory -Force -Path $backupDir

$volumes = @(
  "dashboard-inteligente_influxdb-data",
  "dashboard-inteligente_grafana-data",
  "dashboard-inteligente_nodered-data",
  "dashboard-inteligente_mongodb-data"
)

foreach ($volume in $volumes) {
  Write-Host "Backup do volume: $volume"

  docker run --rm `
    -v ${volume}:/volume `
    -v ${PWD}/${backupDir}:/backup `
    alpine `
    tar -czf /backup/$volume.tar.gz -C /volume .
}

Copy-Item "docker-compose.yml" "$backupDir/docker-compose.yml"

Write-Host ""
Write-Host "Backup concluido em: $backupDir"