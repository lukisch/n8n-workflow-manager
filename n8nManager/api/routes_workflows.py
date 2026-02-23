"""API-Routen fuer Workflows."""
import json
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

def _get_db():
    from n8nManager.api.server import get_db
    return get_db()

class WorkflowCreate(BaseModel):
    name: str
    description: str = ""
    workflow_json: str  # JSON-String des n8n Workflows
    source: str = "api"

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    workflow_json: Optional[str] = None
    is_active: Optional[bool] = None

class WorkflowBuild(BaseModel):
    """Fuer Claude Code: Workflow aus Beschreibung erstellen."""
    name: str
    nodes: list  # [{type, name, parameters}]
    connections: list  # [{from_node, to_node}]

@router.get("/workflows")
async def list_workflows(server_id: Optional[int] = None, source: Optional[str] = None):
    db = _get_db()
    workflows = db.list_workflows(server_id=server_id, source=source)
    return {"data": workflows, "count": len(workflows)}

@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: int):
    db = _get_db()
    wf = db.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow nicht gefunden")
    return wf

@router.post("/workflows")
async def create_workflow(body: WorkflowCreate):
    db = _get_db()
    from n8nManager.core.workflow_parser import validate_workflow
    try:
        data = json.loads(body.workflow_json)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Ungueltiges JSON: {e}")
    valid, err = validate_workflow(data)
    if not valid:
        raise HTTPException(status_code=400, detail=err)
    wf_id = db.add_workflow(
        name=body.name,
        workflow_json=body.workflow_json,
        description=body.description,
        source=body.source,
    )
    return {"id": wf_id, "message": "Workflow erstellt"}

@router.put("/workflows/{workflow_id}")
async def update_workflow(workflow_id: int, body: WorkflowUpdate):
    db = _get_db()
    wf = db.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow nicht gefunden")
    updates = {}
    if body.name is not None:
        updates["name"] = body.name
    if body.description is not None:
        updates["description"] = body.description
    if body.workflow_json is not None:
        from n8nManager.core.workflow_parser import validate_workflow
        try:
            data = json.loads(body.workflow_json)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Ungueltiges JSON: {e}")
        valid, err = validate_workflow(data)
        if not valid:
            raise HTTPException(status_code=400, detail=err)
        updates["workflow_json"] = body.workflow_json
    if body.is_active is not None:
        updates["is_active"] = 1 if body.is_active else 0
    if updates:
        db.update_workflow(workflow_id, **updates)
    return {"message": "Workflow aktualisiert"}

@router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: int):
    db = _get_db()
    wf = db.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow nicht gefunden")
    db.delete_workflow(workflow_id)
    return {"message": "Workflow geloescht"}

@router.post("/workflows/build")
async def build_workflow(body: WorkflowBuild):
    """Claude Code API: Workflow programmatisch erstellen."""
    from n8nManager.core.workflow_builder import WorkflowBuilder
    builder = WorkflowBuilder(name=body.name)
    node_names = {}
    for node_def in body.nodes:
        n = builder.add_node(
            node_type=node_def.get("type", "n8n-nodes-base.noOp"),
            name=node_def.get("name", ""),
            parameters=node_def.get("parameters", {}),
            position=node_def.get("position"),
        )
        node_names[node_def.get("name", n)] = n
    for conn in body.connections:
        source = conn.get("from_node", "")
        target = conn.get("to_node", "")
        if source in node_names and target in node_names:
            builder.connect(node_names[source], node_names[target])
    wf_data = builder.build()
    wf_json = json.dumps(wf_data, ensure_ascii=False)
    db = _get_db()
    wf_id = db.add_workflow(name=body.name, workflow_json=wf_json, source="api-build")
    return {"id": wf_id, "workflow": wf_data, "message": "Workflow erstellt via Builder"}

@router.post("/import")
async def import_workflow(file: UploadFile = File(...)):
    """n8n JSON-Datei importieren."""
    content = await file.read()
    try:
        data = json.loads(content.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise HTTPException(status_code=400, detail=f"Ungueltige Datei: {e}")
    from n8nManager.core.workflow_parser import validate_workflow, compute_content_hash
    valid, err = validate_workflow(data)
    if not valid:
        raise HTTPException(status_code=400, detail=err)
    wf_json = json.dumps(data, ensure_ascii=False)
    content_hash = compute_content_hash(wf_json)
    db = _get_db()
    if db.workflow_exists_by_hash(content_hash):
        raise HTTPException(status_code=409, detail="Workflow existiert bereits (Duplikat)")
    name = data.get("name", file.filename or "Import")
    wf_id = db.add_workflow(name=name, workflow_json=wf_json, source="import")
    return {"id": wf_id, "message": f"Workflow '{name}' importiert"}
