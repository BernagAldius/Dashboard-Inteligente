require('dotenv').config();

const express = require('express');
const cors = require('cors');
const mqtt = require('mqtt');
const http = require('http');
const fs = require("fs");
const path = require("path");
const { Server } = require('socket.io');

const { InfluxDB, Point } = require('@influxdata/influxdb-client');

const app = express();
const server = http.createServer(app);

const io = new Server(server, {
    cors: {
        origin: 'http://localhost:5173',
        methods: ['GET', 'POST']
    }
});

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


// ======================================================
// CARREGAMENTO DA CONFIGURAÇÃO DO DASHBOARD
// ======================================================

function loadDashboardConfig() {
    try {
        const activeConfigPath = path.join(
            '/config',
            'active-config.json'
        );

        const activeConfig = JSON.parse(
            fs.readFileSync(activeConfigPath, 'utf8')
        );

        const scenarioName = activeConfig.activeScenario;

        const scenarioPath = path.join(
            '/config',
            `${scenarioName}.json`
        );

        const scenarioConfig = JSON.parse(
            fs.readFileSync(scenarioPath, 'utf8')
        );

        return scenarioConfig;

    } catch (error) {
        console.error(
            'Erro ao carregar configuração do dashboard:',
            error.message
        );

        return null;
    }
}


// ======================================================
// MQTT
// ======================================================

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

        // Utilizar o timestamp recebido ou a data atual, caso seja inválido
        const receivedDate = new Date(data.timestamp);
        const validDate = Number.isNaN(receivedDate.getTime())
            ? new Date()
            : receivedDate;

        data.timestamp = validDate.toISOString();

        console.log('New Sensor Data:', data);

        const point = new Point('sensor_readings')
            .tag('sensor_id', data.sensor_id)
            .tag('tipo', data.tipo)
            .timestamp(validDate);

        // Guardar campos numéricos dinamicamente
        Object.keys(data).forEach((key) => {
            if (
                key !== 'sensor_id' &&
                key !== 'tipo' &&
                key !== 'timestamp' &&
                key !== 'analytics'
            ) {
                const value = data[key];

                if (typeof value === 'number') {
                    point.floatField(key, value);
                }

                if (typeof value === 'boolean') {
                    point.booleanField(key, value);
                }
            }
        });

        // Guardar analytics, se existirem
        if (data.analytics) {
            Object.keys(data.analytics).forEach((key) => {
                const value = data.analytics[key];

                if (typeof value === 'number') {
                    point.floatField(key, value);
                }

                if (typeof value === 'boolean') {
                    point.booleanField(key, value);
                }

                if (typeof value === 'string') {
                    point.stringField(key, value);
                }

                if (Array.isArray(value)) {
                    point.stringField(key, JSON.stringify(value));
                }
            });
        }

        writeApi.writePoint(point);

        await writeApi.flush();

        console.log('Data saved to InfluxDB');

        io.emit('sensor-data', {
  time: data.timestamp,
  ...data
});

console.log('Data sent to frontend via Socket.io');

    } catch (error) {
        console.error('Error processing MQTT message:', error.message);
    }
});

app.get('/dashboard-config', (req, res) => {
    try {
        const requestedScenario = req.query.scenario;

        if (requestedScenario) {
            const allowedScenarios = [
                'industrial',
                'domotica',
                'agricultura'
            ];

            if (!allowedScenarios.includes(requestedScenario)) {
                return res.status(400).json({
                    error: 'Cenário inválido'
                });
            }

            const scenarioPath = path.join(
                '/config',
                `${requestedScenario}.json`
            );

            const scenarioConfig = JSON.parse(
                fs.readFileSync(scenarioPath, 'utf8')
            );

            return res.json(scenarioConfig);
        }

        const dashboardConfig = loadDashboardConfig();

        if (!dashboardConfig) {
            return res.status(500).json({
                error: 'Não foi possível carregar a configuração do dashboard'
            });
        }

        res.json(dashboardConfig);

    } catch (error) {
        console.error(
            'Erro ao carregar cenário:',
            error.message
        );

        res.status(500).json({
            error: 'Erro ao carregar cenário'
        });
    }
});

app.get('/sensor-data', async (req, res) => {
    const fluxQuery = `
        from(bucket: "${influxBucket}")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "sensor_readings")
        |> pivot(rowKey:["_time", "sensor_id", "tipo"], columnKey: ["_field"], valueColumn: "_value")
    `;

    try {
        const rows = await queryApi.collectRows(fluxQuery);

        const results = rows.map((row) => {
            const {
                result,
                table,
                _start,
                _stop,
                _time,
                _measurement,
                ...metricas
            } = row;

            return {
                time: _time,
                ...metricas
            };
        });

        // Identificar métricas acumuladas nos cenários configurados
        const metricasAcumuladas = new Set();

        for (const cenario of ['agricultura', 'domotica', 'industrial']) {
            const ficheiro = path.join('/config', `${cenario}.json`);

            if (!fs.existsSync(ficheiro)) {
                continue;
            }

            const configuracao = JSON.parse(
                fs.readFileSync(ficheiro, 'utf8')
            );

            for (const zona of configuracao.zones || []) {
                for (const sensor of zona.sensors || []) {
                    for (const metrica of sensor.metrics || []) {
                        if (metrica.measurement_type === 'acumulado') {
                            metricasAcumuladas.add(metrica.field);
                        }
                    }
                }
            }
        }

        // Ordenar cronologicamente para calcular diferenças
        results.sort((a, b) =>
            new Date(a.time) - new Date(b.time)
        );

        // Última leitura de cada métrica por sensor
        const anteriores = new Map();

        for (const registo of results) {
            for (const campo of metricasAcumuladas) {
                const valor = registo[campo];

                if (typeof valor !== 'number') {
                    continue;
                }

                const chave = `${registo.sensor_id}:${campo}`;
                const anterior = anteriores.get(chave);

                if (anterior !== undefined) {
                    const diferenca = valor - anterior;

                    // Uma diminuição pode indicar reinicialização do contador
                    registo[`${campo}_intervalo`] =
                        diferenca >= 0 ? diferenca : null;
                } else {
                    // Não existe leitura anterior dentro da janela consultada
                    registo[`${campo}_intervalo`] = null;
                }

                anteriores.set(chave, valor);
            }
        }

        res.json(results);
    } catch (error) {
        console.error(error);

        res.status(500).json({
            error: 'Error fetching sensor data'
        });
    }
});

server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

process.on('SIGINT', async () => {
    console.log('Closing InfluxDB connection...');
    await writeApi.close();
    process.exit();
});