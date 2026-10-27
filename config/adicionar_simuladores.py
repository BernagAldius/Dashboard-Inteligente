import json
import copy
import uuid
from pathlib import Path

ficheiro = Path("docs/flows-atualizados.json")
backup = Path("docs/flows-atualizados.backup.json")

fluxos = json.loads(ficheiro.read_text(encoding="utf-8"))

if not backup.exists():
    backup.write_bytes(ficheiro.read_bytes())

modelo_inject = next(
    n for n in fluxos
    if n.get("type") == "inject" and n.get("repeat") == "10"
)
modelo_funcao = next(
    n for n in fluxos
    if n.get("name") == "Sensor Sim"
)
modelo_mqtt = next(
    n for n in fluxos
    if n.get("type") == "mqtt out"
)

simuladores = [
    (
        "Humidade Solo Simulator",
        "sensors/agricultura/004",
        """msg.payload = {
    sensor_id: "sensor_004",
    tipo: "agricultura",
    humidade_solo: Math.floor(Math.random() * 61) + 20,
    timestamp: new Date().toISOString()
};
return msg;"""
    ),
    (
        "Consumo Agua Simulator",
        "sensors/domotica/005",
        """let total = context.get("total") ?? 125;
total += Math.round((Math.random() * 2 + 0.2) * 100) / 100;
context.set("total", total);
msg.payload = {
    sensor_id: "sensor_005",
    tipo: "domotica",
    consumo_agua: Math.round(total * 100) / 100,
    timestamp: new Date().toISOString()
};
return msg;"""
    ),
    (
        "Consumo Energetico Simulator",
        "sensors/industrial/006",
        """let total = context.get("total") ?? 250;
total += Math.round((Math.random() * 0.3 + 0.02) * 1000) / 1000;
context.set("total", total);
msg.payload = {
    sensor_id: "sensor_006",
    tipo: "industrial",
    consumo_energetico: Math.round(total * 1000) / 1000,
    timestamp: new Date().toISOString()
};
return msg;"""
    )
]

for nome, topico, codigo in simuladores:
    if any(n.get("name") == nome for n in fluxos):
        print(f"[OK] Já existe: {nome}")
        continue

    inject = copy.deepcopy(modelo_inject)
    funcao = copy.deepcopy(modelo_funcao)
    mqtt = copy.deepcopy(modelo_mqtt)

    for no in (inject, funcao, mqtt):
        no["id"] = uuid.uuid4().hex[:16]

    inject.update({
        "name": f"Gerar {nome}",
        "x": 180,
        "y": 600 + len(fluxos) * 5,
        "wires": [[funcao["id"]]]
    })

    funcao.update({
        "name": nome,
        "func": codigo,
        "x": 440,
        "y": inject["y"],
        "wires": [[mqtt["id"]]]
    })

    mqtt.update({
        "name": f"MQTT {nome}",
        "topic": topico,
        "x": 720,
        "y": inject["y"],
        "wires": []
    })

    fluxos.extend([inject, funcao, mqtt])
    print(f"[OK] Criado: {nome}")

ficheiro.write_text(
    json.dumps(fluxos, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8"
)

print(f"[OK] Total de nós: {len(fluxos)}")
print(f"[OK] Backup: {backup}")
