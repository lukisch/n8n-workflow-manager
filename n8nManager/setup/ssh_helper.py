"""SSH-Verbindung und Befehlsausfuehrung fuer Remote-Server."""
import subprocess
import shlex
from pathlib import Path
from typing import Optional


class SSHHelper:
    """SSH-Verbindung via subprocess (ssh-Befehl)."""

    def __init__(self, host: str, user: str = "root",
                 ssh_key: Optional[str] = None, port: int = 22):
        self.host = host
        self.user = user
        self.ssh_key = ssh_key
        self.port = port

    def _ssh_cmd(self) -> list:
        """Basis-SSH-Befehl zusammenbauen."""
        cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=10"]
        if self.ssh_key:
            cmd.extend(["-i", str(self.ssh_key)])
        if self.port != 22:
            cmd.extend(["-p", str(self.port)])
        cmd.append(f"{self.user}@{self.host}")
        return cmd

    def run(self, command: str, timeout: int = 120) -> dict:
        """Befehl auf Remote-Server ausfuehren."""
        full_cmd = self._ssh_cmd() + [command]
        try:
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "ok": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "stdout": "", "stderr": "Timeout", "returncode": -1}
        except FileNotFoundError:
            return {"ok": False, "stdout": "", "stderr": "ssh nicht gefunden", "returncode": -1}

    def test_connection(self) -> dict:
        """Verbindung testen."""
        return self.run("echo 'SSH OK' && hostname && uptime", timeout=15)

    def file_exists(self, path: str) -> bool:
        """Pruefen ob Datei auf Server existiert."""
        result = self.run(f"test -f {shlex.quote(path)} && echo 'yes' || echo 'no'", timeout=10)
        return result.get("stdout", "").strip() == "yes"

    def command_exists(self, cmd: str) -> bool:
        """Pruefen ob Befehl auf Server verfuegbar ist."""
        result = self.run(f"which {shlex.quote(cmd)} && echo 'yes' || echo 'no'", timeout=10)
        return "yes" in result.get("stdout", "")
