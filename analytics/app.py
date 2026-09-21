import os

import numpy as np
from flask import Flask, jsonify
from influxdb_client import InfluxDBClient
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

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


def get_sensor_data(sensor_id, metric):
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
      |> tail(n: 20)
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

        if metric not in SENSOR_MAP:
            return jsonify({
                "error": "Métrica inválida"
            }), 400

        sensor_id = SENSOR_MAP[metric]

        values = get_sensor_data(sensor_id, metric)

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
        if metric not in SENSOR_MAP:
            return jsonify({
                "error": "Métrica inválida"
            }), 400

        sensor_id = SENSOR_MAP[metric]

        values = get_sensor_data(sensor_id, metric)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)