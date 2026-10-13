import os
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FLUXOS = RAIZ / "docs" / "flows-atualizados.json"
CONTENTOR = os.environ.get("NODERED_CONTAINER", "nodered")


def executar(*comando):
    return subprocess.run(
        comando,
        capture_output=True,
        text=True,
        check=False,
    )


def main():
    if not FLUXOS.is_file():
        print("[ERRO] Ficheiro de fluxos não encontrado.")
        return 1

    with FLUXOS.open(encoding="utf-8") as ficheiro:
        fluxos = json.load(ficheiro)

    print(f"[INFO] Fluxos disponíveis: {len(fluxos)} nós.")

    # O instalador já determina como executar o Docker.
    # O importador utiliza esse acesso, sem pedir sudo internamente.
    docker = ["docker"]

    teste = executar(*docker, "info")

    if teste.returncode != 0:
        print("[ERRO] Sem acesso ao Docker.")
        print("[INFO] Execute o importador com permissões Docker.")
        return 1

    # Verificar se existem fluxos reais no volume.
    verificacao = executar(
        *docker,
        "exec",
        CONTENTOR,
        "cat",
        "/data/flows.json",
    )

    if verificacao.returncode == 0:
        try:
            existentes = json.loads(verificacao.stdout)

            if not isinstance(existentes, list):
                print("[ERRO] Formato inesperado dos fluxos existentes.")
                return 1

            # Uma instalação inicial do Node-RED pode conter
            # apenas um separador vazio e um comentário informativo.
            tipos_iniciais = {"tab", "comment"}

            instalacao_inicial = (
                len(existentes) <= 2
                and all(
                    isinstance(no, dict)
                    and no.get("type") in tipos_iniciais
                    for no in existentes
                )
                and not any(
                    no.get("type") == "tab"
                    and no.get("label") != "Flow 1"
                    for no in existentes
                )
            )

            if existentes and not instalacao_inicial:
                print(f"[OK] Fluxos existentes preservados: {len(existentes)} nós.")
                return 0

            if instalacao_inicial:
                print("[INFO] Apenas os nós iniciais do Node-RED foram encontrados.")

        except json.JSONDecodeError:
            print("[ERRO] Ficheiro de fluxos existente inválido.")
            return 1

    # Copiar os fluxos apenas numa instalação nova.
    copia = executar(
        *docker,
        "cp",
        str(FLUXOS),
        f"{CONTENTOR}:/data/flows.json",
    )

    if copia.returncode != 0:
        print("[ERRO] Não foi possível copiar os fluxos.")
        print(copia.stderr)
        return 1

    reinicio = executar(
        *docker,
        "restart",
        CONTENTOR,
    )

    if reinicio.returncode != 0:
        print("[ERRO] Não foi possível reiniciar o Node-RED.")
        print(reinicio.stderr)
        return 1

    print("[OK] Fluxos do Node-RED instalados automaticamente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())