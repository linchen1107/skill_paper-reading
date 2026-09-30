# Build the reading page

`<plugin>` is the directory above `skills/`. Use the supplied template and widgets; their headers contain the API examples.

## Files and layout

| File | Action |
|---|---|
| `<topic>/index.html` | Copy `templates/page.html`; fill content using its existing classes, sections and navigation |
| `widgets.js`, `katex/`, `serve.py` | Copy from `templates/` and `scripts/` unchanged |
| `demos.js` | Declare computations and checks for all units |
| `papers/`, `figs/`, `data/` | Notes, publication figures and approved sourced samples |
| `_work/` | Extraction, checks, temporary browser profiles and project dependencies |

The page works as plain files: no modules or `fetch` in the reading page; embed small demonstration data. Model- or Python-dependent computation belongs to paper-reading:presentation. Keep delivery assets outside `_work/` so clearing temporary work does not break them.

```text
Brief opening → problem and failure → traditional method → paper cluster
              → idea and evidence → knowledge units → short recap
              → cluster comparison → formula appendix → check results
```

Keep the template's section titles. Add a section on the user's own work only when they provide it. Prefer diagrams and side-by-side results; do not fill each section with prose that repeats the same explanation.

## Units, figures and terms

| Element | Contract |
|---|---|
| Knowledge map | Every numbered point links to its source and `<section class="kp" data-kp="…">`; prerequisites come first |
| Demo | One `PR.demo(id, spec)` per computable point; every input change recomputes; at least one `PR.check` tests a hand calculation or trusted reference |
| Traditional method | At least one `data-traditional="1"` unit, before the new method, comparing the same data; retain cases where the old method performs better |
| Formula animation | `data-formula="1"`; `compute` returns `anim` frames using current inputs, with play/pause/step |
| Noncomputable point | Explain with an appropriate figure or table and say why no computation applies |
| Terms | Register needed terms with `PR.terms`; use `<dfn data-term="…">` at first use and explain in that sentence |
| Publication figure | Copy `fig<N>-real.*` to `figs/`; use `<figure class="figure">`, source caption and working popup; never the captioned reading copy or a page screenshot |

Each unit connects example, difficulty, traditional method, new method and extension; link to shared explanations instead of repeating them. Tell the reader what to change and what to observe. Distinguish generated demonstration data from real dataset results.

## Formulas

Inventory every numbered equation, definition, theorem and algorithm, plus unnumbered formulas and appendices needed by the method. Record symbols, values/ranges, locations and derivation links.

Show only 1–5 key formulas in the units, **after** the corresponding demo. Each `.keyeq` card has a plain sentence with `.w-a` through `.w-d` words matching `\ca` through `\cd` formula terms, and collapsible symbols/source links. No display formula in the storyline.

Place the full inventory in `#appendix`: `PR.formulaMap` with working derivation links and caption, symbol table, then one `section.eq-sec[data-tag]` per formula with LaTeX, symbols, source and previous/next links. Keep explanations brief; let diagrams, worked values and animation carry the mechanism.

## Check and deliver

```sh
python <plugin>/scripts/check_page.py <topic>
```

The checker operates controls, formula animations, reference checks and figures; it checks map links, term introductions, formula placement and the latest cold read. Run [Cold read](cold-read.md) after it writes `_work/verify/reading_text.txt`. Fix concrete failures; stop after 3 unsuccessful rounds and report the remaining issues.

The teaching page contains sourced or computed content. Resolve checkable questions; keep unsettled interpretations in paper notes rather than presenting them as facts. Stated limitations still belong in the explanation.

| Visible record | Include |
|---|---|
| Paper comparison | Role, problem, design, evidence/location, limits and reading depth for each paper |
| Knowledge map | Every point, source and unit link |
| Verification table | Per point: controls operated, animation, reference check, actual status and limitation |
| 報告要求對照 | Understanding/interaction; cluster; research problem; failure/example; traditional method; every knowledge point; restored background; math animation; sourced content; formula layout; newcomer comprehension. One row per item, content link, 符合 or 不符合 |

Keep detailed checks on the page. The final reply links the page and main-paper note, states incomplete items briefly, and does not repeat its tables.

Open the result using available host tools. If an authorized server is needed, use `python <topic>/serve.py`; give the address and start/stop instructions. Stop only processes started for checking. Keep temporary profiles under `_work/tmp/` and remove them after checks. Give concise cleanup guidance only for resources created by this run.
