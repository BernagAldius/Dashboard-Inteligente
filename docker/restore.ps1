param (
  [string]$backupFolder
)

if (-not $backupFolder) {
  Write-Host "Uso:"
  Write-Host ".\docker\restore.ps1 docker/backups/NOME_DA_PASTA"
  exit
}

if (!(Test-Path $backupFolder)) {
  Write-Host "A pasta de backup nao existe: $backupFolder"
  exit
}

Write-Host ""
Write-Host "======================================="
Write-Host " Dashboard Inteligente - Restore"
Write-Host "======================================="
Write-Host ""

Write-Host "A parar containers..."
docker compose down

$volumes = @(
  "dashboard-inteligente_influxdb-data",
  "dashboard-inteligente_grafana-data",
  "dashboard-inteligente_nodered-data",
  "dashboard-inteligente_mongodb-data"
)

foreach ($volume in $volumes) {
  $backupFile = "$backupFolder/$volume.tar.gz"

  if (Test-Path $backupFile) {
    Write-Host "A restaurar volume: $volume"

    docker volume create $volume | Out-Null

    docker run --rm `
      -v ${volume}:/volume `
      -v ${PWD}/${backupFolder}:/backup `
      alpine `
      sh -c "rm -rf /volume/* && tar -xzf /backup/$volume.tar.gz -C /volume"
  } else {
    Write-Host "Backup nao encontrado para: $volume"
  }
}

Write-Host ""
Write-Host "Restore concluido."
Write-Host "A iniciar containers..."
docker compose up -d