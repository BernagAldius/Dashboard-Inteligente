// ======================================================
// AQUISICAO GENERICA DE DADOS REST
// ======================================================

const fs = require('fs');
const path = require('path');

// Carregar as fontes REST do cenario ativo
function loadRestSources() {
    const activePath = path.join('/config', 'active-config.json');

    const activeConfig = JSON.parse(
        fs.readFileSync(activePath, 'utf8')
    );

    const scenario = activeConfig.activeScenario;

    if (!['agricultura', 'domotica', 'industrial'].includes(scenario)) {
        throw new Error('Cenario ativo invalido');
    }

    const scenarioPath = path.join('/config', `${scenario}.json`);

    const scenarioConfig = JSON.parse(
        fs.readFileSync(scenarioPath, 'utf8')
    );

    return (scenarioConfig.data_sources || []).filter(
        source => source.enabled === true && source.type === 'rest'
    );
}

// Extrair um valor de um JSON através de um caminho como:
// current.temperature_2m
function extractJsonValue(data, jsonPath) {
    return jsonPath.split('.').reduce((value, key) => {
        return value != null ? value[key] : undefined;
    }, data);
}

// Consultar uma fonte REST e preparar a leitura
async function fetchRestSource(source) {
    const url = new URL(source.url);

    // Nesta fase, apenas fontes HTTPS.
    if (url.protocol !== 'https:') {
        throw new Error('A fonte REST deve utilizar HTTPS');
    }

    const response = await fetch(url, {
        method: 'GET',
        redirect: 'error',
        signal: AbortSignal.timeout(10000),
        headers: {
            'Accept': 'application/json'
        }
    });

    if (!response.ok) {
        throw new Error(`Erro HTTP ${response.status}`);
    }

    const json = await response.json();

    const value = extractJsonValue(json, source.json_path);

    if (typeof value !== 'number' || !Number.isFinite(value)) {
        throw new Error(
            `Valor inválido para a métrica ${source.metric}`
        );
    }

    return {
        sensor_id: source.sensor_id,
        tipo: 'rest',
        [source.metric]: value,
        timestamp: new Date().toISOString()
    };
}

// ======================================================
// EXECUCAO PERIODICA DAS FONTES REST
// ======================================================

function startRestSources(saveSensorData) {
    let sources;

    try {
        sources = loadRestSources();
    } catch (error) {
        console.error('[REST] Erro na configuração:', error.message);
        return;
    }

    console.log(`[REST] ${sources.length} fonte(s) ativa(s)`);

    for (const source of sources) {
        const interval = Number(source.interval_seconds);

        if (!Number.isInteger(interval) || interval < 30) {
            console.error(
                `[REST] Intervalo inválido na fonte ${source.id}`
            );
            continue;
        }

        let running = false;

        async function collect() {
            if (running) return;
            running = true;

            try {
                const data = await fetchRestSource(source);

                await saveSensorData(data);

                console.log(
                    `[REST] Leitura guardada: ${source.id} / ${source.metric}`
                );
            } catch (error) {
                console.error(
                    `[REST] Erro na fonte ${source.id}: ${error.message}`
                );
            } finally {
                running = false;
            }
        }

        // Primeira aquisição imediata
        collect();

        // Aquisições seguintes no intervalo configurado
        setInterval(collect, interval * 1000);
    }
}

module.exports = {
    loadRestSources,
    fetchRestSource,
    startRestSources
};