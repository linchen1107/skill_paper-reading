/* Loaded by index.html only with ?selftest (copied to _work/ by check_page.py).
 * For every knowledge-point section: move each control, confirm the demo's
 * output changes, restore it. Then run every PR.check. Writes JSON into
 * <pre id="selftest-result"> for check_page.py to read. */
(function () {
  'use strict';
  const out = { errors: [], sections: [], checks: [], mapMissing: [] };
  const EN = !/^zh/i.test(document.documentElement.lang || '');
  out.lang = EN ? 'en' : 'zh';
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
    // key formulas: inside a knowledge point, after its demo, with a plain sentence whose coloured words match
    // coloured terms of the formula, and live: moving each control changes the line with the numbers substituted
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
      const live = c.querySelector('.live'), lout = live && live.querySelector('.live-out');
      let liveControls = 0, liveChanged = 0;
      if (lout) {
        live.querySelectorAll('input').forEach(inp => {
          liveControls++;
          const before = lout.innerText, orig = inp.value;
          inp.value = String(inp.value) === String(inp.max) ? inp.min : inp.max; fire(inp);
          if (lout.innerText !== before) liveChanged++;
          inp.value = orig; fire(inp);
        });
        live.querySelectorAll('.live-seg').forEach(seg => {
          const bs = [...seg.querySelectorAll('button')], cur = bs.find(b => b.getAttribute('aria-pressed') === 'true'), other = bs.find(b => b !== cur);
          if (!other) return;
          liveControls++;
          const before = lout.innerText; other.click();
          if (lout.innerText !== before) liveChanged++;
          if (cur) cur.click();
        });
      }
      return { kp: kp ? kp.dataset.kp : null, formulaKp: !!kp && kp.dataset.formula === '1', name: c.dataset.live || '',
               live: !!lout, liveControls, liveChanged,
               plain: plain ? plain.innerText.trim().length : 0, words: words.length, unmatched, hover,
               afterDemo: !!demo && !!(demo.compareDocumentPosition(c) & Node.DOCUMENT_POSITION_FOLLOWING),
               typeset: !!c.querySelector('.tex-block .katex') };
    });
    out.storyFormulas = [...document.querySelectorAll('.tex-block')].filter(n => !n.closest('section[data-kp]') && !n.closest('#appendix')).length;
    // structure: six cards in a fixed order at the top, each opening its chapter; every knowledge point inside a chapter
    const cards = [...document.querySelectorAll('#story .ov-card')];
    out.structure = {
      cards: cards.map(c => { const k = c.querySelector('.ov-kicker'); return k ? k.textContent.trim() : ''; }),
      cardLinks: cards.map(c => { const a = c.querySelector('a[href^="#ch-"]'); return a && document.querySelector(a.getAttribute('href')) ? a.getAttribute('href') : ''; }),
      chapters: [...document.querySelectorAll('main section.chapter[id]')].map(ch => ({ id: ch.id, name: ch.dataset.tocName || '', kps: ch.querySelectorAll('section[data-kp]').length,
        lead: !!(ch.querySelector('.chapter-lead') && ch.querySelector('.chapter-lead').innerText.trim()) })),
      kpOutside: [...document.querySelectorAll('section[data-kp]')].filter(k => !k.closest('section.chapter')).map(k => k.dataset.kp)
    };
    const fmap = document.querySelector('.fmap');
    out.overviewInAppendix = !fmap || !!fmap.closest('#appendix');
    // terms: each registered term is explained (<dfn data-term>) at or before its first use in reading order;
    // capitalised jargon in the opening and the storyline must be registered
    const mainEl = document.querySelector('main');
    // prose in reading order: headings, the knowledge-point map, source lines, demo output and the appendix are labels
    // or generated text, so a term's first use is counted in the prose only
    const SKIP = 'h1, h2, h3, #map, .src, .kp-nav, .demo, .katex, .tex, .tex-block, code, .keyeq-head, #appendix, #checks';
    const walker = document.createTreeWalker(mainEl, NodeFilter.SHOW_TEXT, { acceptNode: n => (n.parentElement.closest(SKIP) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT) });
    let full = '';
    const starts = new Map();
    while (walker.nextNode()) { const n = walker.currentNode; if (!starts.has(n.parentElement)) starts.set(n.parentElement, full.length); full += n.data; }
    const offsetOf = node => { for (const [elx, off] of starts) if (node === elx || node.contains(elx)) return off; return Infinity; };
    const gloss = (window.PR && PR.glossary) || {};
    const dfns = [...mainEl.querySelectorAll('dfn[data-term]')];
    out.terms = { count: Object.keys(gloss).length, late: [], notExplained: [], dfnNotListed: [], unlisted: [] };
    // a term inside a longer registered term ("spectrum" in "hyperspectral camera") is not a use of the shorter one
    const masked = k => Object.keys(gloss).filter(l => l !== k && l.length > k.length && l.includes(k))
      .reduce((t, l) => t.replace(new RegExp(PR.termRe(l).source, 'g' + PR.termRe(l).flags.replace('g', '')), x => '\u0000'.repeat(x.length)), full);
    Object.keys(gloss).forEach(k => {
      const m = PR.termRe(k).exec(masked(k));
      if (!m) return;
      const d = dfns.find(x => x.dataset.term === k);
      if (!d) out.terms.notExplained.push(k);
      else if (offsetOf(d) > m.index) out.terms.late.push({ term: k, context: full.slice(Math.max(0, m.index - 30), m.index + k.length + 20).replace(/\s+/g, ' ') });
    });
    dfns.forEach(d => { if (!(d.dataset.term in gloss)) out.terms.dfnNotListed.push(d.dataset.term); });
    const known = Object.keys(gloss).map(k => k.toLowerCase());
    const story = [...document.querySelectorAll('#story, .chapter-lead, section.chapter > p')];
    const words = new Set();
    story.forEach(sec => {
      const c = sec.cloneNode(true);
      // only the prose the writer wrote: not demo output, source lines or links
      c.querySelectorAll('.katex, .tex, .tex-block, code, a, .demo, .src, .cite').forEach(x => x.remove());
      const tw = document.createTreeWalker(c, NodeFilter.SHOW_TEXT);
      let txt = '';
      while (tw.nextNode()) txt += ' ' + tw.currentNode.data;
      (txt.match(/[A-Za-z][A-Za-z0-9.\-]*[A-Za-z0-9]/g) || []).forEach(w => {
        const caps = (w.match(/[A-Z]/g) || []).length, digit = /[0-9]/.test(w);
        if (caps < 2 && !(caps && digit)) return;
        if (/^[IVX]+(-[A-Z0-9]+)?$/.test(w) || /^[IVX]+-[A-Z]\d?$/.test(w)) return;
        if (known.some(k => k === w.toLowerCase() || PR.termRe(w).test(k))) return;
        words.add(w);
      });
    });
    out.terms.unlisted = [...words];
    // the text a cold reader gets: the teaching prose in reading order. Left out: demos, source lines, the
    // knowledge-point map and the cluster table (reference material), the appendix and the check tables
    const blocks = [...mainEl.querySelectorAll('h1, h2, h3, p, li, dt, dd, figcaption, th, td, .stat, .keyeq .tex-block')]
      .filter(b => !b.closest('.demo, .live, #appendix, #checks, #map, #cluster, .backup-divider, .src') && !b.parentElement.closest('p, li, dd, td, th, figcaption'));
    // what a reader sees: an inline formula as its glyphs (not the LaTeX kept for screen readers), superscripts as ^
    const visibleText = b => {
      const c = b.cloneNode(true);
      c.querySelectorAll('.katex').forEach(k => { const h = k.querySelector('.katex-html'); k.replaceWith(h ? h.textContent : ''); });
      c.querySelectorAll('.cite').forEach(x => x.remove());
      c.querySelectorAll('sup').forEach(x => x.replaceWith('^' + x.textContent));
      c.querySelectorAll('sub').forEach(x => x.replaceWith('_' + x.textContent));
      return c.textContent;
    };
    // a typeset formula reaches the reader as symbols, not LaTeX source; its symbols are listed in the card below it
    out.readingText = blocks.map(b => (/^H[123]$/.test(b.tagName) ? '\n' + '#'.repeat(+b.tagName[1]) + ' ' : '') +
      (b.classList.contains('tex-block') ? '[formula: typeset with mathematical symbols on the page; each symbol is explained under "Symbols and source"]'
        : b.classList.contains('stat') ? '[number card] ' + [...b.children].map(x => x.textContent.trim()).join(': ')
        : visibleText(b).replace(/\s+/g, ' ').trim())).join('\n');
    // figures of the paper are the real files (original bitmap or vector), not screenshots
    out.figures = [...document.querySelectorAll('main .figure img, main figure img')].map(i => ({ src: i.getAttribute('src') || '', crop: !!i.closest('.pdf-crop'), ok: !!i.closest('.pdf-crop') || /-real\.(svg|png|jpe?g|gif|webp)$/i.test(i.getAttribute('src') || ''), loaded: i.complete && i.naturalWidth > 0 }));
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
    ['not yet confirmed', 'to be verified', 'unverified', 'TBD'].forEach(w => {
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
