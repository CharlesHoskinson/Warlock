import {adapt} from './model-adapter.js';

const $ = selector => document.querySelector(selector);
const el = (tag, text, className) => { const node = document.createElement(tag); if (text != null) node.textContent = text; if (className) node.className = className; return node; };
const sourceBase = 'https://github.com/charleshoskinson/Warlock/blob/bc3daf7b80ac7295a1ba1e56639a0e130e520a3c/';
fetch('./architecture.json').then(response => { if (!response.ok) throw new Error('Model unavailable'); return response.json(); }).then(raw => {
  const {model, nodes, match} = adapt(raw);
  const map = $('#map'), svg = $('#edges'), details = $('#details'), selectedConnections = $('#selected-connections');
  const buttons = new Map(); let selected = null, highlighted = null, stepIndex = -1;
  const select = $('#flow-select');
  model.flows.forEach(flow => {const option = el('option', flow.name); option.value = flow.id; select.append(option);});
  const flow = () => model.flows.find(item => item.id === select.value);
  const name = id => nodes.get(id)?.name || id;
  function draw() {
    svg.replaceChildren();
    if (!highlighted) return;
    const a = buttons.get(highlighted.from), b = buttons.get(highlighted.to);
    if (!a || !b) return;
    const box = map.getBoundingClientRect(), ar = a.getBoundingClientRect(), br = b.getBoundingClientRect();
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    for (const [key, value] of Object.entries({x1: ar.left + ar.width / 2 - box.left, y1: ar.top + ar.height / 2 - box.top, x2: br.left + br.width / 2 - box.left, y2: br.top + br.height / 2 - box.top})) line.setAttribute(key, value);
    svg.append(line);
  }
  function highlight(edge) {
    highlighted = edge;
    buttons.forEach(button => delete button.dataset.hop);
    if (edge) {buttons.get(edge.from).dataset.hop = 'from'; buttons.get(edge.to).dataset.hop = 'to';}
    draw();
  }
  function selectNode(id, moveFocus = false) {
    const node = nodes.get(id); if (!node) return;
    selected = id;
    buttons.forEach((button, key) => button.setAttribute('aria-pressed', String(key === id)));
    const heading = el('h3', node.name); heading.id = 'details-heading'; details.replaceChildren(heading);
    const list = el('dl');
    function field(label, values, links = false) {
      list.append(el('dt', label)); const dd = el('dd');
      if (Array.isArray(values) && values.length) {const ul = el('ul'); values.forEach(value => {const li = el('li'); if (links) {const a = el('a', value + ' (GitHub)'); a.href = sourceBase + value.split('/').map(encodeURIComponent).join('/'); li.append(a);} else li.textContent = value; ul.append(li);}); dd.append(ul);}
      else dd.textContent = Array.isArray(values) ? 'None listed' : values;
      list.append(dd);
    }
    field('Summary', node.summary); field('Kind', node.kind); field('Language', node.language); field('Layer', model.layers.find(layer => layer.id === node.layer).name); field('Source files', node.files, true); field('Ports', node.ports); field('Rendered windows', node.renders); field('Variant', node.variant);
    details.append(list); details.setAttribute('aria-label', 'Details for ' + node.name);
    selectedConnections.replaceChildren();
    const connections = model.edges.filter(edge => edge.from === id || edge.to === id);
    if (!connections.length) selectedConnections.append(el('p', 'No connections listed.'));
    const ul = el('ul'); connections.forEach(edge => {const li = el('li'); const button = el('button', `${name(edge.from)} → ${name(edge.to)}: ${edge.channel}`); button.type = 'button'; button.addEventListener('click', () => highlight(edge)); li.append(button, el('p', `Messages: ${edge.messages.join('; ')}. ${edge.summary}`)); ul.append(li);}); selectedConnections.append(ul);
    if (moveFocus) details.focus();
  }
  model.layers.forEach((layer, layerIndex) => {
    const section = el('section', null, 'architecture-band'); section.append(el('h3', layer.name), el('p', layer.summary));
    const group = el('div', null, 'architecture-nodes'); const members = model.nodes.filter(node => node.layer === layer.id);
    members.forEach((node, index) => {
      const button = el('button', node.name, 'architecture-node'); button.type = 'button'; button.setAttribute('aria-pressed', 'false'); button.dataset.node = node.id;
      button.addEventListener('click', () => selectNode(node.id, true));
      button.addEventListener('keydown', event => {
        let target;
        if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') target = members[(index + (event.key === 'ArrowRight' ? 1 : -1) + members.length) % members.length];
        if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {const nextLayer = model.layers[layerIndex + (event.key === 'ArrowDown' ? 1 : -1)]; if (nextLayer) {const next = model.nodes.filter(item => item.layer === nextLayer.id); target = next[Math.min(index, next.length - 1)];}}
        if (target) {event.preventDefault(); buttons.get(target.id).focus();}
      });
      buttons.set(node.id, button); group.append(button);
    }); section.append(group); map.append(section);
  });
  document.querySelectorAll('#components [data-node]').forEach(button => button.addEventListener('click', () => {selectNode(button.dataset.node, true); details.scrollIntoView({block:'nearest'});}));
  details.addEventListener('keydown', event => {if (event.key === 'Escape' && selected) {event.preventDefault(); buttons.get(selected).focus();}});
  function renderFlow(announce = false) {
    const current = flow(); $('#flow-summary').textContent = current.summary;
    $('#previous').disabled = stepIndex < 0; $('#next').disabled = stepIndex >= current.steps.length - 1;
    const list = $('#current-steps'); list.replaceChildren();
    current.steps.forEach((step, index) => {const li = el('li', `${name(step.from)} → ${name(step.to)}: ${step.message}. ${step.summary}`); if (index === stepIndex) li.setAttribute('aria-current', 'step'); list.append(li);});
    if (stepIndex < 0) {$('#step-display').textContent = 'Ready. Select Next to begin.'; highlight(null); return;}
    const step = current.steps[stepIndex], connection = match(step);
    const text = `Step ${stepIndex + 1} of ${current.steps.length}. ${name(step.from)} to ${name(step.to)}. ${step.message}. ${step.summary}`;
    $('#step-display').textContent = connection ? `${text} Channel: ${connection.edge.channel}.` : `${text} Data-consistency error: no unique matching connection in the model.`;
    highlight(connection ? connection.edge : null);
    if (announce) $('#step-announcement').textContent = text;
  }
  select.addEventListener('change', () => {stepIndex = -1; renderFlow();});
  $('#next').addEventListener('click', () => {stepIndex = Math.min(stepIndex + 1, flow().steps.length - 1); renderFlow(true);});
  $('#previous').addEventListener('click', () => {stepIndex = Math.max(-1, stepIndex - 1); renderFlow(stepIndex >= 0);});
  $('#reset').addEventListener('click', () => {stepIndex = -1; renderFlow(); $('#step-announcement').textContent = 'Flow reset.';});
  $('#interactive').hidden = false; $('#player').hidden = false; renderFlow();
  window.addEventListener('resize', draw);
}).catch(() => {$('#load-error').textContent = 'The interactive model could not load. The complete tables and flow steps are available below.';});
