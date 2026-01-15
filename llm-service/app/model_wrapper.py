import subprocess
import json
import tempfile


def llama_generate(system: str, user: str):
    """
    Вызывает LLaMA через Ollama.
    Собирает system + user в один prompt.
    """

    full_prompt = f"<|system|>\n{system}\n<|user|>\n{user}"

    result = subprocess.run(
        ["ollama", "run", "llama3.2:1b"],
        input=full_prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())

    return result.stdout.decode().strip()
