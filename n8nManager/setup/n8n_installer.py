"""n8n via Docker auf Remote-Server installieren."""
import json
import secrets
from pathlib import Path
from typing import Optional

from n8nManager.setup.ssh_helper import SSHHelper


class N8nInstaller:
    """Installiert n8n per Docker auf einem Remote-Server."""

    def __init__(self, host: str, user: str = "root",
                 ssh_key: Optional[str] = None, port: int = 22,
                 n8n_port: int = 5678):
        self.ssh = SSHHelper(host, user, ssh_key, port)
        self.host = host
        self.n8n_port = n8n_port
        self._log = []

    def log(self, msg: str):
        self._log.append(msg)
        print(f"  [n8n-setup] {msg}")

    def get_log(self) -> list:
        return list(self._log)

    def install(self) -> dict:
        """Komplette n8n-Installation durchfuehren."""
        self.log(f"Verbinde zu {self.host}...")

        # 1. Verbindung testen
        conn = self.ssh.test_connection()
        if not conn["ok"]:
            self.log(f"SSH-Fehler: {conn['stderr']}")
            return {"ok": False, "error": "SSH-Verbindung fehlgeschlagen", "log": self._log}
        self.log(f"Verbunden: {conn['stdout']}")

        # 2. Docker installieren (falls nicht vorhanden)
        if not self.ssh.command_exists("docker"):
            self.log("Docker nicht gefunden, installiere...")
            result = self._install_docker()
            if not result["ok"]:
                return {"ok": False, "error": "Docker-Installation fehlgeschlagen", "log": self._log}
            self.log("Docker installiert")
        else:
            self.log("Docker bereits vorhanden")

        # 3. Pruefen ob n8n Container bereits laeuft
        check = self.ssh.run("docker ps --filter name=n8n --format '{{.Names}}'")
        if "n8n" in check.get("stdout", ""):
            self.log("n8n Container laeuft bereits")
        else:
            # 4. n8n Container starten
            self.log("Starte n8n Container...")
            result = self._start_n8n_container()
            if not result["ok"]:
                return {"ok": False, "error": "n8n-Start fehlgeschlagen", "log": self._log}
            self.log("n8n Container gestartet")

        # 5. Warten bis n8n bereit ist
        self.log("Warte auf n8n Bereitschaft...")
        import time
        for i in range(30):
            health = self.ssh.run(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{self.n8n_port}/healthz", timeout=10)
            if health.get("stdout", "").strip() == "200":
                break
            time.sleep(2)
        else:
            self.log("n8n antwortet nicht nach 60 Sekunden")
            return {"ok": False, "error": "n8n Timeout", "log": self._log}
        self.log("n8n ist bereit")

        # 6. API-Key Info
        self.log("HINWEIS: API-Key muss manuell in n8n unter Settings > API erstellt werden")
        self.log(f"n8n erreichbar unter: http://{self.host}:{self.n8n_port}")

        return {
            "ok": True,
            "url": f"http://{self.host}:{self.n8n_port}",
            "message": "n8n erfolgreich installiert",
            "log": self._log,
        }

    def _install_docker(self) -> dict:
        """Docker auf Ubuntu installieren."""
        commands = [
            "apt-get update -y",
            "apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release",
            "curl -fsSL https://get.docker.com | sh",
            "systemctl enable docker && systemctl start docker",
        ]
        for cmd in commands:
            self.log(f"  > {cmd[:60]}...")
            result = self.ssh.run(cmd, timeout=300)
            if not result["ok"]:
                self.log(f"  FEHLER: {result['stderr'][:200]}")
                return result
        return {"ok": True}

    def _start_n8n_container(self) -> dict:
        """n8n Docker Container starten."""
        cmd = (
            f"docker run -d "
            f"--name n8n "
            f"--restart unless-stopped "
            f"-p {self.n8n_port}:5678 "
            f"-v n8n_data:/home/node/.n8n "
            f"-e N8N_SECURE_COOKIE=false "
            f"n8nio/n8n"
        )
        return self.ssh.run(cmd, timeout=180)

    def uninstall(self) -> dict:
        """n8n Container stoppen und entfernen."""
        self.log("Stoppe n8n Container...")
        self.ssh.run("docker stop n8n", timeout=30)
        self.ssh.run("docker rm n8n", timeout=30)
        self.log("n8n Container entfernt")
        return {"ok": True, "log": self._log}

    def status(self) -> dict:
        """n8n Status abfragen."""
        result = self.ssh.run("docker ps --filter name=n8n --format '{{.Status}}'")
        running = bool(result.get("stdout", "").strip())
        return {
            "running": running,
            "status": result.get("stdout", "").strip() or "nicht gefunden",
            "url": f"http://{self.host}:{self.n8n_port}" if running else None,
        }
