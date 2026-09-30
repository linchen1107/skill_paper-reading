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
    if (!labs.length) { $('#lab').innerHTML = '<p class="empty">studio/server.py 還沒有註冊任何實驗。</p>'; return; }
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
      el('h1', { text: '後端還沒有啟動' }),
      el('p', { html: '實驗由 Python 後端計算，所以這一頁要透過後端開啟。在主題資料夾執行 <code>python serve.py</code>，頁面會在 <code>http://127.0.0.1:&lt;埠號&gt;/studio/lab.html</code> 打開。' }),
      el('p', { html: '閱讀頁不需要後端：<a href="../index.html">開啟閱讀頁</a>。' })));
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
    document.title = current.title + '・真實資料實驗';
    const main = $('#lab');
    main.innerHTML = '';
    const chips = el('div', { class: 'chips' }, el('span', { class: 'chip', text: '原論文：' + current.source }));
    current.knowledge.forEach(k => chips.append(el('a', { class: 'chip', href: '../index.html#kp-' + k, text: '知識點 ' + k })));
    main.append(el('h1', { text: current.title }), el('p', { class: 'question', text: current.question }), chips);
    const panel = el('aside', { class: 'panel' }, el('h2', { text: '設定' }));
    current.params.forEach(p => panel.append(control(p)));
    const reset = el('button', { type: 'button', text: '重設' });
    reset.addEventListener('click', () => open(current.name));
    const share = el('button', { type: 'button', text: '複製連結' });
    share.addEventListener('click', async () => { try { await navigator.clipboard.writeText(location.href); share.textContent = '已複製'; } catch (e) { share.textContent = '複製失敗'; } setTimeout(() => (share.textContent = '複製連結'), 1500); });
    panel.append(el('div', { class: 'actions' }, reset, share), el('div', { class: 'status', id: 'status' }, el('span', { class: 'dot' }), el('span', { text: '就緒' })));
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
    setStatus('busy', '後端計算中…');
    try {
      const r = await fetch('/api/labs/' + current.name, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(params), signal: ctrl.signal });
      const data = await r.json();
      if (ctrl !== inflight) return;
      if (!r.ok || data.error) throw Object.assign(new Error(data.error || r.statusText), { trace: data.trace });
      render(data); lastOk = data;
      setStatus('', `完成，耗時 ${data.elapsed_ms} ms`);
    } catch (e) {
      if (e.name === 'AbortError') return;
      renderError(e);
      setStatus('err', '計算失敗');
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
      const c = el('div', { class: 'card' }, el('h3', { text: d.input.title || '輸入' }));
      res.append(c);  // on the page first, so the plot can take the card's width
      if (d.input.plot) plot(c, d.input.plot);
      if (d.input.image) c.append(el('figure', { class: 'figure' }, el('img', { class: 'input-img', src: '../' + d.input.image.replace(/^\/+/, ''), alt: d.input.title || '輸入' })));
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
        const head = el('div', { class: 'head' }, el('span', { class: 'kind ' + (m.kind || ''), text: m.kind === 'paper' ? '本論文方法' : m.kind === 'traditional' ? '傳統作法' : (m.kind || '') }), el('h3', { text: m.name, style: 'margin:0' }));
        if (m === best) head.append(el('span', { class: 'win-tag', text: '✓ 這筆輸入上較好' }));
        card.append(head);
        if (m.metric) card.append(el('div', { class: 'metric' }, el('b', { text: fmt(m.metric.value) }), el('span', { text: m.metric.label + (m.metric.better ? `（${m.metric.better === 'lower' ? '越低越好' : '越高越好'}）` : '') })));
        if (m.plot) plot(card, m.plot);
        if (m.text) card.append(el('p', { class: 'note', text: m.text }));
      });
    }
    if (d.table && window.PR && PR.table) res.append(el('div', { class: 'card' }, PR.table(d.table)));
    if (d.failures && d.failures.length) {
      const c = el('div', { class: 'card' }, el('h3', { text: `論文方法表現較差的樣本（${d.failures.length} 個，點一下載入）` }));
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
    const prov = el('div', { class: 'card prov' }, el('h3', { text: '這些數字從哪裡來' }), el('div', { class: 'live', text: d.provenance.live }));
    (d.provenance.remote || []).forEach(m => prov.append(el('div', { class: 'remote', text: `由專案既有的後端計算：${m.about}（${m.url}，${m.ms} ms）` })));
    (d.provenance.cached || []).forEach(m => prov.append(el('div', { class: 'cache', text: `快取：${m.about}，${m.computed.replace('T', ' ')} 在這台電腦算好（耗時 ${m.seconds} 秒），這次直接沿用` })));
    if (d.note) prov.append(el('div', { class: 'note', text: d.note }));
    res.append(prov);
  }

  function renderError(e) {
    const res = $('#results');
    const retry = el('button', { type: 'button', text: '重試', class: 'chip', style: 'cursor:pointer;background:none' });
    retry.addEventListener('click', run);
    const card = el('div', { class: 'card error' }, el('h3', { text: '後端無法計算這組設定' }), el('p', { text: e.message }));
    if (e.trace) card.append(el('details', {}, el('summary', { text: '錯誤細節' }), el('pre', { text: e.trace.join('\n') })));
    card.append(retry);
    if (lastOk) { render(lastOk); res.prepend(card, el('p', { class: 'note', text: '下方是上一組成功計算的結果。' })); }
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
