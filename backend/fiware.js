
const ORION_URL = process.env.ORION_URL || 'http://orion:1026';

function buildAttributes(data) {
    const attributes = {
        sensor_id: {
            type: 'Text',
            value: data.sensor_id
        },
        source_type: {
            type: 'Text',
            value: data.tipo
        },
        timestamp: {
            type: 'DateTime',
            value: data.timestamp
        }
    };

    if (typeof data.scenario === 'string' && data.scenario.trim()) {
        attributes.scenario = {
            type: 'Text',
            value: data.scenario
        };
    }

    const restMetadata = data.rest_metadata;

    if (
        restMetadata &&
        typeof restMetadata.metric === 'string' &&
        Object.prototype.hasOwnProperty.call(data, restMetadata.metric)
    ) {
        const metric = restMetadata.metric;

        attributes[metric] = {
            type: 'Number',
            value: data[metric],
            metadata: {
                unit: {
                    type: 'Text',
                    value: restMetadata.unit
                },
                min: {
                    type: 'Number',
                    value: restMetadata.min
                },
                max: {
                    type: 'Number',
                    value: restMetadata.max
                }
            }
        };
    }

    for (const [key, value] of Object.entries(data)) {
        if (restMetadata && key === restMetadata.metric) {
            continue;
        }
        if (
            ['sensor_id', 'tipo', 'timestamp', 'analytics', 'scenario', 'rest_metadata'].includes(key)
        ) {
            continue;
        }

        if (typeof value === 'number' && Number.isFinite(value)) {
            attributes[key] = { type: 'Number', value };
        } else if (typeof value === 'boolean') {
            attributes[key] = { type: 'Boolean', value };
        }
    }

    return attributes;
}

async function syncSensorToFiware(data) {
    const entityId = data.sensor_id;

    if (!/^[a-zA-Z0-9_:-]+$/.test(entityId)) {
        throw new Error('Identificador FIWARE inválido');
    }

    const attributes = buildAttributes(data);

    const response = await fetch(
        `${ORION_URL}/v2/entities/${encodeURIComponent(entityId)}/attrs`,
        {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(attributes),
            signal: AbortSignal.timeout(5000)
        }
    );

    if (response.status === 204) {
        return;
    }

    if (response.status !== 404) {
        const errorBody = await response.text();
        throw new Error(`FIWARE HTTP ${response.status}: ${errorBody}`);
    }

    const createResponse = await fetch(`${ORION_URL}/v2/entities`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            id: entityId,
            type: 'IoTSensor',
            ...attributes
        }),
        signal: AbortSignal.timeout(5000)
    });

    if (!createResponse.ok && createResponse.status !== 422) {
        throw new Error(`FIWARE criação HTTP ${createResponse.status}`);
    }

    if (createResponse.status === 422) {
        const retryResponse = await fetch(
            `${ORION_URL}/v2/entities/${encodeURIComponent(entityId)}/attrs`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(attributes),
                signal: AbortSignal.timeout(5000)
            }
        );

        if (!retryResponse.ok) {
            throw new Error(`FIWARE atualização HTTP ${retryResponse.status}`);
        }
    }
}

module.exports = { syncSensorToFiware };
