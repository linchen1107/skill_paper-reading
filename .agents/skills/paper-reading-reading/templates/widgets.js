/* paper-reading shared widgets. Copied unchanged into each topic folder.
 *
 * A demo is declared in demos.js:
 *   PR.demo('3', {
 *     controls: [{key: 'alpha', label: 'α', min: 0, max: 1, step: 0.01, value: 0.8},
 *                {key: 'method', label: '方法', options: ['log', 'PCEN'], value: 'PCEN'},
 *                {key: 'noise', label: '加入雜訊', checkbox: true, value: false}],
 *     compute: p => ({
 *       plots: [{title: '...', xlabel: '...', ylabel: '...', type: 'line',   // or 'bar', 'heatmap'
 *                series: [{name: 'log', x: [...], y: [...]}]}],             // heatmap: z: [[...]]
 *       anim: {title: 'Eq. 3 逐步計算',       // the formula animated: play, pause, step
 *              frames: [{label: '第 1 步', expr: 'p(y1) = e^3 / Σ e^l', value: 0.77,
 *                        plot: {...}}]},        // optional plot redrawn at this frame
 *       steps: [['步驟', '代入數值', 0.6]],   // a static table, for results that are not a derivation
 *       table: [['欄 1', '欄 2'], [1, 2]],     // first row is the header
 *       note: '本次實際重現，合成資料'
 *     })
 *   });
 * It renders into <div class="demo" id="demo-3"> and recomputes on every change.
 *
 * A hand calculation the demo must reproduce:
 *   PR.check('3', 'α = 1 時增益不變', () => ({expected: 0, actual: f(1), tol: 1e-9}));
 */
(function () {
  'use strict';
  const PR = (window.PR = { demos: {}, checks: [], errors: [] });
  const COLORS = ['#2563eb', '#dc2626', '#16a34a', '#9333ea', '#ea580c', '#0891b2'];

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

  function drawPlot(box, spec) {
    const W = 640, H = 300, L = 56, R = 16, T = 28, B = 44;
    const dpr = window.devicePixelRatio || 1;
    const cv = el('canvas', { width: W * dpr, height: H * dpr, style: `width:100%;max-width:${W}px` });
    const g = cv.getContext('2d');
    g.scale(dpr, dpr);
    g.fillStyle = '#fff'; g.fillRect(0, 0, W, H);
    g.font = '12px system-ui, sans-serif'; g.fillStyle = '#333';
    if (spec.title) g.fillText(spec.title, L, 16);
    const type = spec.type || 'line';
    const pw = W - L - R, ph = H - T - B;

    if (type === 'heatmap') {
      const z = spec.z, rows = z.length, cols = z[0].length;
      const [lo, hi] = range(z.flat());
      for (let i = 0; i < rows; i++) for (let j = 0; j < cols; j++) {
        const t = (z[i][j] - lo) / (hi - lo);
        g.fillStyle = `hsl(${240 - 240 * t},70%,${35 + 30 * t}%)`;
        g.fillRect(L + (j * pw) / cols, T + (i * ph) / rows, pw / cols + 0.5, ph / rows + 0.5);
      }
      g.fillStyle = '#333';
      g.fillText(`${PR.fmt(lo)} → ${PR.fmt(hi)}`, L, H - 8);
    } else {
      const series = spec.series || [];
      const xs = series.flatMap(s => s.x || s.y.map((_, i) => i));
      const ys = series.flatMap(s => s.y);
      const [x0, x1] = spec.xrange || range(xs);
      const [y0, y1] = spec.yrange || range(type === 'bar' ? ys.concat([0]) : ys);
      const X = x => L + ((x - x0) / (x1 - x0)) * pw;
      const Y = y => T + ph - ((y - y0) / (y1 - y0)) * ph;
      g.strokeStyle = '#999'; g.lineWidth = 1;
      g.strokeRect(L, T, pw, ph);
      g.fillStyle = '#555';
      for (let k = 0; k <= 4; k++) {
        const yv = y0 + ((y1 - y0) * k) / 4, xv = x0 + ((x1 - x0) * k) / 4;
        g.fillText(PR.fmt(yv), 4, Y(yv) + 4);
        g.fillText(PR.fmt(xv), X(xv) - 12, T + ph + 16);
      }
      if (spec.xlabel) g.fillText(spec.xlabel, L + pw / 2 - 30, H - 6);
      if (spec.ylabel) { g.save(); g.translate(12, T + ph / 2 + 30); g.rotate(-Math.PI / 2); g.fillText(spec.ylabel, 0, 0); g.restore(); }
      series.forEach((s, k) => {
        const x = s.x || s.y.map((_, i) => i);
        g.strokeStyle = g.fillStyle = s.color || COLORS[k % COLORS.length];
        if (type === 'bar') {
          const n = series.length, bw = (pw / Math.max(x.length, 1)) * 0.8 / n;
          x.forEach((xv, i) => {
            const px = L + (i + 0.1) * (pw / x.length) + k * bw;
            g.fillRect(px, Math.min(Y(s.y[i]), Y(0)), bw, Math.abs(Y(s.y[i]) - Y(0)));
          });
        } else {
          g.lineWidth = 2; g.setLineDash(s.dashed ? [5, 4] : []); g.beginPath();
          x.forEach((xv, i) => (i ? g.lineTo(X(xv), Y(s.y[i])) : g.moveTo(X(xv), Y(s.y[i]))));
          g.stroke(); g.setLineDash([]);
        }
      });
    }
    box.append(cv);
    if (spec.series && spec.series.length > 1) {
      const lg = el('div', { class: 'legend' });
      spec.series.forEach((s, k) => lg.append(el('span', { style: `color:${s.color || COLORS[k % COLORS.length]}`, text: '■ ' + s.name })));
      box.append(lg);
    }
  }

  function tableOf(rows, cls) {
    const t = el('table', { class: cls || '' });
    rows.forEach((r, i) => {
      const tr = el('tr');
      r.forEach(c => tr.append(el(i ? 'td' : 'th', { text: PR.fmt(c) })));
      t.append(tr);
    });
    return t;
  }

  // Formula animation: frames appear one at a time, the current one highlighted,
  // with the numbers of this run filled in; a frame may carry a plot that is redrawn.
  // The animation carries its own styles, so it looks right on any page, old or new.
  const ANIM_CSS = `.anim{border:1px solid #e5e7eb;border-radius:6px;padding:10px 12px;margin:8px 0;background:#f8fafc}
.anim-title{font-weight:700;margin-bottom:6px}
.anim-bar{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:14px}
.anim-bar button{font:inherit;padding:2px 10px;border:1px solid #cbd5e1;border-radius:4px;background:#fff;cursor:pointer}
.anim-pos{color:#6b7280;margin-left:6px}
.anim-frames{margin:8px 0 4px;padding-left:1.6em}
.anim-frames li{padding:2px 6px;border-radius:4px;color:#6b7280}
.anim-frames li.cur{background:#dbeafe;color:#1f2937}
.anim-label{margin-right:8px}
.anim-expr{font-family:"Cambria Math","Times New Roman",serif;font-size:16px;margin-right:6px}
.anim-val{font-weight:700}`;
  function ensureAnimCss() {
    if (document.getElementById('pr-anim-css')) return;
    const st = el('style', { id: 'pr-anim-css' }); st.textContent = ANIM_CSS; document.head.append(st);
  }

  function renderAnim(box, anim, d) {
    ensureAnimCss();
    const wrap = el('div', { class: 'anim' });
    if (anim.title) wrap.append(el('div', { class: 'anim-title', text: anim.title }));
    const bar = el('div', { class: 'anim-bar' });
    const bStart = el('button', { type: 'button', class: 'anim-start', text: '⏮ 從頭' });
    const bPrev = el('button', { type: 'button', class: 'anim-prev', text: '◀ 上一步' });
    const bPlay = el('button', { type: 'button', class: 'anim-play', text: '▶ 播放' });
    const bNext = el('button', { type: 'button', class: 'anim-next', text: '下一步 ▶' });
    const pos = el('span', { class: 'anim-pos' });
    bar.append(bStart, bPrev, bPlay, bNext, pos);
    const list = el('ol', { class: 'anim-frames' });
    const plotBox = el('div', { class: 'anim-plot' });
    wrap.append(bar, list, plotBox);
    box.append(wrap);
    const F = anim.frames || [];
    let i = F.length - 1;
    function show() {
      list.innerHTML = '';
      F.forEach((f, k) => {
        if (k > i) return;
        const li = el('li', { class: k === i ? 'cur' : '' });
        li.append(el('span', { class: 'anim-label', text: f.label || '' }));
        if (f.expr) li.append(el('code', { class: 'anim-expr', text: f.expr }));
        if (f.value !== undefined) li.append(el('span', { class: 'anim-val', text: '= ' + PR.fmt(f.value) }));
        list.append(li);
      });
      pos.textContent = `第 ${i + 1} / ${F.length} 步`;
      plotBox.innerHTML = '';
      for (let k = i; k >= 0; k--) if (F[k] && F[k].plot) { drawPlot(plotBox, F[k].plot); break; }
    }
    function stop() { if (d.timer) { clearInterval(d.timer); d.timer = null; } bPlay.textContent = '▶ 播放'; }
    bStart.addEventListener('click', () => { stop(); i = 0; show(); });
    bPrev.addEventListener('click', () => { stop(); i = Math.max(0, i - 1); show(); });
    bNext.addEventListener('click', () => { stop(); i = Math.min(F.length - 1, i + 1); show(); });
    bPlay.addEventListener('click', () => {
      if (d.timer) { stop(); return; }
      if (i >= F.length - 1) i = 0;
      show(); bPlay.textContent = '⏸ 暫停';
      d.timer = setInterval(() => { if (i >= F.length - 1) { stop(); return; } i++; show(); }, anim.interval || 1100);
    });
    show();
  }

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
        d.out = el('div', { class: 'out' });
        root.append(d.panel, d.out);
      }
      draw();
    }

    function draw() {
      if (d.timer) { clearInterval(d.timer); d.timer = null; }
      d.out.innerHTML = '';
      try {
        const r = spec.compute({ ...params }) || {};
        if (r.anim) renderAnim(d.out, r.anim, d);
        (r.plots || []).forEach(p => drawPlot(d.out, p));
        if (r.steps) d.out.append(tableOf([['步驟', '代入數值', '結果']].concat(r.steps), 'steps'));
        if (r.table) d.out.append(tableOf(r.table));
        if (r.note) d.out.append(el('p', { class: 'note', text: r.note }));
      } catch (e) {
        PR.errors.push(`demo-${id}: ${e.message}`);
        d.out.append(el('p', { class: 'error', text: '計算錯誤：' + e.message }));
      }
    }

    d.render = render;
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', render);
    else render();
  };

  PR.check = function (id, name, fn) { PR.checks.push({ id, name, fn }); };
})();
