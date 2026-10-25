
import json
from copy import deepcopy
from pathlib import Path

ficheiro = Path("grafana/dashboards/intelligent-iot-dashboard.json")
dados = json.loads(ficheiro.read_text(encoding="utf-8"))

variaveis = dados["variables"]

if any(v["spec"]["name"] == "chart_type" for v in variaveis):
    print("[OK] A variável chart_type já existe.")
else:
    unidade = next(
        v for v in variaveis
        if v["spec"]["name"] == "unit"
    )

    nova = deepcopy(unidade)

    nova["spec"]["name"] = "chart_type"
    nova["spec"]["label"] = "Tipo de Gráfico"
    nova["spec"]["hide"] = "hideVariable"
    nova["spec"]["current"] = {
        "text": "linha",
        "value": "linha"
    }

    consulta = nova["spec"]["query"]["spec"]["infinityQuery"]
    consulta["columns"] = [
        {
            "selector": "chart_type",
            "text": "__value",
            "type": "string"
        }
    ]

    variaveis.append(nova)

    ficheiro.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print("[OK] Variável chart_type adicionada.")
