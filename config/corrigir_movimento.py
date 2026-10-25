import json
from pathlib import Path

ficheiro = Path("grafana/dashboards/intelligent-iot-dashboard.json")
dashboard = json.loads(ficheiro.read_text(encoding="utf-8"))

titulos = {
    "Valor Atual — ${metric} (${unit})",
    "Estado da Métrica",
}

alterados = []

for elemento in dashboard["elements"].values():
    titulo = elemento.get("spec", {}).get("title", "")

    if titulo not in titulos:
        continue

    for consulta in elemento["spec"]["data"]["spec"]["queries"]:
        spec = consulta["spec"]["query"]["spec"]
        query = spec["query"]

        # Converter o valor para número antes das comparações.
        query = query.replace(
            "r._value < ${min_threshold}",
            "float(v: r._value) < float(v: ${min_threshold})"
        )

        query = query.replace(
            "r._value > ${max_threshold}",
            "float(v: r._value) > float(v: ${max_threshold})"
        )

        spec["query"] = query

    alterados.append(titulo)

ficheiro.write_text(
    json.dumps(dashboard, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print("Painéis corrigidos:", alterados)