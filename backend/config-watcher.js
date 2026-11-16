const fs = require('fs');
const { execFile } = require('child_process');

const CONFIG_FILE = '/config/configuracao_utilizador.txt';
const GENERATOR = '/app/gerar_config.py';

function startConfigWatcher(reloadRestSources) {
    let lastContent = null;
    let processing = false;

    try {
        lastContent = fs.readFileSync(CONFIG_FILE, 'utf8');
    } catch (error) {
        console.error('[CONFIG] Erro inicial:', error.message);
    }

    setInterval(async () => {
        if (processing) return;

        let currentContent;

        try {
            currentContent = fs.readFileSync(CONFIG_FILE, 'utf8');
        } catch (error) {
            console.error('[CONFIG] Erro de leitura:', error.message);
            return;
        }

        if (currentContent === lastContent) return;

        lastContent = currentContent;
        processing = true;

        console.log('[CONFIG] Alteração detetada.');

        execFile(
            'python3',
            [GENERATOR],
            { timeout: 30000,
                env: {
                    ...process.env,
                    DASHBOARD_CONFIG_DIR: '/config'
                }
            },
            (error, stdout, stderr) => {
                if (error) {
                    console.error(
                        '[CONFIG] Configuração rejeitada:',
                        stderr || stdout || error.message
                    );
                } else {
                    console.log('[CONFIG] Configuração gerada.');

                    if (reloadRestSources()) {
                        console.log('[CONFIG] Fontes REST atualizadas.');
                    } else {
                        console.error('[CONFIG] Falha ao atualizar fontes REST.');
                    }
                }

                processing = false;
            }
        );
    }, 3000);
}

module.exports = { startConfigWatcher };
