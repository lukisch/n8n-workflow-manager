"""Parsing und Validierung von n8n Workflow JSON."""
import json
import hashlib
from typing import Optional


def validate_workflow(data: dict) -> tuple[bool, str]:
    """Prueft ob ein dict ein gueltiger n8n Workflow ist. Returns (valid, error_msg)."""
    if not isinstance(data, dict):
        return False, "Kein dict"
    if "nodes" not in data:
        return False, "Pflichtfeld 'nodes' fehlt"
    if "connections" not in data:
        return False, "Pflichtfeld 'connections' fehlt"
    if not isinstance(data["nodes"], list):
        return False, "'nodes' muss eine Liste sein"
    if not isinstance(data["connections"], dict):
        return False, "'connections' muss ein dict sein"
    return True, ""


def load_workflow_file(path: str) -> tuple[Optional[dict], str]:
    """Laedt n8n JSON-Datei. Returns (data, error_msg)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        valid, err = validate_workflow(data)
        if not valid:
            return None, err
        return data, ""
    except json.JSONDecodeError as e:
        return None, f"JSON-Fehler: {e}"
    except FileNotFoundError:
        return None, f"Datei nicht gefunden: {path}"


def compute_content_hash(workflow_json: str) -> str:
    """SHA-256 Hash des Workflow-JSON fuer Duplikat-Erkennung."""
    normalized = json.dumps(json.loads(workflow_json), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def extract_metadata(data: dict) -> dict:
    """Extrahiert Metadaten aus n8n Workflow dict."""
    nodes = data.get("nodes", [])
    trigger_type = ""
    for node in nodes:
        ntype = node.get("type", "")
        if "trigger" in ntype.lower() or "webhook" in ntype.lower():
            trigger_type = ntype
            break
    tags = [t.get("name", "") for t in data.get("tags", [])] if isinstance(data.get("tags"), list) else []
    return {
        "node_count": len(nodes),
        "trigger_type": trigger_type,
        "tags": tags,
        "name": data.get("name", "Unbenannt"),
    }


def workflow_to_vis_graph(data: dict) -> dict:
    """Konvertiert n8n Workflow in vis.js Graph-Daten (nodes + edges)."""
    vis_nodes = []
    vis_edges = []
    node_map = {}  # n8n node name -> vis id

    for i, node in enumerate(data.get("nodes", [])):
        node_name = node.get("name", f"Node_{i}")
        node_type = node.get("type", "unknown")
        node_map[node_name] = i

        # Position aus n8n uebernehmen
        pos = node.get("position", [100 + i * 200, 200])

        # Farbe nach Kategorie
        color = _get_node_color(node_type)

        vis_nodes.append({
            "id": i,
            "label": node_name,
            "title": f"{node_type}\n{node_name}",
            "x": pos[0] if isinstance(pos, list) and len(pos) > 0 else 100 + i * 200,
            "y": pos[1] if isinstance(pos, list) and len(pos) > 1 else 200,
            "color": color,
            "shape": "box",
            "font": {"color": "#ffffff"},
            "n8n_type": node_type,
            "n8n_params": node.get("parameters", {}),
        })

    connections = data.get("connections", {})
    edge_id = 0
    for source_name, outputs in connections.items():
        source_id = node_map.get(source_name)
        if source_id is None:
            continue
        if isinstance(outputs, dict):
            # n8n v1 format: {"main": [[{"node": "target", "type": "main", "index": 0}]]}
            for output_type, output_lists in outputs.items():
                if isinstance(output_lists, list):
                    for output_list in output_lists:
                        if isinstance(output_list, list):
                            for conn in output_list:
                                target_name = conn.get("node", "")
                                target_id = node_map.get(target_name)
                                if target_id is not None:
                                    vis_edges.append({
                                        "id": edge_id,
                                        "from": source_id,
                                        "to": target_id,
                                        "arrows": "to",
                                    })
                                    edge_id += 1

    return {"nodes": vis_nodes, "edges": vis_edges}


def _get_node_color(node_type: str) -> str:
    """Farbe basierend auf n8n Node-Typ."""
    t = node_type.lower()
    if "trigger" in t or "webhook" in t:
        return "#ff6d5a"  # Orange - Trigger
    elif "if" in t or "switch" in t or "merge" in t:
        return "#ffcc00"  # Gelb - Bedingung
    elif "langchain" in t or "agent" in t or "openai" in t:
        return "#9b59b6"  # Violett - AI
    elif "email" in t or "slack" in t or "telegram" in t or "send" in t:
        return "#28a745"  # Gruen - Aktion
    elif "bach" in t:
        return "#e74c3c"  # Rot - BACH
    else:
        return "#4285f4"  # Blau - Verarbeitung
