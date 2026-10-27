import json
from pathlib import Path


CONFIG_DIR = Path("/config")

ALLOWED_SCENARIOS = {
    "agricultura",
    "domotica",
    "industrial"
}


def load_scenario(scenario=None):
    """Carrega o cenário solicitado ou o cenário ativo."""

    if scenario is None:
        active_path = CONFIG_DIR / "active-config.json"

        with active_path.open(encoding="utf-8") as file:
            active_config = json.load(file)

        scenario = active_config["activeScenario"]

    if scenario not in ALLOWED_SCENARIOS:
        raise ValueError("Cenário inválido")

    scenario_path = CONFIG_DIR / f"{scenario}.json"

    with scenario_path.open(encoding="utf-8") as file:
        return json.load(file)


def find_metric(scenario_config, sensor_id, metric_name):
    """Procura uma métrica pelo sensor e pelo nome do campo."""

    for zone in scenario_config.get("zones", []):
        for sensor in zone.get("sensors", []):
            if sensor.get("id") != sensor_id:
                continue

            for metric in sensor.get("metrics", []):
                if metric.get("field") == metric_name:
                    return {
                        "sensor_id": sensor_id,
                        "sensor_name": sensor.get("name"),
                        "zone": zone.get("name"),
                        "field": metric_name,
                        "label": metric.get("label", metric_name),
                        "unit": metric.get("unit", ""),
                        "data_type": metric.get(
                            "data_type", "number"
                        ),
                        "measurement_type": metric.get(
                            "measurement_type", "instantaneo"
                        ),
                        "alerts": metric.get("alerts", {}),
                        "analysis": metric.get("analysis", {})
                    }

    raise ValueError(
        f"Métrica '{metric_name}' não encontrada "
        f"no sensor '{sensor_id}'"
    )

def prepare_values(readings, measurement_type="instantaneo"):
    """Prepara valores instantâneos ou incrementos acumulados."""

    ordered = sorted(readings, key=lambda item: item["time"])
    values = [float(item["value"]) for item in ordered]

    if measurement_type != "acumulado":
        return values

    increments = []

    for previous, current in zip(values, values[1:]):
        difference = current - previous

        if difference < 0:
            increments = []
            continue

        increments.append(round(difference, 6))

    return increments


def calculate_trend(values, gradual_change, rapid_change):
    """Classifica a tendência da sequência de valores."""

    if len(values) < 3:
        return {
            "classification": "dados_insuficientes",
            "change": None
        }

    change = values[-1] - values[0]
    magnitude = abs(change)

    if magnitude >= rapid_change:
        intensity = "rapida"
    elif magnitude >= gradual_change:
        intensity = "gradual"
    else:
        intensity = "estavel"

    if intensity == "estavel":
        classification = "estavel"
    elif change > 0:
        classification = f"subida_{intensity}"
    else:
        classification = f"descida_{intensity}"

    return {
        "classification": classification,
        "change": round(change, 4),
        "gradual_threshold": gradual_change,
        "rapid_threshold": rapid_change
    }

import statistics


def detect_anomaly(values, threshold=2.0, tolerance=0.0):
    """Compara o último valor com o histórico anterior."""

    if len(values) < 5:
        return {
            "is_anomaly": False,
            "status": "dados_insuficientes",
            "zscore": None
        }

    history = values[:-1]
    current = values[-1]

    mean = statistics.mean(history)
    std = statistics.pstdev(history)
    difference = abs(current - mean)

    if difference <= tolerance:
        is_anomaly = False
        zscore = 0.0 if std == 0 else difference / std

    elif std == 0:
        is_anomaly = True
        zscore = None

    else:
        zscore = difference / std
        is_anomaly = zscore >= threshold

    return {
        "is_anomaly": is_anomaly,
        "status": "anomalia" if is_anomaly else "normal",
        "zscore": round(zscore, 4) if zscore is not None else None,
        "mean": round(mean, 4),
        "std": round(std, 4),
        "current_value": round(current, 4),
        "threshold": threshold,
        "tolerance": tolerance
    }

def evaluate_limits(value, alerts, unit=""):
    """Avalia um valor relativamente aos limites configurados."""

    minimum = alerts.get("min")
    maximum = alerts.get("max")

    if minimum is not None and value < minimum:
        return {
            "status": "abaixo_limite",
            "message": (
                f"Valor de {value:.2f} {unit} abaixo do "
                f"mínimo configurado de {minimum} {unit}."
            ),
            "minimum": minimum,
            "maximum": maximum
        }

    if maximum is not None and value > maximum:
        return {
            "status": "acima_limite",
            "message": (
                f"Valor de {value:.2f} {unit} acima do "
                f"máximo configurado de {maximum} {unit}."
            ),
            "minimum": minimum,
            "maximum": maximum
        }

    return {
        "status": "normal",
        "message": (
            f"Valor de {value:.2f} {unit} dentro "
            "dos limites configurados."
        ),
        "minimum": minimum,
        "maximum": maximum
    }

def explain_trend(trend, unit="", measurement_type="instantaneo"):
    """Produz uma explicação legível da tendência."""

    classification = trend["classification"]
    change = trend["change"]

    if classification == "dados_insuficientes":
        return "Não existem dados suficientes para calcular a tendência."

    basis = (
        "consumo por intervalo"
        if measurement_type == "acumulado"
        else "valor da métrica"
    )

    labels = {
        "estavel": "Estável",
        "subida_gradual": "Subida gradual",
        "subida_rapida": "Subida rápida",
        "descida_gradual": "Descida gradual",
        "descida_rapida": "Descida rápida"
    }

    label = labels.get(classification, classification)

    return (
        f"{label}: variação de {change:+.3f} {unit} "
        f"no {basis}. "
        f"Limiares configurados: "
        f"gradual={trend['gradual_threshold']} {unit}, "
        f"rápida={trend['rapid_threshold']} {unit}."
    )

def analyze_boolean(readings, alerts, window_size=10):
    """Analisa a frequência de deteções numa métrica booleana."""

    ordered = sorted(readings, key=lambda item: item["time"])
    recent = ordered[-window_size:]

    if not recent:
        return {
            "status": "dados_insuficientes",
            "count": 0,
            "detections": 0,
            "percentage": None
        }

    values = [float(item["value"]) for item in recent]

    if any(value not in (0.0, 1.0) for value in values):
        raise ValueError("A métrica booleana deve conter apenas valores 0 ou 1")

    detections = sum(value == 1.0 for value in values)
    count = len(values)

    high = int(alerts.get("high_activity", 7))
    persistent = int(alerts.get("persistent_activity", 9))

    if not 0 <= high <= persistent <= window_size:
        raise ValueError("Limiares de atividade inválidos")

    if detections >= persistent:
        status = "atividade_persistente"
        message = "Movimento detetado de forma persistente na janela analisada."
    elif detections >= high:
        status = "atividade_elevada"
        message = "Frequência elevada de deteções de movimento."
    else:
        status = "normal"
        message = "Frequência de deteções de movimento dentro do esperado."

    return {
        "status": status,
        "message": message,
        "count": count,
        "detections": detections,
        "percentage": round(100 * detections / count, 2),
        "current_value": int(values[-1]),
        "high_activity_threshold": high,
        "persistent_activity_threshold": persistent
    }
