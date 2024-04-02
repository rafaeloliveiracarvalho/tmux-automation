import subprocess

session_config = {
    "name": "work",
    "windows": [
        {
            "name": "mitraPRC",
            "command": "mitra-prc",
            "description": "Mitra para processador Preço",
        },
        {
            "name": "mitraPRCON",
            "command": "mitra-prcon",
            "description": "Mitra para processador Preço Online",
        },
        {
            "name": "dcomp",
            "command": "dcompup",
            "description": "Docker Compose (Kafka, Cassandra, etc.)",
        },
        {
            "name": "med",
            "command": "mediador-run-dev",
            "description": "Mediador",
        },
        {
            "name": "api",
            "command": "api-run",
            "description": "API",
        },
        {
            "name": "apiC",
            "command": "pg-cot && api-cot-run",
            "description": "API de Cotação",
        },
        {
            "name": "prio",
            "command": "priorizador",
            "description": "Processador Priorizador",
        },
        {
            "name": "ped",
            "command": "pedido",
            "description": "Processador de Pedido",
        },
        {
            "name": "reg",
            "command": "registro",
            "description": "Processador de Registro",
        },
        {
            "name": "cad",
            "command": "cadastro",
            "description": "Processador de Cadastro",
        },
        {
            "name": "cons",
            "command": "consulta",
            "description": "Processador de Consulta",
        },
        {
            "name": "prc",
            "command": "preco",
            "description": "Processador de Preco",
        },
        {
            "name": "prcON",
            "command": "preco-online",
            "description": "Processador de Preço Online",
        },
        {
            "name": "fech",
            "command": "fechamento",
            "description": "Processador de Fechamento",
        },
    ],
}


def create_session(session_name):
    subprocess.run(f"tmux new-session -d -s {session_name}", shell=True)


def create_window(session_name):
    subprocess.run(f"tmux new-window -t {session_name}", shell=True)


def rename_window(session_name, window_name, window_old_name_or_pos):
    subprocess.run(
        f"tmux rename-window -t {session_name}:{window_old_name_or_pos} {window_name}",
        shell=True,
    )


def check_session_exist(session_name):
    info = subprocess.run(
        f"tmux has-session -t {session_name}",
        shell=True,
        capture_output=True,
        text=True,
    )

    return info.stderr == ""


def get_windows_list_by_session(session_name):
    result = subprocess.run(
        f"tmux list-windows -t {session_name}",
        shell=True,
        capture_output=True,
        text=True,
    ).stdout

    return [
        {
            "order": int(window.split(":")[0]),
            "name": window.split(":")[1].strip().split(" ")[0],
        }
        for window in filter(lambda x: x != "", result.split("\n"))
    ]


def check_window_exist(pos, win, windows_list):
    return len(windows_list) > pos and win["name"] in windows_list[pos]["name"]


def run_command_in_window(session_name, window_name, command):
    subprocess.run(
        f"tmux send-keys -t {session_name}:{window_name} '{command}' Enter",
        shell=True,
    )


def run_container_if_not_running(container_name, container_command):
    status = subprocess.run(
        f"docker inspect -f {'{{.State.Status}}'} {container_name}",
        shell=True,
        capture_output=True,
        text=True,
    )

    is_running = (
        status.returncode == 0 and "running" in status.stdout and status.stderr == ""
    )

    if is_running:
        print(f"Container {container_name} já está de pé.")
    else:
        print(f"Container {container_name} não está de pé. Subindo agora...")
        subprocess.run(container_command, shell=True)


if __name__ == "__main__":
    subprocess.run("tmux start-server", shell=True)
    windows_list = get_windows_list_by_session(session_config["name"])
    session_exist = check_session_exist(session_config["name"])

    if not session_exist:
        create_session(session_name=session_config["name"])

    for i, win in enumerate(session_config["windows"]):
        windows_list = get_windows_list_by_session(session_config["name"])
        win_exist = check_window_exist(i, win, windows_list)

        if win["name"] == "apiC":
            run_container_if_not_running(
                container_name="pgcotacoes", container_command="pg-cot"
            )
        elif win["name"] == "prio":
            run_container_if_not_running(
                container_name="processador-1", container_command="processador"
            )

        if not win_exist:
            create_window(session_name=session_config["name"])
            rename_window(
                session_name=session_config["name"],
                window_name=win["name"],
                window_old_name_or_pos=i,
            )

        print(f"Subindo {win['description']}")

        run_command_in_window(
            session_name=session_config["name"],
            window_name=win["name"],
            command=win["command"],
        )
