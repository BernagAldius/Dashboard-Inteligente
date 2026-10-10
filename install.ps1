# Diretório onde se encontra este instalador
$projectRoot = $PSScriptRoot

# Garantir que todos os comandos são executados a partir da raiz do projeto
Set-Location $projectRoot

Clear-Host

Write-Host ""
Write-Host "============================================"
Write-Host "      DASHBOARD INTELIGENTE IoT"
Write-Host "============================================"
Write-Host ""
Write-Host "Instalador e verificador de requisitos"
Write-Host ""

Write-Host "A verificar sistema operativo..."

$windows = Get-CimInstance Win32_OperatingSystem
$arquitetura = $env:PROCESSOR_ARCHITECTURE

Write-Host "Windows: $($windows.Caption)"
Write-Host "Versao: $($windows.Version)"
Write-Host "Arquitetura: $arquitetura"
Write-Host ""

$requisitosOK = $true

$wingetCommand = Get-Command winget -ErrorAction SilentlyContinue

Write-Host "A verificar Docker Desktop..."

$dockerDesktopPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"

if (Test-Path $dockerDesktopPath) {
    $dockerDesktopVersion = (Get-Item $dockerDesktopPath).VersionInfo.ProductVersion

    Write-Host "[OK] Docker Desktop encontrado: $dockerDesktopVersion"
    Write-Host "[INFO] Sera utilizada a instalacao existente do Docker Desktop."
}
else {
    Write-Host "[FALTA] Docker Desktop nao foi encontrado."
    $requisitosOK = $false

    if ($wingetCommand) {
        Write-Host "Docker Desktop pode ser instalado automaticamente."
        $respostaDocker = Read-Host "Pretende instalar Docker Desktop? (S/N)"

        if ($respostaDocker -match "^[Ss]$") {
            Write-Host "[INFO] A instalar Docker Desktop..."

            winget install --id Docker.DockerDesktop -e --accept-package-agreements --accept-source-agreements

            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] Instalacao do Docker Desktop concluida."
                Write-Host "[INFO] Pode ser necessario reiniciar o computador antes de continuar."
                Write-Host "[INFO] Depois disso, execute novamente este instalador."
            }
            else {
                Write-Host "[ERRO] Nao foi possivel instalar Docker Desktop automaticamente."
            }
        }
        else {
            Write-Host "[INFO] Instalacao do Docker Desktop nao selecionada."
        }
    }
    else {
        Write-Host "[AVISO] Nao e possivel instalar Docker Desktop automaticamente sem winget."
    }
}

Write-Host ""
Write-Host "A verificar funcionamento do Docker..."

$dockerCommand = Get-Command docker -ErrorAction SilentlyContinue

if ($dockerCommand) {
    docker info *> $null
}
else {
    $global:LASTEXITCODE = 1
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Docker esta operacional."
}
else {
    if (Test-Path $dockerDesktopPath) {
        Write-Host "[AVISO] Docker Desktop esta instalado, mas o Docker nao esta operacional."

        $respostaIniciarDocker = Read-Host "Pretende iniciar Docker Desktop? (S/N)"

        if ($respostaIniciarDocker -match "^[Ss]$") {
            Write-Host "[INFO] A iniciar Docker Desktop..."
            Start-Process $dockerDesktopPath

            Write-Host "[INFO] Docker Desktop foi iniciado."
            Write-Host "[INFO] Aguarde ate o Docker Engine ficar disponivel e execute novamente o instalador."
        }
        else {
            Write-Host "[INFO] Docker Desktop nao foi iniciado."
        }

        $requisitosOK = $false
    }
    else {
        Write-Host "[FALTA] Docker ainda nao esta disponivel."
        $requisitosOK = $false
    }
}

Write-Host ""
Write-Host "A verificar Docker Compose..."

if ($dockerCommand) {
    docker compose version *> $null

    if ($LASTEXITCODE -eq 0) {
        $composeVersion = docker compose version --short
        Write-Host "[OK] Docker Compose encontrado: $composeVersion"
    }
    else {
        Write-Host "[FALTA] Docker Compose nao foi encontrado."
        $requisitosOK = $false
    }
}
else {
    Write-Host "[FALTA] Docker Compose nao pode ser verificado porque Docker nao esta disponivel."
    $requisitosOK = $false
}

Write-Host ""
Write-Host ""
Write-Host "A verificar WSL..."

$wslCommand = Get-Command wsl -ErrorAction SilentlyContinue

if ($wslCommand) {
    $wslStatus = wsl --status 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] WSL encontrado."

        if ($wslStatus -match "2") {
            Write-Host "[OK] WSL 2 esta disponivel."
        }
        else {
            Write-Host "[AVISO] WSL encontrado, mas nao foi possivel confirmar WSL 2."
            $requisitosOK = $false
        }
    }
    else {
        Write-Host "[AVISO] WSL foi encontrado, mas nao esta corretamente configurado."
        $requisitosOK = $false
    }
}
else {
    Write-Host "[FALTA] WSL nao foi encontrado."
    $requisitosOK = $false
}

Write-Host ""
Write-Host "A verificar Python..."

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue

if ($pythonCommand) {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python encontrado: $pythonVersion"
    Write-Host "[INFO] Sera utilizada a instalacao existente do Python."
}
else {
    Write-Host "[FALTA] Python nao foi encontrado."
    $requisitosOK = $false

    if ($wingetCommand) {
        Write-Host "Python pode ser instalado automaticamente."
        $respostaPython = Read-Host "Pretende instalar Python? (S/N)"

        if ($respostaPython -match "^[Ss]$") {
    Write-Host "[INFO] A instalar Python..."

    winget install --id Python.Python.3.14 -e --accept-package-agreements --accept-source-agreements

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Instalacao de Python concluida."
        Write-Host "[INFO] Pode ser necessario reiniciar o terminal antes de utilizar Python."
        Write-Host "[INFO] Depois disso, execute novamente este instalador."
    }
    else {
        Write-Host "[ERRO] Nao foi possivel instalar Python automaticamente."
    }
}
else {
    Write-Host "[INFO] Instalacao de Python nao selecionada."
}
    }
    else {
        Write-Host "[AVISO] Nao e possivel instalar Python automaticamente sem winget."
    }
}

Write-Host ""
Write-Host ""
Write-Host "A verificar ficheiros do projeto..."

$ficheirosObrigatorios = @(
    "docker-compose.yml",
    "config\configuracao_utilizador.txt",
    "config\gerar_config.py"
)

foreach ($ficheiro in $ficheirosObrigatorios) {
    if (Test-Path $ficheiro) {
        Write-Host "[OK] $ficheiro"
    }
    else {
        Write-Host "[FALTA] $ficheiro"
        $requisitosOK = $false
    }
}

Write-Host ""

Write-Host "A verificar configurador da dashboard..."

if ($pythonCommand -and (Test-Path "config\gerar_config.py")) {
    Write-Host "[OK] Configurador Python disponivel."
}
else {
    Write-Host "[FALTA] O configurador nao pode ser executado."
    $requisitosOK = $false
}

Write-Host ""

Write-Host ""
Write-Host "A verificar instalacao existente dos servicos da dashboard..."

Write-Host "[INFO] Os componentes da dashboard sao geridos pelo Docker Compose."
Write-Host "[INFO] Nao e necessaria a instalacao individual de Grafana, Node-RED, InfluxDB, Mosquitto, MongoDB ou FIWARE Orion no Windows."

if ($dockerCommand -and $composeVersion) {
    docker compose config --quiet 2>$null
    $composeConfigValido = ($LASTEXITCODE -eq 0)
}
else {
    $composeConfigValido = $false
}

if ($dockerCommand -and $composeVersion -and -not $composeConfigValido) {
    Write-Host "[ERRO] A configuracao Docker Compose nao e valida."
    Write-Host "[INFO] Verifique o ficheiro docker-compose.yml."
    $requisitosOK = $false
}
elseif (-not $dockerCommand -or -not $composeVersion) {
    Write-Host "[INFO] A instalacao dos servicos nao pode ser analisada sem Docker e Docker Compose."
}

if ($composeConfigValido) {
    $servicosEsperados = @(docker compose config --services 2>$null)
    $servicosExistentes = @(docker compose ps -a --services 2>$null)

    $servicosAtivos = @(
        docker compose ps --services --filter "status=running" 2>$null |
        Where-Object { $_ -and $_ -in $servicosEsperados }
    )

    $servicosEmFalta = @(
    $servicosEsperados | Where-Object { $_ -notin $servicosExistentes }
    )
    $servicosParados = @(
    $servicosExistentes | Where-Object { $_ -notin $servicosAtivos }
    )

    if ($servicosExistentes.Count -eq 0) {
    Write-Host "[INFO] Ainda nao existem contentores da Dashboard Inteligente."
    Write-Host "[INFO] Os $($servicosEsperados.Count) servicos serao criados pelo Docker Compose no primeiro arranque."
    }
    elseif ($servicosEmFalta.Count -eq 0) {
    Write-Host "[OK] A instalacao Docker existente esta completa."
    Write-Host "[INFO] Servicos encontrados: $($servicosExistentes.Count) de $($servicosEsperados.Count)"
    Write-Host "[INFO] Servicos atualmente em execucao: $($servicosAtivos.Count) de $($servicosEsperados.Count)"
    if ($servicosAtivos.Count -eq $servicosEsperados.Count) {
        Write-Host "[OK] Todos os servicos existentes estao em execucao."
    }
    elseif ($servicosAtivos.Count -eq 0) {
        Write-Host "[INFO] Os servicos existentes encontram-se parados."
    }
    else {
        Write-Host "[INFO] Apenas parte dos servicos existentes esta em execucao."
        Write-Host "[INFO] Servicos parados: $($servicosParados -join ', ')"
    }

    Write-Host "[INFO] A configuracao Docker existente sera reutilizada."
    }
    else {
    Write-Host "[AVISO] Foi encontrada uma instalacao Docker parcial."
    Write-Host "[INFO] Servicos encontrados: $($servicosExistentes.Count) de $($servicosEsperados.Count)"
    Write-Host "[INFO] Servicos em falta: $($servicosEmFalta -join ', ')"
    Write-Host "[INFO] Os servicos em falta poderao ser criados no proximo arranque."
    }

}

Write-Host ""

Write-Host "A verificar Git (opcional)..."

$gitCommand = Get-Command git -ErrorAction SilentlyContinue

if ($gitCommand) {
    $gitVersion = git --version
    Write-Host "[OK] Git encontrado: $gitVersion"
}
else {
    Write-Host "[INFO] Git nao foi encontrado."
    Write-Host "       Git e opcional e nao e necessario para executar a dashboard."
}

Write-Host ""
Write-Host "A verificar Windows Package Manager..."

if ($wingetCommand) {
    $wingetVersion = winget --version
    Write-Host "[OK] winget encontrado: $wingetVersion"
}
else {
    Write-Host "[AVISO] winget nao foi encontrado."
    Write-Host "        A instalacao automatica de alguns requisitos podera nao estar disponivel."
}

Write-Host ""

Write-Host ""
Write-Host "============================================"
Write-Host "           RESUMO DOS REQUISITOS"
Write-Host "============================================"

if ($requisitosOK) {
    Write-Host "[OK] Todos os requisitos obrigatorios foram encontrados."
}
else {
    Write-Host "[ATENCAO] Existem requisitos obrigatorios em falta."
}

Write-Host ""
if ($requisitosOK) {
    Write-Host "============================================"
    Write-Host "           CONFIGURACAO DA DASHBOARD"
    Write-Host "============================================"
    Write-Host ""

    $respostaConfig = Read-Host "Pretende abrir o ficheiro de configuracao? (S/N)"

    if ($respostaConfig -match "^[Ss]$") {
        Write-Host "[INFO] A abrir configuracao_utilizador.txt..."
        Start-Process notepad.exe "config\configuracao_utilizador.txt" -Wait
        Write-Host ""
        Write-Host "[INFO] A validar e aplicar a configuracao..."

        python "config\gerar_config.py"

        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "[OK] Configuracao aplicada com sucesso."
        }
        else {
            Write-Host ""
            Write-Host "[ERRO] A configuracao nao foi aplicada."
            Write-Host "[INFO] Corrija o ficheiro configuracao_utilizador.txt e execute novamente o instalador."
            $requisitosOK = $false
        }
    }
    else {
        Write-Host "[INFO] Configuracao atual sera mantida."
    }

    Write-Host ""
}
if ($requisitosOK) {
    Write-Host "============================================"
    Write-Host "           ARRANQUE DA DASHBOARD"
    Write-Host "============================================"
    Write-Host ""

    $respostaArranque = Read-Host "Pretende iniciar a Dashboard Inteligente? (S/N)"

    if ($respostaArranque -match "^[Ss]$") {
        Write-Host "[INFO] Arranque da dashboard selecionado."
        Write-Host "[INFO] A validar docker-compose.yml..."

        docker compose config --quiet

        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] docker-compose.yml valido."
            Write-Host ""
            Write-Host "[INFO] A iniciar os servicos da Dashboard Inteligente..."

            docker compose up -d

            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "[OK] Comando de arranque concluido com sucesso."

                Write-Host ""
                Write-Host "[INFO] A verificar estado dos servicos..."

                docker compose ps

                Write-Host ""
                Write-Host "[INFO] A confirmar servicos em execucao..."

                $servicosEsperados = @(docker compose config --services)
                $servicosAtivos = @(
                    docker compose ps --services --filter "status=running" 2>$null |
                    Where-Object {$_ -and $_ -in $servicosEsperados}
                )

                $faltamServicos = @(
                    $servicosEsperados | Where-Object { $_ -notin $servicosAtivos }
                )

                if ($faltamServicos.Count -eq 0) {
                    Write-Host "[OK] Todos os servicos da dashboard estao em execucao."

                    Write-Host ""
                    Write-Host "============================================"
                    Write-Host "        DASHBOARD PRONTA A UTILIZAR"
                    Write-Host "============================================"
                    Write-Host ""
                    Write-Host "Grafana:  http://localhost:3001"
                    Write-Host "Node-RED: http://localhost:1880"
                    Write-Host ""
                    Write-Host "[INFO] O Grafana e a dashboard principal."
                    Write-Host "[INFO] A antiga interface Vue permanece no projeto apenas como prototipo de uma fase anterior."
                    Write-Host ""

                    $respostaGrafana = Read-Host "Pretende abrir o Grafana no browser? (S/N)"

                    if ($respostaGrafana -match "^[Ss]$") {
                        Write-Host "[INFO] A abrir Grafana..."
                        Start-Process "http://localhost:3001"
                    }
                    else {
                        Write-Host "[INFO] Grafana nao sera aberto automaticamente."
                    }
                }
                else {
                    Write-Host "[ERRO] Nem todos os servicos estao em execucao."
                    Write-Host "[INFO] Servicos em falta: $($faltamServicos -join ', ')"
                    $requisitosOK = $false
                }
            }
            else {
                Write-Host ""
                Write-Host "[ERRO] Ocorreu um erro durante o arranque da dashboard."
                $requisitosOK = $false
            }
        }
        else {
            Write-Host "[ERRO] docker-compose.yml contem erros."
            Write-Host "[INFO] A dashboard nao sera iniciada."
            $requisitosOK = $false
        }
    }
    else {
        Write-Host "[INFO] A dashboard nao sera iniciada."
    }

    Write-Host ""
}