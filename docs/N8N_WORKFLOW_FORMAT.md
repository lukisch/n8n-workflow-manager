# n8n Workflow JSON-Format

## Grundstruktur

```json
{
    "name": "Workflow-Name",
    "nodes": [...],
    "connections": {...},
    "settings": {"executionOrder": "v1"},
    "active": false,
    "tags": [{"name": "Tag1"}]
}
```

## Nodes

Jeder Node hat:

```json
{
    "parameters": {},
    "type": "n8n-nodes-base.httpRequest",
    "typeVersion": 1,
    "position": [500, 300],
    "id": "unique-id",
    "name": "Anzeige-Name"
}
```

### Haeufige Node-Typen

| Typ | Beschreibung | Kategorie |
|-----|-------------|-----------|
| `n8n-nodes-base.manualTrigger` | Manueller Start | Trigger |
| `n8n-nodes-base.scheduleTrigger` | Zeitgesteuerter Start | Trigger |
| `n8n-nodes-base.webhook` | HTTP Webhook | Trigger |
| `n8n-nodes-base.httpRequest` | HTTP-Anfrage | Aktion |
| `n8n-nodes-base.if` | Bedingung | Logik |
| `n8n-nodes-base.switch` | Mehrfach-Bedingung | Logik |
| `n8n-nodes-base.set` | Daten setzen | Transform |
| `n8n-nodes-base.code` | JavaScript-Code | Transform |
| `n8n-nodes-base.emailSend` | Email senden | Aktion |
| `@n8n/n8n-nodes-langchain.agent` | AI-Agent | AI |

## Connections

Verbindungen von Source-Node zu Target-Node:

```json
{
    "Source Node Name": {
        "main": [
            [
                {"node": "Target Node Name", "type": "main", "index": 0}
            ]
        ]
    }
}
```

### Mehrere Ausgaenge (z.B. IF-Node)

```json
{
    "IF": {
        "main": [
            [{"node": "True Branch", "type": "main", "index": 0}],
            [{"node": "False Branch", "type": "main", "index": 0}]
        ]
    }
}
```

- `main[0]` = True/Erster Ausgang
- `main[1]` = False/Zweiter Ausgang

## Position

`[x, y]` Koordinaten fuer die visuelle Darstellung:
- x: Horizontal (links nach rechts)
- y: Vertikal (oben nach unten)
- Typisch: 250px Abstand zwischen Nodes
