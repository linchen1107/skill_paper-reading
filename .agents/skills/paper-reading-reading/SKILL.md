---
name: paper-reading-reading
description: Read a supplied research paper with its same-problem paper cluster, explain prior failures and evidence, map every knowledge point, and build an interactive teaching page. Also use for paper Discussion review or code search.
---

# Paper-cluster reading and interactive teaching material

A paper report is not reading slides aloud; it shows your understanding of the paper. Read the whole cluster of related papers, work out which problem the paper actually solves, turn every knowledge point into interactive material driven by real computation, and animate the math.

Every part must link to the others: **difficulty → why the traditional approach is not enough → the paper's method → knowledge points → demos → back to the original difficulty.** Every entry on the knowledge-point map links to its source location in the paper and to its section.

## Output language and wording

All user-facing output of this skill (the page, notes, and chat replies) is written in **Traditional Chinese as used in Taiwan**. Technical terms stay in English when that is clearer (for example AUC, PCA, token).

- Write complete sentences with a clear subject and verb. Lead with the conclusion, then the reason.
- Explain a technical term in one plain sentence the first time it appears.
- Use Taiwanese terminology, not Mainland terms: 影片 not 視頻, 資料 not 數據 (for data), 品質 not 質量, 資訊 not 信息, 預設 not 默認, 程式碼 not 代碼, 模組 not 模塊, 網路 not 網絡, 支援 not 支持 (for software support), 檔案 not 文件 (for files).
- **Cite papers by author and year** (for example Wang et al. 2017), linked to their note. Short ids such as `wang17` are file names only and never appear in the text.
- **No compressed coined words.** Say it in a plain phrase instead (「背景是否接近白雜訊」, not 「白性」); a technical term gets a plain one-sentence explanation the first time it appears.
- **Evidence labels go in parentheses after the claim**, for example 「……整體平移（原論文報告，Section I）」; never as a sentence fragment on its own.
- No filler, slogans, invented abbreviations or compressed coined phrases. Say what happened, its effect, and the evidence.
- Use Arabic numerals.

## Workflow

Complete the following 6 stages in order. **Do not start stage 1 until the user has authorized the full scope; prior authorization in the conversation counts.** When the user explicitly narrows the scope, follow it and state at the top of the reply which stages were skipped.

| Stage | Goal | Not done when |
|---|---|---|
| 0. Scope confirmation | Read the user's paper in full: the whole text and every figure; list the scale and format; use the user's existing approval or wait for approval | A figure of the user's paper not viewed; no reading log; full reading of other papers, downloads or code before approval |
| 1. Paper cluster | Read about 20 directly related papers (20–30 when the problem needs it), by "How to read a paper"; work out what each solves, how they build on each other, and what gaps remain | Only 1 paper read; titles, abstracts or search results counted as read; a figure cited in a note but not viewed; unrelated papers used as padding |
| 2. Difficulty | Open with a real-life example; explain what makes the problem hard and where the traditional approach falls short | Opening with the paper's method; difficulties without sources; failures invented to justify the motivation; the traditional approach only described, not run |
| 3. Knowledge-point map | List every knowledge point, grouped and numbered, each tied to papers and source locations | Only highlights; sampling; listing only what the paper states without restoring the background it cut |
| 4. Interactive material | Every knowledge point as a section of one page, with a demo computed by shared code; inputs can be adjusted and results update immediately | Pre-drawn animations or hard-coded numbers; interface without computation; a formula without a formula animation; a knowledge point missing from the page; a program written per knowledge point |
| 5. Report storyline | Tie the cluster, difficulties and knowledge points into one storyline: why, how, what the evidence supports, what remains unsolved | Paper-by-paper summaries stacked without their relationships; open questions or unconfirmed statements on the page |

**Completion is judged by actual operation.** A count of knowledge points, existing buttons or screenshots do not mean something is covered or verified.

## Report requirements

These come from the lab's review of how a paper must be reported (see [references/sources.md](references/sources.md)). They define what the user needs. Every run meets all of them, and the page ends with a 報告要求對照 table: one row per requirement, a link to where the page meets it, and 符合 or 不符合. The final reply repeats that table. A requirement that is not met is reported as 不符合, never glossed over.

| # | Requirement (review point) | Met when |
|---|---|---|
| 1 | Show understanding, not slides; interactive and playable | Every computable knowledge point has a demo that `check_page.py` passes |
| 2 | Report a cluster of papers, not one (20+) | The cluster table lists about 20 papers, each tied to a place in the user's paper |
| 3 | Work out what the paper actually solves | Section 1 names the problem and the difficulties before any method appears |
| 4 | Open with a concrete failure and an everyday example | Section 1 starts from one concrete case where the existing approach fails (what was expected, what happened, the effect, with its source), then an everyday example of why it is hard; knowledge points open with an everyday example |
| 5 | Explain the traditional approach in great detail | Section 2 explains it, and at least one knowledge point (`data-traditional="1"`) runs the traditional method on the same data as the paper's method, placed before the paper's method |
| 6 | Explain every knowledge point with a program (10, 20, 60 of them) | The map lists every point, and each has a demo or says why it cannot have one |
| 7 | Do more than the paper; restore what it cut | Background and derivations the paper only names are knowledge points of their own |
| 8 | Animate the math | Every knowledge point with a formula (`data-formula="1"`) has a formula animation that steps through the computation with this run's numbers |
| 9 | The page shows understanding, not open questions | The page contains confirmed content only (see "What the page shows") |
| 10 | Formulas: only the key ones in the text, each after an example; the rest on demand | 1 to 5 key formulas, each a card after its knowledge point's demo, with a plain sentence whose coloured words match the formula's coloured terms; no display formula in the storyline; every formula of the paper, the formula map and the symbol table in the 附錄 at the end |

## What the page shows

The page teaches the paper; it is not an audit of it and not a list of open questions.

- **Confirmed content only.** On `index.html` every statement is either reported by a paper (原論文報告, with location) or computed in this run (本次實際重現). The label 待驗證的推論 and the words 尚未確認, 待驗證 and 還沒確認 do not appear on the page; `check_page.py` fails the page if they do.
- **Check what can be checked, during the run.** When a question can be settled by reading the paper again, its arXiv or supplementary version, the official code, a cited paper, or by recomputing, settle it and write the answer. Do not hand it to the reader.
- **What cannot be settled goes into the notes.** Open questions, suspected typos and interpretations stay in `papers/<short>.md` under 我的判讀, with their label. They do not appear on the page.
- **Errors in the paper, when confirmed**, appear on the page only where a reader needs them to understand a result correctly, inside that knowledge point or evidence paragraph, stated as a fact with its location (for example a table value outside the metric's definition). There is no separate list of the paper's errors on the page.

## Usage budget

Keep the workflow economical without claiming a known quota or token cost; estimate scope before a full run.

- Use the model selected by the user or Codex; do not assume a Claude-specific model is available.
- **Read text, not pages**, by "How to read a paper". Use `sections.tsv` to read one section with an offset instead of the whole file, and search instead of reading a file again.
- **Subagents read in batches** of 5 to 6 papers, write their notes to files and return one line per paper; they do not paste notes or paper text back.
- **Templates, not new code**: the page, the widgets, the download and the checks come from this skill (`templates/`, `scripts/`); the run writes only the content and `demos.js`. Resolve a Python executable on this host before running the bundled scripts.
- **Check by values, not screenshots.** At most one screenshot at the end, if a layout question cannot be settled otherwise.
- **Estimate first.** The stage 0 proposal states the number of papers, knowledge points and demos. If the scope looks too large for the budget, propose a smaller one in the same reply.

## Evidence labels

Every claim carries one of these 3 labels, written exactly like this:

| Label | Meaning |
|---|---|
| 原論文報告 | A number, result or claim the paper itself reports, with page, section, Figure, Table or theorem |
| 本次實際重現 | A result produced by code in this run (demo computation or reproduction experiment), with input, parameters and code location |
| 待驗證的推論 | The reader's interpretation or expectation, not yet supported by evidence. Used in notes only, never on the page |

- **Observing a failure does not mean the cause is known.** Keep the phenomenon and the cause separate; state a cause as confirmed only when the paper's analysis or an experiment supports it.
- **Numbers from different test conditions cannot be ranked directly.** When data splits, model size, training data, evaluation rules or cost differ, describe the conditions under which each number holds.
- **A demo's result is not the paper's experimental result.** A phenomenon computed on demo data is labelled 本次實際重現 with a note that it uses demo data; it must not stand in for the paper's results on the real dataset.

## How to read a paper

**Read from text; look only at real figures.** The text, tables, numbers and equations come from the text layer. Opening page images of text costs usage and adds nothing, so it is not done. Only figures (diagrams, plots, photos) are looked at as images.

1. **Extract.** `<skill>` is the directory containing this `SKILL.md`. For one paper run `python <skill>/scripts/extract_figures.py <paper.pdf> <topic>/_work/extract/<short>/`; for a batch write a list (`<short><TAB><arXiv id, PDF URL or local path>` per line) and run `python <skill>/scripts/fetch_papers.py <list.tsv> <topic>`, which downloads and extracts every paper in one command and reports the ones it could not get. Each paper gets `text.txt` (the whole text layer, with page markers), `sections.tsv` (headings with their line numbers), one `fig<N>.png` per captioned figure (a reading copy with its caption, for looking at the figure), one `fig<N>-real.*` per figure (the figure itself as the paper holds it: the original embedded bitmap at its own resolution, or the vector drawing cropped to SVG), and `figures.tsv`. PyMuPDF is the only requirement; if `python -c "import fitz"` fails, ask the user to approve installing it into `<topic>/_work/.venv/` (`pip install --no-cache-dir pymupdf`, about 20 MB), and do not continue until it is installed.
2. **Read the whole text** of `text.txt` in order, and follow the line of argument section by section: what each section sets up, which figure or table carries it, and how it leads into the next.
3. **Tables and numbers from the text.** Keep original precision. If the text layer leaves unclear which number belongs to which row or column, write 尚未確認 for those cells in the note instead of guessing, and settle them before the page uses them.
4. **Equations from the text.** Only if an equation is garbled beyond reading, crop that one equation from its page (`page.get_pixmap(clip=rect, dpi=150)`) and look at the crop.
5. **Figures in context.** Open each `fig<N>.png` together with its caption, the paragraphs that cite it ("as shown in Fig. 3") and its section. Record what it shows, which claim it supports, and whether the text's claim matches what the figure shows. Numbers read off a plot are approximate and marked as such. A figure listed as `not found` in `figures.tsv` is cropped from its page by hand; only that crop is viewed.
6. **Which figures.** For the user's paper, every figure. For other papers, only the figures their note cites, usually 0 to 2.
7. **Keep a reading log** at the top of the paper's note: text read in full (yes or no), figures viewed out of captioned figures (for example 20/20: Fig. 1 p.2, Fig. 2 p.3, ...), tables read from text (for example Table 1 p.7), and any equation that had to be cropped.

## Stage 0: scope confirmation

Before proposing, **read the user's paper in full by "How to read a paper"**, including every figure; the extracted text and figures may be written to `<topic>/_work/extract/` at this stage. Then do the searches and skimming needed to find candidates (titles, abstracts, reference lists). **The proposal starts with the reading log of the user's paper.** A proposal without it, or one that cites a figure or table not in the log, is not done. Mark everything in the proposal as provisional. Full reading, downloads, agent dispatch and code wait until the user authorizes the full run; reuse authorization already given. If the user has approved it, show the proposal briefly and continue; otherwise wait for a reply. List the following. Wait only if the full run has not already been authorized.

1. **Paper-cluster candidates**: expected count (default 20), initial list, and each paper's role.
2. **Draft knowledge-point list**: groups, numbering, dependency order (foundations first).
3. **Demo for each knowledge point**: what the user manipulates, what the screen shows, where the computation runs.
4. **Real samples to download**: list only when a knowledge point cannot be explained without real data (for example a real recording or a real image), with file name, source and size. If demo data can be generated by code, do not download.
5. **Real backend**: whether the paper's method can run on real samples on this machine, checked, not guessed: `python --version`, the packages that import, the GPU (`nvidia-smi`, and whether torch sees it), free disk space, and whether the data and model weights are public. If it can, propose 2 to 5 labs with the downloads (source, licence, size) as in $paper-reading-presentation's Step 0; after the reading page is accepted, that skill builds them without asking again. If it cannot, say what is missing; the reading page is made either way.
6. **Estimated workload**: number of papers, knowledge points and demos.

Do not ask for the reading purpose. If the user did not state it, identify the problem the paper solves; do not guess the user's own research topic.

## Stage 1: paper cluster

- **The user's paper comes first.** The cluster exists to understand that paper. Read it first and most deeply: every section, every figure and table in context, every equation. Other papers are read for what they explain about it (predecessors, the traditional approach, the baselines it compares against, later work that tests its claims), and the report is about the user's paper. **Every added paper names the passage, figure, table or equation of the user's paper it explains.** A paper that cannot be tied to a specific place in the user's paper is left out, however interesting.
- Even when given 1 paper, use it as the starting point and find its direct predecessors, the traditional approaches, the main comparison methods and follow-up work. Do not shrink this work because the paper is only 5 pages. When the user provides a set of papers, read that set first; any added paper must state which gap in context it fills.
- **When agent delegation is authorized and available, split the reading across subagents.** The main flow first builds the candidate list and each paper's role, then hands papers to subagents in batches of 5 to 6. Each subagent fetches and extracts its whole batch with one command, reads each paper's `text.txt` once, never renders whole pages as images, and writes each note directly to `papers/<short>.md` (research problem, shortcomings of prior approaches, core method, evidence with source locations, role in the cluster, knowledge points involved, how much was read). It returns only one line per paper to the main flow: title, status, and the place in the user's paper it explains. The main flow does not read the notes in full; it searches them for what it needs, and spot-checks key numbers against the original paper.
- **Depth follows the user's paper.** The user's paper is read in full. Direct predecessors and the methods it compares against in its tables are read in full too. Every other paper is read in its relevant parts: abstract, introduction, conclusion, and the sections that explain the place in the user's paper it was chosen for, found through `sections.tsv` and read with an offset. Only the figures a note cites are viewed. Skip appendices unless the user's paper relies on them. Subagents follow this and return their reading log.
- **Look for local copies first.** Before calling a paper unobtainable, search the folder the user's paper came from (and any folder the user named) by title, author or year; use what is there and do not copy it elsewhere.
- Confirm each paper's full title, authors and version, and prefer the original text. Surveys and secondary write-ups can help locate things, but key methods, numbers and conclusions must be checked against the original paper.
- Mark each paper 已讀全文, 已讀相關段落 (list the sections read), 部分閱讀 (abstract or less, or a cited figure not viewed) or 待讀. Anything not obtained is marked 尚未確認.
- If fewer than 20–30 related papers exist, state the actual count and the reason; do not claim the expected scale was reached.
- A problem already addressed by later work must not be described as unsolved.

## Stage 2: difficulty

- **Open with one concrete failure, then an everyday example.** First a real case from the paper or its cluster: what was expected, what actually happened, and the effect, with its source (for LUNA: the model answers that water vapour is denser than air, Fig. 4). Then a technology or phenomenon from everyday life that shows why the problem is hard; for audio normalization, for example, recording and Dolby noise reduction: why signal-to-noise ratio (SNR) and dynamic range are hard to handle. The audience needs a picture first; only then can they follow the method.
- **Explain the traditional approach in great detail, and run it.** How it works, what it solves, and where it falls short are prerequisites for understanding the paper. Papers usually assume the reader already knows this and start from the later part; the report must put it back. The traditional approaches the paper improves on or competes with become knowledge points marked `data-traditional="1"`, placed before the paper's method, and their demos run on the same data as the paper's method so the two can be compared side by side, including the settings where the traditional approach does as well or better.
- **Difficulties need a situation and a source.** Record under which conditions which problem appears, its effect, and the location in the paper or demo. A shortcoming the authors state in the Introduction without supporting evidence is written on the page as the authors' statement (原論文報告, with location); never invent a failure.

## Stage 3: knowledge-point map

- If the user provides a knowledge-point list or course map, it defines the complete scope; reuse its names and numbers. Otherwise, derive the complete list from the cluster and explain the grouping.
- **Every knowledge point is anchored in the user's paper.** It cites the section, figure, table or equation of the user's paper that needs it. Background the paper omits qualifies only when a specific passage of the paper cannot be understood without it; cite that passage. A point with no anchor is dropped.
- **Every knowledge point must be handled; no highlights only, no sampling.** Each has a one-sentence explanation, its relation to the research problem, the papers and source locations, and its section in `index.html`.
- **Do more than the paper.** Background and derivations the paper cut for space (for example Gaussianization or spectral whitening mentioned only by name) are also knowledge points.
- Order by dependency: foundations first, then what builds on them.
- At the end, check item by item. Group-level completion is not enough: a group can be finished while one of its points is missing.
- **Formula inventory.** List every numbered equation, definition, theorem and algorithm of the user's paper, and every unnumbered formula the method depends on (including those in appendices it relies on): its number, page and section, its LaTeX, and its links: which formula it comes from and which it leads to, with the step in between named in a few words (adds mutual information, replaces with a lower bound, takes the mean over the state). Also list every symbol with its meaning and the paper's setting for it (value, range, network, with location). These become the formula map, the symbol table and the formula sections of the 附錄.
- **Key formulas.** Mark 1 to 5 formulas as key: the ones the paper's main result cannot stand without (a reader who skips every other formula still follows the method). Name for each why it is key and the knowledge point whose demo computes it. Most readers see only these; the others stay in the 附錄 and one click away.

## Stage 4: interactive material

All knowledge points live on one page and share one widget library. The page, the widgets and the checks come from the plugin; the run writes only the content and `demos.js`. Resolve a Python executable on this host before running the bundled scripts.

**Files.**

- Copy `<skill>/templates/page.html` to `<topic>/index.html` and fill in its marked places; keep its sections, titles and navigation.
- Copy `<skill>/templates/widgets.js` to `<topic>/widgets.js`, the folder `<skill>/templates/katex/` to `<topic>/katex/` and `<skill>/scripts/serve.py` to `<topic>/serve.py`, unchanged. The widgets provide controls, plots, formula typesetting and animation, the formula map, the sidebar, figure popups and hand-calculation checks; the header of `widgets.js` shows how to use them.
- Write only `<topic>/demos.js`: one `PR.demo(...)` per knowledge point that can be computed, and at least one `PR.check(...)` per demo that compares a setting with a hand calculation. No knowledge point gets its own page or program.
- `index.html`, `widgets.js` and `demos.js` are plain files (no modules, no `fetch`), so the page also works when double-clicked; small data is embedded in `demos.js`.

**Page order.** The page reads from top to bottom as one argument: the conclusion, the problem, the traditional approach, the paper's idea and evidence, then each knowledge point, and last the full formulas for readers who want them. A reader who stops anywhere has understood everything above that point.

1. **重點整理**, then **the storyline** (stage 5). It carries no display formula; it explains in words, numbers and the paper's figures, and links each step to its knowledge point.
2. **The knowledge-point map and the knowledge points**, each showing its key formula card when it has one.
3. **The cluster comparison.**
4. **附錄** (`<div id="appendix">`): the formula map (`PR.formulaMap`: one lane per strand of the method, one box per formula with its number and page, arrows naming the step between formulas, a dashed arrow for a proof, the final objective highlighted, and one caption paragraph telling the derivation in words), the symbol table, then every formula one by one, grouped in the order of the derivation: a `section.eq-sec` with its number as `data-tag`, the formula typeset in LaTeX (`tex-block`, terms coloured with `\ca` `\cb` `\cc` `\cd`), its page and section, each symbol explained in one line, and links to the formula it comes from, the one it leads to, and the knowledge point that computes it.
5. **The check results.**

**Knowledge points.**

- Each is one section of `index.html`: its number as `<span class="chip">` (`chip trad` for a traditional approach), then real-life example, difficulty, traditional approach, the paper's method and extension, one or two sentences each, then its demo, then its key formula card if it has one.
- **Key formula card** (`<div class="keyeq">`, template in `page.html`): after the demo, so the reader has already seen the numbers before the general form. It holds one plain sentence that says what the formula computes, with its key words coloured (`<span class="w-a">` to `w-d`) to match the formula's terms (`\ca` to `\cd`); pointing at either marks both. Then the formula, and a collapsed 符號與出處 with its symbols, location and a link to its 附錄 section. The widgets add links from every knowledge point to its formulas in the 附錄.
- **Real interaction.** When the user changes an input, the result is recomputed by code running the algorithm, not a switch between pre-made images. Keep the cases where the paper's method still does poorly.
- **Animate the math.** A point whose method is a formula is marked `data-formula="1"`, and its `compute` returns `anim`: the formula taken apart into frames, from the definition through each substitution to the result, with the current numbers filled in; a frame may carry a plot that changes with it (for example a transition matrix filling in count by count). The reader can play, pause and step. The animation is recomputed from the current inputs, never pre-drawn.
- **Points without a computation** (a definition, a dataset fact) show the paper's figure or a small table and say why there is no demo.
- The widgets lay a demo out in two columns on wide screens (controls and formula steps on the left, staying in view; results on the right), add a bar with the point's formulas and its previous and next point, and land every jump on its target with a brief highlight. Nothing to write for this.

**Figures.**

- **The paper's own figures, never screenshots.** A figure shown on the page is its `fig<N>-real.*` file, copied to `<topic>/figs/<short>-fig<N>-real.<ext>` and placed in the section that discusses it: `<figure class="figure">` with `<figcaption>原論文 Fig. N（p.X）：…</figcaption>`. The reading copy `fig<N>.png` and page renders never appear on the page. A figure that could not be extracted as a real file is cited by number and page instead.
- Clicking a figure opens it in a popup sized to the window, with its caption; the arrow keys step through all figures.

**Styling.** Use the template's classes rather than new styles: key numbers of the storyline in `.stats` cards, reading status and check results as `.badge` (`ok`, `mid`, `low`, `bad`), wide tables in `.table-wrap`, a paper's name as the link to its note. Prose keeps the template's reading width.

**Where the computation runs.** In the browser. Computation that needs Python packages, a model or large data belongs to the labs of $paper-reading-presentation (stage 0, item 5), not to this page.

**Acceptance.** Run `python <skill>/scripts/check_page.py <topic>`. It opens the page in the Chrome, Edge or Chromium already on the machine, moves every control of every demo and confirms the output changes, steps through every formula animation, runs every `PR.check`, opens every figure, and prints one line per knowledge point (通過 / 未通過 / 無示範). The page as a whole fails when the formula layer is incomplete (no formula map, a box linking nowhere, a formula section missing from the map, an empty symbol table, a formula KaTeX could not typeset), when the key formulas break their rules (none, more than 5, before their demo, without a plain sentence whose coloured words match the formula), when a display formula appears in the storyline, when the formula map is not in the 附錄, when a figure is a screenshot or does not open, when no knowledge point runs a traditional approach, when a map entry has no section, or when unconfirmed wording appears. Fix what fails and run it again. Copy its lines into the 驗收結果 table, then fill the 報告要求對照 table. No screenshots.

## Stage 5: report storyline

The storyline opens `index.html`, right after 重點整理. It connects the cluster, the difficulties and the knowledge points, and each section links to the knowledge-point sections it relies on.

Use these Chinese section titles on the page:

| Section title | What the reader should understand |
|---|---|
| 1. 生活中的例子與困難 | What problem does this cluster address? What does it correspond to in daily life? What makes it hard? |
| 2. 傳統作法與它的限制 | How the traditional approach works, where it falls short, and the effect |
| 3. 論文群與研究缺口 | Scope and each paper's role; how they build on or diverge from each other; which gaps remain |
| 4. 核心想法與方法 | What each paper changes, which difficulty it targets, why it should work; which knowledge points it maps to |
| 5. 證據與改善幅度 | How each paper tests its claims, what the results support, whether conditions are comparable |
| 6. 已解決與未解決 | What is supported by evidence, what improves only under specific conditions, what is still unsolved (a limitation the authors state, or a gap later work addressed; not the reader's open questions) |
| 重點整理 | 3 sentences: the core problem, the improvement the evidence supports, the problem still unsolved |

There is no section of open questions; see "What the page shows".

**Sections connect through their content, not through signposts.** Write "the traditional approach fails when …, so the paper …", not "下一節：…". "Uses module X" is not a research rationale, and a higher average score does not mean every failure is gone. For comparisons, use a table of each paper's difficulty, core design, evidence and remaining problems, with source locations.

## What the user sees at acceptance

`index.html` is the acceptance page. From it the user must be able to see, without opening other files:

1. **Paper-cluster comparison**: one row per paper with its role, the difficulty it addresses, its core design, its evidence (with source location), what it leaves unsolved, and how much was read (已讀全文 / 已讀相關段落 / 部分閱讀 / 待讀).
2. **Formulas**: the key formulas inside their knowledge points, and in the 附錄 the formula map, the symbol table and every formula typeset with its location.
3. **Complete knowledge-point map**: every point, grouped and numbered, with its source location and a link to its section.
4. **Interactive material**: each knowledge-point section with its demo.
5. **Item-by-item check results**: one row per knowledge point with the controls that were operated, whether its formula animation steps, the hand calculation or reference it was checked against, the result (通過 / 未通過 / 未驗收), and any limitation. Totals alone ("279 controls passed") are not enough; each point must be traceable to its own row.
6. **Report requirements**: the 報告要求對照 table from "Report requirements", one row per requirement with a link to where the page meets it.

## Output location

Never write to an Obsidian vault unless the user explicitly asks. Use the user's specified writable location; otherwise place the topic under the current workspace, following any host-specific output-folder rule:

```
<workspace>/paper-reading/<topic>/
  index.html            the one page: storyline, paper-cluster comparison, every knowledge point with its demo, check results
  serve.py              opens the page at a local web address (`python serve.py`); starts studio/server.py instead when presentation has added it
  widgets.js            the plugin's shared widgets, copied unchanged
  katex/                formula typesetting (KaTeX, MIT), copied unchanged; works offline
  demos.js              the computation of each knowledge point's demo
  papers/<short>.md     one note per paper
  data/                 real samples and their sources; created only when the user approved a download
  studio/               the labs of $paper-reading-presentation, when stage 0 approved them
  _work/                by-products; deleting it breaks none of the above
    extract/<short>/    text layer, figures and figures.tsv of each paper read
    .venv/              Python virtual environment
    tmp/                temporary files, emptied when done
    verify/             check_page.py results (check.json)
```

**All source files live inside the output folder.** Neither subagents nor the main flow may keep the source used to assemble pages, generate data or run checks outside it; material kept elsewhere can no longer be edited once that place is cleared.

**When done, open the result for the user; do not leave it for them to open.**

1. Start `python <topic>/serve.py` in the background: it serves the folder at `http://127.0.0.1:<port>/index.html` (standard library only, a free port from 8000) and opens it in the user's default browser. The reply gives the address, the port, how to stop it and the command that starts it again. If it cannot start, open `index.html` directly (Windows: `Start-Process "<path>\index.html"`; macOS: `open`; Linux: `xdg-open`); the page also works as a file.
2. Start the final reply with clickable markdown links: `index.html`, then the note on the user's paper. Do not give plain-text paths only. Then give the 報告要求對照 table (requirement, where on the page, 符合 / 不符合), so the user can see what was delivered against each requirement without searching the page.
3. If the browser cannot be opened (for example a remote session without a desktop), say why, and still give the links.

Before writing a paper note, check by full title or DOI/arXiv id whether it already exists; if it does, update it and keep any comments the user wrote.

## Work only inside the output folder

The run must be easy to clean up: everything it produces is in one folder, and results are kept apart from by-products.

- **Write only inside `<topic>/`** (or the location the user specified). Not the scratchpad, the current working directory, Downloads, the home directory, an Obsidian vault, or this skill's folder. Downloaded papers and data go inside `<topic>/` too.
- **Results at the top level, by-products in `_work/`.** Page images, the virtual environment, temporary files and acceptance evidence go in `_work/`. Deleting `_work/` must not break `index.html`.
- **Install nothing globally.** Python packages, including PyMuPDF, go into `<topic>/_work/.venv/`, installed with `pip install --no-cache-dir`; npm packages stay in that project's `node_modules/`.
- **Subagents get the same boundary.** Every subagent prompt states the absolute path of `<topic>/` and this rule.
- **Browser profiles are temporary.** A headless browser used for checking gets its profile directory (`--user-data-dir`) under `_work/tmp/`, and the directory is deleted when checking ends. Only screenshots and logs are kept, in `_work/verify/`.
- **Stop what you started for checking.** A server or headless browser started for checking is stopped when checking ends. The one server left running is the one started for the user at hand-over; the final reply says how to stop it and the command that starts it again.
- **Check before finishing.** Empty `_work/tmp/`; confirm that `index.html` still works without `_work/`; confirm nothing was written outside `<topic>/`.
- **Tell the user how to clean up.** The final reply lists: to free space, delete `_work/` (with its size); to remove everything, delete `<topic>/`; anything installed with approval; the server still running and how to stop it.

## Actions that require asking the user first

For material downloads, package installs, model weights, or a server start, check the user's existing authorization first. If absent, state the source, size or port and ask; an approved plan covers the actions it listed without repeated requests. Do not use external services that need an API key unless the user asks.

## After stage 5: labs with a real backend

Labs on real dataset samples with a Python backend are built by **$paper-reading-presentation** from this skill's output folder. When stage 0 proposed labs and the user approved them, continue with that skill after stage 5 in the same run, and hand over the reading page and the labs together at one address (`python serve.py`). Otherwise it runs when the user asks.

## Other modes

Use only when the user explicitly asks.

### Reproducing the paper's experiments

Only when the user asks to verify the paper's experimental results; never the default.

- **Dataset**: actually load sourced data, sample ids, annotations and splits; distinguish real data, test data, human annotation and model predictions. No placeholder data.
- **Backend**: compute with the required code, model and weights and return results or specific errors. A startup message, a passing health check or a display of existing results is not evidence that inference ran. If packages, weights, data or hardware are missing, report what is missing.
- **Comparison**: compare the prior method and the paper's method on the same data under compatible conditions; state in advance what counts as an improvement; keep the cases that still fail.
- **Acceptance**: run "select data → load method → compute → show result → compare" end to end, and confirm that failures report their cause.

### Writing or checking a Discussion

Check 5 aspects: explanation of results, comparison with other work, significance, limitations, future work. Then ask:

1. Why might the result have occurred? Which explanations have evidence, and which are 待驗證的推論?
2. Compared with prior methods in the cluster, which difficulty or gap does it improve? Are the comparison conditions compatible?
3. What remains unsolved? What does it suggest for follow-up work, and which verification is still needed?

Point to the specific missing argument, paragraph or evidence. When checking a draft, report problems and suggestions; rewrite only when the user asks. Never fabricate results, mechanisms or citations that were not provided.

### Finding open-source code

Search in this order: the paper itself and its arXiv/OpenReview page, the conference site, the authors' or lab's pages, then GitHub keywords and Awesome lists. Report the repository link, whether it is the official implementation, the star count at query time, and the last update. If nothing is found, write 未找到; if it cannot be verified, write 尚未確認. Never substitute a similarly named repository.

## Per-paper note template

Field names and content are in Traditional Chinese:

```markdown
---
title: "<論文完整標題>"
簡稱: "<方法名或第一作者年份>"
年份: <yyyy>
出處: "<會議、期刊或 arXiv；尚未確認時註明>"
用途: <核心／支撐／背景／待讀／未分類>
狀態: <已讀全文／已讀相關段落／部分閱讀／待讀>
連結: "<原文網址或 DOI>"
程式碼: "<已確認網址／尚未查找／未找到／尚未確認>"
讀取日期: <yyyy-mm-dd>
---

# <簡稱>

**閱讀紀錄**：<全文是否讀完；看過的圖／有圖說的圖，例如 20/20：Fig. 1 p.2、Fig. 2 p.3；從文字讀的表格，例如 Table 1 p.7；需要裁切的公式>
**閱讀範圍**：<版本、全文或已讀章節；補充材料是否已讀>
**論文群中的角色**：<針對哪個困難，如何承接或對比相關論文；附連結>

## 困難點與研究動機
<既有作法不足的情境、證據與影響；現象與原因分開>

## 核心想法與方法
<改善哪個問題、採取什麼設計、為什麼；輸入、關鍵步驟與輸出>

## 論證脈絡
<逐節說明：每一節要建立什麼、由哪張圖或表支撐、如何接到下一節>

## 圖表（逐一，含上下文）
### <Fig./Table 編號>（p.<頁>）
- 呈現什麼：<圖：從抽出的圖片讀到的內容；表格：從文字層讀到的內容>
- 上下文：<圖說，以及引用它的段落與章節>
- 支持的主張：<正文說它證明什麼；圖表實際是否支持>

## 證據
### <要檢驗的主張>（<章節、頁碼、圖表或定理>）
- 標籤：<原論文報告／本次實際重現／待驗證的推論>
- 如何檢驗：<比較對象、資料與重要條件>
- 結果：<原始數字與單位；自行計算的差值要標明>
- 可以支持什麼：<改善程度、適用範圍、與其他論文是否可比>

## 解決的部分與剩餘問題
**作者明列的局限**：
> <短引原句及出處；未讀相關內容時寫「尚未確認」>

**我的判讀**：<有證據的疑問，以及待驗證的推論>

## 對應的知識點與互動單元
<本篇涉及的知識點編號，以及單元檔案位置>
```

## Hard rules

**No plausible-sounding filler.** Every statement about the user's paper cites where in the paper it comes from (page, section, figure, table or equation). General knowledge is labelled as background and never attributed to the paper. If the paper does not say something, write 原文未說明 instead of supplying a reasonable-sounding answer. Content that is correct but does not help understand the user's paper is cut: it pulls the reader off topic.

**Numbers are traceable.** Keep original precision, units, dataset, metric and comparison target, with the source location. Distinguish relative percentages from percentage points. In notes, write 尚未確認 when not read; write 原文未列 only after confirming the paper does not list it. On the page, a number that was not read is not used.

**Conclusions match the strength of the evidence.** Correlation, a comparison result or publication order does not prove causation. When other differences are not controlled, do not attribute the whole improvement to one design.

**Keep the authors' limitations separate from the reader's assessment.** Quote the authors' stated limitations briefly with location; put your own doubts under 我的判讀.

**Agent work follows the host and user settings.** Delegate only when authorized and available; verify each agent's source claims.

**Never present precomputed results as live computation.** If part of a demo uses precomputed data, say so on screen.

**Stay within the task.** Do not rewrite the user's thesis outline, batch-reorganize whole folders, or add index generators unless asked.

## Sources

The user's original requirements, the lab's review points and the origin of each rule are in [references/sources.md](references/sources.md). Read it only when a rule needs checking.
