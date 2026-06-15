<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import VueApexCharts from 'vue3-apexcharts'

const sensorData = ref([])
const latestTemperature = ref(null)
const latestHumidity = ref(null)

const temperatureSeries = ref([
  {
    name: 'Temperatura',
    data: []
  }
])

const humiditySeries = ref([
  {
    name: 'Humidade',
    data: []
  }
])

const chartOptions = ref({
  chart: {
    type: 'line',
    toolbar: {
      show: false
    }
  },
  xaxis: {
    categories: []
  },
  stroke: {
    curve: 'smooth'
  }
})

const fetchSensorData = async () => {
  try {
    const response = await axios.get('http://localhost:3000/sensor-data')

    sensorData.value = response.data

    if (sensorData.value.length > 0) {
      const latest = sensorData.value[sensorData.value.length - 1]

      latestTemperature.value = latest.temperatura
      latestHumidity.value = latest.humidade

      const lastReadings = sensorData.value.slice(-20)

      const labels = lastReadings.map((item) => {
        return new Date(item.time).toLocaleTimeString()
      })

      temperatureSeries.value = [
        {
          name: 'Temperatura',
          data: lastReadings.map((item) => item.temperatura)
        }
      ]

      humiditySeries.value = [
        {
          name: 'Humidade',
          data: lastReadings.map((item) => item.humidade)
        }
      ]

      chartOptions.value = {
        ...chartOptions.value,
        xaxis: {
          categories: labels
        }
      }
    }
  } catch (error) {
    console.error('Erro ao buscar dados dos sensores:', error)
  }
}

onMounted(() => {
  fetchSensorData()

  setInterval(() => {
    fetchSensorData()
  }, 5000)
})
</script>

<template>
  <main class="dashboard">
    <h1>Dashboard Inteligente IoT</h1>

    <section class="cards">
      <div class="card">
        <h2>Temperatura Atual</h2>
        <p v-if="latestTemperature !== null">{{ latestTemperature }} ºC</p>
        <p v-else>Sem dados</p>
      </div>

      <div class="card">
        <h2>Humidade Atual</h2>
        <p v-if="latestHumidity !== null">{{ latestHumidity }} %</p>
        <p v-else>Sem dados</p>
      </div>
    </section>

    <section class="charts">
      <div class="chart-card">
        <h2>Histórico de Temperatura</h2>
        <VueApexCharts
          width="100%"
          height="300"
          type="line"
          :options="chartOptions"
          :series="temperatureSeries"
        />
      </div>

      <div class="chart-card">
        <h2>Histórico de Humidade</h2>
        <VueApexCharts
          width="100%"
          height="300"
          type="line"
          :options="chartOptions"
          :series="humiditySeries"
        />
      </div>
    </section>

    <section class="info">
      <p>Total de leituras recebidas: {{ sensorData.length }}</p>
    </section>
  </main>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  padding: 40px;
  background: #111827;
  color: white;
  font-family: Arial, sans-serif;
}

h1 {
  margin-bottom: 30px;
}

.cards {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 30px;
}

.card {
  background: #1f2937;
  border-radius: 12px;
  padding: 24px;
  min-width: 220px;
}

.card h2,
.chart-card h2 {
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
  grid-template-columns: 1fr;
  gap: 24px;
}

.chart-card {
  background: #1f2937;
  border-radius: 12px;
  padding: 24px;
}

.info {
  margin-top: 30px;
  color: #9ca3af;
}
</style>