<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import VueApexCharts from 'vue3-apexcharts'
import { io } from 'socket.io-client'

const socket = io('http://localhost:3002')

const allData = ref([])
const alertNotification = ref(null)

const visibleSources = ref({
  temperatura: true,
  humidade: true,
  luminosidade: false,
  movimento: false
})

const latest = ref({
  temperatura: null,
  humidade: null,
  luminosidade: null,
  movimento: null
})

const temperatureSeries = ref([{ name: 'Temperatura', data: [] }])
const humiditySeries = ref([{ name: 'Humidade', data: [] }])
const luminositySeries = ref([{ name: 'Luminosidade', data: [] }])
const movementSeries = ref([{ name: 'Movimento', data: [] }])

const baseChartOptions = {
  chart: { type: 'line', toolbar: { show: false } },
  xaxis: { categories: [] },
  stroke: { curve: 'smooth' }
}

const temperatureChartOptions = ref({
  ...baseChartOptions,
  yaxis: {
    title: { text: 'Temperatura (ºC)' },
    labels: { formatter: (value) => `${value} ºC` }
  }
})

const humidityChartOptions = ref({
  ...baseChartOptions,
  yaxis: {
    title: { text: 'Humidade (%)' },
    labels: { formatter: (value) => `${value} %` }
  }
})

const luminosityChartOptions = ref({
  ...baseChartOptions,
  yaxis: {
    title: { text: 'Luminosidade (lux)' },
    labels: { formatter: (value) => `${value} lux` }
  }
})

const movementChartOptions = ref({
  ...baseChartOptions,
  yaxis: {
    min: 0,
    max: 1,
    title: { text: 'Movimento' },
    labels: {
      formatter: (value) => (value === 1 ? 'Sim' : 'Não')
    }
  }
})

const showAlert = (reading) => {
  if (!reading.anomalia && !reading.analytics?.anomalia) return

  const alertas = reading.alertas || reading.analytics?.alertas || []
  const message = Array.isArray(alertas) ? alertas.join(', ') : alertas

  alertNotification.value = {
    sensor: reading.sensor_id,
    message: message || 'Anomalia detetada',
    time: new Date(reading.time || reading.timestamp).toLocaleTimeString()
  }

  setTimeout(() => {
    alertNotification.value = null
  }, 6000)
}

const updateCharts = () => {
  const ambiental = allData.value.filter(
    (item) =>
      item.sensor_id === 'sensor_001' &&
      item.temperatura !== undefined &&
      item.humidade !== undefined
  )

  const luminosidade = allData.value.filter(
    (item) => item.sensor_id === 'sensor_002' && item.luminosidade !== undefined
  )

  const movimento = allData.value.filter(
    (item) => item.sensor_id === 'sensor_003' && item.movimento !== undefined
  )

  const lastAmbiental = ambiental.slice(-20)
  const lastLuminosidade = luminosidade.slice(-20)
  const lastMovimento = movimento.slice(-20)

  if (lastAmbiental.length > 0) {
    const last = lastAmbiental[lastAmbiental.length - 1]
    latest.value.temperatura = last.temperatura
    latest.value.humidade = last.humidade

    const labels = lastAmbiental.map((item) =>
      new Date(item.time || item.timestamp).toLocaleTimeString()
    )

    temperatureSeries.value = [
      { name: 'Temperatura', data: lastAmbiental.map((item) => item.temperatura) }
    ]

    humiditySeries.value = [
      { name: 'Humidade', data: lastAmbiental.map((item) => item.humidade) }
    ]

    temperatureChartOptions.value = {
      ...temperatureChartOptions.value,
      xaxis: { categories: labels }
    }

    humidityChartOptions.value = {
      ...humidityChartOptions.value,
      xaxis: { categories: labels }
    }
  }

  if (lastLuminosidade.length > 0) {
    const last = lastLuminosidade[lastLuminosidade.length - 1]
    latest.value.luminosidade = last.luminosidade

    const labels = lastLuminosidade.map((item) =>
      new Date(item.time || item.timestamp).toLocaleTimeString()
    )

    luminositySeries.value = [
      { name: 'Luminosidade', data: lastLuminosidade.map((item) => item.luminosidade) }
    ]

    luminosityChartOptions.value = {
      ...luminosityChartOptions.value,
      xaxis: { categories: labels }
    }
  }

  if (lastMovimento.length > 0) {
    const last = lastMovimento[lastMovimento.length - 1]
    latest.value.movimento = last.movimento

    const labels = lastMovimento.map((item) =>
      new Date(item.time || item.timestamp).toLocaleTimeString()
    )

    movementSeries.value = [
      { name: 'Movimento', data: lastMovimento.map((item) => (item.movimento ? 1 : 0)) }
    ]

    movementChartOptions.value = {
      ...movementChartOptions.value,
      xaxis: { categories: labels }
    }
  }
}

const updateDashboard = (newReading) => {
  allData.value.push(newReading)

  if (allData.value.length > 300) {
    allData.value.shift()
  }

  showAlert(newReading)
  updateCharts()
}

const fetchSensorData = async () => {
  try {
    const response = await axios.get('http://localhost:3002/sensor-data')
    allData.value = response.data
    updateCharts()
  } catch (error) {
    console.error('Erro ao buscar dados dos sensores:', error)
  }
}

onMounted(() => {
  fetchSensorData()

  socket.on('sensor-data', (newReading) => {
    updateDashboard(newReading)
  })
})
</script>

<template>
  <main class="dashboard">
    <div v-if="alertNotification" class="alert-toast">
      <strong>🚨 Anomalia detetada</strong>
      <span>Sensor: {{ alertNotification.sensor }}</span>
      <span>{{ alertNotification.message }}</span>
      <small>{{ alertNotification.time }}</small>
    </div>

    <nav class="top-nav">
      <a href="#dashboard">Dashboard Inteligente</a>
      <a href="#grafana">Grafana Showcase</a>
    </nav>

    <h1 id="dashboard">Dashboard Inteligente IoT</h1>

    <section class="source-config">
      <h2>Adicionar/remover fonte de dados</h2>

      <label>
        <input type="checkbox" v-model="visibleSources.temperatura" />
        Temperatura
      </label>

      <label>
        <input type="checkbox" v-model="visibleSources.humidade" />
        Humidade
      </label>

      <label>
        <input type="checkbox" v-model="visibleSources.luminosidade" />
        Luminosidade
      </label>

      <label>
        <input type="checkbox" v-model="visibleSources.movimento" />
        Movimento
      </label>
    </section>

    <section class="cards">
      <div v-if="visibleSources.temperatura" class="card">
        <h2>Temperatura Atual</h2>
        <p v-if="latest.temperatura !== null">{{ latest.temperatura }} ºC</p>
        <p v-else>Sem dados</p>
      </div>

      <div v-if="visibleSources.humidade" class="card">
        <h2>Humidade Atual</h2>
        <p v-if="latest.humidade !== null">{{ latest.humidade }} %</p>
        <p v-else>Sem dados</p>
      </div>

      <div v-if="visibleSources.luminosidade" class="card">
        <h2>Luminosidade Atual</h2>
        <p v-if="latest.luminosidade !== null">{{ latest.luminosidade }} lux</p>
        <p v-else>Sem dados</p>
      </div>

      <div v-if="visibleSources.movimento" class="card">
        <h2>Movimento Atual</h2>
        <p v-if="latest.movimento !== null">
          {{ latest.movimento ? 'Detetado' : 'Sem movimento' }}
        </p>
        <p v-else>Sem dados</p>
      </div>
    </section>

    <section class="charts">
      <div v-if="visibleSources.temperatura" class="chart-card">
        <h2>Histórico de Temperatura</h2>
        <VueApexCharts
          width="100%"
          height="300"
          type="line"
          :options="temperatureChartOptions"
          :series="temperatureSeries"
        />
      </div>

      <div v-if="visibleSources.humidade" class="chart-card">
        <h2>Histórico de Humidade</h2>
        <VueApexCharts
          width="100%"
          height="300"
          type="line"
          :options="humidityChartOptions"
          :series="humiditySeries"
        />
      </div>

      <div v-if="visibleSources.luminosidade" class="chart-card">
        <h2>Histórico de Luminosidade</h2>
        <VueApexCharts
          width="100%"
          height="300"
          type="line"
          :options="luminosityChartOptions"
          :series="luminositySeries"
        />
      </div>

      <div v-if="visibleSources.movimento" class="chart-card">
        <h2>Histórico de Movimento</h2>
        <VueApexCharts
          width="100%"
          height="300"
          type="line"
          :options="movementChartOptions"
          :series="movementSeries"
        />
      </div>
    </section>

    <section class="info">
      <p>Total de leituras recebidas: {{ allData.length }}</p>
    </section>

    <section id="grafana" class="grafana-section">
      <h2>Grafana Showcase</h2>

      <p>
        O Grafana OSS é utilizado como dashboard técnico para validar os dados
        armazenados no InfluxDB e comparar os resultados com o dashboard
        inteligente desenvolvido em Vue.js.
      </p>

      <div class="grafana-card">
        <h3>Dashboard Técnico IoT</h3>

        <p>
          Inclui visualização de temperatura, humidade, luminosidade, movimento,
          médias móveis e deteção de anomalias.
        </p>

        <a class="grafana-button" href="http://localhost:3001" target="_blank">
          Abrir Grafana Showcase
        </a>
      </div>
    </section>
  </main>
</template>

<style scoped>
.dashboard {
  max-width: 1600px;
  margin: 0 auto;
  overflow-x: hidden;
  width: 100vw;
  min-height: 100vh;
  aspect-ratio: 16 / 9;
  padding: 32px;
  background: #111827;
  color: white;
  font-family: Arial, sans-serif;
  box-sizing: border-box;
}

.alert-toast {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 999;
  background: #991b1b;
  color: white;
  padding: 18px 22px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
  max-width: 360px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.top-nav {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  background: #1f2937;
  padding: 14px 20px;
  border-radius: 12px;
}

.top-nav a {
  color: #d1d5db;
  text-decoration: none;
  font-weight: bold;
}

.top-nav a:hover {
  color: white;
}

h1 {
  margin-bottom: 30px;
}

.source-config {
  background: #1f2937;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.source-config h2 {
  width: 100%;
  font-size: 18px;
  color: #d1d5db;
}

.source-config label {
  display: flex;
  gap: 8px;
  align-items: center;
  color: #d1d5db;
  font-weight: bold;
}

.cards {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 30px;
}

.card {
  background: #005a10;
  border-radius: 12px;
  padding: 24px;
  min-width: 220px;
}

.card h2,
.chart-card h2,
.grafana-section h2 {
  font-size: 18px;
  margin-bottom: 12px;
  color: #d1d5db;
}

.card p {
  font-size: 32px;
  font-weight: bold;
  margin: 0;
}

.charts {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 24px;
  width: 100%;
}

.chart-card,
.grafana-section {
  background: #1f2937;
  border-radius: 12px;
  padding: 24px;
}

.chart-card {
  min-width: 0;
  overflow: hidden;
}

.grafana-section {
  margin-top: 30px;
}

.grafana-section p {
  color: #d1d5db;
  line-height: 1.6;
}

.grafana-card {
  margin-top: 20px;
  background: #111827;
  border-radius: 12px;
  padding: 20px;
}

.grafana-button {
  display: inline-block;
  margin-top: 16px;
  padding: 12px 18px;
  background: #2563eb;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: bold;
}

.grafana-button:hover {
  background: #1d4ed8;
}

.info {
  margin-top: 30px;
  color: #9ca3af;
}

@media (max-width: 1000px) {
  .charts {
    grid-template-columns: 1fr;
  }

  .dashboard {
    aspect-ratio: auto;
  }
}
</style>