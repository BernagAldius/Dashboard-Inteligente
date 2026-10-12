import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_JSON = ROOT / "grafana" / "dashboards" / "intelligent-iot-dashboard.json"
GRAFANA_ENV = ROOT / "grafana" / ".env.grafana"

GRAFANA_URL = "http://localhost:3001"
DASHBOARD_UID = "adq2fx9"

API_URL = (
    f"{GRAFANA_URL}/apis/dashboard.grafana.app/v2/"
    "namespaces/default/dashboards"
)


def obter_credenciais():
    """Lê as credenciais administrativas geradas pelo instalador."""

    if not GRAFANA_ENV.exists():
        raise RuntimeError("Ficheiro de credenciais do Grafana não encontrado.")

    valores = {}

    for linha in GRAFANA_ENV.read_text(encoding="utf-8").splitlines():
        if "=" in linha and not linha.lstrip().startswith("#"):
            chave, valor = linha.split("=", 1)
            valores[chave.strip()] = valor.strip()

    utilizador = valores.get("GF_SECURITY_ADMIN_USER")
    password = valores.get("GF_SECURITY_ADMIN_PASSWORD")

    if not utilizador or not password:
        raise RuntimeError("Credenciais administrativas do Grafana incompletas.")

    return utilizador, password


def pedido_api(url, metodo, credenciais, dados=None):
    """Executa um pedido autenticado à API do Grafana."""

    utilizador, password = credenciais
    autenticacao = base64.b64encode(
        f"{utilizador}:{password}".encode("utf-8")
    ).decode("ascii")

    cabecalhos = {
        "Authorization": f"Basic {autenticacao}",
        "Accept": "application/json",
    }

    if dados is not None:
        cabecalhos["Content-Type"] = "application/json"

    pedido = urllib.request.Request(
        url,
        data=dados,
        headers=cabecalhos,
        method=metodo,
    )

    return urllib.request.urlopen(pedido, timeout=10)


def main():
    if not DASHBOARD_JSON.exists():
        raise RuntimeError("Ficheiro JSON da dashboard não encontrado.")

    credenciais = obter_credenciais()

    print("[INFO] A aguardar pela API do Grafana...")

    for tentativa in range(60):
        try:
            with pedido_api(f"{GRAFANA_URL}/api/health", "GET", credenciais):
                break
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2)
    else:
        raise RuntimeError("O Grafana não ficou disponível dentro do tempo limite.")

    print("[OK] API do Grafana disponível.")

    url_dashboard = f"{API_URL}/{DASHBOARD_UID}"

    try:
        with pedido_api(url_dashboard, "GET", credenciais):
            print("[OK] Dashboard já existe. Importação dispensada.")
            return
    except urllib.error.HTTPError as erro:
        if erro.code != 404:
            raise

    especificacao = json.loads(DASHBOARD_JSON.read_text(encoding="utf-8"))

    recurso = {
        "apiVersion": "dashboard.grafana.app/v2",
        "kind": "Dashboard",
        "metadata": {
            "name": DASHBOARD_UID,
            "namespace": "default",
        },
        "spec": especificacao,
    }

    dados = json.dumps(recurso).encode("utf-8")

    with pedido_api(API_URL, "POST", credenciais, dados):
        print("[OK] Dashboard v2 importada com sucesso.")


if __name__ == "__main__":
    try:
        main()
    except Exception as erro:
        print(f"[ERRO] Falha na importação da dashboard: {erro}", file=sys.stderr)
        sys.exit(1)