# Dashboard Inteligente IoT

## Descrição

O Dashboard Inteligente IoT é uma aplicação desenvolvida para monitorização de sensores ambientais em tempo real.

O sistema recebe dados de sensores através do protocolo MQTT, armazena-os numa base de dados InfluxDB e apresenta-os num dashboard desenvolvido em Vue.js.

A arquitetura foi desenvolvida utilizando Docker para facilitar a instalação, a portabilidade e a futura migração entre sistemas operativos Windows e Linux.

---

## Objetivos

O projeto pretende:

- Monitorizar sensores ambientais em tempo real.
- Armazenar histórico das leituras.
- Disponibilizar uma API para consulta dos dados.
- Apresentar gráficos interativos através de um dashboard web.
- Permitir futura integração com sensores físicos (ESP32, Raspberry Pi, etc.).
- Garantir uma arquitetura modular baseada em contentores Docker.

---

## Arquitetura

```text
Sensores / Node-RED
        │
        ▼
 MQTT (Mosquitto)
        │
        ▼
 Backend Node.js
        │
 ├──────────────┐
 ▼              ▼
InfluxDB     Socket.io
                 │
                 ▼
           Frontend Vue
```
---

# Tecnologias Utilizadas

| Tecnologia | Função |
|------------|--------|
| Vue.js 3 | Interface gráfica (Frontend) |
| ApexCharts | Visualização de gráficos |
| Node.js | Backend |
| Express | API REST |
| Socket.io | Comunicação em tempo real |
| Node-RED | Simulação e processamento de sensores |
| MQTT (Mosquitto) | Comunicação entre sensores e backend |
| InfluxDB 2 | Base de dados temporal |
| Docker Desktop | Contentorização |
| Docker Compose | Orquestração dos serviços |
| Git | Controlo de versões |
| GitHub | Repositório remoto |

---

# Estrutura do Projeto

```
Dashboard-Inteligente
│
├── backend/
│   ├── Dockerfile
│   ├── server.js
│   └── ...
│
├── frontend/
│   ├── Dockerfile
│   ├── src/
│   └── ...
│
├── docs/
│   └── flows.json
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

# Serviços e Portas

| Serviço | Porta |
|----------|------:|
| Frontend Vue | 5173 |
| Backend API | 3000 |
| Node-RED | 1880 |
| InfluxDB | 8086 |
| MQTT (Mosquitto) | 1883 |

---

# Estado do Projeto

## Funcionalidades implementadas

- Ambiente Docker totalmente funcional
- Backend Node.js com API REST
- Frontend em Vue.js
- Comunicação MQTT
- Base de dados InfluxDB
- Dashboard com gráficos de temperatura e humidade
- Atualização em tempo real através de Socket.io
- Node-RED para simulação de sensores
- Backup do fluxo Node-RED

---

# Requisitos

Antes de executar o projeto, é necessário ter instalado:

- Docker Desktop (Windows) ou Docker Engine + Docker Compose (Linux)
- Git

Opcional (para desenvolvimento):

- Visual Studio Code
- Node.js LTS

---

# Instalação (Linux)

## Instalar Docker e Docker Compose

A instalação depende da distribuição Linux utilizada.

Depois de instalar o Docker:

## 1. Clonar o repositório

```bash
git clone https://github.com/BernagAldius/Dashboard-Inteligente.git
```

## 2. Entrar na pasta do projeto

```bash
cd Dashboard-Inteligente
```

## 3. Iniciar os serviços

```bash
docker compose up -d --build
```

## 4. Confirmar os containers

```bash
docker ps
```
---

# Aceder à aplicação

Depois de iniciar os containers, os serviços estarão disponíveis em:

| Serviço | URL |
|----------|-----|
| Dashboard Vue | http://localhost:5173 |
| Backend API | http://localhost:3000/sensor-data |
| Node-RED | http://localhost:1880 |
| InfluxDB | http://localhost:8086 |

---

# Parar o Projeto

Para parar todos os serviços:

```bash
docker compose down
```

Para iniciar novamente:

```bash
docker compose up -d
```
