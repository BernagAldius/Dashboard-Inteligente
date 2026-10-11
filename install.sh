
#!/usr/bin/env bash

# ============================================
#       DASHBOARD INTELIGENTE IoT
#       Instalador para Linux (Debian)
# ============================================

# Interromper em caso de erro ou variável não definida
set -euo pipefail

# Identificar a pasta onde está localizado o instalador
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# Executar os comandos a partir da raiz do projeto
cd "$PROJECT_ROOT"

echo ""
echo "============================================"
echo "       DASHBOARD INTELIGENTE IoT"
echo "============================================"
echo ""
echo "Instalador e verificador de requisitos - Linux"
echo ""

# Verificar o sistema operativo
echo "A verificar sistema operativo..."

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "[ERRO] Este instalador destina-se a sistemas Linux."
    exit 1
fi

# Identificar a distribuição Linux
if [[ -f /etc/os-release ]]; then
    source /etc/os-release
    echo "Sistema operativo: ${PRETTY_NAME:-Linux}"
else
    echo "[AVISO] Nao foi possivel identificar a distribuicao."
fi

# Identificar a arquitetura
ARQUITETURA="$(uname -m)"
echo "Arquitetura: $ARQUITETURA"
echo ""

echo "[OK] Verificacao inicial concluida."


# ============================================
# VERIFICAR PERMISSOES DE ADMINISTRADOR
# ============================================

echo ""
echo "A verificar permissoes de administrador..."

if ! command -v sudo >/dev/null 2>&1; then
    echo "[ERRO] O comando sudo nao foi encontrado."
    echo "[INFO] E necessario configurar permissoes administrativas."
    exit 1
fi

if [[ "$EUID" -eq 0 ]]; then
    echo "[ERRO] Execute este instalador com um utilizador normal, nao como root."
    exit 1
fi

echo "[INFO] A verificar autorizacao sudo..."

if sudo -v; then
    echo "[OK] Permissoes administrativas confirmadas."
else
    echo "[ERRO] Nao foi possivel obter permissoes administrativas."
    exit 1
fi


# ============================================
# VERIFICAR DOCKER E DOCKER COMPOSE
# ============================================

echo ""
echo "A verificar Docker..."

DOCKER_INSTALADO=false
COMPOSE_INSTALADO=false
DOCKER_OPERACIONAL=false

if command -v docker >/dev/null 2>&1; then
    DOCKER_INSTALADO=true
    echo "[OK] Docker encontrado: $(docker --version)"
else
    echo "[FALTA] Docker nao foi encontrado."
fi

echo ""
echo "A verificar Docker Compose..."

if [[ "$DOCKER_INSTALADO" == true ]] &&
   docker compose version >/dev/null 2>&1; then
    COMPOSE_INSTALADO=true
    echo "[OK] Docker Compose encontrado: $(docker compose version --short)"
else
    echo "[FALTA] Docker Compose nao foi encontrado."
fi

echo ""
echo "A verificar funcionamento do Docker Engine..."

if [[ "$DOCKER_INSTALADO" == true ]] &&
   docker info >/dev/null 2>&1; then
    DOCKER_OPERACIONAL=true
    echo "[OK] Docker Engine esta operacional."
else
    echo "[AVISO] Docker Engine nao esta disponivel para este utilizador."
fi


# ============================================
# VERIFICAR COMPATIBILIDADE COM DEBIAN
# ============================================

echo ""
echo "A verificar compatibilidade para instalacao do Docker..."

if [[ "$DOCKER_INSTALADO" != true ||
      "$COMPOSE_INSTALADO" != true ]]; then

    if [[ "${ID:-}" != "debian" ]]; then
        echo "[ERRO] A instalacao automatica do Docker esta preparada para Debian."
        exit 1
    fi

    if [[ "${VERSION_CODENAME:-}" != "trixie" ]]; then
        echo "[ERRO] Esta versao do instalador foi preparada para Debian 13 (trixie)."
        exit 1
    fi

    if [[ "$ARQUITETURA" != "x86_64" ]]; then
        echo "[ERRO] Esta versao do instalador requer arquitetura x86_64."
        exit 1
    fi

    if ! command -v apt-get >/dev/null 2>&1; then
        echo "[ERRO] O gestor de pacotes apt-get nao foi encontrado."
        exit 1
    fi

    echo "[OK] Debian 13 (trixie), arquitetura x86_64, compatível."
    echo "[INFO] O sistema esta preparado para a instalacao automatica do Docker."
else
    echo "[OK] Docker e Docker Compose ja estao instalados."
    echo "[INFO] Nao sera necessario configurar os repositorios do Docker."
fi

# ============================================
# VERIFICAR PACOTES DOCKER CONFLITUANTES
# ============================================

if [[ "$DOCKER_INSTALADO" != true ||
      "$COMPOSE_INSTALADO" != true ]]; then

    echo ""
    echo "A verificar possiveis conflitos com pacotes Docker..."

    PACOTES_CONFLITUANTES=(
        docker.io
        docker-compose
        docker-compose-v2
        docker-doc
        podman-docker
        containerd
        runc
    )

    PACOTES_ENCONTRADOS=()

    for pacote in "${PACOTES_CONFLITUANTES[@]}"; do

        if dpkg-query -W -f='${Status}' "$pacote" 2>/dev/null |
           grep -qx "install ok installed"; then

            PACOTES_ENCONTRADOS+=("$pacote")
        fi

    done

    if [[ "${#PACOTES_ENCONTRADOS[@]}" -gt 0 ]]; then

        echo ""
        echo "[AVISO] Foram encontrados pacotes potencialmente conflituantes:"
        printf ' - %s\n' "${PACOTES_ENCONTRADOS[@]}"

        echo ""
        echo "[ERRO] A instalacao automatica foi interrompida."
        echo "[INFO] Os pacotes existentes nao foram alterados."
        echo "[INFO] Reveja os conflitos antes de continuar."

        exit 1

    else
        echo "[OK] Nao foram encontrados pacotes Docker conflituantes."
    fi

fi

# ============================================
# CONFIGURAR REPOSITORIO OFICIAL DO DOCKER
# ============================================

if [[ "$DOCKER_INSTALADO" != true ||
      "$COMPOSE_INSTALADO" != true ]]; then

    echo ""
    echo "A preparar repositorio oficial do Docker..."

    # Instalar dependencias necessarias
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl

    # Criar pasta para as chaves dos repositorios
    sudo install -m 0755 -d /etc/apt/keyrings

    # Obter a chave oficial do Docker
    sudo curl -fsSL \
        https://download.docker.com/linux/debian/gpg \
        -o /etc/apt/keyrings/docker.asc

    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Identificar a arquitetura utilizada pelo apt
    ARQUITETURA_APT="$(dpkg --print-architecture)"

    # Configurar o repositorio oficial
    printf '%s\n' \
        "Types: deb" \
        "URIs: https://download.docker.com/linux/debian" \
        "Suites: ${VERSION_CODENAME}" \
        "Components: stable" \
        "Architectures: ${ARQUITETURA_APT}" \
        "Signed-By: /etc/apt/keyrings/docker.asc" |
        sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null

    echo "[OK] Repositorio oficial do Docker configurado."
fi


# ============================================
# INSTALAR DOCKER ENGINE E DOCKER COMPOSE
# ============================================

if [[ "$DOCKER_INSTALADO" != true ||
      "$COMPOSE_INSTALADO" != true ]]; then

    echo ""
    echo "A instalar Docker Engine e Docker Compose..."

    # Atualizar a lista de pacotes
    sudo apt-get update

    # Instalar os componentes oficiais do Docker
    sudo apt-get install -y \
        docker-ce \
        docker-ce-cli \
        containerd.io \
        docker-buildx-plugin \
        docker-compose-plugin

    echo "[OK] Instalacao dos pacotes Docker concluida."

    # Iniciar o Docker e ativar o arranque automatico
    echo ""
    echo "A iniciar Docker Engine..."

    sudo systemctl enable --now docker

    # Confirmar as versoes instaladas
    docker --version
    docker compose version

    echo "[OK] Docker Engine e Docker Compose instalados."

else
    echo ""
    echo "[OK] Docker e Docker Compose ja estavam instalados."
    echo "[INFO] A instalacao existente sera reutilizada."
fi


# ============================================
# GARANTIR QUE O DOCKER ENGINE ESTA ATIVO
# ============================================

echo ""
echo "A verificar o servico Docker..."

if command -v systemctl >/dev/null 2>&1; then

    if systemctl is-active --quiet docker; then
        echo "[OK] O servico Docker ja esta ativo."
    else
        echo "[INFO] O servico Docker esta parado."
        echo "[INFO] A tentar iniciar Docker Engine..."

        if sudo systemctl start docker; then
            echo "[OK] Docker Engine iniciado com sucesso."
        else
            echo "[ERRO] Nao foi possivel iniciar Docker Engine."
            exit 1
        fi
    fi

else
    echo "[AVISO] systemctl nao esta disponivel."
    echo "[INFO] O acesso ao Docker sera verificado a seguir."
fi

# ============================================
# VERIFICAR PERMISSOES DE ACESSO AO DOCKER
# ============================================

echo ""
echo "A verificar acesso ao Docker Engine..."

# Utilizar Docker sem sudo quando possivel.
# Caso contrario, executar Docker atraves de sudo.
DOCKER_CMD=(docker)

if docker info >/dev/null 2>&1; then
    echo "[OK] O utilizador atual tem acesso ao Docker."

elif sudo docker info >/dev/null 2>&1; then
    DOCKER_CMD=(sudo docker)
    echo "[OK] Docker operacional com permissoes administrativas."
    echo "[INFO] Os comandos Docker serao executados atraves de sudo."

else
    echo "[ERRO] Nao foi possivel comunicar com o Docker Engine."
    echo "[INFO] Verifique se o servico Docker esta ativo."
    exit 1
fi

echo ""
echo "A confirmar Docker Compose..."

if "${DOCKER_CMD[@]}" compose version >/dev/null 2>&1; then
    echo "[OK] Docker Compose esta operacional."
else
    echo "[ERRO] Docker Compose nao esta disponivel."
    exit 1
fi


# ============================================
# VERIFICAR PYTHON E GIT
# ============================================

echo ""
echo "A verificar Python 3..."

if command -v python3 >/dev/null 2>&1; then
    echo "[OK] Python encontrado: $(python3 --version)"
    echo "[INFO] Sera utilizada a instalacao existente."
else
    echo "[FALTA] Python 3 nao foi encontrado."
    echo "[INFO] A instalar Python 3..."

    sudo apt-get update
    sudo apt-get install -y python3

    echo "[OK] Python instalado: $(python3 --version)"
fi

echo ""
echo "A verificar Git..."

if command -v git >/dev/null 2>&1; then
    echo "[OK] Git encontrado: $(git --version)"
else
    echo "[FALTA] Git nao foi encontrado."
    echo "[INFO] A instalar Git..."

    sudo apt-get update
    sudo apt-get install -y git

    echo "[OK] Git instalado: $(git --version)"
fi


# ============================================
# VERIFICAR FICHEIROS OBRIGATORIOS DO PROJETO
# ============================================

echo ""
echo "A verificar ficheiros do projeto..."

FICHEIROS_OBRIGATORIOS=(
    "docker-compose.yml"
    "config/configuracao_utilizador.txt"
    "config/gerar_config.py"
)

FICHEIROS_OK=true

for ficheiro in "${FICHEIROS_OBRIGATORIOS[@]}"; do
    if [[ -f "$PROJECT_ROOT/$ficheiro" ]]; then
        echo "[OK] $ficheiro"
    else
        echo "[FALTA] $ficheiro"
        FICHEIROS_OK=false
    fi
done

if [[ "$FICHEIROS_OK" != true ]]; then
    echo ""
    echo "[ERRO] Existem ficheiros obrigatorios em falta."
    echo "[INFO] Confirme que o instalador esta na raiz do projeto."
    exit 1
fi

echo ""
echo "[OK] Todos os ficheiros obrigatorios foram encontrados."

# ============================================
# VALIDAR DOCKER COMPOSE
# ============================================

# Preparar configuracoes de ambiente
echo ""
echo "A preparar configuracoes de ambiente..."

if [[ ! -f "config/preparar_ambiente.py" ]]; then
    echo "[ERRO] O ficheiro config/preparar_ambiente.py nao foi encontrado."
    exit 1
fi

if ! python3 config/preparar_ambiente.py; then
    echo "[ERRO] Falha ao preparar configuracoes de ambiente."
    exit 1
fi

echo "[OK] Preparacao do ambiente concluida."

echo ""
echo "A validar docker-compose.yml..."

if "${DOCKER_CMD[@]}" compose config --quiet; then
    echo "[OK] Configuracao Docker Compose valida."
else
    echo "[ERRO] O ficheiro docker-compose.yml contem erros."
    echo "[INFO] Corrija a configuracao antes de iniciar os servicos."
    exit 1
fi


# ============================================
# CONFIGURACAO DA DASHBOARD INTELIGENTE
# ============================================

echo ""
echo "============================================"
echo "       CONFIGURACAO DA DASHBOARD"
echo "============================================"
echo ""

read -r -p "Pretende abrir o ficheiro de configuracao? (S/N): " RESPOSTA_CONFIG

if [[ "$RESPOSTA_CONFIG" =~ ^[Ss]$ ]]; then

    echo ""
    echo "[INFO] A abrir configuracao_utilizador.txt..."

    # Procurar um editor de texto disponivel no Linux
    if command -v mousepad >/dev/null 2>&1; then
        mousepad "$PROJECT_ROOT/config/configuracao_utilizador.txt"
    elif command -v leafpad >/dev/null 2>&1; then
        leafpad "$PROJECT_ROOT/config/configuracao_utilizador.txt"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$PROJECT_ROOT/config/configuracao_utilizador.txt"
    else
        echo "[ERRO] Nao foi encontrado um editor de texto."
        exit 1
    fi

    echo ""
    read -r -p "Depois de guardar e fechar o ficheiro, pressione Enter para continuar..."


else
    echo "[INFO] Configuracao atual sera mantida."
fi


# Validar e aplicar a configuracao, mesmo sem edicao do TXT
echo ""
echo "[INFO] A validar e aplicar a configuracao..."

if python3 "$PROJECT_ROOT/config/gerar_config.py"; then
    echo "[OK] Configuracao aplicada com sucesso."
else
    echo "[ERRO] A configuracao nao foi aplicada."
    echo "[INFO] Corrija configuracao_utilizador.txt e execute novamente o instalador."
    exit 1
fi


# ============================================
# ARRANQUE DA DASHBOARD INTELIGENTE
# ============================================

echo ""
echo "============================================"
echo "         ARRANQUE DA DASHBOARD"
echo "============================================"
echo ""

read -r -p "Pretende iniciar a Dashboard Inteligente? (S/N): " RESPOSTA_ARRANQUE

if [[ "$RESPOSTA_ARRANQUE" =~ ^[Ss]$ ]]; then

    echo ""
    echo "[INFO] A validar docker-compose.yml..."

    if ! "${DOCKER_CMD[@]}" compose config --quiet; then
        echo "[ERRO] A configuracao Docker Compose nao e valida."
        exit 1
    fi

    echo "[OK] docker-compose.yml valido."
    echo ""
    echo "[INFO] A construir e iniciar os servicos..."

    # --build permite construir as imagens locais numa maquina limpa.
    if ! "${DOCKER_CMD[@]}" compose up -d --build; then
        echo "[ERRO] Ocorreu um erro durante o arranque da dashboard."
        exit 1
    fi

    echo ""
    echo "[INFO] A verificar o estado dos servicos..."
    "${DOCKER_CMD[@]}" compose ps

    # Obter os nomes dos servicos definidos no Compose
    mapfile -t SERVICOS_ESPERADOS < <(
        "${DOCKER_CMD[@]}" compose config --services
    )

    mapfile -t SERVICOS_ATIVOS < <(
        "${DOCKER_CMD[@]}" compose ps --services --filter "status=running"
    )

    SERVICOS_EM_FALTA=()

    for servico in "${SERVICOS_ESPERADOS[@]}"; do
        encontrado=false

        for ativo in "${SERVICOS_ATIVOS[@]}"; do
            if [[ "$servico" == "$ativo" ]]; then
                encontrado=true
                break
            fi
        done

        if [[ "$encontrado" == false ]]; then
            SERVICOS_EM_FALTA+=("$servico")
        fi
    done

    echo ""

    if [[ "${#SERVICOS_EM_FALTA[@]}" -eq 0 ]]; then

        echo "[OK] Todos os servicos estao em execucao."
        echo "[INFO] Servicos ativos: ${#SERVICOS_ATIVOS[@]} de ${#SERVICOS_ESPERADOS[@]}"

        echo ""
        echo "============================================"
        echo "       DASHBOARD PRONTA A UTILIZAR"
        echo "============================================"
        echo ""
        echo "Grafana:  http://localhost:3001"
        echo "Node-RED: http://localhost:1880"
        echo ""
        echo "[INFO] O Grafana e a dashboard principal."
        echo "[INFO] A interface Vue permanece apenas como prototipo anterior."
        echo ""

        read -r -p "Pretende abrir o Grafana no browser? (S/N): " RESPOSTA_GRAFANA

        if [[ "$RESPOSTA_GRAFANA" =~ ^[Ss]$ ]]; then
            if command -v xdg-open >/dev/null 2>&1; then
                xdg-open "http://localhost:3001" >/dev/null 2>&1 || true
            else
                echo "[INFO] Abra manualmente http://localhost:3001"
            fi
        fi

    else
        echo "[ERRO] Nem todos os servicos estao em execucao."
        echo "[INFO] Servicos em falta: ${SERVICOS_EM_FALTA[*]}"
        exit 1
    fi

else
    echo "[INFO] A dashboard nao sera iniciada."
fi