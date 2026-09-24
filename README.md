# Dashboard Inteligente IoT

## Descrição

O Dashboard Inteligente IoT é uma aplicação desenvolvida para monitorização e análise de dados provenientes de diferentes tipos de sensores.

O sistema utiliza MQTT para comunicação, Node-RED para simulação e processamento dos sensores, InfluxDB para armazenamento temporal dos dados e Grafana como principal interface de monitorização e visualização.

A dashboard foi generalizada para permitir a utilização do mesmo sistema em diferentes cenários de aplicação, nomeadamente Domótica, Ambiente Industrial e Agricultura Inteligente.

Através do Grafana, o utilizador pode selecionar o cenário e a métrica que pretende analisar. A configuração apresentada é adaptada automaticamente, incluindo sensores, limites mínimos e máximos, unidades de medida e zonas associadas ao cenário.

A arquitetura foi desenvolvida utilizando Docker, facilitando a instalação, portabilidade, persistência dos serviços e futura migração entre sistemas operativos Windows e Linux.

---

## Objetivos

O projeto pretende:

- Monitorizar diferentes tipos de sensores em tempo real.
- Armazenar o histórico das leituras em InfluxDB.
- Processar dados através de Node-RED.
- Aplicar regras de análise, deteção de tendências, médias móveis e identificação de anomalias.
- Disponibilizar uma API para consulta dos dados.
- Utilizar Grafana como interface principal de monitorização.
- Permitir a configuração dinâmica da dashboard para diferentes cenários.
- Adaptar sensores, métricas, limites, unidades e zonas ao cenário selecionado.
- Controlar a visibilidade dos painéis de acordo com a métrica e o cenário selecionados.
- Manter uma arquitetura modular e contentorizada através de Docker.
- Preparar o sistema para futura integração com sensores físicos e métodos de análise avançada de dados.

---

## Arquitetura

```text
Sensores simulados / Node-RED
            │
            ▼
      MQTT (Mosquitto)
            │
            ▼
      Backend Node.js
            │
            ├──────────────► InfluxDB
            │                    │
            │                    ▼
            │                 Grafana
            │
            ├──────────────► Socket.io
            │                    │
            │                    ▼
            │                Frontend Vue
            │
            ▼
       FIWARE Orion
            │
            ▼
         MongoDB
```

O Node-RED é atualmente utilizado para simular diferentes sensores e realizar processamento inicial dos dados.

Os dados são enviados através de MQTT para o backend Node.js, que os armazena no InfluxDB e os disponibiliza em tempo real através de Socket.io.

O Grafana consulta os dados armazenados no InfluxDB e constitui a principal interface de monitorização e configuração do Dashboard Inteligente.

Paralelamente, existe integração com o FIWARE Orion Context Broker, utilizando MongoDB como base de dados necessária ao funcionamento do Orion.

---

# Tecnologias Utilizadas

| Tecnologia | Função |
|------------|--------|
| Grafana OSS | Dashboard principal e visualização dos dados |
| Vue.js 3 | Frontend complementar |
| Node.js | Backend |
| Express | API REST |
| Socket.io | Comunicação em tempo real com o frontend Vue |
| Node-RED | Simulação, processamento e análise dos sensores |
| MQTT (Mosquitto) | Comunicação entre sensores e backend |
| InfluxDB 2 | Base de dados temporal |
| FIWARE Orion | Context Broker para gestão de entidades IoT |
| MongoDB | Persistência de dados do FIWARE Orion |
| Docker Desktop | Contentorização |
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

# Dashboard Dinâmica e Cenários

A dashboard Grafana foi generalizada para permitir a reutilização da mesma interface em diferentes contextos de aplicação.

Atualmente estão configurados três cenários:

- Domótica
- Ambiente Industrial
- Agricultura Inteligente

Para cada cenário podem ser definidos:

- sensores disponíveis;
- métricas disponíveis;
- zonas;
- limites mínimos e máximos;
- unidades de medida.

As principais métricas atualmente utilizadas são:

- Temperatura
- Humidade
- Luminosidade

A informação apresentada no Grafana é atualizada dinamicamente de acordo com o cenário e a métrica selecionados.

Foram também implementadas regras de visibilidade condicional através de Rows do Grafana. Desta forma, os painéis associados a Temperatura, Humidade e Luminosidade são apresentados apenas quando a respetiva métrica é selecionada.

Foram igualmente criadas Rows específicas para:

- Análise — Domótica
- Análise — Industrial
- Análise — Agricultura

Estas Rows são apresentadas apenas quando o respetivo cenário está ativo, permitindo adicionar futuramente análises ou visualizações específicas de cada contexto sem duplicar toda a dashboard.

A funcionalidade foi validada através das nove combinações entre os três cenários e as três principais métricas.

A monitorização de movimento permanece implementada no sistema, mas encontra-se temporariamente fora da visualização principal da dashboard.

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

Foram implementados:

- múltiplos cenários;
- configuração dinâmica dos sensores;
- configuração dinâmica das métricas;
- unidades dependentes da métrica;
- limites dependentes do cenário e da métrica;
- títulos e visualizações dinâmicas;
- histórico e valor atual das métricas;
- classificação automática do estado da métrica;
- Organização dos painéis através de Rows no Grafana.
- Visibilidade condicional dos painéis de acordo com a métrica selecionada.
- Visibilidade condicional de Rows específicas de acordo com o cenário selecionado.
- Validação das nove combinações entre os três cenários e as três principais métricas.
- representação visual dos diferentes estados;
- organização dos painéis através de Rows;
- visibilidade condicional dos painéis de acordo com a métrica selecionada;
- visibilidade condicional de Rows específicas de acordo com o cenário selecionado.

Foram realizados testes com as métricas:

- Temperatura
- Humidade
- Luminosidade

nos cenários:

- Casa Inteligente / Domótica
- Agricultura Inteligente
- Ambiente Industrial

As nove combinações entre os três cenários e as três métricas foram testadas, confirmando que o dashboard adapta corretamente o cenário, sensor, métrica, unidade, limites e visualização apresentada.

Foram também criadas Rows específicas para análises futuras de cada cenário:

- Análise — Domótica
- Análise — Industrial
- Análise — Agricultura

Estas Rows são apresentadas apenas quando o respetivo cenário se encontra selecionado.

A funcionalidade de movimento permanece implementada no sistema, mas foi temporariamente retirada da visualização principal da dashboard, mantendo-se disponível para futura utilização.

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

A funcionalidade de movimento permanece implementada no sistema, mas encontra-se temporariamente fora da visualização principal da dashboard.

# Semana 16 — Análise Avançada com Python

Durante a Semana 16 foi desenvolvida a componente de análise avançada de dados do sistema, complementando a análise baseada em regras já existente no Node-RED.

Para esta componente foi criado um serviço independente denominado **Python Analytics**, desenvolvido em Python e integrado na arquitetura através de Docker.

O serviço obtém os dados históricos armazenados no InfluxDB e disponibiliza os resultados das análises através de uma API REST, posteriormente utilizada pelo Grafana para visualização.

## Arquitetura da análise

A divisão de responsabilidades ficou definida da seguinte forma:

```text
Sensores / Simulação
        ↓
      MQTT
        ↓
    Node-RED
        ↓
    InfluxDB
        ↓
Python Analytics
        ↓
      Grafana

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
| Python Analytics | `http://localhost:5000` |

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

# Semana 17 — Consolidação e Estabilização

Durante a Semana 17 foi realizada a consolidação da camada inteligente do sistema, a validação da integração entre os diferentes serviços e a estabilização do ambiente Docker.

## Integração da Camada Inteligente

Foi validado o fluxo completo de dados entre os principais componentes do sistema:

```text
Sensores simulados
        ↓
     Node-RED
        ↓
      MQTT
        ↓
     Backend
        ↓
    InfluxDB
        ↓
Python Analytics
        ↓
     Grafana

# Configuração do Dashboard

O sistema permite adaptar o dashboard a diferentes cenários através de ficheiros JSON localizados na pasta `config/`, sem necessidade de alterar o código da aplicação.

## Seleção do cenário ativo

O ficheiro `config/active-config.json` define o cenário ativo por defeito.

Exemplo:

```json
{
  "activeScenario": "agricultura"
}
```

Os cenários atualmente disponíveis são:

- `industrial`
- `domotica`
- `agricultura`

Cada cenário possui o respetivo ficheiro de configuração:

```text
config/
├── active-config.json
├── industrial.json
├── domotica.json
└── agricultura.json
```

## Ativação e desativação de gráficos

Cada ficheiro de cenário contém a secção `dashboard.charts`, que permite definir quais as métricas apresentadas no dashboard.

Exemplo:

```json
"dashboard": {
  "charts": {
    "temperatura": true,
    "humidade": true,
    "luminosidade": true,
    "movimento": false
  }
}
```

O valor `true` permite a apresentação dos gráficos associados à métrica.

O valor `false` oculta esses gráficos.

Desta forma, o dashboard pode ser adaptado às necessidades de cada cenário através do ficheiro de configuração, sem necessidade de modificar os painéis ou o código da aplicação.

## Zonas

A propriedade `zones` permite organizar os sensores por zonas do cenário.

Exemplo:

```json
{
  "id": "estufa",
  "name": "Estufa",
  "sensors": []
}
```

As zonas definidas no ficheiro são apresentadas dinamicamente no dashboard.

Por exemplo:

- Industrial: Zona de Produção e Zona de Acesso
- Domótica: Sala e Entrada
- Agricultura: Estufa e Zona de Acesso

## Sensores e métricas

Cada zona pode conter um ou mais sensores através da propriedade `sensors`.

Cada sensor possui:

- identificador (`id`);
- nome (`name`);
- tipo (`type`);
- métricas (`metrics`).

As métricas permitem definir o campo monitorizado, nome apresentado, unidade e limites associados.

Exemplo:

```json
{
  "field": "temperatura",
  "label": "Temperatura",
  "unit": "°C",
  "alerts": {
    "min": 10,
    "max": 35
  }
}
```

## Limites

Os limites configurados em `alerts.min` e `alerts.max` são utilizados pelo sistema para avaliar o estado das métricas.

Exemplo:

```json
"alerts": {
  "min": 10,
  "max": 35
}
```

Neste exemplo, a temperatura possui um intervalo configurado entre `10 °C` e `35 °C`.

Os limites podem variar entre cenários e são utilizados dinamicamente pelo dashboard e pela camada de análise baseada em regras.

## Procedimento básico de configuração

Para adaptar o sistema:

1. Selecionar o cenário em `config/active-config.json`.
2. Editar o respetivo ficheiro de cenário, se necessário.
3. Definir as zonas e sensores pretendidos.
4. Configurar métricas, unidades e limites.
5. Definir em `dashboard.charts` quais os gráficos que devem ser apresentados.
6. Guardar os ficheiros de configuração.
7. Iniciar o ambiente:

```bash
docker compose up -d
```

8. Aceder ao Grafana em `http://localhost:3001`.
9. No seletor `Cenário`, selecionar o cenário que se pretende visualizar.
10. Confirmar que as zonas, sensores, métricas, limites e gráficos apresentados correspondem ao ficheiro de configuração desse cenário.

> **Nota:** O ficheiro `active-config.json` define o cenário ativo utilizado pelo sistema e pela camada de processamento. O Grafana mantém um seletor de cenário independente, permitindo ao utilizador consultar manualmente qualquer um dos cenários disponíveis. Por esse motivo, após alterar o cenário ativo, deve ser selecionado no Grafana o cenário correspondente quando se pretende visualizar a mesma configuração.

## Demonstração da configuração

A seguinte sequência pode ser utilizada para demonstrar a adaptação do sistema através dos ficheiros de configuração.

### 1. Verificar o cenário ativo

Antes de iniciar a demonstração, verificar qual o cenário atualmente definido em `config/active-config.json`:

```powershell
Get-Content .\config\active-config.json
```

O ficheiro deverá indicar um dos cenários disponíveis:

- `domotica`
- `industrial`
- `agricultura`

O cenário apresentado corresponde à configuração atualmente selecionada pelo sistema.

### 2. Alterar o cenário ativo

Para demonstrar a configuração dinâmica do sistema, selecionar um cenário diferente do atualmente definido.

Editar o ficheiro `config/active-config.json` e definir um dos cenários disponíveis.

Por exemplo:

```json
{
  "activeScenario": "agricultura"
}
```

Se `agricultura` já for o cenário ativo, pode ser utilizado `domotica` ou `industrial`.

Guardar o ficheiro antes de iniciar ou atualizar o ambiente.

### 3. Iniciar ou atualizar o ambiente

Executar:

```powershell
docker compose up -d
```

Este comando inicia os serviços necessários. Caso os contentores já se encontrem em execução, o Docker Compose mantém os serviços ativos, permitindo que a configuração guardada seja utilizada pelo sistema.

### 4. Confirmar a configuração carregada

Executar:

```powershell
(Invoke-RestMethod http://localhost:3002/dashboard-config).scenario
```

O comando apresenta a identificação (`id`), o nome (`name`) e a descrição (`description`) do cenário atualmente carregado pelo sistema.

Confirmar que o cenário apresentado corresponde ao valor definido anteriormente em `config/active-config.json`.

### 5. Verificar o dashboard

Aceder ao Grafana em:

```text
http://localhost:3001
```

No seletor `Cenário`, selecionar o mesmo cenário definido anteriormente em `config/active-config.json`.

Confirmar que o dashboard apresenta corretamente:

- o nome do cenário;
- as zonas configuradas;
- os sensores associados;
- as métricas disponíveis;
- as unidades de medida;
- os limites mínimos e máximos definidos.

O seletor de cenário do Grafana é independente do cenário ativo do sistema, permitindo consultar manualmente qualquer um dos cenários disponíveis.

### 6. Demonstrar a ativação e desativação de gráficos

Abrir o ficheiro de configuração correspondente ao cenário selecionado:

- `config/domotica.json`
- `config/industrial.json`
- `config/agricultura.json`

Deve ser editado o ficheiro correspondente ao cenário definido anteriormente em `config/active-config.json`.

Localizar a secção `dashboard.charts`:

```json
"dashboard": {
  "charts": {
    "temperatura": true,
    "humidade": true,
    "luminosidade": true,
    "movimento": false
  }
}
```

Para ocultar os gráficos associados a uma métrica, alterar o respetivo valor de `true` para `false`.

Por exemplo:

```json
"luminosidade": false
```

Guardar o ficheiro e executar:

```powershell
docker compose up -d
```

No Grafana, atualizar o dashboard e selecionar a métrica alterada.

Confirmar que a métrica continua disponível na configuração do cenário, mas que a respetiva área de gráficos deixa de ser apresentada.

Para voltar a apresentar os gráficos, alterar novamente o valor para:

```json
"luminosidade": true
```

Guardar o ficheiro, executar novamente:

```powershell
docker compose up -d
```

e atualizar o dashboard no Grafana.

A área de gráficos correspondente deverá voltar a ser apresentada.

Este procedimento permite adaptar a interface às necessidades de cada cenário através dos ficheiros de configuração, sem modificar o código da aplicação ou os painéis do Grafana.

### 7. Demonstrar a alteração dos limites

Os limites de cada métrica podem ser alterados através das propriedades `alerts.min` e `alerts.max` do respetivo ficheiro de cenário.

Por exemplo, para uma métrica de luminosidade:

```json
"alerts": {
  "min": 100,
  "max": 700
}
```

Para demonstrar a configuração dinâmica dos limites, estes valores podem ser temporariamente alterados, por exemplo, para:

```json
"alerts": {
  "min": 200,
  "max": 600
}
```

Guardar o ficheiro e executar:

```powershell
docker compose up -d
```

No Grafana, atualizar o dashboard e selecionar o cenário e a métrica correspondentes.

Confirmar que os novos limites mínimo e máximo são apresentados no dashboard.

Quando o valor atual da métrica se encontrar fora do intervalo configurado, o sistema deverá refletir essa situação através do estado da métrica e da análise baseada em regras.

Por exemplo, para um limite máximo de `600 lux`, uma leitura superior a esse valor deverá ser identificada como estando acima do limite.

Este teste demonstra que os limites podem ser adaptados através dos ficheiros de configuração sem necessidade de modificar o código da aplicação.

