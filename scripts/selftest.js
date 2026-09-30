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
        const outs = [...demo.querySelectorAll('.out')];
        const area = { get innerText() { return (outs.length ? outs : [demo]).map(o => o.innerText).join('|'); }, querySelectorAll: q => (outs.length ? outs : [demo]).flatMap(o => [...o.querySelectorAll(q)]) };
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
    // formulas: the map links every formula section, every link lands, symbols are listed, KaTeX typeset them
    const eqIds = [...document.querySelectorAll('section.eq-sec[id]')].map(s => s.id);
    const nodeHrefs = [...document.querySelectorAll('.fmap .node')].map(n => n.getAttribute('data-href') || '');
    out.formulas = {
      sections: eqIds.length,
      mapNodes: nodeHrefs.length,
      brokenLinks: nodeHrefs.filter(h => h && !document.querySelector(h)).concat(nodeHrefs.filter(h => !h).map(() => '(no href)')),
      notOnMap: eqIds.filter(id => !nodeHrefs.includes('#' + id)),
      symbols: document.querySelectorAll('#symbol-table tr').length - 1,
      texErrors: document.querySelectorAll('.katex-error').length,
      texFallback: document.querySelectorAll('.tex-fallback').length
    };
    // key formulas: at most 5, inside a knowledge point, after its demo, with a plain sentence whose coloured
    // words match coloured terms of the formula; the full formula layer lives in #appendix, the storyline has none
    out.keyFormulas = [...document.querySelectorAll('.keyeq')].map(c => {
      const kp = c.closest('section[data-kp]');
      const demo = kp && kp.querySelector('.demo');
      const plain = c.querySelector('.plain');
      const words = plain ? [...plain.querySelectorAll('.w-a, .w-b, .w-c, .w-d')] : [];
      const cls = w => [...w.classList].find(x => /^w-[abcd]$/.test(x));
      const unmatched = words.filter(w => !PR.termsIn(c, cls(w)).length).map(w => w.textContent.trim());
      let hover = false;
      if (words.length) {
        words[0].dispatchEvent(new MouseEvent('mouseenter'));
        hover = PR.termsIn(c, cls(words[0])).some(n => n.classList.contains('pr-hl'));
        words[0].dispatchEvent(new MouseEvent('mouseleave'));
      }
      return { kp: kp ? kp.dataset.kp : null, formulaKp: !!kp && kp.dataset.formula === '1',
               plain: plain ? plain.innerText.trim().length : 0, words: words.length, unmatched, hover,
               afterDemo: !!demo && !!(demo.compareDocumentPosition(c) & Node.DOCUMENT_POSITION_FOLLOWING),
               typeset: !!c.querySelector('.tex-block .katex') };
    });
    out.storyFormulas = [...document.querySelectorAll('.tex-block')].filter(n => !n.closest('#kps') && !n.closest('#appendix')).length;
    const fmap = document.querySelector('.fmap');
    out.overviewInAppendix = !fmap || !!fmap.closest('#appendix');
    // figures of the paper are the real files (original bitmap or vector), not screenshots
    out.figures = [...document.querySelectorAll('main .figure img, main figure img')].map(i => ({ src: i.getAttribute('src') || '', ok: /-real\.(svg|png|jpe?g|gif|webp)$/i.test(i.getAttribute('src') || ''), loaded: i.complete && i.naturalWidth > 0 }));
    // clicking a figure opens it in the popup
    out.figures.forEach(f => {
      const img = [...document.querySelectorAll('main .figure img, main figure img')].find(i => i.getAttribute('src') === f.src);
      img.click();
      const lb = document.querySelector('#pr-lightbox .lb-stage img');
      f.popup = !!lb && lb.getAttribute('src') === f.src;
      if (window.PR && PR.lightbox) PR.lightbox.close();
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
