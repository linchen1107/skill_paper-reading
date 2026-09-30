# Sources and scope of the rules

This plugin (`paper-reading:reading` and `paper-reading:presentation`) is written from the user's explicit requirements and the lab's review points, with reference to short-video posts and a Discussion screenshot the user collected. Each requirement is summarised here, so the rules stay checkable without the chat history or local files.

## The user's core requirements (2026-09-29)

- Read a whole cluster of papers at once, not a single paper, and work out which problem it solves.
- The backend must really run; the report needs pictures, a dataset and a real playground.
- Other people's failures are the starting point of the report: they explain why the research is worth doing.
- Every knowledge point must be covered.
- Before presenting a 5-page paper, process 20–30 papers.

The summary the user confirmed as the intended concept:

| Concept | What it must achieve |
|---|---|
| Research motivation | Where existing methods fail, the effect, and why it is worth studying |
| Paper cluster | Around one problem: which bottleneck each paper addresses, how they build on each other, what gaps remain |
| Research design | Every design choice maps to a concrete gap, with why it should work and how to verify it |
| Dataset and pictures | Actually load sourced images, annotations and splits; failure cases can be inspected |
| Backend | Actually run the method or model; return computed results and errors; verify the whole inference flow |
| Playground | Choose data, method and parameters; trigger backend execution; see pictures, predictions and evaluation; compare failure and improvement |
| Report | Answer why, how, what the evidence supports, and what is unsolved |

These parts link to each other: gap → method → experiment → data and results → back to the original failure. Evidence is labelled 原論文報告 (reported by the paper), 本次實際重現 (reproduced in this run), or 待驗證的推論 (inference to be verified, notes only). Observing a failure does not mean knowing its cause; numbers from different test conditions cannot be ranked directly.

Other confirmed requirements:

- One uniform format unless asked otherwise → the full workflow is the default; other modes only on explicit request.
- Never write to an Obsidian vault.
- Default output under the user's `Documents/claude/` → `~/Documents/claude/paper-reading/<topic>/`. It must work on any machine → the home directory is resolved at run time, and the PDF renderer is detected per machine.
- Reading outputs are in Traditional Chinese; presentation outputs are in English; the skill files themselves are in English (see each skill's language section).

## Lab review points (2026-09-29 paper-report meeting)

During a student's talk on an audio-normalization paper, the reviewer stopped the talk and demonstrated how a paper should be reported. Times are positions in the meeting recording.

| Time | Review point | Rule |
|---|---|---|
| 00:00–00:20 | Ignore the slides; show your understanding of the paper as interactive, playable material | Output is interactive material, not slides |
| 01:33–01:52 | A paper yields 10, 20 or 60 knowledge points; explain each one with a program | Reading stages 3–4 |
| 07:03–07:30 | Report a cluster of papers, not one; the reviewer found more than 20 related papers on the spot | Reading stage 1 |
| 08:22–08:29 | Work out what the paper actually solves | Reading stage 2 and storyline |
| 03:55–05:02 | Start from something in everyday life (Dolby noise reduction, recording) so the problem is easy to picture | Open with a real-life example |
| 14:15–14:35 | The paper assumes the reader knows everything and starts from the back | Restore the background the paper omits |
| 16:35–17:22 | Go from motivation to the traditional solution to the paper; the traditional (log) method must be explained in great detail | Traditional approach in detail, and run |
| 17:24–18:27 | Build out Gaussianization and spectral whitening; do more than the paper, which cut a lot for space | Add knowledge points the paper cut |
| 18:50–19:20 | Animate the mathematical formulas; this is not a slide report | Animate the math |

## Adjustment log

### 1st adjustment (2026-09-29)

In the first trial, the skill defaulted the playground to reproducing the paper's experiments. It asked for API keys and large dataset downloads mid-run, a concept-demo interface could never count as done, and scope was not confirmed first. Changes: "real" means results computed by code running the algorithm; reproduction became an optional mode; stage 0 (scope confirmation) was added; API-key questions were removed; 20–30 papers and full knowledge-point coverage were kept.

### 2nd adjustment (2026-09-29, after the LUNA trial)

The LUNA trial (28 papers, 36 units) went smoothly. Three fixes: every subagent uses Sonnet; source files must live in the output folder (two groups kept theirs only in the scratchpad); small data is embedded in JS instead of loaded with `fetch` (one unit needed a server, which was left running).

### 3rd adjustment (2026-09-29): plugin and presentation

The user asked for a presentation branch named `paper-reading:presentation`, so the skill became a plugin with two skills. The user rejected a slide page and pointed to a locally run teaching application as the model: a backend and a front end with modules and labs, real dataset slices, and a requirement to work offline. The user restated that the backend must really run and that a real dataset and playground are needed. These points define the presentation skill. The oral-report mode was removed from reading and replaced with a pointer to presentation.

### 4th adjustment (2026-09-29, after the IndVisSGG trial and an outside review)

The IndVisSGG trial (37 papers, 25 knowledge points, 25 units, 279 controls operated headlessly) worked well. The user asked for results to be opened for them, and set the acceptance requirement: the user must be able to see the paper-cluster comparison, the complete knowledge points, the interactive material, and the item-by-item check results. In that trial the check results existed only as totals.

An outside review raised three points, all adopted:

- Stage 0 forbade reading yet required candidate lists → searching and skimming are allowed before approval, marked provisional; full reading, downloads and code wait for approval.
- presentation required every number to come from a paper, yet also required measurement and backend computation → numbers now carry one of three sources: reported by the paper, computed in this run, or measured on this machine.
- presentation counted modules and labs, which can hide a missing knowledge point → the complete knowledge-point list is kept and checked item by item.

### 5th adjustment (2026-09-30, after the LaVIT trial)

The run fell back to text extraction and did not look at a single figure or table. The user pointed out that a paper is mainly its figures and tables, and that they must be read in context. Changes: look at every figure; read each figure with its caption, the paragraphs that cite it and its section; follow the paper's argument section by section; the user's paper is read first and most deeply, and the cluster serves it. The user then warned that breadth without anchoring produces plausible-sounding content that leads away from the topic, so every added paper and every knowledge point must cite the place in the user's paper it explains, every statement about the paper cites its location, general knowledge is labelled as background, and correct-but-irrelevant content is cut.

### 6th adjustment (2026-09-30, after independent acceptance testing)

An end-to-end test showed stage 0 read the user's paper as text only and still cited figures, because the figure rule lived under stage 1. The reading procedure became its own section used by stage 0 and stage 1, stage 0 must open with a reading log, and the server rules in reading and presentation were made consistent. Re-test: every figure was viewed, and every cited figure and table was in the log.

### 7th adjustment (2026-09-30): a run that is easy to clean up

The rules allowed temporary files in the scratchpad and a global install of the PDF renderer, and subagents were not told where they may write. The user required work to stay inside the designated folder and the result to be clean and easy to remove. Changes: write only inside the output folder; results at the top level and by-products in `_work/`, whose deletion breaks nothing; the renderer goes into `_work/.venv/`; every subagent prompt carries the boundary; the final reply says how to clean up. The same rule applies to presentation inside `studio/`.

### 8th adjustment (2026-09-30, overnight trials)

A trial left headless browser profiles (over 1,000 files) in `verify/` → browser profiles go in `_work/tmp/` and are deleted. A paper was listed as paywalled although it sat next to the user's paper → look for local copies first. The user asked for a bilingual annotated reading of the main paper only → `paper-reading:annotate`. A full run stopped when the usage window ran out because subagents viewed page images of long cluster papers and their appendices → only the user's paper is read closely; other papers are read from the text layer, with only the figures their notes cite.

### 9th adjustment (2026-09-30): usage budget

The user objected to reading every page as an image, asked for images only where there is a real figure, set a budget of about 10% of a small plan's weekly usage (about 1% on the largest plan), and asked for Sonnet subagents. Changes: text, tables, numbers and equations come from the text layer; only captioned figures are viewed, extracted by `scripts/extract_figures.py`; the whole skill runs on Sonnet; all knowledge points share one page and one script; checks read values instead of screenshots; a usage-budget section was added.

### 10th adjustment (2026-09-30): presentation made light

A trial of presentation stopped at a design-brief page, which the user took for slides; the user wanted a running backend and a real playground, and agreed to a light version. Changes: no brief page and no phases; the plan is confirmed once in chat; the build is one Python file (`server.py`, standard library by default) and one lab page next to the reading page, with real samples in `data/`; labs compute on request on real samples and show the input picture, both methods and the metric; the usage budget applies.

### 11th adjustment (2026-09-30, after the PCEN full run)

The main flow re-read large notes every turn, subagents took many turns, and one rendered whole pages. The page read oddly: papers cited by file ids, coined words, evidence labels as stray fragments, signpost sentences. Changes: subagents extract a batch with one command, read each text once, write notes to files and return one line per paper; the main flow searches notes instead of reading them; papers cited by author and year; plain phrases instead of coined words; labels in parentheses; no signposts; fixed Chinese section titles.

### 12th adjustment (2026-09-30): making reading stable

Across three full runs the cost, the checking method and the scale all varied, because every run rewrote the same tools. Changes: the plugin ships the tools — `scripts/fetch_papers.py`, `scripts/extract_figures.py` (also writes `sections.tsv`), `scripts/check_page.py` with `selftest.js`, and `templates/page.html` and `templates/widgets.js`; about 20 papers by default; papers other than the user's, its predecessors and its baselines are read in their relevant sections; `data/` only when a download was approved. Verified locally: the check catches a control that changes nothing, a wrong hand calculation and a knowledge point missing from the map.

### 13th adjustment (2026-09-30, after the LUNA run with the stable tools)

The LUNA run (23 papers, 24 knowledge points, all checks passed) ended with a section of 10 open questions. The user said it should not appear and that the skill must produce what they need. Comparing the run with the lab review points showed that the section had been added by the skill author, not asked for; about half of its items could have been settled in the run (the official code, the arXiv version); the page drifted from teaching the paper to auditing it; and two review points were not met by any run: the math was never animated, and the traditional approach was described but not run. Changes: a "Report requirements" table maps each review point to a check, and the page and the final reply end with it; a "What the page shows" rule keeps the page to confirmed content, requires settling checkable questions during the run, and moves open questions to the notes; the open-questions section is removed from the template; `widgets.js` gains a formula animation (play, pause, step, with a plot per frame) that carries its own styles; sections marked `data-formula="1"` must animate their formula, and at least one section marked `data-traditional="1"` must run the traditional approach on the same data; `check_page.py` enforces both and fails a page containing 尚未確認, 待驗證 or 還沒確認.

### 14th adjustment (2026-09-30): formulas first, in the lab's presentation style

The user showed photos of a formula walkthrough of another paper and asked for the same presentation: a dark reading page with a left sidebar grouped by topic and tagged with formula numbers; an overview that first shows how the formulas connect, as a map in lanes whose boxes carry the formula number and page, whose arrows name the step between formulas, with a dashed arrow for a proof and the final objective highlighted, each box jumping to its formula; a symbol table of symbol, meaning and the paper's setting; and then every formula typeset, coloured by term, with its page and section and each symbol explained. Changes: the template became that page; `widgets.js` gained KaTeX typesetting (bundled under `templates/katex/`, MIT, works offline), `PR.formulaMap` and the sidebar; stage 3 gained a formula inventory; the page opens with the overview and the formulas before the storyline; requirement 10 and `check_page.py` require the map to link every formula section, a non-empty symbol table, and no untypeset formula. KaTeX reads a `#` inside a macro body as an argument, so the colour macros write hex colours without `#`.

The user then asked to improve the layout and interface. Screenshots showed lines of about 60 characters, plots using half their width with raw tick values and overlapping labels, browser-default controls, a crowded cluster table and a 70-item sidebar. Changes: prose limited to about 45 characters per line; key numbers as cards; plots fill their box, two side by side, with readable ticks and title, axis name and legend on separate rows; dark controls; number chips on knowledge points; badges for reading status and results; scrolling tables with a fixed first column; a collapsible sidebar, a reading progress bar and a back-to-top button.

The user then asked for the view after clicking a knowledge point to be improved. Measured in a headless browser, opening an address with #kp-A6 landed back at the overview, because the formulas, map and plots drawn after the jump changed the page height; and once there, the controls, 6 to 15 formula steps and the plots took more than a screen, so changing a control meant scrolling away from its result. Changes: every jump (sidebar, map, links, an address with #) lands after drawing is done and highlights its target, measured at 14 px from the top in all three cases; a demo is two columns on wide screens, controls and steps on the left and results on the right; each knowledge point has a bar with its formulas, the previous and next point and the formula map.

A research platform whose backend had started but reported a missing framework and showed a placeholder data slice illustrates what "not done" means for a real backend.

## Short-video posts used

Posts are the authors' personal experience; their reading methods are adopted, but their scenarios are not treated as rules for every paper.

| Source | Adopted |
|---|---|
| A post on reading literature efficiently as a PhD student | Decide what to look for before reading; classify by use (core / supporting / background / to read); 3-sentence notes |
| A post on what supervisors want from a new student's group-meeting report | Known / unknown / hypothesis; group figures by argument, not by number; the authors' stated limitations; causal links between sections; the reader's assessment |
| A post on how top-venue AI papers are assembled | Every design must answer a concrete bottleneck; check contributions with controls, ablations and scope; watch training conditions, data splits and cost |
| A Discussion screenshot provided by the user (2026-09-25) | The 5 aspects of a Discussion and the 3 self-check questions |
| A post on finding open-source papers and code | Channels for finding code |

Not adopted: secondary paper-explainer series (they cannot replace the papers); posts with too little information; posts on colour palettes and diagram design (visual presentation only).

## Rules added by the author of the skill

Not from a post, the reviewer or the user, but added to carry out the requirements above: disclosing the reading scope and how much was read; checking comparison conditions; splitting reading across subagents; asking before downloads and installs; the output folder layout; computing units in the browser by default; the unit acceptance procedure; demo-data results are not the paper's results.
