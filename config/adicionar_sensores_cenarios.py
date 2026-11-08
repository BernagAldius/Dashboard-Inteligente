
import json
import copy
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
ficheiro = raiz / "docs" / "flows-atualizados.json"

with ficheiro.open("r", encoding="utf-8-sig") as f:
    flows = json.load(f)

base_inject = next(n for n in flows if n["id"] == "61332c29592423f3")
base_func = next(n for n in flows if n["id"] == "fe1d970e26a147cd")
base_mqtt = next(n for n in flows if n["id"] == "dbe94f5134464cf1")

sensores = [
    ("dom_sensor_001", "Domotica Ambiental", "sensors/domotica/ambiental", "domotica", "ambiental"),
    ("dom_sensor_002", "Domotica Luminosidade", "sensors/domotica/luminosidade", "domotica", "luminosidade"),
    ("ind_sensor_001", "Industrial Ambiental", "sensors/industrial/ambiental", "industrial", "ambiental"),
    ("ind_sensor_002", "Industrial Luminosidade", "sensors/industrial/luminosidade", "industrial", "luminosidade"),
]

for i, (sensor_id, nome, topico, cenario, tipo) in enumerate(sensores):
    ids = [f"inject_{sensor_id}", f"sim_{sensor_id}", f"mqtt_{sensor_id}"]

    existentes = {n["id"] for n in flows}
    if all(ident in existentes for ident in ids):
        print(f"[OK] {sensor_id} ja existe.")
        continue
    if any(ident in existentes for ident in ids):
        raise ValueError(f"Conjunto incompleto: {sensor_id}")

    inject = copy.deepcopy(base_inject)
    func = copy.deepcopy(base_func)
    mqtt = copy.deepcopy(base_mqtt)

    y = 1100 + i * 90

    inject.update(id=ids[0], name=f"Timer {nome}", x=160, y=y,
                  wires=[[ids[1]]])
    func.update(id=ids[1], name=nome, x=440, y=y,
                wires=[[ids[2]]])
    mqtt.update(id=ids[2], name=f"MQTT {nome}", topic=topico,
                x=770, y=y, wires=[])

    if tipo == "ambiental":
        valores = (
            "temperatura: Math.floor(Math.random() * 15) + 18, "
            "humidade: Math.floor(Math.random() * 35) + 40,"
        )
    else:
        valores = "luminosidade: Math.floor(Math.random() * 900) + 50,"

    func["func"] = (
        "msg.payload = { "
        f"sensor_id: '{sensor_id}', "
        f"tipo: '{cenario}', "
        f"{valores} "
        "timestamp: new Date().toISOString() "
        "}; return msg;"
    )

    flows.extend([inject, func, mqtt])

ids_finais = [n["id"] for n in flows]
if len(ids_finais) != len(set(ids_finais)):
    raise ValueError("Foram encontrados IDs duplicados.")

with ficheiro.open("w", encoding="utf-8") as f:
    json.dump(flows, f, ensure_ascii=False, indent=2)

print(f"[OK] Total de nos: {len(flows)}")
