/**
 * vis.js Graph Renderer fuer n8n Workflows
 */
let network = null;

function initGraph(containerId, graphData) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const nodes = new vis.DataSet(graphData.nodes.map(n => ({
        id: n.id,
        label: n.label,
        title: n.title || n.label,
        x: n.x,
        y: n.y,
        color: {background: n.color, border: n.color, highlight: {background: n.color, border: '#fff'}},
        shape: n.shape || 'box',
        font: n.font || {color: '#ffffff', size: 14},
        shadow: true,
    })));

    const edges = new vis.DataSet(graphData.edges.map(e => ({
        id: e.id,
        from: e.from,
        to: e.to,
        arrows: e.arrows || 'to',
        color: {color: '#888', highlight: '#333'},
        smooth: {type: 'cubicBezier'},
    })));

    const options = {
        physics: false,
        interaction: {hover: true, tooltipDelay: 200},
        edges: {width: 2},
        nodes: {borderWidth: 2, borderWidthSelected: 3},
    };

    network = new vis.Network(container, {nodes, edges}, options);

    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const node = graphData.nodes.find(n => n.id === nodeId);
            if (node) showNodeDetails(node);
        }
    });

    return network;
}

function showNodeDetails(node) {
    const nameEl = document.getElementById('detail-name');
    const paramsEl = document.getElementById('detail-params');
    const panel = document.getElementById('node-details');
    if (!nameEl || !paramsEl || !panel) return;
    nameEl.textContent = node.label + ' (' + (node.n8n_type || 'unknown') + ')';
    paramsEl.textContent = JSON.stringify(node.n8n_params || {}, null, 2);
    panel.classList.remove('hidden');
}
