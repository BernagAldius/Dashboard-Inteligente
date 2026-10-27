import os

import numpy as np
from flask import Flask, jsonify, request
from influxdb_client import InfluxDBClient
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from generic_analysis import (
    load_scenario,
    find_metric,
    prepare_values,
    calculate_trend,
    detect_anomaly,
    evaluate_limits,
    explain_trend,
    analyze_boolean
)

app = Flask(__name__)

INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")

SENSOR_MAP = {
    "temperatura": "sensor_001",
    "humidade": "sensor_001",
    "luminosidade": "sensor_002"
}


def get_sensor_data(sensor_id, metric, window_size=20):
    client = InfluxDBClient(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG
    )

    query = f'''
    from(bucket: "{INFLUX_BUCKET}")
      |> range(start: -1h)
      |> filter(fn: (r) => r._measurement == "sensor_readings")
      |> filter(fn: (r) => r.sensor_id == "{sensor_id}")
      |> filter(fn: (r) => r._field == "{metric}")
      |> tail(n: {window_size})
    '''

    tables = client.query_api().query(query)

    values = []

    for table in tables:
        for record in table.records:
            values.append({
                "time": record.get_time().isoformat(),
                "value": float(record.get_value())
            })

    client.close()

    return values


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "python-analytics"
    })


@app.route("/temperature", methods=["GET"])
def temperature():
    try:
        values = get_sensor_data("sensor_001", "temperatura")

        return jsonify({
            "sensor_id": "sensor_001",
            "metric": "temperatura",
            "count": len(values),
            "data": values
        })

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500

@app.route("/humidity", methods=["GET"])
def humidity():
    try:
        values = get_sensor_data("sensor_001", "humidade")

        return jsonify({
            "sensor_id": "sensor_001",
            "metric": "humidade",
            "count": len(values),
            "data": values
        })

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500

@app.route("/luminosity", methods=["GET"])
def luminosity():
    try:
        values = get_sensor_data("sensor_002", "luminosidade")

        return jsonify({
            "sensor_id": "sensor_002",
            "metric": "luminosidade",
            "count": len(values),
            "data": values
        })

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500

@app.route("/zscore/<metric>", methods=["GET"])
def zscore(metric):
    try:

        scenario = request.args.get("scenario")
        sensor_id = request.args.get("sensor_id")

        if scenario and sensor_id:
            scenario_config = load_scenario(scenario)
            metric_config = find_metric(
                scenario_config, sensor_id, metric
            )

            if metric_config["data_type"] == "boolean":
                return jsonify({
                    "error": "Esta análise requer uma métrica numérica"
                }), 400
        elif not scenario and not sensor_id and metric in SENSOR_MAP:
            sensor_id = SENSOR_MAP[metric]
        else:
            return jsonify({
                "error": "Indique um cenário e sensor válidos"
            }), 400

        values = get_sensor_data(sensor_id, metric)
        values = sorted(values, key=lambda item: item["time"])

        if scenario and sensor_id:
            measurement_type = metric_config["measurement_type"]
            if measurement_type == "acumulado":
                increments = []
                for previous, current in zip(values, values[1:]):
                    difference = current["value"] - previous["value"]
                    if difference < 0:
                        increments = []
                        continue
                    increments.append({
                        "time": current["time"],
                        "value": round(difference, 6)
                    })
                values = increments

        if len(values) < 2:
            return jsonify({
                "error": "Dados insuficientes para calcular Z-score"
            }), 400

        numeric_values = np.array(
            [item["value"] for item in values],
            dtype=float
        )

        mean = np.mean(numeric_values)
        std = np.std(numeric_values)

        results = []

        for item in values:
            if std == 0:
                z_score = 0.0
            else:
                z_score = (item["value"] - mean) / std

            results.append({
                "time": item["time"],
                "value": item["value"],
                "z_score": round(float(z_score), 3),
                "anomalia": bool(abs(z_score) >= 2)
            })

        return jsonify({
            "sensor_id": sensor_id,
            "metric": metric,
            "method": "z-score",
            "threshold": 2,
            "mean": round(float(mean), 3),
            "std": round(float(std), 3),
            "count": len(results),
            "data": results
        })

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500

@app.route("/isolation-forest/<metric>", methods=["GET"])
def isolation_forest(metric):
    try:
        scenario = request.args.get("scenario")
        sensor_id = request.args.get("sensor_id")

        if scenario and sensor_id:
            scenario_config = load_scenario(scenario)
            metric_config = find_metric(
                scenario_config, sensor_id, metric
            )

            if metric_config["data_type"] == "boolean":
                return jsonify({
                    "error": "Esta análise requer uma métrica numérica"
                }), 400
        elif not scenario and not sensor_id and metric in SENSOR_MAP:
            sensor_id = SENSOR_MAP[metric]
        else:
            return jsonify({
                "error": "Indique um cenário e sensor válidos"
            }), 400

        values = get_sensor_data(sensor_id, metric)
        values = sorted(values, key=lambda item: item["time"])

        if scenario and sensor_id:
            measurement_type = metric_config["measurement_type"]
            if measurement_type == "acumulado":
                increments = []
                for previous, current in zip(values, values[1:]):
                    difference = current["value"] - previous["value"]
                    if difference < 0:
                        increments = []
                        continue
                    increments.append({
                        "time": current["time"],
                        "value": round(difference, 6)
                    })
                values = increments

        if len(values) < 5:
            return jsonify({
                "error": "Dados insuficientes para executar Isolation Forest"
            }), 400

        numeric_values = np.array(
            [item["value"] for item in values],
            dtype=float
        ).reshape(-1, 1)

        model = IsolationForest(
            contamination=0.05,
            random_state=42
        )

        predictions = model.fit_predict(numeric_values)
        scores = model.decision_function(numeric_values)

        results = []

        for item, prediction, score in zip(values, predictions, scores):
            results.append({
                "time": item["time"],
                "value": item["value"],
                "score": round(float(score), 4),
                "anomalia": bool(prediction == -1)
            })

        return jsonify({
            "sensor_id": sensor_id,
            "metric": metric,
            "method": "isolation-forest",
            "contamination": 0.05,
            "count": len(results),
            "data": results
        })

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500

@app.route("/forecast", methods=["GET"])
def forecast():
    try:
        values = get_sensor_data("sensor_001", "temperatura")

        if len(values) < 5:
            return jsonify({
                "error": "Dados insuficientes para realizar previsão"
            }), 400

        y = np.array(
            [item["value"] for item in values],
            dtype=float
        )

        x = np.arange(len(y)).reshape(-1, 1)

        model = LinearRegression()
        model.fit(x, y)

        future_x = np.arange(
            len(y),
            len(y) + 5
        ).reshape(-1, 1)

        predictions = model.predict(future_x)

        forecast_data = []

        last_time = datetime.fromisoformat(values[-1]["time"])

        for index, prediction in enumerate(predictions, start=1):
            future_time = last_time + timedelta(seconds=10 * index)

            forecast_data.append({
                "time": future_time.isoformat(),
                "step": index,
                "predicted_value": round(float(prediction), 2)
            })

        return jsonify({
            "sensor_id": "sensor_001",
            "metric": "temperatura",
            "method": "linear-regression",
            "historical_count": len(values),
            "forecast_count": len(forecast_data),
            "slope": round(float(model.coef_[0]), 4),
            "intercept": round(float(model.intercept_), 4),
            "forecast": forecast_data
        })

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500

@app.route("/analysis", methods=["GET"])
def generic_analysis():
    try:
        scenario = request.args.get("scenario")
        sensor_id = request.args.get("sensor_id")
        metric_name = request.args.get("metric")

        if not sensor_id or not metric_name:
            return jsonify({
                "error": "sensor_id e metric são obrigatórios"
            }), 400

        scenario_config = load_scenario(scenario)

        metric = find_metric(
            scenario_config,
            sensor_id,
            metric_name
        )


        analysis_config = metric["analysis"]

        if analysis_config.get("enabled", True) is False:
            return jsonify({
                "scenario": scenario_config["scenario"]["id"],
                "sensor_id": sensor_id,
                "metric": metric_name,
                "status": "analysis_disabled",
                "message": "A análise está desativada para esta métrica."
            }), 200

        window_size = int(analysis_config.get("window_size", 20))

        if not 5 <= window_size <= 1000:
            raise ValueError("window_size deve estar entre 5 e 1000")

        readings = get_sensor_data(
            sensor_id,
            metric_name,
            window_size=window_size
        )

        readings = sorted(readings, key=lambda item: item["time"])

        if metric["data_type"] == "boolean":
            boolean_window = 10

            if len(readings) < boolean_window:
                return jsonify({
                    "scenario": scenario_config["scenario"]["id"],
                    "sensor_id": sensor_id,
                    "metric": metric_name,
                    "status": "dados_insuficientes",
                    "count": len(readings),
                    "required_count": boolean_window
                }), 200

            result = analyze_boolean(
                readings,
                metric["alerts"],
                window_size=boolean_window
            )

            return jsonify({
                "scenario": scenario_config["scenario"]["id"],
                "sensor_id": sensor_id,
                "metric": metric_name,
                "label": metric["label"],
                "data_type": "boolean",
                "analysis_basis": "frequencia_deteccoes",
                "activity": result
            }), 200

        if not readings:
            return jsonify({
                "sensor_id": sensor_id,
                "metric": metric_name,
                "status": "dados_insuficientes",
                "count": 0
            })

        measurement_type = metric["measurement_type"]
        values = prepare_values(readings, measurement_type)


        trend_config = analysis_config.get("trend", {})
        anomaly_config = analysis_config.get("anomaly", {})

        gradual = float(trend_config.get("gradual_change", 2.0))
        rapid = float(trend_config.get("rapid_change", 5.0))

        threshold = float(anomaly_config.get("threshold", 2.0))
        tolerance = float(anomaly_config.get("tolerance", 0.0))

        trend = calculate_trend(values, gradual, rapid)

        anomaly = detect_anomaly(
            values,
            threshold=threshold,
            tolerance=tolerance
        )

        current_value = float(readings[-1]["value"])

        limits = evaluate_limits(
            current_value,
            metric["alerts"],
            metric["unit"]
        )

        return jsonify({
            "scenario": scenario_config["scenario"]["id"],
            "sensor_id": sensor_id,
            "metric": metric_name,
            "label": metric["label"],
            "unit": metric["unit"],
            "measurement_type": measurement_type,
            "count": len(readings),
            "current_value": current_value,
            "analysis_value": values[-1] if values else None,
            "analysis_basis": (
                "incremento_por_intervalo"
                if measurement_type == "acumulado"
                else "valor_instantaneo"
            ),
            "limits": limits,
            "trend": trend,
            "trend_explanation": explain_trend(
                trend,
                metric["unit"],
                measurement_type
            ),
            "anomaly": anomaly
        })

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception as error:
        return jsonify({"error": str(error)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)