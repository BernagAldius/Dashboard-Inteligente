require('dotenv').config();

const express = require('express');
const cors = require('cors');
const mqtt = require('mqtt');

const { InfluxDB, Point } = require('@influxdata/influxdb-client');

const app = express();

app.use(cors());

const PORT = 3000;

const mqttUrl = process.env.MQTT_URL;
const mqttTopic = process.env.MQTT_TOPIC;

const influxUrl = process.env.INFLUX_URL;
const influxToken = process.env.INFLUX_TOKEN;
const influxOrg = process.env.INFLUX_ORG;
const influxBucket = process.env.INFLUX_BUCKET;

const influxDB = new InfluxDB({
    url: influxUrl,
    token: influxToken
});

const writeApi = influxDB.getWriteApi(influxOrg, influxBucket, 'ns');

const queryApi = influxDB.getQueryApi(influxOrg);

const client = mqtt.connect(mqttUrl);

client.on('connect', () => {
    console.log('Connected to MQTT Broker');

    client.subscribe(mqttTopic, (err) => {
        if (err) {
            console.error('MQTT subscription error:', err.message);
            return;
        }

        console.log(`Subscribed to topic: ${mqttTopic}`);
    });
});

client.on('message', async (topic, message) => {
    try {
        const data = JSON.parse(message.toString());

        console.log('New Sensor Data:', data);

        const point = new Point('sensor_readings')
            .tag('sensor_id', data.sensor_id)
            .tag('tipo', data.tipo)
            .floatField('temperatura', Number(data.temperatura))
            .floatField('humidade', Number(data.humidade))
            .timestamp(new Date(data.timestamp));

        writeApi.writePoint(point);

        await writeApi.flush();

        console.log('Data saved to InfluxDB');

    } catch (error) {
        console.error('Error processing MQTT message:', error.message);
    }
});

app.get('/sensor-data', async (req, res) => {

    const fluxQuery = `
        from(bucket: "${influxBucket}")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "sensor_readings")
        |> keep(columns: ["_time", "_field", "_value", "sensor_id", "tipo"])
    `;

    try {
        const results = [];

        const rows = await queryApi.collectRows(fluxQuery);

        rows.forEach((row) => {
            results.push({
                time: row._time,
                field: row._field,
                value: row._value,
                sensor_id: row.sensor_id,
                tipo: row.tipo
            });
        });

        res.json(results);

    } catch (error) {
        console.error(error);

        res.status(500).json({
            error: 'Error fetching sensor data'
        });
    }
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

process.on('SIGINT', async () => {
    console.log('Closing InfluxDB connection...');
    await writeApi.close();
    process.exit();
});