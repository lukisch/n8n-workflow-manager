# n8nManager Architektur

## Ueberblick

n8nManager ist ein FastAPI-basiertes Tool zur Verwaltung von n8n Workflows.
Es folgt dem MODULAR_AGENTS-Pattern (standalone + BACH-integrierbar).

## Schichten

```
+------------------------------------------+
|       Web-UI (Jinja2 + vis.js)           |
+------------------------------------------+
|       REST API (FastAPI)                 |
+------------------------------------------+
|  Core: Config | Database | Parser | Client | Builder
+------------------------------------------+
|  Setup: SSH | Docker | n8n Installer     |
+------------------------------------------+
|  Export: JSON | Markdown | BACH          |
+------------------------------------------+
|       SQLite (WAL-Modus)                 |
+------------------------------------------+
```

## Datenbank

6 Tabellen:
- `workflows` -- Workflow-JSON + Metadaten (Content-Hash, Nodes, Trigger)
- `servers` -- n8n Server-Instanzen (URL, API-Key, Default)
- `sync_history` -- Import/Export-Protokoll
- `templates` -- Workflow-Vorlagen mit Platzhaltern
- `workflow_versions` -- Aenderungsverlauf
- `node_catalog` -- Bekannte n8n Node-Typen + Farben

## Design-Entscheidungen

### Warum FastAPI + Jinja2 statt React?
- `&` im Pfad `KI&AI` bricht npm-Scripts (bekanntes Problem)
- BACH-Oekosystem ist 100% Python
- vis.js ueber CDN braucht keinen Build-Schritt
- FastAPI liefert automatische Swagger-Docs

### Warum vis.js?
- Robuste Graphen-Bibliothek fuer interaktive Netzwerke
- CDN-faehig (kein npm Build noetig)
- Manipulation-Modus fuer Editor-Funktionalitaet
- Gute Dokumentation

### Warum SQLite statt JSON-Dateien?
- Konsistentes Pattern mit ApiProber und BACH
- WAL-Modus fuer gleichzeitige Lese-/Schreibzugriffe
- Strukturierte Queries (Duplikat-Check, Versionierung)
- Content-Hash fuer Deduplizierung

## n8n Workflow-Format

n8n Workflows bestehen aus:
- `nodes`: Array von Node-Objekten (type, name, parameters, position)
- `connections`: Dict mit Source-Node -> Target-Node Mappings
- `settings`: Ausfuehrungseinstellungen
- `active`: Boolean
- `tags`: Array von Tag-Objekten

## vis.js Graph-Mapping

| n8n | vis.js |
|-----|--------|
| node.name | node.label |
| node.position[x,y] | node.x, node.y |
| node.type | node.color (Farbkodierung) |
| connections[source] | edge (from -> to) |

### Farbkodierung
- Orange (#ff6d5a): Trigger/Webhook
- Blau (#4285f4): Verarbeitung/HTTP/Code
- Gelb (#ffcc00): Bedingung (IF/Switch)
- Violett (#9b59b6): AI/LangChain
- Gruen (#28a745): Aktion (Email/Slack)
- Rot (#e74c3c): BACH

## API-Design

REST-Endpoints unter `/api/`:
- CRUD fuer Workflows, Server, Templates
- `/api/workflows/build` -- Programmatische Erstellung (Claude Code)
- `/api/export/{id}/to-server` -- Push zu n8n
- `/api/pull/{id}` -- Pull von n8n
- `/api/bach/register-workflow` -- BACH-Integration
- `/api/status` -- System-Info

Swagger-UI automatisch auf `/docs`.
