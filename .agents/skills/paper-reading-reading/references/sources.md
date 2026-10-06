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

These parts link to each other: gap → method → experiment → data and results → back to the original failure. Evidence is labelled "Reported by the paper", "Computed in this run", or "Unverified inference" (notes only). Observing a failure does not mean knowing its cause; numbers from different test conditions cannot be ranked directly.

Other confirmed requirements:

- One uniform format unless asked otherwise → the full workflow is the default; other modes only on explicit request.
- Never write to an Obsidian vault.
- Default output under the user's `Documents/claude/` → `~/Documents/claude/paper-reading/<topic>/`. It must work on any machine → the home directory is resolved at run time, and the PDF renderer is detected per machine.
- Everything the skills produce (pages, paper notes, check tables, lab pages, cold read files) is in English; the annotate skill adds a Traditional Chinese translation of each paragraph; chat replies to the user are in Traditional Chinese (Taiwan); the skill files themselves are in English (see each skill's language section).

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

The main flow re-read large notes every turn, subagents took many turns, and one rendered whole pages. The page read oddly: papers cited by file ids, coined words, evidence labels as stray fragments, signpost sentences. Changes: subagents extract a batch with one command, read each text once, write notes to files and return one line per paper; the main flow searches notes instead of reading them; papers cited by author and year; plain phrases instead of coined words; labels in parentheses; no signposts; fixed section titles.

### 12th adjustment (2026-09-30): making reading stable

Across three full runs the cost, the checking method and the scale all varied, because every run rewrote the same tools. Changes: the plugin ships the tools — `scripts/fetch_papers.py`, `scripts/extract_figures.py` (also writes `sections.tsv`), `scripts/check_page.py` with `selftest.js`, and `templates/page.html` and `templates/widgets.js`; about 20 papers by default; papers other than the user's, its predecessors and its baselines are read in their relevant sections; `data/` only when a download was approved. Verified locally: the check catches a control that changes nothing, a wrong hand calculation and a knowledge point missing from the map.

### 13th adjustment (2026-09-30, after the LUNA run with the stable tools)

The LUNA run (23 papers, 24 knowledge points, all checks passed) ended with a section of 10 open questions. The user said it should not appear and that the skill must produce what they need. Comparing the run with the lab review points showed that the section had been added by the skill author, not asked for; about half of its items could have been settled in the run (the official code, the arXiv version); the page drifted from teaching the paper to auditing it; and two review points were not met by any run: the math was never animated, and the traditional approach was described but not run. Changes: a "Report requirements" table maps each review point to a check, and the page and the final reply end with it; a "What the page shows" rule keeps the page to confirmed content, requires settling checkable questions during the run, and moves open questions to the notes; the open-questions section is removed from the template; `widgets.js` gains a formula animation (play, pause, step, with a plot per frame) that carries its own styles; sections marked `data-formula="1"` must animate their formula, and at least one section marked `data-traditional="1"` must run the traditional approach on the same data; `check_page.py` enforces both and fails a page containing "not yet confirmed", "to be verified" or "unverified".

### 14th adjustment (2026-09-30): formulas first, in the lab's presentation style

The user showed photos of a formula walkthrough of another paper and asked for the same presentation: a dark reading page with a left sidebar grouped by topic and tagged with formula numbers; an overview that first shows how the formulas connect, as a map in lanes whose boxes carry the formula number and page, whose arrows name the step between formulas, with a dashed arrow for a proof and the final objective highlighted, each box jumping to its formula; a symbol table of symbol, meaning and the paper's setting; and then every formula typeset, coloured by term, with its page and section and each symbol explained. Changes: the template became that page; `widgets.js` gained KaTeX typesetting (bundled under `templates/katex/`, MIT, works offline), `PR.formulaMap` and the sidebar; stage 3 gained a formula inventory; the page opens with the overview and the formulas before the storyline; requirement 10 and `check_page.py` require the map to link every formula section, a non-empty symbol table, and no untypeset formula. KaTeX reads a `#` inside a macro body as an argument, so the colour macros write hex colours without `#`.

The user then asked to improve the layout and interface. Screenshots showed lines of about 60 characters, plots using half their width with raw tick values and overlapping labels, browser-default controls, a crowded cluster table and a 70-item sidebar. Changes: prose limited to about 45 characters per line; key numbers as cards; plots fill their box, two side by side, with readable ticks and title, axis name and legend on separate rows; dark controls; number chips on knowledge points; badges for reading status and results; scrolling tables with a fixed first column; a collapsible sidebar, a reading progress bar and a back-to-top button.

The user then asked for the view after clicking a knowledge point to be improved. Measured in a headless browser, opening an address with #kp-A6 landed back at the overview, because the formulas, map and plots drawn after the jump changed the page height; and once there, the controls, 6 to 15 formula steps and the plots took more than a screen, so changing a control meant scrolling away from its result. Changes: every jump (sidebar, map, links, an address with #) lands after drawing is done and highlights its target, measured at 14 px from the top in all three cases; a demo is two columns on wide screens, controls and steps on the left and results on the right; each knowledge point has a bar with its formulas, the previous and next point and the formula map.

The user then asked for the paper's real figures instead of screenshots. `extract_figures.py` had rendered each figure region at 150 DPI, a picture of the page; in LUNA, Fig. 6 is a 2023 × 684 JPEG embedded in the PDF and the other eight figures are vector drawings. Changes: the script also writes `fig<N>-real.*`, the embedded bitmap as stored or the vector drawing cropped to SVG with the page content outside the figure removed and a 4 pt margin that never reaches the caption; `fig<N>.png` stays as a reading copy; pages (reading and annotate) show only the real files, and `check_page.py` fails any page figure that is not one.

Clicking a figure then opened the file in a new browser tab; the user asked for a popup, and asked whether the skill should start a backend. Changes: `widgets.js` opens paper figures in a popup sized to the window (vector figures included), with the caption, a counter, arrow keys, Esc and a link to the original file, and `check_page.py` fails a figure that does not open; `scripts/serve.py`, copied into each topic, serves the folder at a local address (standard library, free port from 8000) and starts presentation's `studio/server.py` instead when it exists; presentation's backend serves the whole topic folder so the lab page, the reading page and the figures share one address.

### 15th adjustment (2026-09-30): a backend the skill ships, and wording

The user asked for the skill itself, not one paper, to have a backend, with UI/UX as the first concern and the wording tightened. presentation had rules for a backend but no code, so every run would write a server, a page and checks from scratch, as reading did before its 12th adjustment. Changes: `templates/studio/` ships `server.py` (standard library; serves the whole topic folder and one JSON endpoint per lab; labs are registered with `@lab`, which also defines their controls; `cached()` computes expensive intermediate results once and the page states what was cached and when), `lab.html` and `lab.js` (lab list, sticky settings, one-sentence result, input, both methods side by side with the better one marked, failure cases loadable with one click, provenance of every number, a computing state that keeps the last result, an error card with retry, settings kept in the address); `scripts/check_lab.py` starts the backend, runs every lab with two settings through the page, runs the reference checks and stops the backend. reading's stage 0 now checks whether the method can run on real data here (packages, GPU, disk, public weights) and proposes labs, which presentation builds after stage 5 in the same run; the reading page links to the labs when served. Stage 4 of reading was reorganised into files, page order, knowledge points, figures, styling and acceptance, and passages that had fallen out of date (a backend of its own, `backend/`, stopping every server) were corrected.

A research platform whose backend had started but reported a missing framework and showed a placeholder data slice illustrates what "not done" means for a real backend.

### 16th adjustment (2026-09-30): key formulas only, after the example

Looking at the LUNA page, the user said a page led by mathematics was hard to follow and asked whether only the key formulas were needed, after looking at how others explain papers. The page opened with a formula map, a symbol table and 21 formula sections before the storyline, so a reader met every formula before knowing the problem. Published advice agrees on the opposite order: give examples before the general case and treat a few parts in depth (Peyton Jones, Hughes and Launchbury 1993, "How to give a good research talk"); analogy, diagram, example and plain words before the technical definition (Azad, BetterExplained, the ADEPT method); start concrete and fade to the abstract (Fyfe, McNeil, Son and Goldstone 2014, Educational Psychology Review 26(1)); tie the words of a plain sentence to the terms of the formula by colour (Riffle's one-sentence Fourier transform) and let the reader point at one to see the other, with details on demand (Hohman et al. 2020, "Communicating with Interactive Articles", Distill); name the key concepts first, present in segments and signal what to look at (Mayer, Multimedia Learning, 2nd ed.). The user's own notes on the lab meeting also give the order: a concrete failure, the necessary background and the traditional approach, the cluster, the main paper's design, the interactive experiments, then the improvement and what remains. Changes: the page reads top to bottom as one argument (summary, storyline, knowledge points, cluster, then an appendix with the formula map, the symbol table and every formula); section 1 opens with a concrete failure; stage 3 marks 1 to 5 key formulas; each is a card after its knowledge point's demo, a plain sentence whose coloured words match the formula's coloured terms (pointing at one marks the other), the formula, and collapsed symbols; `check_page.py` fails a page with no key formula or more than 5, a card before its demo or without matching words, a display formula in the storyline, or the formula map outside the appendix.

### 17th adjustment (2026-09-30): feedback from two project runs

Two runs in other projects reported what the skill did not cover. A hyperspectral-imaging project had to choose one paper out of 52 before any reading could start, already had 54 notes including cluster notes, found 3 local file names whose author or year did not match the paper, and could only offer a related task as real data (material detection instead of defect detection) with no polarised images at all. A reliability-measurement project already had a working backend with tests on real data, a literature inventory of 352 papers read to their first 3 pages, a failure measured on real data rather than reported by the paper (an estimate 11% to 31% low with 3 votes per item), and needed a closing section on its own work. Both had project rules that confine output to one work folder, and noticed that the reading page was in Chinese while the lab page was in English. Changes: an optional step before stage 0 scores candidate papers on 5 criteria; stage 0 builds candidates from existing notes and inventories first while still reading chosen papers to the required depth; stage 1 checks file names against the papers; a failure measured in this run on real data is evidence, labelled "Computed in this run" with its data; an optional section 7 covers the user's own work, only when the user supplies it; the output folder follows the user, then the project's rules, then the default; presentation allows a substitute task stated as such, calls an existing backend through `remote()` instead of rewriting it, and its lab page is in Traditional Chinese.

Measured cost, for later estimates: 5 Sonnet subagents reading 52 papers in full used about 1.24 million tokens together, about 7 minutes per cluster. Reading 20 to 30 papers in their relevant parts, as stage 1 asks, should cost less; it has not been measured.

### 18th adjustment (2026-10-01): shorter pages without noise, and a page that works in daily use

On a hyperspectral-imaging run (Benmoussat et al. 2012), the user said that a page full of text made them not want to read it, that the wording had problems and that there was too much noise. The page had about 30,000 characters; the opening, a summary and storyline sections 1 to 6 told the same story three times; 45 inline "Reported by the paper" labels, about 105 "Section" and 140 page numbers sat inside sentences; and the writer had made up names ("brightness string" for a spectrum, "linkage" for covariance). The rules asked for a label in brackets after every claim, so the noise followed from the skill. Published practice: most web readers scan (Nielsen Norman Group, "How Users Read on the Web": 79% scan, 16% read word by word; write half the words of conventional text); split sentences over 25 words and keep paragraphs to 5 sentences (GOV.UK, "Writing to GOV.UK standards: clear language"); the text must stand without the interaction (Victor, "Explorable Explanations"); details on demand, sources as small marks (Hohman et al. 2020, Distill; Distill author guide); other paper-explainer skills open with a 5-minute overview and fail the build with a deterministic checker. Changes: a 4-line takeaway and 6 short steps replace the opening, the summary and the cluster section of the storyline; length limits (storyline 3,000 characters, 5 sentences per paragraph, 40 characters per sentence, 2 sentences per knowledge-point field); sources move to one line at the end of each step; made-up names are banned; `check_page.py` checks all of these on the page source, and the cold read also lists what can be deleted (repetition, side facts, made-up names). Rewriting the page this way took the storyline from about 10,500 to about 2,700 characters with the same figures, numbers and demos.

The same run found faults that only show in daily use, now fixed in the template: the back button did not return from a long jump or from a note; a middle click on a link did not open a new tab; on a phone the sidebar pushed the page sideways and wide result tables widened it; a paper figure could fill one and a half screens; notes opened as raw Markdown (now `build_notes.py`); and in a remote session the user's browser could not open 127.0.0.1 (now `--host` and a printed hint, with the Tailscale address when there is one).

### 19th adjustment (2026-10-01): an acceptance run of 1.1.0

A Sonnet agent ran 1.1.0 on the same page and the result was checked by hand. It found: the cold reader was given the source lines, the cluster table and the map, so it flagged reference material as noise; a term inside a longer term ("spectrum" in "hyperspectral camera") counted as an early use; a cite after a sentence reached the cold reader glued to it ("RXFig. 3"); the step limit said "1 figure or 1 table" while step 5 asks for both; and the cold read never converged: successive readers listed 19, 41 and 14 unclear items, and with severity marks 2, 1 and 2 blocking items, each time different ones, while every reader's 3-sentence understanding was correct. Changes: the cold reader gets only the teaching prose; longer terms mask shorter ones; cites are left out of the reading text; at most 1 figure and 1 table per step; the cold read runs once, the writer checks the reader's understanding against the paper (the understanding check) and fixes and marks every blocking item, and minor items are listed rather than looped on. The agent also introduced one factual error while shortening (that the camera kept only photos "bright but not too bright"; the paper drops weak colour channels and keeps saturated photos), found by comparing the page with the paper's note: shortening is a point where facts change, so numbers and claims are checked against the notes after it.

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
