/* paper-reading lab page. Copied unchanged into studio/. Builds each lab's controls from GET /api/labs,
 * runs the lab on the backend (POST /api/labs/<name>) whenever a control changes, and shows the result:
 * summary, input, the traditional method and the paper's method side by side, failure cases, provenance.
 * With ?selftest it runs every lab with two settings and writes the outcome into <pre id="lab-selftest">. */
(function () {
  'use strict';
  const $ = (sel, root) => (root || document).querySelector(sel);
  const el = (tag, attrs, ...kids) => {
    const e = document.createElement(tag);
    for (const k in attrs || {}) {
      if (k === 'class') e.className = attrs[k]; else if (k === 'text') e.textContent = attrs[k];
      else if (k === 'html') e.innerHTML = attrs[k]; else e.setAttribute(k, attrs[k]);
    }
    kids.forEach(c => c != null && e.append(c));
    return e;
  };
  const fmt = v => (window.PR && PR.fmt ? PR.fmt(v) : String(v));

  let labs = [], current = null, params = {}, inflight = null, timer = null, lastOk = null;

  // ---------- address: #lab=name&key=value keeps the view shareable ----------
  function readHash() {
    const h = new URLSearchParams(location.hash.slice(1));
    return { lab: h.get('lab'), values: Object.fromEntries([...h.entries()].filter(([k]) => k !== 'lab')) };
  }
  function writeHash() {
    const h = new URLSearchParams({ lab: current.name });
    Object.entries(params).forEach(([k, v]) => h.set(k, v));
    history.replaceState(null, '', '#' + h.toString());
  }

  // ---------- start ----------
  async function start() {
    if (location.protocol === 'file:') return notServed();
    try {
      const r = await fetch('/api/labs');
      labs = await r.json();
    } catch (e) { return notServed(); }
    if (!labs.length) { $('#lab').innerHTML = '<p class="empty">studio/server.py has no labs registered yet.</p>'; return; }
    const list = $('#lab-list');
    labs.forEach(l => {
      const b = el('button', { type: 'button', 'data-lab': l.name }, l.title, el('span', { class: 'src', text: l.source }));
      b.addEventListener('click', () => open(l.name));
      list.append(b);
    });
    if (location.search.includes('selftest')) return selftest();
    const h = readHash();
    open(labs.some(l => l.name === h.lab) ? h.lab : labs[0].name, h.values);
    window.addEventListener('keydown', ev => {
      if (ev.target.matches('input, select, textarea')) return;
      const i = labs.findIndex(l => l.name === current.name);
      if (ev.key === ']' && labs[i + 1]) open(labs[i + 1].name);
      if (ev.key === '[' && labs[i - 1]) open(labs[i - 1].name);
    });
  }

  function notServed() {
    $('#lab').innerHTML = '';
    $('#lab').append(el('div', { class: 'empty' },
      el('h1', { text: 'The backend is not running' }),
      el('p', { html: 'Labs are computed by the Python backend, so this page must be opened through it. Run <code>python serve.py</code> in the topic folder; the page opens at <code>http://127.0.0.1:&lt;port&gt;/studio/lab.html</code>.' }),
      el('p', { html: 'The reading page needs no backend: <a href="../index.html">open the reading page</a>.' })));
  }

  // ---------- one lab ----------
  function open(name, values) {
    current = labs.find(l => l.name === name);
    params = {};
    current.params.forEach(p => {
      let v = values && values[p.key] !== undefined ? values[p.key] : p.value;
      if (p.type === 'range') v = +v; else if (p.type === 'check') v = v === true || v === 'true';
      else if (p.type === 'sample') { const o = p.options.find(o => String(o.value) === String(v)); v = o ? o.value : p.value; }
      params[p.key] = v;
    });
    document.querySelectorAll('#lab-list button').forEach(b => b.classList.toggle('on', b.dataset.lab === name));
    document.title = current.title + ' - Real-data labs';
    const main = $('#lab');
    main.innerHTML = '';
    const chips = el('div', { class: 'chips' }, el('span', { class: 'chip', text: 'Paper source: ' + current.source }));
    current.knowledge.forEach(k => chips.append(el('a', { class: 'chip', href: '../index.html#kp-' + k, text: 'Knowledge point ' + k })));
    main.append(el('h1', { text: current.title }), el('p', { class: 'question', text: current.question }), chips);
    const panel = el('aside', { class: 'panel' }, el('h2', { text: 'Settings' }));
    current.params.forEach(p => panel.append(control(p)));
    const reset = el('button', { type: 'button', text: 'Reset' });
    reset.addEventListener('click', () => open(current.name));
    const share = el('button', { type: 'button', text: 'Copy link' });
    share.addEventListener('click', async () => { try { await navigator.clipboard.writeText(location.href); share.textContent = 'Copied'; } catch (e) { share.textContent = 'Copy failed'; } setTimeout(() => (share.textContent = 'Copy link'), 1500); });
    panel.append(el('div', { class: 'actions' }, reset, share), el('div', { class: 'status', id: 'status' }, el('span', { class: 'dot' }), el('span', { text: 'Ready' })));
    main.append(el('div', { class: 'work' }, panel, el('section', { class: 'results', id: 'results' })));
    lastOk = null;
    run();
  }

  function control(p) {
    const box = el('div', { class: 'ctl' });
    const val = el('span', { class: 'v' });
    let input;
    if (p.type === 'range') {
      input = el('input', { type: 'range', min: p.min, max: p.max, step: p.step || 1, value: params[p.key], 'aria-label': p.label });
      val.textContent = fmt(params[p.key]);
      input.addEventListener('input', () => { params[p.key] = +input.value; val.textContent = fmt(+input.value); schedule(220); });
    } else if (p.type === 'check') {
      input = el('input', { type: 'checkbox', 'aria-label': p.label });
      input.checked = !!params[p.key];
      input.addEventListener('change', () => { params[p.key] = input.checked; schedule(0); });
    } else {
      input = el('select', { 'aria-label': p.label });
      p.options.forEach(o => { const v = typeof o === 'object' ? o.value : o, t = typeof o === 'object' ? o.label : o; input.append(el('option', { value: v, text: t })); });
      input.value = params[p.key];
      input.addEventListener('change', () => {
        const o = p.options.find(o => String(typeof o === 'object' ? o.value : o) === input.value);
        params[p.key] = typeof o === 'object' ? o.value : o; schedule(0);
      });
    }
    input.dataset.key = p.key;
    const row = el('div', { class: 'row' }, el('label', { text: p.label }), p.type === 'range' ? val : null);
    box.append(row, input);
    if (p.help) box.append(el('div', { class: 'help', text: p.help }));
    return box;
  }

  function schedule(ms) { clearTimeout(timer); timer = setTimeout(run, ms); }

  function setStatus(kind, text) {
    const s = $('#status'); if (!s) return;
    s.className = 'status' + (kind ? ' ' + kind : '');
    s.lastChild.textContent = text;
  }

  // ---------- run on the backend; a newer request cancels an older one ----------
  async function run() {
    writeHash();
    if (inflight) inflight.abort();
    const ctrl = (inflight = new AbortController());
    const results = $('#results');
    results.classList.add('busy');
    setStatus('busy', 'Computing on the backend…');
    try {
      const r = await fetch('/api/labs/' + current.name, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(params), signal: ctrl.signal });
      const data = await r.json();
      if (ctrl !== inflight) return;
      if (!r.ok || data.error) throw Object.assign(new Error(data.error || r.statusText), { trace: data.trace });
      render(data); lastOk = data;
      setStatus('', `Done in ${data.elapsed_ms} ms`);
    } catch (e) {
      if (e.name === 'AbortError') return;
      renderError(e);
      setStatus('err', 'Computation failed');
    } finally {
      if (ctrl === inflight) { results.classList.remove('busy'); inflight = null; }
    }
  }

  function plot(box, spec) { if (spec && window.PR && PR.plot) PR.plot(box, spec); }

  function render(d) {
    const res = $('#results');
    res.innerHTML = '';
    res.append(el('p', { class: 'summary', text: d.summary || '' }));
    if (d.input) {
      const c = el('div', { class: 'card' }, el('h3', { text: d.input.title || 'Input' }));
      res.append(c);  // on the page first, so the plot can take the card's width
      if (d.input.plot) plot(c, d.input.plot);
      if (d.input.image) c.append(el('figure', { class: 'figure' }, el('img', { class: 'input-img', src: '../' + d.input.image.replace(/^\/+/, ''), alt: d.input.title || 'Input' })));
      if (d.input.text) c.append(el('p', { text: d.input.text }));
    }
    if (d.methods && d.methods.length) {
      const row = el('div', { class: 'methods' });
      res.append(row);
      const scored = d.methods.filter(m => m.metric && typeof m.metric.value === 'number');
      let best = null;
      if (scored.length > 1) {
        const lower = (scored[0].metric.better || 'higher') === 'lower';
        best = scored.reduce((a, b) => ((lower ? b.metric.value < a.metric.value : b.metric.value > a.metric.value) ? b : a));
        if (scored.every(m => m.metric.value === best.metric.value)) best = null;
      }
      d.methods.forEach(m => {
        const card = el('div', { class: 'card method' + (m === best ? ' win' : '') });
        row.append(card);
        const head = el('div', { class: 'head' }, el('span', { class: 'kind ' + (m.kind || ''), text: m.kind === 'paper' ? "This paper's method" : m.kind === 'traditional' ? 'Traditional method' : (m.kind || '') }), el('h3', { text: m.name, style: 'margin:0' }));
        if (m === best) head.append(el('span', { class: 'win-tag', text: '✓ Better on this input' }));
        card.append(head);
        if (m.metric) card.append(el('div', { class: 'metric' }, el('b', { text: fmt(m.metric.value) }), el('span', { text: m.metric.label + (m.metric.better ? `(${m.metric.better === 'lower' ? 'lower is better' : 'higher is better'})` : '') })));
        if (m.plot) plot(card, m.plot);
        if (m.text) card.append(el('p', { class: 'note', text: m.text }));
      });
    }
    if (d.table && window.PR && PR.table) res.append(el('div', { class: 'card' }, PR.table(d.table)));
    if (d.failures && d.failures.length) {
      const c = el('div', { class: 'card' }, el('h3', { text: `Samples where the paper's method does worse (${d.failures.length}; click to load)` }));
      const f = el('div', { class: 'failures' });
      d.failures.forEach(x => {
        const b = el('button', { type: 'button' }, x.title, x.detail ? el('small', { text: x.detail }) : null);
        const sp = current.params.find(p => p.type === 'sample');
        if (sp && x.sample !== undefined) b.addEventListener('click', () => { params[sp.key] = x.sample; const s = document.querySelector(`[data-key="${sp.key}"]`); if (s) s.value = x.sample; run(); });
        else b.disabled = true;
        f.append(b);
      });
      c.append(f); res.append(c);
    }
    const prov = el('div', { class: 'card prov' }, el('h3', { text: 'Where these numbers come from' }), el('div', { class: 'live', text: d.provenance.live }));
    (d.provenance.remote || []).forEach(m => prov.append(el('div', { class: 'remote', text: `Computed by the project's existing backend: ${m.about} (${m.url}, ${m.ms} ms)` })));
    (d.provenance.cached || []).forEach(m => prov.append(el('div', { class: 'cache', text: `Cached: ${m.about}, computed on this machine at ${m.computed.replace('T', ' ')} (took ${m.seconds} s) and reused this time` })));
    if (d.note) prov.append(el('div', { class: 'note', text: d.note }));
    res.append(prov);
  }

  function renderError(e) {
    const res = $('#results');
    const retry = el('button', { type: 'button', text: 'Retry', class: 'chip', style: 'cursor:pointer;background:none' });
    retry.addEventListener('click', run);
    const card = el('div', { class: 'card error' }, el('h3', { text: 'The backend could not compute this setting' }), el('p', { text: e.message }));
    if (e.trace) card.append(el('details', {}, el('summary', { text: 'Error details' }), el('pre', { text: e.trace.join('\n') })));
    card.append(retry);
    if (lastOk) { render(lastOk); res.prepend(card, el('p', { class: 'note', text: 'Below is the result of the last successful computation.' })); }
    else { res.innerHTML = ''; res.append(card); }
  }

  // ---------- self-test: every lab with its defaults and one changed setting ----------
  async function selftest() {
    const out = [];
    for (const l of labs) {
      const row = { lab: l.name, ok: false };
      try {
        const base = Object.fromEntries(l.params.map(p => [p.key, p.value]));
        const alt = { ...base };
        const p = l.params.find(p => p.type === 'range') || l.params.find(p => p.type !== 'check');
        if (p) alt[p.key] = p.type === 'range' ? (p.value === p.max ? p.min : p.max) : (p.options.map(o => (typeof o === 'object' ? o.value : o)).find(v => v !== p.value));
        const call = async q => { const r = await fetch('/api/labs/' + l.name, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(q) }); return r.json(); };
        const a = await call(base), b = await call(alt);
        const strip = x => JSON.stringify({ ...x, elapsed_ms: 0, provenance: 0, params: 0 });
        row.error = a.error || b.error;
        row.changed = strip(a) !== strip(b);
        open(l.name); await new Promise(r => setTimeout(r, 50));
        while (inflight) await new Promise(r => setTimeout(r, 30));
        row.rendered = !!$('#results .summary') && ($('#results .summary').textContent || '').length > 0;
        row.methods = document.querySelectorAll('#results .method').length;
        row.ok = !row.error && row.changed && row.rendered;
      } catch (e) { row.error = String(e); }
      out.push(row);
    }
    let checks = [];
    try { checks = await (await fetch('/api/checks')).json(); } catch (e) { checks = [{ name: 'checks endpoint', ok: false, error: String(e) }]; }
    document.body.append(el('pre', { id: 'lab-selftest', text: JSON.stringify({ labs: out, checks }) }));
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
