# Dashboard Inteligente IoT

## Descrição

O Dashboard Inteligente IoT é uma plataforma modular para monitorização, análise e visualização de dados provenientes de sensores IoT.

O sistema permite simular diferentes tipos de sensores através do Node-RED, transmitir dados utilizando MQTT, armazenar séries temporais no InfluxDB e visualizar a informação através de dashboards configuráveis em Grafana.

A plataforma inclui ainda integração com FIWARE Orion Context Broker, permitindo representar sensores e respetivos dados através de entidades de contexto.

A arquitetura encontra-se contentorizada com Docker e Docker Compose, facilitando a instalação, portabilidade e execução dos diferentes componentes do sistema.

---

## Objetivos

O projeto pretende:

- Monitorizar dados provenientes de sensores IoT.
- Suportar diferentes tipos de sensores e métricas.
- Armazenar o histórico das leituras.
- Processar e analisar dados provenientes dos sensores.
- Identificar tendências, limites e possíveis anomalias.
- Disponibilizar uma API para consulta dos dados.
- Disponibilizar atualização de dados em tempo real.
- Permitir a configuração dinâmica do dashboard.
- Suportar diferentes cenários de utilização.
- Integrar tecnologias FIWARE para gestão de contexto IoT.
- Permitir futura integração com sensores físicos, como ESP32 ou Raspberry Pi.
- Garantir uma arquitetura modular e portável através de Docker.

---

# Arquitetura

A arquitetura atual do sistema pode ser representada de forma simplificada por:

```text
                  Node-RED
          (Simulação de Sensores)
                       │
                       │
              Análise dos Dados
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
       MQTT / Mosquitto      FIWARE
              │            Orion Context
              │               Broker
              ▼                 │
       Backend Node.js          │
              │                 │
       ┌──────┴───────┐         │
       │              │         │
       ▼              ▼         ▼
   InfluxDB        Socket.io   MongoDB
       │              │
       │              ▼
       │          Frontend Vue
       │
       ▼
     Grafana
       │
       ▼
Dashboard Inteligente
```

O Node-RED é atualmente utilizado para simular diferentes sensores e realizar processamento inicial dos dados.

Os dados são enviados através de MQTT para o backend Node.js, que os armazena no InfluxDB e os disponibiliza em tempo real através de Socket.io.

O Grafana consulta os dados armazenados no InfluxDB e constitui a principal interface de monitorização e configuração do Dashboard Inteligente.

Paralelamente, existe integração com o FIWARE Orion Context Broker, utilizando MongoDB como base de dados necessária ao funcionamento do Orion.

---

# Tecnologias Utilizadas

| Tecnologia | Função |
|------------|--------|
| Grafana OSS | Dashboard principal e visualização dinâmica |
| Vue.js 3 | Frontend web complementar |
| ApexCharts | Visualização de gráficos no frontend Vue |
| Node.js | Backend |
| Express | API REST |
| Socket.io | Comunicação em tempo real |
| Node-RED | Simulação e processamento de sensores |
| MQTT / Mosquitto | Comunicação entre sensores e backend |
| InfluxDB 2 | Base de dados temporal |
| FIWARE Orion | Context Broker para integração IoT |
| MongoDB | Persistência utilizada pelo FIWARE Orion |
| Docker | Contentorização dos componentes |
| Docker Compose | Orquestração dos serviços |
| Git | Controlo de versões |
| GitHub | Repositório remoto |

---

# Sensores e Métricas

O sistema encontra-se preparado para trabalhar com diferentes tipos de dados IoT.

Atualmente são simuladas as seguintes métricas:

| Sensor | Métrica |
|--------|---------|
| Sensor Ambiental | Temperatura |
| Sensor Ambiental | Humidade |
| Sensor de Luminosidade | Luminosidade |
| Sensor de Movimento | Movimento |

A utilização da métrica de movimento na experiência principal encontra-se em avaliação.

Os sensores são atualmente simulados através do Node-RED, mas a arquitetura permite que futuramente sejam substituídos por sensores físicos sem alterar a estrutura principal da plataforma.

---

# Processamento e Análise no Node-RED

O Node-RED não é utilizado apenas para geração de valores simulados.

Foram também implementados mecanismos básicos de análise dos dados, incluindo:

- cálculo de médias móveis;
- deteção de tendências;
- identificação de subidas e descidas;
- comparação com limites;
- deteção de variações bruscas;
- geração de estados de aviso;
- identificação de possíveis anomalias.

Por exemplo, para sensores ambientais podem ser produzidas informações adicionais como:

```text
temperatura_media_movel
humidade_media_movel
tendencia_temperatura
tendencia_humidade
estado
anomalia
alertas
```

Desta forma, a plataforma evolui de uma simples visualização de sensores para um sistema com capacidade de análise dos dados recebidos.

---

# Dashboard Grafana

O Grafana constitui atualmente a principal interface de monitorização do projeto.

O dashboard foi desenvolvido para se adaptar dinamicamente às escolhas realizadas pelo utilizador.

## Variáveis dinâmicas

Atualmente encontram-se disponíveis variáveis para:

- Cenário
- Métrica
- Sensor
- Limite mínimo
- Limite máximo
- Unidade

Estas variáveis permitem modificar dinamicamente os dados apresentados no dashboard.

---

## Cenários

Foram configurados três cenários principais para demonstrar a generalização da plataforma:

### Casa Inteligente / Domótica

Exemplo de monitorização de:

- temperatura;
- humidade;
- luminosidade;
- sensores associados às diferentes zonas da habitação.

### Agricultura Inteligente

Exemplo de monitorização de uma estufa através de:

- temperatura;
- humidade;
- luminosidade;
- sensores associados ao ambiente agrícola.

### Ambiente Industrial

Exemplo de monitorização ambiental numa instalação industrial através de:

- temperatura;
- humidade;
- luminosidade;
- sensores associados às zonas industriais.

Cada cenário pode possuir diferentes:

- nomes de sensores;
- zonas;
- limites mínimos;
- limites máximos;
- unidades;
- configurações.

---

# Configuração Dinâmica

Uma das principais funcionalidades implementadas é a generalização do dashboard.

Ao alterar o cenário, o sistema atualiza dinamicamente a configuração apresentada ao utilizador.

A relação pode ser representada por:

```text
Cenário
   │
   ▼
Sensores disponíveis
   │
   ▼
Métricas disponíveis
   │
   ├── Limite mínimo
   ├── Limite máximo
   └── Unidade
```

Isto permite reutilizar o mesmo dashboard para diferentes contextos IoT sem ser necessário criar um dashboard separado para cada cenário.

---

# Painéis do Dashboard

O dashboard Grafana inclui atualmente painéis para:

### Configuração do cenário

Apresenta informação relativa ao cenário atualmente selecionado.

### Zonas do cenário

Apresenta as zonas associadas ao cenário.

### Sensores do cenário

Apresenta os sensores disponíveis e respetivos identificadores e tipos.

### Métricas do cenário

Apresenta as métricas disponíveis e respetivas unidades.

### Histórico da Métrica

Apresenta graficamente o histórico da métrica selecionada.

O título e a unidade são atualizados dinamicamente.

Exemplos:

```text
Histórico — Temperatura (°C)
Histórico — Humidade (%)
Histórico — Luminosidade (lux)
```

### Limites

Apresenta os limites mínimo e máximo associados à configuração atual.

### Valor Atual

Apresenta o último valor recebido para a métrica selecionada.

Exemplos:

```text
Valor Atual — Temperatura (°C)
Valor Atual — Humidade (%)
Valor Atual — Luminosidade (lux)
```

### Estado da Métrica

Compara automaticamente o valor atual com os limites configurados.

Os estados possíveis são:

```text
NORMAL
ABAIXO DO LIMITE
ACIMA DO LIMITE
```

O estado é também representado visualmente através de cores no Grafana.

---

# Estrutura do Projeto

```text
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

A configuração atual utiliza os seguintes serviços:

| Serviço | Porta |
|----------|------:|
| Frontend Vue | 5173 |
| Backend | 3002 |
| Grafana | 3001 |
| FIWARE Orion | 1026 |
| Node-RED | 1880 |
| InfluxDB | 8086 |
| MQTT / Mosquitto | 1883 |
| MongoDB | 27017 |

> O backend é executado internamente na porta 3000 do contentor e exposto no host através da porta 3002.

---

# Estado Atual do Projeto

## Funcionalidades implementadas

- Arquitetura contentorizada com Docker Compose.
- Backend Node.js.
- API REST.
- Frontend Vue.js.
- Comunicação MQTT através do Mosquitto.
- Armazenamento temporal através do InfluxDB.
- Atualização em tempo real através de Socket.io.
- Simulação de sensores através do Node-RED.
- Sensores de temperatura, humidade, luminosidade e movimento.
- Processamento e análise básica no Node-RED.
- Cálculo de médias móveis.
- Deteção de tendências.
- Deteção de variações e anomalias.
- Grafana OSS integrado no projeto.
- Dashboard Grafana dinâmico.
- Integração com FIWARE Orion Context Broker.
- MongoDB integrado para suporte ao Orion.
- Configuração de múltiplos cenários.
- Seleção dinâmica de sensores e métricas.
- Limites mínimo e máximo dependentes do cenário/métrica.
- Unidades dinâmicas.
- Painéis com títulos dinâmicos.
- Histórico das métricas.
- Visualização do valor atual.
- Classificação automática do estado da métrica.
- Backup do fluxo Node-RED.

---

# Semana 15 — Generalização do Dashboard

Durante a Semana 15 foi realizada uma evolução significativa do dashboard Grafana, com foco na generalização da plataforma.

O objetivo foi deixar de ter uma interface dependente de um único caso de utilização e permitir que o mesmo dashboard possa representar diferentes cenários IoT.

## Funcionalidades desenvolvidas

Foram implementados:

- múltiplos cenários;
- configuração dinâmica dos sensores;
- configuração dinâmica das métricas;
- unidades dependentes da métrica;
- limites dependentes do cenário;
- títulos dinâmicos;
- histórico dinâmico;
- valor atual da métrica;
- estado automático da métrica;
- representação visual do estado.

Foram realizados testes com:

```text
Temperatura
Humidade
Luminosidade
```

nos cenários:

```text
Casa Inteligente
Agricultura Inteligente
Ambiente Industrial
```

Os testes confirmaram que o dashboard adapta corretamente:

```text
cenário
   ↓
sensor
   ↓
métrica
   ↓
unidade
   ↓
limites
   ↓
visualização
   ↓
estado
```

A decisão sobre a utilização da métrica de movimento na experiência principal permanece em pausa até validação com o orientador.

---

# Requisitos

Para executar o projeto é necessário:

- Docker Desktop no Windows

ou

- Docker Engine + Docker Compose no Linux

Também é necessário:

- Git

Opcionalmente, para desenvolvimento:

- Visual Studio Code
- Node.js LTS

---

# Instalação

## 1. Clonar o repositório

```bash
git clone https://github.com/BernagAldius/Dashboard-Inteligente.git
```

## 2. Entrar na pasta do projeto

```bash
cd Dashboard-Inteligente
```

## 3. Construir e iniciar os serviços

```bash
docker compose up -d --build
```

## 4. Confirmar o estado dos contentores

```bash
docker compose ps
```

Todos os principais serviços deverão aparecer com estado `Up`.

---

# Aceder aos Serviços

Depois de iniciar os contentores:

| Serviço | Endereço |
|---------|----------|
| Frontend Vue | `http://localhost:5173` |
| Backend | `http://localhost:3002` |
| Grafana | `http://localhost:3001` |
| FIWARE Orion | `http://localhost:1026` |
| Node-RED | `http://localhost:1880` |
| InfluxDB | `http://localhost:8086` |

Para confirmar que o Orion está operacional:

```bash
curl http://localhost:1026/version
```

---

# Parar o Projeto

Para parar os serviços:

```bash
docker compose down
```

Para voltar a iniciá-los:

```bash
docker compose up -d
```

Para reconstruir os serviços depois de alterações:

```bash
docker compose up -d --build
```

---
