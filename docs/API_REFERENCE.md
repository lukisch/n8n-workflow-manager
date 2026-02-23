# n8nManager API-Referenz

Die vollstaendige, interaktive API-Dokumentation ist verfuegbar unter:
**http://localhost:8100/docs** (Swagger UI)

## Endpoints

### Workflows

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| GET | `/api/workflows` | Alle Workflows auflisten |
| GET | `/api/workflows/{id}` | Workflow abrufen |
| POST | `/api/workflows` | Workflow erstellen |
| PUT | `/api/workflows/{id}` | Workflow aktualisieren |
| DELETE | `/api/workflows/{id}` | Workflow loeschen |
| POST | `/api/workflows/build` | Workflow programmatisch erstellen |
| POST | `/api/import` | JSON-Datei importieren |

### Server

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| GET | `/api/servers` | Alle Server auflisten |
| GET | `/api/servers/{id}` | Server abrufen |
| POST | `/api/servers` | Server hinzufuegen |
| PUT | `/api/servers/{id}` | Server aktualisieren |
| POST | `/api/servers/{id}/ping` | Verbindung testen |

### Sync

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| POST | `/api/export/{id}/to-server` | Workflow auf Server pushen |
| POST | `/api/pull/{server_id}` | Workflows vom Server ziehen |
| GET | `/api/sync/history` | Sync-Historie abrufen |

### Templates

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| GET | `/api/templates` | Vorlagen auflisten |
| GET | `/api/templates/{id}` | Vorlage abrufen |
| POST | `/api/templates` | Vorlage erstellen |
| POST | `/api/templates/{id}/instantiate` | Vorlage instanziieren |

### BACH

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| POST | `/api/bach/register-workflow` | In BACH registrieren |

### System

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| GET | `/api/status` | System-Status |

## Workflow erstellen (Build API)

Fuer Claude Code und programmatische Nutzung:

```json
POST /api/workflows/build
{
    "name": "Mein Workflow",
    "nodes": [
        {
            "type": "n8n-nodes-base.webhook",
            "name": "Trigger",
            "parameters": {"path": "/test", "httpMethod": "POST"}
        },
        {
            "type": "n8n-nodes-base.code",
            "name": "Verarbeitung",
            "parameters": {"jsCode": "return $input.all();"}
        }
    ],
    "connections": [
        {"from_node": "Trigger", "to_node": "Verarbeitung"}
    ]
}
```

## Authentifizierung

Aktuell keine Authentifizierung (lokales Tool).
n8n-Server-Kommunikation nutzt `X-N8N-API-KEY` Header.
