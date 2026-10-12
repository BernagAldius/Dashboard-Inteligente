from pathlib import Path
import secrets

ROOT = Path(__file__).resolve().parent.parent

BACKEND_ENV = ROOT / "backend" / ".env.docker"
ANALYTICS_ENV = ROOT / "analytics" / ".env.docker"
INFLUX_ENV = ROOT / ".env.influxdb"
GRAFANA_ENV = ROOT / "grafana" / ".env.grafana"


def criar_ficheiro(caminho, conteudo):
    if caminho.exists():
        print(f"[OK] Configuracao existente preservada: {caminho.name}")
        return False

    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(conteudo, encoding="utf-8")

    try:
        caminho.chmod(0o600)
    except OSError:
        pass

    print(f"[OK] Configuracao criada: {caminho}")
    return True

def preparar_grafana():
    """Cria credenciais administrativas do Grafana, se ainda não existirem."""

    if GRAFANA_ENV.exists():
        print("[OK] Credenciais do Grafana existentes preservadas.")
        return

    password = secrets.token_urlsafe(32)

    conteudo = (
        "GF_SECURITY_ADMIN_USER=admin\n"
        f"GF_SECURITY_ADMIN_PASSWORD={password}\n"
    )

    criar_ficheiro(GRAFANA_ENV, conteudo)

    print("[OK] Credenciais administrativas do Grafana preparadas.")


def main():
    preparar_grafana()
    
    print("\nA preparar configuracoes do Dashboard Inteligente...")

    # Não misturar credenciais novas com configurações antigas.
    ficheiros = [BACKEND_ENV, ANALYTICS_ENV, INFLUX_ENV]
    existentes = [ficheiro for ficheiro in ficheiros if ficheiro.exists()]

    if len(existentes) == len(ficheiros):
        print("[OK] Configuracao de ambiente existente preservada.")
        return

    if existentes:
        # Compatibilidade com a instalacao Windows anterior.
        if (
            BACKEND_ENV.exists()
            and ANALYTICS_ENV.exists()
            and not INFLUX_ENV.exists()
        ):
            print("[OK] Configuracao Windows existente preservada.")
            print("[INFO] Nao sera criado um novo token InfluxDB.")
            return

        print("[ERRO] Foram encontrados ficheiros de configuracao incompletos.")
        print("[INFO] Nenhum ficheiro sera alterado.")
        raise SystemExit(1)

    token = secrets.token_urlsafe(48)
    password = secrets.token_urlsafe(24)

    influx_config = (
        "DOCKER_INFLUXDB_INIT_MODE=setup\n"
        "DOCKER_INFLUXDB_INIT_USERNAME=dashboard_admin\n"
        f"DOCKER_INFLUXDB_INIT_PASSWORD={password}\n"
        "DOCKER_INFLUXDB_INIT_ORG=ipp\n"
        "DOCKER_INFLUXDB_INIT_BUCKET=iot_data\n"
        f"DOCKER_INFLUXDB_INIT_ADMIN_TOKEN={token}\n"
    )

    backend_config = (
        "MQTT_URL=mqtt://mosquitto:1883\n"
        "MQTT_TOPIC=sensors/+/+\n"
        "INFLUX_URL=http://influxdb:8086\n"
        f"INFLUX_TOKEN={token}\n"
        "INFLUX_ORG=ipp\n"
        "INFLUX_BUCKET=iot_data\n"
    )

    analytics_config = (
        "INFLUX_URL=http://influxdb:8086\n"
        f"INFLUX_TOKEN={token}\n"
        "INFLUX_ORG=ipp\n"
        "INFLUX_BUCKET=iot_data\n"
    )

    criar_ficheiro(INFLUX_ENV, influx_config)
    criar_ficheiro(BACKEND_ENV, backend_config)
    criar_ficheiro(ANALYTICS_ENV, analytics_config)

    print("[OK] Configuracoes preparadas com sucesso.")


if __name__ == "__main__":
    main()

