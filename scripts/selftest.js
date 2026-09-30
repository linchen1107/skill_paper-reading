/* Loaded by index.html only with ?selftest (copied to _work/ by check_page.py).
 * For every knowledge-point section: move each control, confirm the demo's
 * output changes, restore it. Then run every PR.check. Writes JSON into
 * <pre id="selftest-result"> for check_page.py to read. */
(function () {
  'use strict';
  const out = { errors: [], sections: [], checks: [], mapMissing: [] };
  window.addEventListener('error', e => out.errors.push(String(e.message)));

  function snap(root) {
    let s = root.innerText;
    root.querySelectorAll('canvas').forEach(c => {
      try {
        const d = c.toDataURL();
        let h = 0;
        for (let i = 0; i < d.length; i += 7) h = (h * 31 + d.charCodeAt(i)) | 0;
        s += '#' + h;
      } catch (e) { /* tainted canvas */ }
    });
    return s;
  }

  function fire(inp) {
    inp.dispatchEvent(new Event('input', { bubbles: true }));
    inp.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function run() {
    document.querySelectorAll('section[data-kp]').forEach(sec => {
      const demo = sec.querySelector('.demo');
      const h = sec.querySelector('h3');
      const r = { kp: sec.dataset.kp, title: h ? h.textContent.trim() : '', demo: !!demo, controls: 0, changed: 0, unchanged: [],
                  formula: sec.dataset.formula === '1', traditional: sec.dataset.traditional === '1', anim: false, animSteps: 0 };
      if (demo) {
        // compare the output only; the value shown next to a slider always changes
        const area = demo.querySelector('.out') || demo;
        demo.querySelectorAll('input, select').forEach(inp => {
          r.controls++;
          const before = snap(area);
          const orig = inp.type === 'checkbox' ? inp.checked : inp.value;
          if (inp.type === 'checkbox') inp.checked = !inp.checked;
          else if (inp.tagName === 'SELECT') inp.selectedIndex = (inp.selectedIndex + 1) % inp.options.length;
          else inp.value = String(inp.value) === String(inp.max) ? inp.min : inp.max;
          fire(inp);
          if (snap(area) !== before) r.changed++;
          else r.unchanged.push(inp.getAttribute('aria-label') || inp.name || 'control');
          if (inp.type === 'checkbox') inp.checked = orig; else inp.value = orig;
          fire(inp);
        });
        // formula animation: going back to the first frame and stepping forward must change what is shown
        const anim = demo.querySelector('.anim');
        if (anim) {
          const start = anim.querySelector('.anim-start'), next = anim.querySelector('.anim-next');
          r.animSteps = anim.querySelectorAll('.anim-frames li').length;
          if (start && next) {
            start.click(); const a = snap(anim); next.click(); const b = snap(anim);
            r.anim = r.animSteps > 1 && a !== b;
          }
        }
      }
      out.sections.push(r);
    });
    // the page shows confirmed content only; unconfirmed items belong in the paper notes
    const text = (document.querySelector('main') || document.body).innerText;
    out.unconfirmed = [];
    ['尚未確認', '待驗證', '還沒確認'].forEach(w => {
      let i = text.indexOf(w);
      while (i >= 0) { out.unconfirmed.push(text.slice(Math.max(0, i - 30), i + w.length + 10).replace(/\s+/g, ' ')); i = text.indexOf(w, i + 1); }
    });
    const have = new Set([...document.querySelectorAll('section[data-kp]')].map(s => 'kp-' + s.dataset.kp));
    document.querySelectorAll('#map a[href^="#kp-"]').forEach(a => {
      const id = a.getAttribute('href').slice(1);
      if (!have.has(id)) out.mapMissing.push(id);
    });
    ((window.PR && PR.checks) || []).forEach(c => {
      try {
        const v = c.fn();
        const tol = v.tol === undefined ? 1e-6 : v.tol;
        const ok = Math.abs(v.actual - v.expected) <= tol * Math.max(1, Math.abs(v.expected));
        out.checks.push({ kp: c.id, name: c.name, expected: v.expected, actual: v.actual, ok });
      } catch (e) {
        out.checks.push({ kp: c.id, name: c.name, ok: false, error: String(e.message) });
      }
    });
    out.errors = out.errors.concat((window.PR && PR.errors) || []);
    const pre = document.createElement('pre');
    pre.id = 'selftest-result';
    pre.textContent = JSON.stringify(out);
    document.body.append(pre);
  }

  if (document.readyState === 'complete') setTimeout(run, 300);
  else window.addEventListener('load', () => setTimeout(run, 300));
})();
