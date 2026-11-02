require('dotenv').config();

const { InfluxDB } = require('@influxdata/influxdb-client');

const influxDB = new InfluxDB({
    url: process.env.INFLUX_URL,
    token: process.env.INFLUX_TOKEN
});

const queryApi = influxDB.getQueryApi(process.env.INFLUX_ORG);

const query = `
from(bucket: "${process.env.INFLUX_BUCKET}")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "sensor_readings")
  |> filter(fn: (r) => r.tipo == "rest")
  |> group(columns: ["sensor_id", "_field"])
  |> last()
`;

async function testar() {
    try {
        const rows = await queryApi.collectRows(query);

        if (rows.length === 0) {
            console.log('Nenhuma leitura REST encontrada na última hora.');
            return;
        }

        for (const row of rows) {
            console.log({
                sensor: row.sensor_id,
                metrica: row._field,
                valor: row._value,
                data: row._time
            });
        }
    } catch (error) {
        console.error('Erro na consulta:', error.message);
        process.exitCode = 1;
    }
}

testar();