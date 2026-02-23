"""JSON-Export fuer Workflows."""
import json
from pathlib import Path


def export_workflow_json(workflow: dict, output_path: str) -> str:
    """Workflow als n8n-kompatible JSON-Datei exportieren."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    wf_data = json.loads(workflow["workflow_json"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(wf_data, f, indent=2, ensure_ascii=False)

    return str(path)


def export_all_workflows(db, output_dir: str) -> list:
    """Alle Workflows als einzelne JSON-Dateien exportieren."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    exported = []

    for wf in db.list_workflows():
        safe_name = wf["name"].replace(" ", "_").replace("/", "_")[:50]
        filename = f"{wf['id']}_{safe_name}.json"
        path = export_workflow_json(wf, str(out / filename))
        exported.append(path)

    return exported
