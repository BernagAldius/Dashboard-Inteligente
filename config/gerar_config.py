import json
import shutil
import sys
from pathlib import Path

CONFIG_DIR = Path(__file__).parent
TXT_FILE = CONFIG_DIR / "configuracao_utilizador.txt"

CENARIOS_VALIDOS = {"domotica", "industrial", "agricultura"}

# Campos que podem ser definidos para cada nova métrica
CAMPOS_METRICA = {
    "nome",
    "unidade",
    "tipo",
    "sensor",
    "min",
    "max",
    "grafico",
}


def ler_configuracao():
    configuracao = {}

    with TXT_FILE.open("r", encoding="utf-8") as ficheiro:
        for numero_linha, linha in enumerate(ficheiro, start=1):
            linha = linha.strip()

            # Ignorar linhas vazias e comentários
            if not linha or linha.startswith("#"):
                continue

            if "=" not in linha:
                raise ValueError(
                    f"Linha {numero_linha} inválida: falta o sinal '='."
                )

            chave, valor = linha.split("=", 1)

            chave = chave.strip()
            valor = valor.strip()

            if not chave:
                raise ValueError(
                    f"Linha {numero_linha} inválida: chave vazia."
                )

            configuracao[chave] = valor

    return configuracao

def identificar_novas_metricas(configuracao):
    novas_metricas = {}

    for chave, valor in configuracao.items():
        if not chave.startswith("metrica_"):
            continue

        restante = chave[len("metrica_"):]

        campo_encontrado = None
        nome_metrica = restante

        for campo in CAMPOS_METRICA:
            sufixo = f"_{campo}"

            if restante.endswith(sufixo):
                nome_metrica = restante[:-len(sufixo)]
                campo_encontrado = campo
                break

        if not nome_metrica:
            raise ValueError(
                f"Nome de métrica inválido: '{chave}'."
            )

        if nome_metrica not in novas_metricas:
            novas_metricas[nome_metrica] = {}

        if campo_encontrado:
            novas_metricas[nome_metrica][campo_encontrado] = valor
        else:
            novas_metricas[nome_metrica]["ativo"] = valor

    return novas_metricas

def validar_novas_metricas(configuracao):
    novas_metricas = identificar_novas_metricas(configuracao)

    campos_obrigatorios = {
        "ativo", "nome", "unidade",
        "tipo", "sensor", "min", "max"
    }

    for identificador, dados in novas_metricas.items():
        em_falta = campos_obrigatorios - dados.keys()

        if em_falta:
            raise ValueError(
                f"Métrica '{identificador}': "
                f"faltam os campos {', '.join(sorted(em_falta))}."
            )

        if dados["ativo"].lower() not in {"true", "false"}:
            raise ValueError(
                f"Métrica '{identificador}': "
                "o estado deve ser true ou false."
            )

        dados["ativo"] = dados["ativo"].lower() == "true"

        if dados["tipo"] not in {"instantaneo", "acumulado"}:
            raise ValueError(
                f"Métrica '{identificador}': "
                "o tipo deve ser instantaneo ou acumulado."
            )

        grafico = dados.get("grafico", "automatico").lower()

        if grafico not in {"automatico", "linha", "barra"}:
            raise ValueError(
                f"Métrica '{identificador}': "
                "o gráfico deve ser automatico, linha ou barra."
            )

        if grafico == "automatico":
            grafico = (
                "barra"
                if dados["tipo"] == "acumulado"
                else "linha"
            )

        dados["grafico"] = grafico

        if not dados["nome"].strip():
            raise ValueError(
                f"Métrica '{identificador}': nome vazio."
            )

        if not dados["sensor"].strip():
            raise ValueError(
                f"Métrica '{identificador}': sensor vazio."
            )

        try:
            minimo = float(dados["min"])
            maximo = float(dados["max"])
        except ValueError:
            raise ValueError(
                f"Métrica '{identificador}': "
                "os limites devem ser números."
            )

        if minimo >= maximo:
            raise ValueError(
                f"Métrica '{identificador}': "
                "o mínimo deve ser inferior ao máximo."
            )

        dados["min"] = minimo
        dados["max"] = maximo

    return novas_metricas

def validar_configuracao(configuracao):
    campos_obrigatorios = [
        "cenario",
        "temperatura",
        "temperatura_min",
        "temperatura_max",
        "humidade",
        "humidade_min",
        "humidade_max",
        "luminosidade",
        "luminosidade_min",
        "luminosidade_max",
        "movimento",
    ]

    # Confirmar campos obrigatórios
    for campo in campos_obrigatorios:
        if campo not in configuracao or not configuracao[campo]:
            raise ValueError(
                f"O campo '{campo}' é obrigatório."
            )

    # Validar cenário
    if configuracao["cenario"] not in CENARIOS_VALIDOS:
        raise ValueError(
            "Cenário inválido. Utilize: domotica, industrial ou agricultura."
        )

    # Validar true / false
    campos_booleanos = [
        "temperatura",
        "humidade",
        "luminosidade",
        "movimento",
    ]

    for campo in campos_booleanos:
        valor = configuracao[campo].lower()

        if valor not in {"true", "false"}:
            raise ValueError(
                f"O campo '{campo}' deve ter o valor true ou false."
            )

        configuracao[campo] = valor == "true"

    # Validar limites numéricos
    metricas = [
        "temperatura",
        "humidade",
        "luminosidade",
    ]

    for metrica in metricas:
        campo_min = f"{metrica}_min"
        campo_max = f"{metrica}_max"

        try:
            minimo = float(configuracao[campo_min])
            maximo = float(configuracao[campo_max])
        except ValueError:
            raise ValueError(
                f"Os limites de '{metrica}' devem ser números."
            )

        if minimo >= maximo:
            raise ValueError(
                f"Em '{metrica}', o limite mínimo deve ser inferior ao máximo."
            )

        configuracao[campo_min] = minimo
        configuracao[campo_max] = maximo

    print("Configuração validada com sucesso.")
    print(f"Cenário selecionado: {configuracao['cenario']}")

def aplicar_novas_metricas(dados, novas_metricas):
    for identificador, definicao in novas_metricas.items():

        sensor_encontrado = None

        # Procurar o sensor indicado na configuração
        for zona in dados["zones"]:
            for sensor in zona["sensors"]:
                if sensor["id"] == definicao["sensor"]:
                    sensor_encontrado = sensor
                    break

            if sensor_encontrado:
                break

        # Criar o sensor caso ainda não exista
        if sensor_encontrado is None:
            sensor_encontrado = {
                "id": definicao["sensor"],
                "name": f"Sensor {definicao['nome']}",
                "type": "personalizado",
                "metrics": []
            }

            dados["zones"][0]["sensors"].append(sensor_encontrado)

        # Procurar a métrica para evitar duplicados
        metrica_encontrada = None

        for metrica in sensor_encontrado["metrics"]:
            if metrica["field"] == identificador:
                metrica_encontrada = metrica
                break

        if metrica_encontrada is None:
            metrica_encontrada = {}
            sensor_encontrado["metrics"].append(metrica_encontrada)

        metrica_encontrada.update({
            "field": identificador,
            "label": definicao["nome"],
            "unit": definicao["unidade"],
            "data_type": "number",
            "measurement_type": definicao["tipo"],
            "chart_type": definicao["grafico"],
            "alerts": {
                "min": definicao["min"],
                "max": definicao["max"]
            }
        })

        # Atualizar a visibilidade da métrica
        dados["dashboard"]["charts"][identificador] = definicao["ativo"]

        print(f"Métrica '{identificador}' configurada com sucesso.")

def atualizar_json(configuracao):
    cenario = configuracao["cenario"]
    json_file = CONFIG_DIR / f"{cenario}.json"

    if not json_file.exists():
        raise FileNotFoundError(
            f"Não foi encontrado o ficheiro '{json_file.name}'."
        )

    # Ler configuração JSON existente
    with json_file.open("r", encoding="utf-8") as ficheiro:
        dados = json.load(ficheiro)

    # Atualizar visibilidade dos gráficos
    dados["dashboard"]["charts"]["temperatura"] = configuracao["temperatura"]
    dados["dashboard"]["charts"]["humidade"] = configuracao["humidade"]
    dados["dashboard"]["charts"]["luminosidade"] = configuracao["luminosidade"]
    dados["dashboard"]["charts"]["movimento"] = configuracao["movimento"]

    # Procurar métricas e atualizar os respetivos limites
    for zona in dados["zones"]:
        for sensor in zona["sensors"]:
            for metrica in sensor["metrics"]:
                campo = metrica["field"]

                if campo in {"temperatura", "humidade", "luminosidade"}:
                    metrica["alerts"]["min"] = configuracao[f"{campo}_min"]
                    metrica["alerts"]["max"] = configuracao[f"{campo}_max"]

     # Aplicar novas métricas definidas no TXT
    novas_metricas = validar_novas_metricas(configuracao)
    aplicar_novas_metricas(dados, novas_metricas)

    print(f"Configuração preparada para '{json_file.name}'.")

    backup_file = json_file.with_suffix(".json.bak")

    if not backup_file.exists():
        shutil.copy2(json_file, backup_file)
        print(f"Backup original criado: '{backup_file.name}'.")
    else:
        print(f"Backup original já existente: '{backup_file.name}'.")

    with json_file.open("w", encoding="utf-8") as ficheiro:
        json.dump(dados, ficheiro, indent=2, ensure_ascii=False)
        ficheiro.write("\n")

    print(f"Ficheiro '{json_file.name}' atualizado com sucesso.")

    return json_file, dados

def atualizar_cenario_ativo(configuracao):
    active_file = CONFIG_DIR / "active-config.json"

    if not active_file.exists():
        raise FileNotFoundError(
            "Não foi encontrado o ficheiro 'active-config.json'."
        )

    with active_file.open("r", encoding="utf-8") as ficheiro:
        dados = json.load(ficheiro)

    dados["activeScenario"] = configuracao["cenario"]

    with active_file.open("w", encoding="utf-8") as ficheiro:
        json.dump(dados, ficheiro, indent=2, ensure_ascii=False)
        ficheiro.write("\n")

    print(
        f"Cenário ativo atualizado para '{configuracao['cenario']}'."
    )

if __name__ == "__main__":
    try:
        config = ler_configuracao()
        validar_configuracao(config)

        json_file, dados = atualizar_json(config)
        atualizar_cenario_ativo(config)

        print("\nPré-visualização da configuração:")
        print(json.dumps(dados, indent=2, ensure_ascii=False))

        print(
            f"\nConfiguração aplicada com sucesso a '{json_file.name}'."
        )

    except (OSError, ValueError, KeyError, IndexError, json.JSONDecodeError) as erro:
        print(f"\nERRO: {erro}")
        sys.exit(1)