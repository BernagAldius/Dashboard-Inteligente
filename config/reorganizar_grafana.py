
import json
from pathlib import Path

ficheiro = Path("grafana/dashboards/intelligent-iot-dashboard.json")
dados = json.loads(ficheiro.read_text(encoding="utf-8"))

linhas = dados["layout"]["spec"]["rows"]

geral = next(
    r for r in linhas
    if r["spec"].get("title") == "Informação Geral"
)

titulo = "Métrica Personalizada"
mover = {"panel-19", "panel-21"}


def itens(linha):
    return linha["spec"]["layout"]["spec"]["items"]


def nome(item):
    return item["spec"]["element"]["name"]


selecionados = [
    item for item in itens(geral)
    if nome(item) in mover
]

if {nome(item) for item in selecionados} != mover:
    raise RuntimeError("Não foram encontrados os dois painéis em Informação Geral.")

# Remover os painéis da secção Informação Geral.
geral["spec"]["layout"]["spec"]["items"] = [
    item for item in itens(geral)
    if nome(item) not in mover
]

# Reutilizar a secção se já existir.
nova = next(
    (r for r in linhas if r["spec"].get("title") == titulo),
    None
)

if nova is None:
    nova = {
        "kind": "RowsLayoutRow",
        "spec": {
            "collapse": False,
            "layout": {
                "kind": "GridLayout",
                "spec": {
                    "items": []
                }
            },
            "title": titulo
        }
    }

    posicao = linhas.index(geral) + 1
    linhas.insert(posicao, nova)


# Mostrar apenas para métricas personalizadas.
metricas_originais = [
    "temperatura",
    "humidade",
    "luminosidade",
    "movimento"
]

nova["spec"]["conditionalRendering"] = {
    "kind": "ConditionalRenderingGroup",
    "spec": {
        "condition": "and",
        "items": [
            {
                "kind": "ConditionalRenderingVariable",
                "spec": {
                    "operator": "notEquals",
                    "value": metrica,
                    "variable": "metric"
                }
            }
            for metrica in metricas_originais
        ],
        "visibility": "show"
    }
}


# Colocar os painéis na nova secção.
for indice, item in enumerate(selecionados):
    item["spec"]["x"] = 0
    item["spec"]["y"] = indice * 9
    item["spec"]["width"] = 24
    item["spec"]["height"] = 9

    itens(nova).append(item)

ficheiro.write_text(
    json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
)

print("[OK] Painéis movidos para Métrica Personalizada.")
