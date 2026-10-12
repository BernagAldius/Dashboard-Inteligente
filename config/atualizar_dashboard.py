import base64
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / "grafana" / ".env.grafana"
DASHBOARD = ROOT / "grafana" / "dashboards" / "intelligent-iot-dashboard.json"

env = dict(
    line.split("=", 1)
    for line in ENV.read_text(encoding="utf-8").splitlines()
    if "=" in line
)

username = env["GF_SECURITY_ADMIN_USER"]
password = env["GF_SECURITY_ADMIN_PASSWORD"]

url = (
    "http://localhost:3001/apis/dashboard.grafana.app/v2/"
    "namespaces/default/dashboards/adq2fx9"
)

credentials = base64.b64encode(
    f"{username}:{password}".encode()
).decode()

headers = {
    "Authorization": f"Basic {credentials}",
    "Content-Type": "application/json",
}

# Obter a versão atual para preservar os metadados.
request = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(request) as response:
    current = json.load(response)

# Carregar o JSON corrigido.
spec = json.loads(DASHBOARD.read_text(encoding="utf-8"))

# Atualizar apenas o conteúdo da dashboard.
current["spec"] = spec

request = urllib.request.Request(
    url,
    data=json.dumps(current).encode("utf-8"),
    headers=headers,
    method="PUT",
)

with urllib.request.urlopen(request) as response:
    result = json.load(response)

print("[OK] Dashboard v2 atualizada com sucesso.")
print("[OK] Elementos:", len(result["spec"]["elements"]))