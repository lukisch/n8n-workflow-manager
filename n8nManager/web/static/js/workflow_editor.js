/**
 * Workflow Editor -- vis.js Manipulation-Modus
 */
let editorNetwork = null;
let editorNodes = null;
let editorEdges = null;
let currentNodeCatalog = [];

function initEditor(containerId, graphData, nodeCatalog, workflowId) {
    currentNodeCatalog = nodeCatalog || [];
    renderCatalog();

    const container = document.getElementById(containerId);
    editorNodes = new vis.DataSet(graphData.nodes.map(n => ({
        id: n.id,
        label: n.label,
        x: n.x, y: n.y,
        color: {background: n.color, border: n.color},
        shape: 'box',
        font: {color: '#fff', size: 14},
        shadow: true,
    })));
    editorEdges = new vis.DataSet(graphData.edges.map(e => ({
        id: e.id, from: e.from, to: e.to, arrows: 'to',
        color: {color: '#888'}, smooth: {type: 'cubicBezier'},
    })));

    editorNetwork = new vis.Network(container, {nodes: editorNodes, edges: editorEdges}, {
        physics: false,
        manipulation: {
            enabled: true,
            addNode: function(data, callback) {
                data.label = 'Neuer Node';
                data.color = {background: '#4285f4', border: '#4285f4'};
                data.shape = 'box';
                data.font = {color: '#fff'};
                callback(data);
            },
            addEdge: function(data, callback) {
                data.arrows = 'to';
                callback(data);
            },
        },
        interaction: {hover: true},
    });
}

function initCreator(containerId, nodeCatalog) {
    initEditor(containerId, {nodes: [], edges: []}, nodeCatalog, null);
}

function renderCatalog() {
    const list = document.getElementById('node-catalog-list');
    if (!list) return;
    list.innerHTML = '';
    const categories = {};
    currentNodeCatalog.forEach(n => {
        const cat = n.category || 'other';
        if (!categories[cat]) categories[cat] = [];
        categories[cat].push(n);
    });
    Object.entries(categories).forEach(([cat, nodes]) => {
        const h4 = document.createElement('h4');
        h4.textContent = cat;
        list.appendChild(h4);
        nodes.forEach(n => {
            const btn = document.createElement('button');
            btn.className = 'catalog-btn';
            btn.style.borderLeft = '4px solid ' + (n.color || '#666');
            btn.textContent = n.display_name || n.node_type;
            btn.title = n.description || '';
            btn.onclick = () => addNodeFromCatalog(n);
            list.appendChild(btn);
        });
    });
}

function addNodeFromCatalog(catalogNode) {
    if (!editorNodes) return;
    const id = Date.now();
    editorNodes.add({
        id: id,
        label: catalogNode.display_name || catalogNode.node_type,
        color: {background: catalogNode.color || '#666', border: catalogNode.color || '#666'},
        shape: 'box',
        font: {color: '#fff'},
        x: 300 + Math.random() * 200,
        y: 200 + Math.random() * 200,
    });
}

async function saveWorkflow() {
    alert('Speichern wird implementiert -- Workflow-ID: ' + (typeof workflowId !== 'undefined' ? workflowId : 'neu'));
}

async function saveNewWorkflow() {
    const name = document.getElementById('workflow-name')?.value || 'Neuer Workflow';
    alert('Workflow "' + name + '" erstellen -- wird implementiert');
}
