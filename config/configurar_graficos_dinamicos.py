
import json
from copy import deepcopy
from pathlib import Path

ficheiro = Path("grafana/dashboards/intelligent-iot-dashboard.json")
dados = json.loads(ficheiro.read_text(encoding="utf-8"))

elementos = dados["elements"]
linhas = dados["layout"]["spec"]["rows"]

def condicao(variavel, operador, valor):
    return {
        "kind": "ConditionalRenderingVariable",
        "spec": {
            "operator": operador,
            "value": valor,
            "variable": variavel
        }
    }

def grupo_condicional(condicoes):
    return {
        "kind": "ConditionalRenderingGroup",
        "spec": {
            "condition": "and",
            "items": condicoes,
            "visibility": "show"
        }
    }

def item_painel(nome, y=0):
    return {
        "kind": "GridLayoutItem",
        "spec": {
            "element": {
                "kind": "ElementReference",
                "name": nome
            },
            "height": 9,
            "width": 24,
            "x": 0,
            "y": y
        }
    }

# Identificar a secção existente.
indice = next(
    i for i, linha in enumerate(linhas)
    if linha["spec"].get("title") == "Métrica Personalizada"
)

original = linhas[indice]

# Preservar a condição que exclui as métricas padrão.
condicoes_base = deepcopy(
    original["spec"]["conditionalRendering"]["spec"]["items"]
)

# Criar o painel alternativo de barras.
if "panel-26" not in elementos:
    elementos["panel-26"] = deepcopy(elementos["panel-19"])

elementos["panel-19"]["spec"]["vizConfig"]["spec"]["fieldConfig"]["defaults"]["custom"]["drawStyle"] = "line"

elementos["panel-26"]["spec"]["title"] = "Histórico em Barras — ${metric} (${unit})"
elementos["panel-26"]["spec"]["vizConfig"]["spec"]["fieldConfig"]["defaults"]["custom"]["drawStyle"] = "bars"

# Secção com gráfico de linha e valor atual.
linha = deepcopy(original)
linha["spec"]["title"] = "Métrica Personalizada — Linha"
linha["spec"]["layout"]["spec"]["items"] = [
    item_painel("panel-19"),
    item_painel("panel-21", 9)
]
linha["spec"]["conditionalRendering"] = grupo_condicional(
    condicoes_base + [condicao("chart_type", "equals", "linha")]
)

# Secção com gráfico de barras e valor atual.
barras = deepcopy(original)
barras["spec"]["title"] = "Métrica Personalizada — Barras"
barras["spec"]["layout"]["spec"]["items"] = [
    item_painel("panel-26"),
    item_painel("panel-21", 9)
]
barras["spec"]["conditionalRendering"] = grupo_condicional(
    condicoes_base + [condicao("chart_type", "equals", "barra")]
)

# Substituir a secção original pelas duas alternativas.
linhas[indice:indice + 1] = [linha, barras]

ficheiro.write_text(
    json.dumps(dados, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
)

print("[OK] Gráficos dinâmicos configurados.")
print("[OK] Linha: panel-19")
print("[OK] Barras: panel-26")
print("[OK] Valor atual preservado: panel-21")
