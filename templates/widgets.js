/* paper-reading shared widgets. Copied unchanged into each topic folder.
 *
 * A demo is declared in demos.js:
 *   PR.demo('3', {
 *     controls: [{key: 'alpha', label: 'α', min: 0, max: 1, step: 0.01, value: 0.8},
 *                {key: 'method', label: 'Method', options: ['log', 'PCEN'], value: 'PCEN'},
 *                {key: 'noise', label: 'Add noise', checkbox: true, value: false}],
 *     compute: p => ({
 *       plots: [{title: '...', xlabel: '...', ylabel: '...', type: 'line',   // or 'bar', 'heatmap'
 *                series: [{name: 'log', x: [...], y: [...]}]}],             // heatmap: z: [[...]]
 *       anim: {title: 'Eq. 3 step by step',       // the formula animated: play, pause, step
 *              frames: [{label: 'Step 1', expr: 'p(y1) = e^3 / Σ e^l', value: 0.77,
 *                        plot: {...}}]},        // optional plot redrawn at this frame
 *       steps: [['Step', 'Numbers', 0.6]],   // a static table, for results that are not a derivation
 *       table: [['Column 1', 'Column 2'], [1, 2]],     // first row is the header
 *       note: 'Reproduced in this run, synthetic data'
 *     })
 *   });
 * It renders into <div class="demo" id="demo-3"> and recomputes on every change.
 *
 * Formulas: <div class="tex-block">\ca{L_{Adv}} = …</div> or <span class="tex">…</span> hold LaTeX and are
 * typeset with katex/ (colour macros \ca \cb \cc \cd); anim frames take tex: '…' as well.
 * Terms: PR.terms({'term': 'one plain sentence', …}); the first use is <dfn data-term="term">…</dfn>, later uses get the
 * explanation on hover.
 * Key formula card, placed after a demo: <div class="keyeq"> with a plain sentence whose coloured words
 * (<span class="w-a">…</span>, w-b, w-c, w-d) match the formula's \ca \cb \cc \cd terms; pointing at one marks both.
 * Live formula card: <div class="keyeq" data-live="name"> plus PR.live('name', {controls, tex}) in demos.js adds
 * sliders or buttons and the formula with the current numbers substituted (spec above PR.live below).
 * Formula map (how the formulas connect; nodes jump to their section): PR.formulaMap('fmap', {...}),
 * spec documented above the function below. The left sidebar #toc is built from sections with data-toc;
 * a group with data-toc-open starts expanded, and groups inside #appendix are set apart and dimmed.
 *
 * A hand calculation the demo must reproduce:
 *   PR.check('3', 'gain is unchanged when α = 1', () => ({expected: 0, actual: f(1), tol: 1e-9}));
 */
(function () {
  'use strict';
  const PR = (window.PR = { demos: {}, checks: [], errors: [] });
  const COLORS = ['#60a5fa', '#f87171', '#4ade80', '#c084fc', '#fb923c', '#22d3ee'];

  function el(tag, attrs, ...kids) {
    const e = document.createElement(tag);
    for (const k in attrs || {}) {
      if (k === 'class') e.className = attrs[k];
      else if (k === 'text') e.textContent = attrs[k];
      else e.setAttribute(k, attrs[k]);
    }
    kids.forEach(c => e.append(c));
    return e;
  }

  PR.fmt = function (v) {
    if (typeof v !== 'number') return String(v);
    if (!isFinite(v)) return String(v);
    const a = Math.abs(v);
    if (a !== 0 && (a >= 1e5 || a < 1e-3)) return v.toExponential(3);
    return String(+v.toFixed(4));
  };

  function range(arr) {
    let lo = Infinity, hi = -Infinity;
    arr.forEach(v => { if (isFinite(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); } });
    if (lo === hi) { lo -= 1; hi += 1; }
    return [lo, hi];
  }

  // Readable tick values: steps of 1, 2 or 5 times a power of ten.
  function niceStep(span, n) {
    const raw = span / n, p = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / p;
    return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * p;
  }
  function tickFmt(v, step) {
    const d = Math.max(0, -Math.floor(Math.log10(step) + 1e-9));
    const a = Math.abs(v);
    if (a !== 0 && (a >= 1e5 || a < 1e-3)) return v.toExponential(1);
    return v.toFixed(Math.min(d, 4));
  }

  // One plot, as wide as its box. Title and y-axis name sit above the axes; the legend sits inside, top right.
  function drawPlot(box, spec) {
    const cell = el('div', { class: 'plot' });
    box.append(cell);
    const W = Math.max(300, Math.min(cell.clientWidth || 640, 1100)), H = spec.height || 280;
    const L = 52, R = 14, T = 50, B = 40;
    const dpr = window.devicePixelRatio || 1;
    const cv = el('canvas', { width: Math.round(W * dpr), height: Math.round(H * dpr), style: `width:${W}px;max-width:100%;height:auto` });
    const g = cv.getContext('2d');
    g.scale(dpr, dpr);
    g.fillStyle = '#0f172a'; g.fillRect(0, 0, W, H);
    g.font = '600 13px system-ui, "Microsoft JhengHei", sans-serif'; g.fillStyle = '#e2e8f0';
    if (spec.title) g.fillText(spec.title, 12, 18);
    g.font = '12px system-ui, "Microsoft JhengHei", sans-serif';
    const type = spec.type || 'line';
    const pw = W - L - R, ph = H - T - B;

    if (type === 'heatmap') {
      const z = spec.z, rows = z.length, cols = z[0].length;
      const [lo, hi] = range(z.flat());
      const colour = t => `hsl(${220 - 190 * t},75%,${22 + 42 * t}%)`;
      for (let i = 0; i < rows; i++) for (let j = 0; j < cols; j++) {
        g.fillStyle = colour((z[i][j] - lo) / (hi - lo));
        g.fillRect(L + (j * pw) / cols, T + (i * ph) / rows, pw / cols + 0.5, ph / rows + 0.5);
      }
      const gx = L, gy = H - 18, gw = Math.min(180, pw);
      for (let k = 0; k < gw; k++) { g.fillStyle = colour(k / gw); g.fillRect(gx + k, gy, 1, 8); }
      g.fillStyle = '#94a3b8';
      g.fillText(PR.fmt(lo), gx, gy - 3); g.fillText(PR.fmt(hi), gx + gw - 30, gy - 3);
    } else {
      const series = spec.series || [];
      const xs = series.flatMap(s => s.x || s.y.map((_, i) => i));
      const ys = series.flatMap(s => s.y).filter(v => isFinite(v));
      let [y0, y1] = spec.yrange || range(type === 'bar' ? ys.concat([0]) : ys);
      const ys_ = niceStep(y1 - y0, 4);
      if (!spec.yrange) { y0 = Math.floor(y0 / ys_ + 1e-9) * ys_; y1 = Math.ceil(y1 / ys_ - 1e-9) * ys_; if (y0 === y1) y1 = y0 + ys_; }
      const Y = y => T + ph - ((y - y0) / (y1 - y0)) * ph;
      g.strokeStyle = '#1e293b'; g.lineWidth = 1; g.fillStyle = '#94a3b8'; g.textAlign = 'right';
      for (let v = Math.ceil(y0 / ys_ - 1e-9) * ys_; v <= y1 + ys_ * 1e-6; v += ys_) {
        g.beginPath(); g.moveTo(L, Y(v)); g.lineTo(L + pw, Y(v)); g.stroke();
        g.fillText(tickFmt(v, ys_), L - 6, Y(v) + 4);
      }
      g.textAlign = 'left';
      if (spec.ylabel) { g.fillStyle = '#94a3b8'; g.fillText(spec.ylabel, 12, T - 10); }
      g.strokeStyle = '#475569'; g.strokeRect(L, T, pw, ph);
      if (type === 'bar') {
        const n = Math.max(1, ...series.map(s => s.y.length)), slot = pw / n, k0 = series.length;
        const labels = (series[0] && series[0].x) || series[0].y.map((_, i) => i + 1);
        g.fillStyle = '#94a3b8'; g.textAlign = 'center';
        if (n <= 16) labels.forEach((lv, i) => g.fillText(String(PR.fmt(lv)), L + (i + 0.5) * slot, T + ph + 16));
        g.textAlign = 'left';
        series.forEach((s, k) => {
          g.fillStyle = s.color || COLORS[k % COLORS.length];
          const bw = (slot * 0.76) / k0;
          s.y.forEach((v, i) => { const px = L + i * slot + slot * 0.12 + k * bw; g.fillRect(px, Math.min(Y(v), Y(Math.max(0, y0))), bw, Math.abs(Y(v) - Y(Math.max(0, y0)))); });
        });
      } else {
        let [x0, x1] = spec.xrange || range(xs);
        const xs_ = niceStep(x1 - x0, 5);
        const X = x => L + ((x - x0) / (x1 - x0)) * pw;
        g.fillStyle = '#94a3b8'; g.textAlign = 'center';
        for (let v = Math.ceil(x0 / xs_ - 1e-9) * xs_; v <= x1 + xs_ * 1e-6; v += xs_) g.fillText(tickFmt(v, xs_), X(v), T + ph + 16);
        g.textAlign = 'left';
        series.forEach((s, k) => {
          const x = s.x || s.y.map((_, i) => i);
          g.strokeStyle = s.color || COLORS[k % COLORS.length];
          g.lineWidth = 2; g.setLineDash(s.dashed ? [5, 4] : []); g.beginPath();
          x.forEach((xv, i) => (i ? g.lineTo(X(xv), Y(s.y[i])) : g.moveTo(X(xv), Y(s.y[i]))));
          g.stroke(); g.setLineDash([]);
        });
      }
      if (spec.xlabel) { g.fillStyle = '#94a3b8'; g.textAlign = 'center'; g.fillText(spec.xlabel, L + pw / 2, H - 6); g.textAlign = 'left'; }
      if (series.length > 1) {
        let lx = L + pw; const ly = T - 28;
        const items = series.map((s, k) => [s.name, s.color || COLORS[k % COLORS.length], s.dashed]).reverse();
        const widths = items.map(it => g.measureText(it[0]).width + 26);
        const total = widths.reduce((a, b) => a + b, 0);
        items.forEach((it, i) => {
          lx -= widths[i];
          g.strokeStyle = it[1]; g.lineWidth = 2.5; g.setLineDash(it[2] ? [4, 3] : []);
          g.beginPath(); g.moveTo(lx, ly + 8); g.lineTo(lx + 16, ly + 8); g.stroke(); g.setLineDash([]);
          g.fillStyle = '#e2e8f0'; g.fillText(it[0], lx + 20, ly + 12);
        });
      }
    }
    cell.append(cv);
  }

  function tableOf(rows, cls) {
    const t = el('table', { class: cls || '' });
    rows.forEach((r, i) => {
      const tr = el('tr');
      r.forEach(c => tr.append(el(i ? 'td' : 'th', { text: PR.fmt(c) })));
      t.append(tr);
    });
    // a wide result table scrolls inside its own box instead of widening the page
    return el('div', { class: 'tscroll' }, t);
  }

  // ---------- Formulas typeset with KaTeX (katex/ next to the page; falls back to the source text) ----------
  // Colour macros for the terms of a formula: \ca{..} cyan, \cb{..} amber, \cc{..} violet, \cd{..} green.
  // Defined inside the source with \def (plain TeX). Hex colours are written without '#', which TeX would read
  // as a macro argument (#6…); KaTeX adds the '#' back in the CSS it emits.
  const TEX_DEFS = '\\def\\ca#1{\\textcolor{67e8f9}{#1}}\\def\\cb#1{\\textcolor{fbbf24}{#1}}\\def\\cc#1{\\textcolor{c4b5fd}{#1}}\\def\\cd#1{\\textcolor{86efac}{#1}}';
  PR.tex = function (src, display) {
    if (window.katex) {
      try { return window.katex.renderToString(TEX_DEFS + src, { displayMode: !!display, throwOnError: false, strict: false }); }
      catch (e) { PR.errors.push('tex: ' + e.message); }
    }
    const span = el('code', { class: 'tex-fallback', text: src });
    return span.outerHTML;
  };
  // <span class="tex">…</span> inline, <div class="tex-block">…</div> display; the text is LaTeX source.
  function renderTexIn(root) {
    root.querySelectorAll('.tex, .tex-block').forEach(n => {
      if (n.dataset.done) return;
      const src = n.textContent;
      n.dataset.src = src;
      n.innerHTML = PR.tex(src, n.classList.contains('tex-block'));
      n.dataset.done = '1';
    });
  }
  PR.renderTex = renderTexIn;

  // ---------- Key formula card: a plain sentence whose coloured words match the formula's coloured terms ----------
  // <div class="keyeq"> … <p class="plain"><span class="w-a">…</span> …</p><div class="tex-block">\ca{…}</div> …
  // w-a ↔ \ca, w-b ↔ \cb, w-c ↔ \cc, w-d ↔ \cd. Pointing at a word marks its term in the formula, and back.
  PR.TERM_HEX = { 'w-a': '67e8f9', 'w-b': 'fbbf24', 'w-c': 'c4b5fd', 'w-d': '86efac' };
  PR.termsIn = function (card, cls) {
    const hex = PR.TERM_HEX[cls];
    return [...card.querySelectorAll('.katex [style*="color"]')].filter(n => (n.getAttribute('style') || '').toLowerCase().includes(hex));
  };
  // ---------- Terms: every technical term is explained where it first appears ----------
  // demos.js lists the page's terms:  PR.terms({'hidden state': 'The long list of numbers the model builds inside as it reads each word.', …});
  // The first use in reading order is written <dfn data-term="hidden state">hidden state</dfn>, with the explanation
  // in the same sentence. Later uses get the explanation on hover (the first later use in each section).
  PR.glossary = {};
  PR.terms = function (map) { Object.assign(PR.glossary, map); };
  const escRe = k => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  PR.termRe = function (k, flags) {
    const body = escRe(k);
    return new RegExp(/^[\x20-\x7e]+$/.test(k) ? '(?<![A-Za-z0-9])' + body + '(?![A-Za-z0-9])' : body, flags || 'i');
  };
  const NO_TERMS = 'dfn, .term-ref, .katex, .tex, .tex-block, code, pre, script, style, .demo, .fmap, a, h1, h2, h3, #symbol-table, button, select, label, .keyeq-head';
  function markTerms() {
    const main = document.querySelector('main');
    const keys = Object.keys(PR.glossary).sort((a, b) => b.length - a.length);
    document.querySelectorAll('dfn[data-term]').forEach(d => {
      const g = PR.glossary[d.dataset.term];
      if (g) { d.setAttribute('data-tip', g); d.tabIndex = 0; }
    });
    if (!main || !keys.length) return;
    const re = new RegExp(keys.map(k => PR.termRe(k).source).join('|'), 'gi');
    const walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT, {
      acceptNode: n => (n.parentElement.closest(NO_TERMS) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT) });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    const seen = new Map();
    nodes.forEach(n => {
      const sec = n.parentElement.closest('section') || main;
      if (!seen.has(sec)) seen.set(sec, new Set());
      const done = seen.get(sec);
      re.lastIndex = 0;
      let m, last = 0, hit = false;
      const frag = document.createDocumentFragment();
      while ((m = re.exec(n.data))) {
        const key = keys.find(k => k.toLowerCase() === m[0].toLowerCase());
        if (!key || done.has(key)) continue;
        done.add(key); hit = true;
        frag.append(n.data.slice(last, m.index), el('span', { class: 'term-ref', 'data-tip': PR.glossary[key], tabindex: '0', text: m[0] }));
        last = m.index + m[0].length;
      }
      if (!hit) return;
      frag.append(n.data.slice(last));
      n.replaceWith(frag);
    });
  }

  function linkTerms() {
    document.querySelectorAll('.keyeq').forEach(card => {
      if (card.dataset.linked) return;
      card.dataset.linked = '1';
      Object.keys(PR.TERM_HEX).forEach(cls => {
        const words = [...card.querySelectorAll('.plain .' + cls)];
        const all = words.concat(PR.termsIn(card, cls));
        const on = v => { all.forEach(n => n.classList.toggle('pr-hl', v)); card.classList.toggle('pr-focus', v); };
        all.forEach(n => { n.addEventListener('mouseenter', () => on(true)); n.addEventListener('mouseleave', () => on(false)); });
        words.forEach(w => { w.tabIndex = 0; w.addEventListener('focus', () => on(true)); w.addEventListener('blur', () => on(false)); });
      });
    });
  }

  // ---------- Styles carried by the widgets, so they look right on any page ----------
  const WIDGET_CSS = `.anim{border:1px solid #334155;border-radius:8px;padding:10px 12px;margin:8px 0;background:#0b1220}
.anim-title{font-weight:700;margin-bottom:6px;color:#e2e8f0}
.anim-bar{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:14px}
.anim-bar button{font:inherit;padding:2px 10px;border:1px solid #475569;border-radius:4px;background:#1e293b;color:#e2e8f0;cursor:pointer}
.anim-bar button:hover{border-color:#67e8f9}
.anim-pos{color:#94a3b8;margin-left:6px}
.anim-frames{margin:8px 0 4px;padding-left:1.6em}
.anim-frames li{padding:3px 8px;border-radius:4px;color:#94a3b8}
.anim-frames li.cur{background:#164e63;color:#f1f5f9}
.anim-label{margin-right:10px}
.anim-expr{font-family:"Cambria Math","Times New Roman",serif;font-size:16px;margin-right:6px}
.anim-tex{margin-right:8px}
.anim-val{font-weight:700;color:#fbbf24}
#toc .toc-head{display:flex;align-items:center;margin-top:10px}
#toc .toc-caret{background:none;border:0;color:#64748b;cursor:pointer;width:18px;padding:0;font-size:12px;transition:transform .15s}
#toc .toc-grp.open .toc-caret{transform:rotate(90deg)}
#toc .toc-head a{flex:1;color:#e2e8f0;font-weight:700}
#toc .toc-sub{display:none;margin:2px 0 4px 10px;border-left:1px solid #1e293b}
#toc .toc-grp.open .toc-sub{display:block}
#pr-progress{position:fixed;top:0;left:0;height:3px;width:0;background:linear-gradient(90deg,#22d3ee,#fbbf24);z-index:50}
#pr-top{position:fixed;right:22px;bottom:22px;width:40px;height:40px;border-radius:50%;border:1px solid #334155;background:#111820;color:#67e8f9;font-size:18px;cursor:pointer;opacity:0;pointer-events:none;transition:opacity .2s;z-index:50}
#pr-top.show{opacity:1;pointer-events:auto}
#pr-top:hover{border-color:#67e8f9}
#pr-back{position:fixed;right:72px;bottom:22px;height:40px;padding:0 14px;border-radius:20px;border:1px solid #155e75;background:#0e2530;color:#67e8f9;font:inherit;font-size:14px;cursor:pointer;display:none;z-index:50}
#pr-back.show{display:block}
#pr-back:hover{border-color:#67e8f9}
#toc .toc-lab{margin:0 0 12px;padding:8px 10px;border:1px solid #155e75;border-radius:8px;background:#0e2530;color:#67e8f9;font-weight:700}
#toc .toc-lab:hover{border-color:#67e8f9}
#pr-lightbox{position:fixed;inset:0;z-index:100;background:rgba(3,7,12,.92);display:flex;flex-direction:column}
#pr-lightbox .lb-stage{flex:1;display:flex;align-items:center;justify-content:center;padding:56px 70px 8px;min-height:0}
#pr-lightbox .lb-stage img{box-sizing:border-box;background:#fff;border-radius:6px;padding:12px;box-shadow:0 10px 40px rgba(0,0,0,.6)}
#pr-lightbox .lb-foot{display:flex;flex-wrap:wrap;gap:6px 18px;align-items:baseline;justify-content:center;padding:10px 24px 18px;color:#cbd5e1;font-size:14px}
#pr-lightbox .lb-pos{color:#94a3b8;font-family:ui-monospace,Consolas,monospace}
#pr-lightbox .lb-cap{max-width:70em}
#pr-lightbox .lb-open{color:#67e8f9}
#pr-lightbox button{position:absolute;background:rgba(15,23,42,.8);color:#e2e8f0;border:1px solid #334155;border-radius:50%;width:44px;height:44px;font-size:24px;line-height:1;cursor:pointer}
#pr-lightbox button:hover{border-color:#67e8f9;color:#67e8f9}
#pr-lightbox .lb-close{top:14px;right:18px}
#pr-lightbox .lb-prev{left:14px;top:50%;transform:translateY(-50%)}
#pr-lightbox .lb-next{right:14px;top:50%;transform:translateY(-50%)}
main .figure img{cursor:zoom-in}
.pr-flash{animation:prflash 2.2s ease-out}
@keyframes prflash{0%,35%{box-shadow:0 0 0 2px #67e8f9,0 0 26px rgba(103,232,249,.45)}100%{box-shadow:0 0 0 0 transparent}}
.kp-nav{display:flex;flex-wrap:wrap;justify-content:space-between;gap:6px 16px;margin:6px 0 10px;font-size:13px;color:#94a3b8}
.kp-nav a{text-decoration:none}
.kp-eqs a.kp-eq{display:inline-block;margin:0 3px;padding:0 7px;border:1px solid #155e75;border-radius:4px;font:12px/1.8 ui-monospace,Consolas,monospace}
.kp-step a{margin-left:14px;color:#cbd5e1}
.kp-step a:hover,.kp-eqs a:hover{color:#67e8f9}
.demo.split{display:grid;grid-template-columns:minmax(330px,5fr) 7fr;gap:14px;align-items:start}
.demo.split.no-steps{grid-template-columns:1fr}
.demo-left{position:sticky;top:10px;max-height:calc(100vh - 20px);overflow:auto;min-width:0}
.demo-right{min-width:0}
.demo-left .controls{flex-direction:column;align-items:stretch;gap:8px;padding:10px;border:1px solid #1e293b;border-radius:8px;background:#0b1220}
.demo-left .controls label{display:grid;grid-template-columns:minmax(6em,40%) 1fr auto;align-items:center;gap:8px}
.demo-left .controls input[type=range]{width:100%;min-width:80px}
.demo-left .controls select{justify-self:start}
.demo.split.no-steps .demo-left{position:static;max-height:none}
.demo.split.no-steps .demo-left .controls{flex-direction:row;flex-wrap:wrap}
.demo.split.no-steps .demo-left .controls label{display:flex}
@media (max-width:1100px){.demo.split{grid-template-columns:1fr}.demo-left{position:static;max-height:none}}
.plots{display:grid;gap:12px;margin:10px 0}
.plots.two{grid-template-columns:repeat(auto-fit,minmax(380px,1fr))}
.plot canvas{display:block;border-radius:6px;border:1px solid #1e293b}
.controls input[type=range]{accent-color:#67e8f9;width:150px}
.controls select{background:#1e293b;color:#e2e8f0;border:1px solid #475569;border-radius:5px;padding:2px 6px;font:inherit}
.controls input[type=checkbox]{accent-color:#67e8f9;width:16px;height:16px}
.controls .val{display:inline-block;min-width:3.2em;padding:0 6px;border-radius:4px;background:#1e293b;color:#67e8f9;font:12px/1.8 ui-monospace,Consolas,monospace;text-align:center}
.tscroll{overflow-x:auto;max-width:100%}
.fmap{position:relative;overflow-x:auto;border:1px solid #334155;border-radius:10px;background:#0b1220;padding:8px}
.fmap svg{display:block}
.fmap .node{cursor:pointer}
.fmap .node:hover rect{stroke:#67e8f9}
.fmap .nbox{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;text-align:center;font-size:15px;line-height:1.35;color:#e2e8f0;padding:4px}
.fmap .nbox .ntag{font-size:13px;color:#94a3b8;font-family:ui-monospace,Consolas,monospace}
.fmap .nbox b{font-weight:700}
.fmap .elabel{font-size:13px;line-height:1.3;color:#cbd5e1;text-align:center;height:100%;display:flex;align-items:flex-end;justify-content:center}
.fmap .lane{font-size:13px;fill:#94a3b8;font-family:ui-monospace,Consolas,monospace}
.keyeq{border:1px solid #334155;border-left:3px solid #67e8f9;border-radius:8px;background:#0e1620;padding:12px 18px 10px;margin:16px 0 4px}
.keyeq-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 10px;font-size:13px;color:#94a3b8}
.keyeq-head b{color:#67e8f9;font-weight:600;font-size:14px}
.keyeq .plain{font-size:16px;line-height:1.9;margin:6px 0 4px;max-width:50em;color:#e2e8f0}
.keyeq .tex-block{overflow-x:auto;overflow-y:hidden;font-size:1.12em;padding:6px 0 2px}
.keyeq details{margin-top:4px;font-size:14px;color:#cbd5e1}
.keyeq summary{cursor:pointer;color:#94a3b8;width:max-content}
.keyeq summary:hover{color:#67e8f9}
.keyeq dl{display:grid;grid-template-columns:max-content 1fr;gap:4px 16px;margin:8px 0 4px}
.keyeq dd{margin:0}
dfn[data-term]{font-style:normal;font-weight:600;color:#f1f5f9;border-bottom:2px solid #155e75;cursor:help;position:relative}
.term-ref{border-bottom:1px dotted #64748b;cursor:help;position:relative}
[data-tip]:hover::after,[data-tip]:focus::after{content:attr(data-tip);position:absolute;left:0;top:calc(100% + 4px);z-index:60;width:max-content;max-width:min(340px,80vw);background:#0b1220;color:#e2e8f0;border:1px solid #334155;border-radius:6px;padding:6px 10px;font:400 13px/1.6 "Noto Sans TC","Microsoft JhengHei",system-ui,sans-serif;box-shadow:0 6px 20px rgba(0,0,0,.45);white-space:normal}
.lede{font-size:17px;line-height:1.9;color:#e2e8f0;max-width:46em;margin:18px 0 6px}
.w-a{color:#67e8f9}.w-b{color:#fbbf24}.w-c{color:#c4b5fd}.w-d{color:#86efac}
.w-a,.w-b,.w-c,.w-d{font-weight:600;border-bottom:1px dashed currentColor;cursor:help;border-radius:2px}
.pr-hl{background:rgba(148,163,184,.22);box-shadow:0 0 0 2px rgba(148,163,184,.22);border-radius:3px}
.katex .pr-hl{background:none;box-shadow:none;text-shadow:0 0 10px currentColor}
.keyeq.pr-focus .tex-block .katex{color:#64748b}
.keyeq.pr-focus .katex [style*="color"]:not(.pr-hl){opacity:.35}
.keyeq .tex-block .katex *{transition:opacity .15s}
.toc-grp:not(.toc-appx)+.toc-appx{margin-top:10px;padding-top:10px;border-top:1px solid #2b3643}
#toc .toc-appx a.toc-group{color:#64748b}
.live{margin-top:12px;padding-top:10px;border-top:1px dashed #334155}
.live-row{display:flex;flex-wrap:wrap;gap:8px 18px;align-items:center}
.live-ctl{display:inline-flex;align-items:center;gap:8px;color:#cbd5e1;font-size:14px}
.live-ctl input{width:130px;accent-color:#67e8f9}
.live-ctl output{min-width:2.6em;color:#fbbf24;font-variant-numeric:tabular-nums}
.live-note{color:#94a3b8;font-size:14px}
.live-seg{display:flex;flex-wrap:wrap;gap:6px}
.live-seg button{background:#1e293b;color:#e2e8f0;border:1px solid #475569;border-radius:999px;padding:3px 12px;font:13px inherit;cursor:pointer}
.live-seg button[aria-pressed="true"]{background:#155e75;border-color:#67e8f9;color:#fff}
.live-out{margin-top:8px;overflow-x:auto;color:#e2e8f0}
@media (max-width:860px){.keyeq dl{grid-template-columns:1fr}}`;
  function ensureCss() {
    if (document.getElementById('pr-widget-css')) return;
    const st = el('style', { id: 'pr-widget-css' }); st.textContent = WIDGET_CSS; document.head.append(st);
  }
  const ensureAnimCss = ensureCss;

  // ---------- Formula map: how the formulas connect ----------
  // PR.formulaMap('fmap', {
  //   lanes: [{id: 'a', label: 'InfoGAN term'}, ...],                   // rows, top to bottom
  //   nodes: [{id: 'e1', lane: 'a', col: 0, tag: '(1) · p.3', title: 'GAN adversarial loss', href: '#eq-1',
  //            kind: 'base' | 'new' | 'target' | 'algo' | 'chip', span: 2}],   // span: rows a target covers
  //   edges: [{from: 'e1', to: 'e2', label: 'add mutual information', dashed: false, route: 'side' | 'over' | 'under' | 'up' | 'arc'}],
  //   (side: right edge to left edge; over/under: around the lane above/below; up: straight up to the box above;
  //    arc: curved, the default for a dashed proof arrow)
  //   caption: '…'                                                   // one paragraph: the derivation in words
  // });
  const KIND = { base: ['#0f172a', '#cbd5e1'], new: ['#083344', '#22d3ee'], target: ['#3b2f1a', '#fbbf24'], algo: ['#2a2410', '#facc15'], chip: ['#1e293b', '#475569'], aux: ['#111827', '#64748b'] };
  PR.formulaMap = function (id, spec) {
    function draw() {
      ensureCss();
      const root = document.getElementById(id);
      if (!root) { PR.errors.push(`formulaMap ${id}: no element`); return; }
      root.classList.add('fmap'); root.innerHTML = '';
      const CW = 236, NW = 148, NH = 64, LH = 124, LX = 96, TOP = 44;
      const lanes = spec.lanes || [], li = {}; lanes.forEach((l, i) => (li[l.id] = i));
      const cols = Math.max(...spec.nodes.map(n => n.col + 1));
      const W = LX + cols * CW + 20, H = TOP + lanes.length * LH + 10;
      const pos = {};
      spec.nodes.forEach(n => {
        const span = n.span || 1, h = n.kind === 'chip' ? 34 : NH + (span - 1) * LH;
        const x = LX + n.col * CW + (CW - NW) / 2, y = TOP + li[n.lane] * LH + (LH - NH) / 2 + (n.kind === 'chip' ? (NH - 34) / 2 : 0);
        pos[n.id] = { x, y, w: NW, h, n };
      });
      const NS = 'http://www.w3.org/2000/svg';
      const svg = document.createElementNS(NS, 'svg');
      svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.style.width = '100%'; svg.style.maxWidth = W + 'px'; svg.style.height = 'auto';
      const mk = (t, a) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); return e; };
      const defs = mk('defs', {}); const mkArrow = (idn, c) => { const m = mk('marker', { id: idn, viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse' }); m.append(mk('path', { d: 'M0,0 L10,5 L0,10 z', fill: c })); defs.append(m); };
      mkArrow(id + '-ar', '#cbd5e1'); mkArrow(id + '-ar2', '#fbbf24'); svg.append(defs);
      lanes.forEach((l, i) => {
        const y = TOP + i * LH;
        if (i > 0) svg.append(mk('line', { x1: 8, x2: W - 8, y1: y, y2: y, stroke: '#334155', 'stroke-dasharray': '5 5' }));
        const t = mk('text', { x: 10, y: y + LH / 2 + 4, class: 'lane' }); t.textContent = l.label; svg.append(t);
      });
      const fo = (x, y, w, h, html, cls) => { const f = mk('foreignObject', { x, y, width: w, height: h }); const d = document.createElement('div'); d.className = cls; d.innerHTML = html; f.append(d); return f; };
      (spec.edges || []).forEach(e => {
        const a = pos[e.from], b = pos[e.to];
        if (!a || !b) { PR.errors.push(`formulaMap edge ${e.from}->${e.to}: unknown node`); return; }
        let d, lx, ly, lw = 150;
        const route = e.route || (e.dashed ? 'arc' : 'side');
        if (route === 'over') { const yy = b.y + b.h < a.y ? (b.y + b.h + a.y) / 2 : Math.min(a.y, b.y) - 22; d = `M${a.x + a.w / 2},${a.y} V${yy} H${b.x + b.w / 2} V${yy > b.y + b.h ? b.y + b.h : b.y}`; lx = (a.x + b.x + b.w) / 2; ly = yy - 4; }
        else if (route === 'under') { const yy = b.y > a.y + a.h ? (a.y + a.h + b.y) / 2 : Math.max(a.y + a.h, b.y + b.h) + 16; d = `M${a.x + a.w / 2},${a.y + a.h} V${yy} H${b.x + b.w / 2} V${yy < b.y ? b.y : b.y + b.h}`; lx = (a.x + b.x + b.w) / 2; ly = yy - 4; }
        else if (route === 'up') { const x = a.x + a.w / 2; d = `M${x},${a.y} V${b.y + b.h}`; lx = x - 80; ly = (a.y + b.y + b.h) / 2 + 12; lw = 150; }
        else if (route === 'arc') { const x1 = a.x + a.w / 2, x2 = b.x + b.w / 2, y0 = Math.min(a.y, b.y), yy = y0 - 34; d = `M${x1},${a.y} Q${(x1 + x2) / 2},${yy} ${x2},${b.y}`; lx = (x1 + x2) / 2; ly = yy + 8; }
        else { const sx = a.x + a.w, sy = a.y + a.h / 2, ex = b.x, ey = b.y + b.h / 2, mx = (sx + ex) / 2; d = sy === ey ? `M${sx},${sy} H${ex}` : `M${sx},${sy} H${mx} V${ey} H${ex}`; lx = mx; ly = Math.min(sy, ey) - 4; lw = Math.max(64, ex - sx - 8); }
        const col = e.dashed ? '#fbbf24' : '#cbd5e1';
        svg.append(mk('path', { d, fill: 'none', stroke: col, 'stroke-width': 1.6, 'stroke-dasharray': e.dashed ? '6 5' : '', 'marker-end': `url(#${id}-${e.dashed ? 'ar2' : 'ar'})` }));
        if (e.label || e.tex) {
          const html = (e.label ? e.label : '') + (e.tex ? PR.tex(e.tex) : '');
          svg.append(fo(lx - lw / 2, ly - 36, lw, 36, `<span style="background:#0b1220;padding:0 3px;${e.dashed ? 'color:#fbbf24' : ''}">${html}</span>`, 'elabel'));
        }
      });
      Object.values(pos).forEach(p => {
        const [bg, stroke] = KIND[p.n.kind || 'base'];
        const g = mk('g', { class: 'node', 'data-href': p.n.href || '', tabindex: 0 });
        g.append(mk('rect', { x: p.x, y: p.y, width: p.w, height: p.h, rx: p.n.kind === 'chip' ? 17 : 8, fill: bg, stroke, 'stroke-width': p.n.kind === 'target' || p.n.kind === 'new' ? 2 : 1.3 }));
        const title = p.n.tex ? PR.tex(p.n.tex) : (p.n.title || '');
        const tag = p.n.tag ? `<span class="ntag" style="${p.n.kind === 'target' || p.n.kind === 'algo' ? 'color:#fbbf24' : ''}">${p.n.tag}</span>` : '';
        g.append(fo(p.x, p.y, p.w, p.h, `${tag}<b>${title}</b>${p.n.tex && p.n.title ? `<span>${p.n.title}</span>` : ''}`, 'nbox'));
        const go = () => { if (p.n.href) PR.jump(p.n.href, true); };
        g.addEventListener('click', go); g.addEventListener('keydown', ev => { if (ev.key === 'Enter') go(); });
        svg.append(g);
      });
      root.append(svg);
      if (spec.caption) { const cap = el('p', { class: 'fmap-caption' }); cap.innerHTML = spec.caption; root.after(cap); renderTexIn(cap); }
    }
    PR.maps = PR.maps || {}; PR.maps[id] = spec;
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', draw); else draw();
  };

  // ---------- Left sidebar: built from the page's sections ----------
  // A section with id and data-toc-group starts a group; inside it, sections with id and data-tag become items.
  function buildToc() {
    const side = document.getElementById('toc');
    if (!side) return;
    side.innerHTML = '';
    const list = el('div', { class: 'toc-list' });
    let sub = null;
    document.querySelectorAll('main section[id][data-toc]').forEach(s => {
      const lvl = s.dataset.toc;
      const h = s.querySelector('h2, h3');
      let name = s.dataset.tocName;
      if (!name && h) { const c = h.cloneNode(true); c.querySelectorAll('.chip, .mark').forEach(x => x.remove()); name = c.textContent.replace(/^\s*\d+\.\s*/, '').trim(); }
      name = name || s.id;
      const a = el('a', { href: '#' + s.id, class: 'toc-' + lvl });
      if (s.dataset.tag) a.append(el('span', { class: 'toc-tag', text: s.dataset.tag }));
      a.append(el('span', { class: 'toc-name', text: name }));
      if (lvl === 'group') {
        const grp = el('div', { class: 'toc-grp' });
        const caret = el('button', { type: 'button', class: 'toc-caret', 'aria-label': 'Expand or collapse', text: '▸' });
        const head = el('div', { class: 'toc-head' }, caret, a);
        sub = el('div', { class: 'toc-sub' });
        caret.addEventListener('click', () => grp.classList.toggle('open'));
        if (s.hasAttribute('data-toc-open')) grp.classList.add('open');
        if (s.closest('#appendix')) grp.classList.add('toc-appx');
        grp.append(head, sub); list.append(grp);
      } else (sub || list).append(a);
    });
    list.querySelectorAll('.toc-grp').forEach(g => { if (!g.querySelector('.toc-sub a')) g.querySelector('.toc-caret').style.visibility = 'hidden'; });
    side.append(list);
    const links = [...side.querySelectorAll('a')];
    const spy = () => {
      let cur = null;
      links.forEach(a => { const t = document.querySelector(a.getAttribute('href')); if (t && t.getBoundingClientRect().top < 120) cur = a; });
      links.forEach(a => a.classList.toggle('on', a === cur));
      const g = cur && cur.closest('.toc-grp');
      if (g && !g.classList.contains('open')) { side.querySelectorAll('.toc-grp.auto').forEach(x => x !== g && x.classList.remove('open', 'auto')); g.classList.add('open', 'auto'); }
      if (cur) { const r = cur.getBoundingClientRect(), sr = side.getBoundingClientRect(); if (r.top < sr.top + 40 || r.bottom > sr.bottom - 40) side.scrollTop += r.top - sr.top - sr.height / 3; }
    };
    let ticking = false;
    window.addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(() => { spy(); ticking = false; }); } }, { passive: true });
    spy();
  }

  // Reading progress bar at the top and a back-to-top button.
  function pageChrome() {
    if (document.getElementById('pr-progress')) return;
    // on a narrow screen the table of contents folds into a bar at the top; this button opens it
    const toc = document.getElementById('toc');
    if (toc && !document.getElementById('toc-toggle')) {
      const tg = el('button', { id: 'toc-toggle', type: 'button', text: '☰ Contents' });
      tg.addEventListener('click', () => toc.classList.toggle('open'));
      toc.prepend(tg);
      toc.addEventListener('click', ev => { if (ev.target.closest('a')) toc.classList.remove('open'); });
    }
    const bar = el('div', { id: 'pr-progress' });
    const top = el('button', { id: 'pr-top', type: 'button', 'aria-label': 'Back to top', text: '↑' });
    top.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    document.body.append(bar, top);
    const upd = () => {
      const h = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (h > 0 ? (100 * window.scrollY) / h : 0) + '%';
      top.classList.toggle('show', window.scrollY > 600);
    };
    window.addEventListener('scroll', upd, { passive: true }); upd();
  }

  // ---------- Jumping to a section: land on it after everything has been drawn, and show where you landed ----------
  // Every history entry keeps its own scroll position in history.state.y, so the browser's back button
  // returns to the exact spot, also when coming back from a note page. Entries made by a jump carry jumped: true.
  const saveY = () => { try { history.replaceState({ ...(history.state || {}), y: window.scrollY }, '', location.href); } catch (e) {} };
  function showBack() { const b = document.getElementById('pr-back'); if (b) b.classList.toggle('show', !!(history.state && history.state.jumped)); }
  PR.jump = function (hash, smooth, push) {
    let t = null;
    try { t = document.querySelector(decodeURIComponent(hash)); } catch (e) { t = null; }
    if (!t) return false;
    const y = Math.max(0, t.getBoundingClientRect().top + window.scrollY - 14);
    if (push) { saveY(); history.pushState({ y, jumped: true }, '', hash); }
    else history.replaceState({ ...(history.state || {}), y }, '', hash);
    window.scrollTo({ top: y, behavior: smooth ? 'smooth' : 'auto' });
    showBack();
    t.classList.remove('pr-flash'); void t.offsetWidth; t.classList.add('pr-flash');
    setTimeout(() => t.classList.remove('pr-flash'), 2200);
    return true;
  };
  function wireLinks() {
    document.addEventListener('click', ev => {
      const a = ev.target.closest && ev.target.closest('a[href^="#"]');
      // middle click and modifier clicks keep the browser default (a new tab)
      if (!a || ev.button !== 0 || ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.altKey) return;
      const h = a.getAttribute('href');
      if (h.length > 1 && PR.jump(h, true, true)) ev.preventDefault();
    });
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    let saveTimer = 0;
    window.addEventListener('scroll', () => { clearTimeout(saveTimer); saveTimer = setTimeout(saveY, 200); }, { passive: true });
    window.addEventListener('pagehide', saveY);
    window.addEventListener('popstate', ev => {
      if (ev.state && typeof ev.state.y === 'number') window.scrollTo({ top: ev.state.y, behavior: 'auto' });
      else if (location.hash) PR.jump(location.hash, false);
      showBack();
    });
    const back = el('button', { id: 'pr-back', type: 'button', text: '↩ Back to where you were' });
    back.addEventListener('click', () => history.back());
    document.body.append(back);
    showBack();
    // landing: a remembered position (back from another page, or a reload) wins over the #…; either way land
    // again after the demos, formulas and fonts have changed the page height
    const st = history.state;
    const land = st && typeof st.y === 'number' ? () => window.scrollTo({ top: st.y, behavior: 'auto' })
      : location.hash ? () => PR.jump(location.hash, false) : null;
    if (land) {
      land();
      window.addEventListener('load', () => { land(); setTimeout(land, 300); });
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => setTimeout(land, 50));
    }
  }

  // ---------- Navigation bar on each knowledge point: its formulas, previous and next, back to the map ----------
  function kpNav() {
    const kps = [...document.querySelectorAll('section.kp[id]')];
    kps.forEach((k, i) => {
      if (k.querySelector('.kp-nav')) return;
      const nav = el('div', { class: 'kp-nav' });
      const eqs = [...document.querySelectorAll('section.eq-sec[id]')].filter(e => e.querySelector(`a[href="#${k.id}"]`));
      if (eqs.length) {
        const f = el('span', { class: 'kp-eqs' }, 'Full formulas (appendix): ');
        eqs.forEach(e => f.append(el('a', { href: '#' + e.id, class: 'kp-eq', text: e.dataset.tag || e.id })));
        nav.append(f);
      }
      const tag = x => (x.dataset.kp || x.id.replace(/^kp-/, ''));
      const side = el('span', { class: 'kp-step' });
      if (kps[i - 1]) side.append(el('a', { href: '#' + kps[i - 1].id, text: '← ' + tag(kps[i - 1]) }));
      if (document.getElementById('map-formulas')) side.append(el('a', { href: '#map-formulas', text: 'Formula map' }));
      if (kps[i + 1]) side.append(el('a', { href: '#' + kps[i + 1].id, text: tag(kps[i + 1]) + ' →' }));
      nav.append(side);
      const src = k.querySelector('.src');
      (src || k.querySelector('h3')).after(nav);
    });
  }

  // ---------- Figure popup: a paper figure opens large over the page, with its caption; arrows step through all ----------
  function lightbox() {
    const figs = () => [...document.querySelectorAll('main .figure img, main figure img')];
    let box = null, idx = 0;
    function close() { if (box) { box.remove(); box = null; document.body.style.overflow = ''; } }
    function show(i) {
      const list = figs(); if (!list.length) return;
      idx = (i + list.length) % list.length;
      const img = list[idx], fig = img.closest('figure, .figure');
      const cap = fig && fig.querySelector('figcaption, .note');
      const src = img.getAttribute('src');
      if (!box) {
        box = el('div', { id: 'pr-lightbox', role: 'dialog', 'aria-modal': 'true' });
        box.addEventListener('click', ev => { if (ev.target === box || ev.target.classList.contains('lb-stage')) close(); });
        document.body.append(box); document.body.style.overflow = 'hidden';
      }
      box.innerHTML = '';
      const btn = (cls, text, label, fn) => { const b = el('button', { type: 'button', class: cls, 'aria-label': label, text }); b.addEventListener('click', ev => { ev.stopPropagation(); fn(); }); return b; };
      const big = el('img', { src, alt: img.getAttribute('alt') || '' });
      const stage = el('div', { class: 'lb-stage' }, big);
      // scale the figure to fill the stage: vector figures have a small built-in size, so enlarge them too
      const fit = () => {
        const w = big.naturalWidth || 800, h = big.naturalHeight || 600;
        const cs = getComputedStyle(stage);
        const sw = stage.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight), sh = stage.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
        if (sw <= 0 || sh <= 0) return;
        const k = Math.min(sw / w, sh / h);
        big.style.width = Math.round(w * k) + 'px'; big.style.height = Math.round(h * k) + 'px';
      };
      big.addEventListener('load', fit); requestAnimationFrame(fit);
      box._fit = fit;
      const foot = el('div', { class: 'lb-foot' });
      foot.append(el('span', { class: 'lb-pos', text: `${idx + 1} / ${list.length}` }));
      if (cap) foot.append(el('span', { class: 'lb-cap', text: cap.textContent }));
      foot.append(el('a', { href: src, target: '_blank', rel: 'noopener', class: 'lb-open', text: 'Open the original file' }));
      box.append(btn('lb-close', '×', 'Close', close), stage, foot);
      if (list.length > 1) box.append(btn('lb-prev', '‹', 'Previous', () => show(idx - 1)), btn('lb-next', '›', 'Next', () => show(idx + 1)));
    }
    document.addEventListener('click', ev => {
      const img = ev.target.closest && ev.target.closest('main .figure img, main figure img');
      if (!img || ev.button !== 0 || ev.ctrlKey || ev.metaKey || ev.shiftKey) return;
      ev.preventDefault(); show(figs().indexOf(img));
    });
    window.addEventListener('resize', () => { if (box && box._fit) box._fit(); });
    document.addEventListener('keydown', ev => {
      if (!box) return;
      if (ev.key === 'Escape') close(); else if (ev.key === 'ArrowLeft') show(idx - 1); else if (ev.key === 'ArrowRight') show(idx + 1);
    });
    PR.lightbox = { show, close, isOpen: () => !!box };
  }

  // When the page is served (python serve.py) and the topic has labs, the sidebar offers them.
  function labLink() {
    const side = document.getElementById('toc');
    if (!side || !/^https?:/.test(location.protocol)) return;
    fetch('studio/lab.html', { method: 'HEAD' }).then(r => {
      if (!r.ok || side.querySelector('.toc-lab')) return;
      const a = el('a', { href: 'studio/lab.html', class: 'toc-lab' }, el('span', { class: 'toc-tag', text: 'LAB' }), el('span', { class: 'toc-name', text: 'Labs on real data →' }));
      side.prepend(a);
    }).catch(() => {});
  }

  function boot() {
    ensureCss(); renderTexIn(document); linkTerms(); markTerms(); buildToc(); pageChrome(); kpNav(); wireLinks(); lightbox(); labLink();
    let t = null, w0 = window.innerWidth;
    window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(() => {
      if (Math.abs(window.innerWidth - w0) < 40) return; w0 = window.innerWidth;
      Object.values(PR.demos).forEach(d => d.redraw && d.redraw());
    }, 250); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();

  // Formula animation: frames appear one at a time, the current one highlighted,
  // with the numbers of this run filled in; a frame may carry LaTeX (tex) and a plot that is redrawn.
  function renderAnim(box, anim, d, plotHost) {
    ensureAnimCss();
    const wrap = el('div', { class: 'anim' });
    if (anim.title) wrap.append(el('div', { class: 'anim-title', text: anim.title }));
    const bar = el('div', { class: 'anim-bar' });
    const bStart = el('button', { type: 'button', class: 'anim-start', text: '⏮ Start' });
    const bPrev = el('button', { type: 'button', class: 'anim-prev', text: '◀ Back' });
    const bPlay = el('button', { type: 'button', class: 'anim-play', text: '▶ Play' });
    const bNext = el('button', { type: 'button', class: 'anim-next', text: 'Next ▶' });
    const pos = el('span', { class: 'anim-pos' });
    bar.append(bStart, bPrev, bPlay, bNext, pos);
    const list = el('ol', { class: 'anim-frames' });
    const plotBox = el('div', { class: 'anim-plot' });
    wrap.append(bar, list);
    box.append(wrap);
    (plotHost || wrap).append(plotBox);
    const F = anim.frames || [];
    let i = F.length - 1;
    function show() {
      list.innerHTML = '';
      F.forEach((f, k) => {
        if (k > i) return;
        const li = el('li', { class: k === i ? 'cur' : '' });
        li.append(el('span', { class: 'anim-label', text: f.label || '' }));
        if (f.tex) { const t = el('span', { class: 'anim-tex' }); t.innerHTML = PR.tex(f.tex); li.append(t); }
        else if (f.expr) li.append(el('code', { class: 'anim-expr', text: f.expr }));
        if (f.value !== undefined) li.append(el('span', { class: 'anim-val', text: '= ' + PR.fmt(f.value) }));
        list.append(li);
      });
      pos.textContent = `Step ${i + 1} of ${F.length}`;
      plotBox.innerHTML = '';
      for (let k = i; k >= 0; k--) if (F[k] && F[k].plot) { drawPlot(plotBox, F[k].plot); break; }
    }
    function stop() { if (d.timer) { clearInterval(d.timer); d.timer = null; } bPlay.textContent = '▶ Play'; }
    bStart.addEventListener('click', () => { stop(); i = 0; show(); });
    bPrev.addEventListener('click', () => { stop(); i = Math.max(0, i - 1); show(); });
    bNext.addEventListener('click', () => { stop(); i = Math.min(F.length - 1, i + 1); show(); });
    bPlay.addEventListener('click', () => {
      if (d.timer) { stop(); return; }
      if (i >= F.length - 1) i = 0;
      show(); bPlay.textContent = '⏸ Pause';
      d.timer = setInterval(() => { if (i >= F.length - 1) { stop(); return; } i++; show(); }, anim.interval || 1100);
    });
    show();
  }

  const root = id => document.getElementById('demo-' + id);

  PR.demo = function (id, spec) {
    const params = {};
    spec.controls.forEach(c => (params[c.key] = c.value));
    const d = (PR.demos[id] = { spec, params });

    function render() {
      const root = document.getElementById('demo-' + id);
      if (!root) { PR.errors.push(`demo-${id}: no element`); return; }
      if (!d.panel) {
        d.panel = el('div', { class: 'controls' });
        spec.controls.forEach(c => {
          const val = el('span', { class: 'val' });
          let input;
          if (c.options) {
            input = el('select', { 'aria-label': c.label });
            c.options.forEach(o => input.append(el('option', { value: o, text: o })));
            input.value = c.value;
          } else if (c.checkbox) {
            input = el('input', { type: 'checkbox', 'aria-label': c.label });
            input.checked = !!c.value;
          } else {
            input = el('input', { type: 'range', min: c.min, max: c.max, step: c.step || (c.max - c.min) / 100, value: c.value, 'aria-label': c.label });
            val.textContent = PR.fmt(+c.value);
          }
          input.addEventListener('input', () => {
            params[c.key] = c.options ? input.value : c.checkbox ? input.checked : +input.value;
            if (!c.options && !c.checkbox) val.textContent = PR.fmt(+input.value);
            draw();
          });
          d.panel.append(el('label', {}, c.label + ' ', input, val));
        });
        // two columns on wide screens: controls and formula steps stay in view on the left, results on the right
        d.outL = el('div', { class: 'out out-steps' });
        d.out = el('div', { class: 'out out-main' });
        root.classList.add('split');
        root.append(el('div', { class: 'demo-left' }, d.panel, d.outL), el('div', { class: 'demo-right' }, d.out));
      }
      draw();
    }

    function draw() {
      if (d.timer) { clearInterval(d.timer); d.timer = null; }
      d.out.innerHTML = ''; d.outL.innerHTML = '';
      try {
        const r = spec.compute({ ...params }) || {};
        if (r.anim) renderAnim(d.outL, r.anim, d, d.out);
        root(id).classList.toggle('no-steps', !r.anim);
        if (r.plots && r.plots.length) {
          const grid = el('div', { class: 'plots' + (r.plots.length > 1 ? ' two' : '') });
          d.out.append(grid);
          r.plots.forEach(p => drawPlot(grid, p));
        }
        if (r.steps) d.out.append(tableOf([['Step', 'Numbers', 'Result']].concat(r.steps), 'steps'));
        if (r.table) d.out.append(tableOf(r.table));
        if (r.note) d.out.append(el('p', { class: 'note', text: r.note }));
      } catch (e) {
        PR.errors.push(`demo-${id}: ${e.message}`);
        d.out.append(el('p', { class: 'error', text: 'Computation error: ' + e.message }));
      }
    }

    d.render = render; d.redraw = () => d.out && draw();
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', render);
    else render();
  };

  // Live formula card: one row of controls under a key formula card and one line that shows the formula with the
  // current numbers substituted and the result, recomputed on every change.
  //   <div class="keyeq" data-live="sam">…</div>   in the page, then in demos.js:
  //   PR.live('sam', {controls: [{key: 'x1', label: 'x₁', min: 0, max: 200, step: 1, value: 50},
  //                              {key: 'light', label: 'light', options: [['wl', 'white'], ['505', '505 nm']], value: 'wl'}],
  //                   tex: p => String.raw`\cos\cc{\theta} = ${…} = ${…}`});
  PR.live = function (name, spec) {
    function render() {
      const card = document.querySelector(`.keyeq[data-live="${name}"]`);
      if (!card) { PR.errors.push(`live ${name}: no .keyeq[data-live="${name}"]`); return; }
      if (card.querySelector('.live')) return;
      const p = {};
      const row = el('div', { class: 'live-row' }), out = el('div', { class: 'live-out' });
      const draw = () => {
        try { out.innerHTML = PR.tex(spec.tex({ ...p }), true); }
        catch (e) { PR.errors.push(`live ${name}: ${e.message}`); out.textContent = 'Computation error: ' + e.message; }
      };
      (spec.controls || []).forEach(c => {
        p[c.key] = c.value;
        if (c.options) {
          const seg = el('div', { class: 'live-seg', role: 'group', 'aria-label': c.label || c.key });
          c.options.forEach(([v, label]) => {
            const b = el('button', { type: 'button', text: label, 'aria-pressed': String(v === c.value) });
            b.addEventListener('click', () => { p[c.key] = v; seg.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b))); draw(); });
            seg.append(b);
          });
          row.append(c.label ? el('span', { class: 'live-ctl' }, el('span', { text: c.label }), seg) : seg);
        } else {
          const val = el('output', { text: PR.fmt(+c.value) });
          const input = el('input', { type: 'range', min: c.min, max: c.max, step: c.step || (c.max - c.min) / 100, value: c.value, 'aria-label': c.label || c.key });
          input.addEventListener('input', () => { p[c.key] = +input.value; val.textContent = PR.fmt(+input.value); draw(); });
          row.append(el('label', { class: 'live-ctl' }, el('span', { text: c.label || c.key }), input, val));
        }
      });
      if (spec.note) row.append(el('span', { class: 'live-note', text: spec.note }));
      card.append(el('div', { class: 'live' }, row, out));
      draw();
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', render); else render();
  };

  PR.check = function (id, name, fn) { PR.checks.push({ id, name, fn }); };

  // For other pages built on these widgets (the presentation lab page): draw a plot, typeset, run a formula animation.
  PR.plot = (box, spec) => drawPlot(box, spec);
  PR.anim = (box, anim, plotHost) => renderAnim(box, anim, {}, plotHost);
  PR.table = rows => tableOf(rows);
})();
