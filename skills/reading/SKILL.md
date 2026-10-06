---
name: reading
model: sonnet
description: Turn a paper into one interactive page a speaker can present from top to bottom. Starting from a paper PDF, arXiv link, title or set of papers the user provides, read the papers on the same research problem (about 20–30) group by group, each group serving one of six cards (Problem, Before, This paper, Result, Weak spots, Next steps); the page opens with the six cards and below each card a chapter whose knowledge points explain it, every knowledge point with a demo computed by code and every formula as a live card with the numbers substituted (the full formula set goes to an appendix). When the method can run on real data on this machine, stage 0 proposes labs that paper-reading:presentation then builds with a Python backend. Also used for checking a Discussion section, finding open-source code, and reproducing a paper's experiments when the user asks.
---

# Paper-group reading and one interactive page to present

A paper report is not reading slides aloud; it shows your understanding of the paper. Read the related papers group by group, work out which problem the paper actually solves, turn every knowledge point into interactive material driven by real computation, and make every formula live.

**The structure is fixed: six cards, then one chapter per card.** The page opens by saying what the paper did, in six cards: **Problem, Before, This paper, Result, Weak spots, Next steps**. Below them come six chapters in the same order; each chapter explains its card, and the knowledge points that the card needs sit inside that chapter. The page reads from top to bottom without jumping back, so the user can present it as it is. Material for questions (knowledge-point map, paper groups, formula appendix, checks) comes after a "Backup material" divider at the end.

| Card and chapter | What it says | Knowledge points inside |
|---|---|---|
| 1. Problem | The question in everyday words and one concrete failure | The basics a newcomer needs to follow the problem, in dependency order (for an optics paper: light and spectrum, polarization, reflection), then the failure |
| 2. Before | How it was done before and where it falls short | The traditional approach, run on the same data as the paper's method |
| 3. This paper | The idea and the method step by step | One point per step of the method, each with its live formula cards |
| 4. Result | What is measured, what number is good, what came out | The metrics, the evaluation, our recomputation next to the paper's numbers |
| 5. Weak spots | Confirmed problems of the paper and the limits the authors state | Each error stated as a fact with page and section and a crop of the paper's text with the phrase boxed |
| 6. Next steps | What the authors did next and where the field went | Follow-up work from the last paper group, each with its source |

Every part links to the others: a card states the point, its chapter explains it, and a knowledge point deepens one part of it. Every entry on the knowledge-point map links to its source location in the paper and to its section.

## Who reads the page

**The reader is intelligent but knows nothing about this field**, for example a graduate student from another lab. The writer has just read 20 papers and can no longer see which words and steps a newcomer lacks, so this is not left to the writer's judgement: every term is registered and checked, and a reader who has only the page tests it (the cold read, [references/cold-read.md](references/cold-read.md)).

- **Every technical term is explained where it first appears in reading order**, in plain words, in the same sentence or the short sentence right after it (the hover text is extra; a skimming reader and the cold read do not see it): names of models, datasets and methods, abbreviations, and English terms. List them in `demos.js` with `PR.terms({'hidden state': 'the long list of numbers a model produces inside itself for each word it reads', …})`, and write the first use as `<dfn data-term="hidden state">hidden state</dfn>`; later uses show the explanation on hover. A term the cards and chapters do not need is left out, not explained.
- **Every number has a scale or a comparison**: what is good, what is chance, what the traditional approach gets (for example "AUC 0.65, where 0.5 is guessing and 1 is perfect").
- **Nothing is referred to before it is introduced.** A sentence that needs a later section either moves after it or says the needed idea in one plain sentence. This is why the basics sit at the start of chapter 1.
- **The page opens without jargon**: the six cards, each heading one sentence in everyday words.
- **The reader scans; write for that.** Most web readers scan rather than read word by word (Nielsen Norman Group: 79% scan, 16% read word by word) and plain-language guidance splits sentences over 25 English words and keeps paragraphs to 5 sentences (GOV.UK). So:
  - **Each thing is said once.** The cards, the chapter text and the knowledge points do not repeat each other; there is no separate summary. A knowledge point may restate in one sentence the chapter point it deepens, then goes further.
  - **Length limits**, checked by `check_page.py`: the six cards together at most 450 words (900 characters on a Chinese page); a chapter at most 3 paragraphs of its own, plus at most 1 figure and 1 table, before its knowledge points; a paragraph at most 5 sentences; a sentence at most 25 words (40 characters on a Chinese page); a knowledge-point field at most 2 sentences.
  - **The first sentence of every card, chapter and field is its conclusion**; what follows supports it. Each chapter opens with that sentence as its `.chapter-lead`.
  - **The text must make sense without touching a demo**; the demo lets the reader check it (Victor, "Explorable Explanations"; Hohman et al. 2020).
  - **Cut what does not serve the paper**: history of a name, side facts, a second example of the same point.

## Output language and wording

**The page is in English** (`<html lang="en">`), the whole page in one language, including the six card names. Make it Chinese only when the user asks; then set `<html lang="zh-Hant">`, write Traditional Chinese as used in Taiwan with Taiwanese terminology (影片 not 視頻, 資料 not 數據, 品質 not 質量, 資訊 not 信息, 預設 not 默認, 程式碼 not 代碼, 模組 not 模塊, 網路 not 網絡, 支援 not 支持, 檔案 not 文件), and keep the six card names in English. The widgets follow the page's `lang` for their buttons. Paper notes and chat replies to the user are in Traditional Chinese (Taiwan).

Wording, on every page, because a reader who is new to the field must follow it on first reading:

- **Conclusion first.** The first sentence says what matters; the rest supports it. Complete sentences with a clear subject and verb; no filler, slogans or padding. If a passage can be cut without losing the point, cut it.
- **A concrete example with real numbers before the rule.** Show the idea on one case the reader can check (for SAM: a background point A = [100, 50], a darker normal spot B = 0.5·A and a dent C = [60, 90]; the distance calls B a defect, the angle does not), then state the general rule. The numbers in the example must be the ones the demo computes.
- **Say what a word refers to.** A word that has a special meaning here (for example "background": the normal metal surface around the defect) is explained in one plain sentence where it first appears. A range or unit gets its meaning (for example "380 to 750 nm, the wavelengths the human eye can see").
- **One name per thing.** Once a thing has a name, use that name everywhere on the page; do not switch between synonyms.
- **No names the page makes up and no compressed coined words.** Use the paper's term or the standard term of the field, so a reader can look it up ("spectrum", not "brightness string"). Sentences such as "we call this …", "this page calls …", 「本頁稱為……」 or 「我們稱它……」 fail `check_page.py`.
- **Cite papers by author and year** (for example Wang et al. 2017), linked to their note. Short ids such as `wang17` are file names only and never appear in the text.
- **Sources stay out of the sentences.** A card or chapter block ends with one grey line, `<p class="src">In the paper: Table III (p.5); our computation: knowledge point 7</p>`; a knowledge point keeps its sources in its `.src` line under the title; when one number needs its own location, a small `<span class="cite">p.5</span>` after the sentence. Brackets such as "(Section III.A, p.3)" inside a sentence fail `check_page.py`.
- Use Arabic numerals.

## Workflow

Complete the following 6 stages in order. **Do not start stage 1 until the user replies to stage 0.** When the user explicitly narrows the scope, follow it and state at the top of the reply which stages were skipped.

| Stage | Goal | Not done when |
|---|---|---|
| 0. Scope confirmation | Read the user's paper in full: the whole text and every figure; list the scale and format; wait for the user's approval | A figure of the user's paper not viewed; no reading log; full reading of other papers, downloads or code before approval |
| 1. Paper groups | Read about 20 directly related papers (20–30 when the problem needs it) group by group, each group serving one card, by "How to read a paper"; work out what each solves, how they build on each other, and what gaps remain | Only 1 paper read; a paper in no group; titles, abstracts or search results counted as read; a figure cited in a note but not viewed; unrelated papers used as padding |
| 2. Difficulty | Open with a real-life example; explain what makes the problem hard and where the traditional approach falls short | Opening with the paper's method; difficulties without sources; failures invented to justify the motivation; the traditional approach only described, not run |
| 3. Knowledge-point map | List every knowledge point, numbered in reading order and placed under the card it serves, each tied to papers and source locations | Only highlights; sampling; a point under no card; listing only what the paper states without restoring the background it cut |
| 4. Interactive material | Every knowledge point as a section inside its chapter, with a demo computed by shared code and a live card for each formula it uses; inputs can be adjusted and results update immediately | Pre-drawn animations or hard-coded numbers; interface without computation; a formula that is not live; a knowledge point missing from the page; a program written per knowledge point |
| 5. Cards and chapters | Write the six cards and the six chapters around the knowledge points: why, how, what the evidence supports, what is weak, what came next | Paper-by-paper summaries stacked without their relationships; a card whose chapter does not explain it; open questions or unconfirmed statements on the page |

**Completion is judged by actual operation.** A count of knowledge points, existing buttons or screenshots do not mean something is covered or verified.

## Report requirements

These come from the lab's review of how a paper must be reported (see [references/sources.md](references/sources.md)). They define what the user needs. Every run meets all of them, and the page's backup material ends with a Report requirements table: one row per requirement, a link to where the page meets it, and Met or Not met. The final reply repeats that table (符合 / 不符合). A requirement that is not met is reported as not met, never glossed over.

| # | Requirement (review point) | Met when |
|---|---|---|
| 1 | Show understanding, not slides; interactive and playable | Every computable knowledge point has a demo that `check_page.py` passes |
| 2 | Report a cluster of papers, not one (20+) | The paper-groups table lists about 20 papers in groups, each group tied to the chapter it serves and each paper to a place in the user's paper |
| 3 | Work out what the paper actually solves | The Problem card and chapter 1 name the problem and the difficulties before any method appears |
| 4 | Open with a concrete failure and an everyday example | The Problem card and chapter 1 start from one concrete case where the existing approach fails (what was expected, what happened, the effect, with its source), then an everyday example of why it is hard; knowledge points open with an everyday example |
| 5 | Explain the traditional approach in great detail | Chapter 2 (Before) explains it, and at least one knowledge point (`data-traditional="1"`) runs the traditional method on the same data as the paper's method, placed before the paper's method |
| 6 | Explain every knowledge point with a program (10, 20, 60 of them) | The map lists every point, and each has a demo or says why it cannot have one |
| 7 | Do more than the paper; restore what it cut | Background and derivations the paper only names are knowledge points of their own |
| 8 | Animate the math | Every knowledge point with a formula (`data-formula="1"`) has a formula animation that steps through the computation with this run's numbers, and every formula card is live (`PR.live`): moving a control changes the formula with the numbers substituted |
| 9 | The page shows understanding, not open questions | The page contains confirmed content only (see "What the page shows") |
| 10 | Formulas: each after an example; the full set on demand | Every formula a knowledge point uses is a live card after that point's demo (the user asked for more formulas, all interactive, in place of the review's 1 to 5), with a plain sentence whose coloured words match the formula's coloured terms; no display formula in the cards or chapter text; every formula of the paper, the formula map and the symbol table in the appendix at the end |
| 11 | Written for a reader who knows nothing about the field | Every term is in the term list and explained at its first use, capitalised jargon in the cards and chapter leads is all listed, and the cold read's reader understood the paper correctly and every item it marked as blocking is fixed (`check_page.py`) |
| 12 | Short enough to read; no noise | Each thing is said once; the cards, paragraphs, sentences and knowledge-point fields are within their limits; no source inside a sentence; no made-up names; the cold read's 可以刪掉 items are fixed where one sentence does it, and the rest are listed in the final reply (`check_page.py`) |
| 13 | One structure: six cards, a chapter under each | The page opens with the six cards in order (Problem, Before, This paper, Result, Weak spots, Next steps), each linking to its chapter, and every knowledge point sits inside the chapter of the card it serves (`check_page.py`) |

## What the page shows

The page teaches the paper; it is not a list of open questions. Weak spots and Next steps are part of that teaching, and like the rest they hold confirmed content only.

- **Confirmed content only.** On `index.html` every statement is either reported by a paper or computed in this run, and the block's source line says which (In the paper: … with location; our computation: … with the knowledge point). The labels 原論文報告 and 本次實際重現 are for the notes and the check tables, not for the prose. The label 待驗證的推論 and the words "not yet confirmed", "to be verified", "unverified", 尚未確認, 待驗證 and 還沒確認 do not appear on the page; `check_page.py` fails the page if they do.
- **Check what can be checked, during the run.** When a question can be settled by reading the paper again, its arXiv or supplementary version, the official code, a cited paper, or by recomputing, settle it and write the answer. Do not hand it to the reader.
- **What cannot be settled goes into the notes.** Open questions, suspected typos and interpretations stay in `papers/<short>.md` under 我的判讀, with their label. They do not appear on the page.
- **Errors in the paper, when confirmed, go to chapter 5 (Weak spots)**, each stated as a fact with page and section and, as evidence, a crop of the paper's own text with the wrong phrase boxed in red (`scripts/crop_pdf_text.py`, see Stage 5). Confirmed means checked against the paper's text, its tables or a recomputation; a suspicion stays in the notes. Where a reader needs an error to read a result correctly, the knowledge point says so too and links to it.
- **Next steps are sourced.** Chapter 6 names what the authors published next and where the field went, each with its paper; the user's own ideas appear only when the user supplied them.

## Usage budget

Assume the user is on a small plan: a whole run, stages 0 to 5, should use no more than about 10% of a Pro plan's weekly usage (about 1% on Max 20x).

- **Sonnet throughout.** This skill runs on Sonnet, and every subagent is dispatched with `model: sonnet`.
- **Read text, not pages**, by "How to read a paper". Use `sections.tsv` to read one section with an offset instead of the whole file, and search instead of reading a file again.
- **Subagents read one paper group per batch** (5 to 6 papers; a larger group is split), write their notes to files and return one line per paper; they do not paste notes or paper text back.
- **Templates, not new code**: the page, the widgets, the download and the checks come from the plugin (`templates/`, `scripts/`); the run writes only the content and `demos.js`.
- **Check by values, not screenshots.** At most one screenshot at the end, if a layout question cannot be settled otherwise.
- **Estimate first.** The stage 0 proposal states the number of papers, knowledge points and demos. If the scope looks too large for the budget, propose a smaller one in the same reply.

## Evidence labels

Every claim in the notes carries one of these 3 labels, written exactly like this. On the page the same distinction is made in the source lines (see "Output language and wording"), not with the label words inside the sentences.

| Label | Meaning |
|---|---|
| 原論文報告 | A number, result or claim the paper itself reports, with page, section, Figure, Table or theorem |
| 本次實際重現 | A result produced by code in this run (demo computation or reproduction experiment), with input, parameters and code location |
| 待驗證的推論 | The reader's interpretation or expectation, not yet supported by evidence. Used in notes only, never on the page |

- **Observing a failure does not mean the cause is known.** Keep the phenomenon and the cause separate; state a cause as confirmed only when the paper's analysis or an experiment supports it.
- **Numbers from different test conditions cannot be ranked directly.** When data splits, model size, training data, evaluation rules or cost differ, describe the conditions under which each number holds.
- **A demo's result is not the paper's experimental result.** A phenomenon computed on demo data is marked as our computation with a note that it uses demo data; it must not stand in for the paper's results on the real dataset.

## How to read a paper

**Read from text; look only at real figures.** The text, tables, numbers and equations come from the text layer. Opening page images of text costs usage and adds nothing, so it is not done. Only figures (diagrams, plots, photos) are looked at as images.

1. **Extract.** `<plugin>` is the folder of this plugin (the parent of `skills/`). For one paper run `python <plugin>/scripts/extract_figures.py <paper.pdf> <topic>/_work/extract/<short>/`; for a batch write a list (`<short><TAB><arXiv id, PDF URL or local path>` per line) and run `python <plugin>/scripts/fetch_papers.py <list.tsv> <topic>`, which downloads and extracts every paper in one command and reports the ones it could not get. Each paper gets `text.txt` (the whole text layer, with page markers), `sections.tsv` (headings with their line numbers), one `fig<N>.png` per captioned figure (a reading copy with its caption, for looking at the figure), one `fig<N>-real.*` per figure (the figure itself as the paper holds it: the original embedded bitmap at its own resolution, or the vector drawing cropped to SVG), and `figures.tsv`. PyMuPDF is the only requirement; if `python -c "import fitz"` fails, ask the user to approve installing it into `<topic>/_work/.venv/` (`pip install --no-cache-dir pymupdf`, about 20 MB), and do not continue until it is installed.
2. **Read the whole text** of `text.txt` in order, and follow the line of argument section by section: what each section sets up, which figure or table carries it, and how it leads into the next.
3. **Tables and numbers from the text.** Keep original precision. If the text layer leaves unclear which number belongs to which row or column, write 尚未確認 for those cells in the note instead of guessing, and settle them before the page uses them.
4. **Equations from the text.** Only if an equation is garbled beyond reading, crop that one equation from its page (`page.get_pixmap(clip=rect, dpi=150)`) and look at the crop.
5. **Figures in context.** Open each `fig<N>.png` together with its caption, the paragraphs that cite it ("as shown in Fig. 3") and its section. Record what it shows, which claim it supports, and whether the text's claim matches what the figure shows. Numbers read off a plot are approximate and marked as such. A figure listed as `not found` in `figures.tsv` is cropped from its page by hand; only that crop is viewed.
6. **Which figures.** For the user's paper, every figure. For other papers, only the figures their note cites, usually 0 to 2.
7. **Keep a reading log** at the top of the paper's note: text read in full (yes or no), figures viewed out of captioned figures (for example 20/20: Fig. 1 p.2, Fig. 2 p.3, ...), tables read from text (for example Table 1 p.7), and any equation that had to be cropped.

## Before stage 0: choosing one paper from a batch

Only when the user asks which paper of a set to report. Score every candidate on the same 5 criteria and give the table before recommending one:

1. Length of the main text in pages.
2. Whether it can open with an everyday example.
3. Whether its traditional approach can actually be run on the same data.
4. Whether real data at hand (the project's own or public) can reproduce its core experiment.
5. How many papers in the local library form one cluster with it.

Read each candidate far enough to score it (abstract, introduction, method overview, experiments); mark scores that rest on the abstract only. Recommend one with the reason, name the runner-up, and wait for the user's choice. The chosen paper then goes through stage 0 as usual.

## Stage 0: scope confirmation

Before proposing, **read the user's paper in full by "How to read a paper"**, including every figure; the extracted text and figures may be written to `<topic>/_work/extract/` at this stage. Then do the searches and skimming needed to find candidates (titles, abstracts, reference lists). **The proposal starts with the reading log of the user's paper.** A proposal without it, or one that cites a figure or table not in the log, is not done. **Reuse what the project already has.** Before searching, look in the project and in any folder the user named for existing paper notes, cluster notes and literature inventories (a table of papers with their fields), and build the candidate list from them first. An existing note or inventory entry is a lead, not a reading: a chosen paper is still read to the depth stage 1 requires, unless its note already records that depth. The proposal says which candidates came from existing material and which notes will be reused. Mark everything in the proposal as provisional. Full reading, downloads, subagent dispatch and code wait until the user approves. List the following and wait for the user's reply.

1. **Paper groups**: expected count (default 20), the candidates sorted into groups, each group named after the card it serves, each paper with its role. Typical groups: background (Problem: the physics or math a newcomer needs), traditional approach (Before), method sources (This paper: where each step of the method comes from), evaluation (Result), follow-up work (Next steps). Weak spots draws on all groups.
2. **The six cards in draft**: one sentence each for Problem, Before, This paper, Result, Weak spots and Next steps, marked provisional. Weak spots lists the candidate errors to confirm; Next steps the candidate follow-ups to read.
3. **Draft knowledge-point list**: under each card, its points in reading order (foundations first), numbered across the page.
4. **Demo for each knowledge point**: what the user manipulates, what the screen shows, where the computation runs; and the formulas it uses, each a live card.
5. **Real samples to download**: list only when a knowledge point cannot be explained without real data (for example a real recording or a real image), with file name, source and size. If demo data can be generated by code, do not download.
6. **Real backend**: whether the paper's method can run on real samples on this machine, checked, not guessed: `python --version`, the packages that import, the GPU (`nvidia-smi`, and whether torch sees it), free disk space, and whether the data and model weights are public. If it can, propose 2 to 5 labs with the downloads (source, licence, size) as in paper-reading:presentation's Step 0; after the reading page is accepted, that skill builds them without asking again. If it cannot, say what is missing; the reading page is made either way.
7. **Estimated workload**: number of papers, knowledge points, demos and formula cards.

Do not ask for the reading purpose. If the user did not state it, identify the problem the paper solves; do not guess the user's own research topic.

## Stage 1: paper groups

- **The user's paper comes first.** The cluster exists to understand that paper. Read it first and most deeply: every section, every figure and table in context, every equation. Other papers are read for what they explain about it (predecessors, the traditional approach, the baselines it compares against, later work that tests its claims), and the report is about the user's paper. **Every added paper names the passage, figure, table or equation of the user's paper it explains.** A paper that cannot be tied to a specific place in the user's paper is left out, however interesting.
- Even when given 1 paper, use it as the starting point and find its direct predecessors, the traditional approaches, the main comparison methods and follow-up work. Do not shrink this work because the paper is only 5 pages. When the user provides a set of papers, read that set first; any added paper must state which gap in context it fills.
- **Read group by group.** Each paper belongs to one group, and each group serves one card; a paper that serves no card is left out. Finish a group, then write the knowledge points of its chapter from it before the next group, so each chapter is grounded in its own papers. The paper-groups table on the page keeps this order: one heading row per group naming the chapter it supports.
- **Split the reading across subagents.** The main flow first builds the groups and each paper's role, then hands each group to a subagent (a group over 6 papers is split). Each subagent fetches and extracts its whole batch with one command, reads each paper's `text.txt` once, never renders whole pages as images, and writes each note directly to `papers/<short>.md` (research problem, shortcomings of prior approaches, core method, evidence with source locations, role in the cluster, knowledge points involved, how much was read). It returns only one line per paper to the main flow: title, status, and the place in the user's paper it explains. The main flow does not read the notes in full; it searches them for what it needs, and spot-checks key numbers against the original paper.
- **Depth follows the user's paper.** The user's paper is read in full. Direct predecessors and the methods it compares against in its tables are read in full too. Every other paper is read in its relevant parts: abstract, introduction, conclusion, and the sections that explain the place in the user's paper it was chosen for, found through `sections.tsv` and read with an offset. Only the figures a note cites are viewed. Skip appendices unless the user's paper relies on them. Subagents follow this and return their reading log.
- **Look for local copies first.** Before calling a paper unobtainable, search the folder the user's paper came from (and any folder the user named) by title, author or year; use what is there and do not copy it elsewhere.
- **Check each file name against the paper.** A local file's name often carries an author and a year; compare them with the title page of the PDF and report every mismatch (wrong author, wrong year, wrong paper) in the stage 1 summary. Notes use the paper's own details, never the file name's.
- Confirm each paper's full title, authors and version, and prefer the original text. Surveys and secondary write-ups can help locate things, but key methods, numbers and conclusions must be checked against the original paper.
- Mark each paper 已讀全文, 已讀相關段落 (list the sections read), 部分閱讀 (abstract or less, or a cited figure not viewed) or 待讀 in its note; the page's table shows the same as full text, relevant sections, partly read. Anything not obtained is marked 尚未確認 in the note.
- If fewer than 20–30 related papers exist, state the actual count and the reason; do not claim the expected scale was reached.
- A problem already addressed by later work must not be described as unsolved.

## Stage 2: difficulty

- **Open with one concrete failure, then an everyday example.** First a real case from the paper or its cluster: what was expected, what actually happened, and the effect, with its source (for LUNA: the model answers that water vapour is denser than air, Fig. 4). Then a technology or phenomenon from everyday life that shows why the problem is hard; for audio normalization, for example, recording and Dolby noise reduction: why signal-to-noise ratio (SNR) and dynamic range are hard to handle. The audience needs a picture first; only then can they follow the method.
- **Explain the traditional approach in great detail, and run it.** How it works, what it solves, and where it falls short are prerequisites for understanding the paper. Papers usually assume the reader already knows this and start from the later part; the report must put it back. The traditional approaches the paper improves on or competes with become knowledge points marked `data-traditional="1"`, placed before the paper's method, and their demos run on the same data as the paper's method so the two can be compared side by side, including the settings where the traditional approach does as well or better.
- **Difficulties need a situation and a source.** Record under which conditions which problem appears, its effect, and the location in the paper or demo. A shortcoming the authors state in the Introduction without supporting evidence is written on the page as the authors' statement (「作者指出……」, with the location in the source line); never invent a failure.
- **A failure measured in this run counts as evidence.** When the traditional approach or the paper's method is run on real data and fails (for example an estimate that comes out 11% to 31% low), the failure is written on the page as our computation, with the dataset, the files or sample count, the settings and the knowledge point in the source line. On generated data it is stated as generated data, and it shows how the method behaves, not how it behaves on the real task.

## Stage 3: knowledge-point map

- If the user provides a knowledge-point list or course map, it defines the complete scope; reuse its names and numbers. Otherwise, derive the complete list from the paper groups.
- **Every knowledge point serves one card** and sits in that card's chapter. Number the points in reading order across the page (1, 2, 3 … from chapter 1 on), so the numbers rise as the speaker goes down the page.
- **Every knowledge point is anchored in the user's paper.** It cites the section, figure, table or equation of the user's paper that needs it. Background the paper omits qualifies only when a specific passage of the paper cannot be understood without it; cite that passage. A point with no anchor is dropped.
- **Every knowledge point must be handled; no highlights only, no sampling.** Each has a one-sentence explanation, its relation to the research problem, the papers and source locations, and its section in `index.html`.
- **Do more than the paper.** Background and derivations the paper cut for space (for example Gaussianization or spectral whitening mentioned only by name) are also knowledge points.
- Order by dependency inside each chapter: foundations first, then what builds on them. A basic idea several chapters need goes into chapter 1.
- At the end, check item by item. Group-level completion is not enough: a group can be finished while one of its points is missing.
- **Formula inventory.** List every numbered equation, definition, theorem and algorithm of the user's paper, and every unnumbered formula the method depends on (including those in appendices it relies on): its number, page and section, its LaTeX, and its links: which formula it comes from and which it leads to, with the step in between named in a few words (adds mutual information, replaces with a lower bound, takes the mean over the state). Also list every symbol with its meaning and the paper's setting for it (value, range, network, with location). These become the formula map, the symbol table and the formula sections of the appendix.
- **Formula cards.** Every formula a knowledge point uses (the paper's equations, and the standard formulas of the basics, for example Malus's law or a detection rate) becomes a live card in that point, after its demo: a plain sentence, the formula, and one row of controls with the formula recomputed with the current numbers. Name for each the knowledge point and the numbers it uses; real data where the page has it, small round numbers otherwise. The full set, with derivations, stays in the appendix.

## Stage 4: interactive material

All knowledge points live on one page and share one widget library. The page, the widgets and the checks come from the plugin; the run writes only the content and `demos.js`.

**Files.**

- Copy `<plugin>/templates/page.html` to `<topic>/index.html` and fill in its marked places; keep its sections, titles and navigation.
- Copy `<plugin>/templates/widgets.js` to `<topic>/widgets.js`, the folder `<plugin>/templates/katex/` to `<topic>/katex/` and `<plugin>/scripts/serve.py` to `<topic>/serve.py`, unchanged. The widgets provide controls, plots, formula typesetting and animation, the formula map, the sidebar, figure popups and hand-calculation checks; the header of `widgets.js` shows how to use them.
- Write only `<topic>/demos.js`: one `PR.demo(...)` per knowledge point that can be computed, and at least one `PR.check(...)` per demo that compares a setting with a hand calculation. No knowledge point gets its own page or program.
- `index.html`, `widgets.js` and `demos.js` are plain files (no modules, no `fetch`), so the page also works when double-clicked; small data is embedded in `demos.js`.
- **Warm theme by default.** When the page is filled in, run `python <plugin>/scripts/warm_theme.py <topic>`: cream paper and serif headings for reading, and every demo canvas, formula map and key formula card on a dark espresso "screen" so light labels and data colours keep their contrast. It is safe to run again. Skip it only when the user asks for the dark theme.

**Page order.** The page reads from top to bottom without jumping back, so a speaker can present it as it is. A reader who stops anywhere has understood everything above that point, and nothing is said twice.

1. **Title and six cards** (`<section id="story">` with `.overview` and six `.ov-card`): Problem, Before, This paper, Result, Weak spots, Next steps, in this order. Each card: its name as `.ov-kicker`, a one-sentence heading in everyday words, 1 to 3 short sentences, at most one small paper figure or a 3-step flow, a source line, and a link to its chapter. The cards replace a separate summary.
2. **Six chapters** (`section.chapter` `#ch-1` to `#ch-6`), one per card, in the same order. Each opens with its number and the card's name in the heading, one `.chapter-lead` sentence with its conclusion, at most 3 short paragraphs with 1 figure or 1 table, and a source line; then its knowledge points. No display formula outside the knowledge points.
3. **Backup material** after the `#backup` divider: the knowledge-point map (grouped by chapter), the paper-groups table, the appendix and the checks.
4. **Appendix** (`<div id="appendix">`): the formula map (`PR.formulaMap`: one lane per strand of the method, one box per formula with its number and page, arrows naming the step between formulas, a dashed arrow for a proof, the final objective highlighted, and one caption paragraph telling the derivation in words), the symbol table, then every formula one by one, grouped in the order of the derivation: a `section.eq-sec` with its number as `data-tag`, the formula typeset in LaTeX (`tex-block`, terms coloured with `\ca` `\cb` `\cc` `\cd`), its page and section, each symbol explained in one line, and links to the formula it comes from, the one it leads to, and the knowledge point that computes it.
5. **The checks**: the per-point check table and the Report requirements table.

**Knowledge points.**

- Each is one section inside the chapter of the card it serves: its number as `<span class="chip">` (`chip trad` for a traditional approach), its `.src` line with the paper's location and related papers, then Example, Difficulty, Before, This paper and Further, at most 2 sentences each with the conclusion first and no source inside them, then its demo, then a live formula card for each formula it uses. What the demo shows is said in the demo's own result line, not repeated in the fields.
- **Live formula card** (`<div class="keyeq" data-live="name">`, template in `page.html`): after the demo, so the reader has already seen the numbers before the general form. It holds one plain sentence that says what the formula computes, with its key words coloured (`<span class="w-a">` to `w-d`) to match the formula's terms (`\ca` to `\cd`); pointing at either marks both. Then the formula, a collapsed "Symbols and source", and the live row from `PR.live('name', {controls, tex})` in `demos.js`: sliders or buttons for the quantities a listener would want to change, and one line that shows the formula with the current numbers substituted and its result (for example `cos θ = (100·50 + 50·100) / (111.8 × 111.8) = 0.800 ⇒ θ = 36.9°`). Every control must change that line. Use the page's real data where it has it (the detection rate at the chosen threshold on a real sample); a toy example says so in its `note`.
- **Real interaction.** When the user changes an input, the result is recomputed by code running the algorithm, not a switch between pre-made images. Keep the cases where the paper's method still does poorly.
- **Animate the math.** A point whose method is a formula is marked `data-formula="1"`, and its `compute` returns `anim`: the formula taken apart into frames, from the definition through each substitution to the result, with the current numbers filled in; a frame may carry a plot that changes with it. The reader can play, pause and step. The animation is recomputed from the current inputs, never pre-drawn.
- **Points from the paper groups.** An idea the paper takes from another group's paper and assumes the reader knows (for example the reflection model behind a lighting choice) is a knowledge point of its own, with a demo, its source paper, and one grey line stating where that model does not hold.
- **Points without a computation** (a definition, a dataset fact) show the paper's figure or a small table and say why there is no demo.
- The widgets lay a demo out in two columns on wide screens (controls and formula steps on the left, staying in view; results on the right), add a bar with the point's formulas and its previous and next point, and land every jump on its target with a brief highlight. Nothing to write for this.

**Figures.**

- **The paper's own figures, never screenshots.** A figure shown on the page is its `fig<N>-real.*` file, copied to `<topic>/figs/<short>-fig<N>-real.<ext>` and placed in the section that discusses it: `<figure class="figure">` with `<figcaption>Fig. N (p.X): …</figcaption>`, the caption one or two sentences on what to look at. The template caps a figure's height at about half a screen; the popup shows it large. The reading copy `fig<N>.png` and page renders never appear on the page. A figure that could not be extracted as a real file is cited by number and page instead.
- **The one exception: text crops as evidence in Weak spots.** A confirmed error is shown with the paper's own sentence, cropped from the PDF with the wrong phrase boxed in red: list the items as `<number><TAB><page><TAB><exact phrase>` in `_work/crit.tsv` and run `python <plugin>/scripts/crop_pdf_text.py <paper.pdf> _work/crit.tsv <topic>/figs` (PyMuPDF and Pillow in `_work/.venv/`). It renders without the PDF's annotations, crops whole lines of the phrase's column with one line of context, and stops when a phrase is not found. Place each as `<figure class="pdf-crop">` under its item.
- Clicking a figure opens it in a popup sized to the window, with its caption; the arrow keys step through all figures.

**Styling.** Use the template's classes rather than new styles: the cards in `.overview`/`.ov-card`, a chapter's opening sentence in `.chapter-lead`, a block's sources in its last `<p class="src">`, a single location after a sentence in `<span class="cite">`, key numbers in `.stats` cards, the Weak spots items in `ol.crit`, reading status and check results as `.badge` (`ok`, `mid`, `low`, `bad`), wide tables in `.table-wrap`, a paper's name as the link to its note. Prose keeps the template's reading width.

**Where the computation runs.** In the browser. Computation that needs Python packages, a model or large data belongs to the labs of paper-reading:presentation (stage 0, item 6), not to this page.

**Acceptance.** Run `python <plugin>/scripts/check_page.py <topic>`. It opens the page in the Chrome, Edge or Chromium already on the machine, moves every control of every demo and of every live formula card and confirms the output changes, steps through every formula animation, runs every `PR.check`, opens every figure, and prints one line per knowledge point (通過 / 未通過 / 無示範). The page as a whole fails when the structure breaks (not six cards in the fixed order, a card without its chapter, a chapter without its lead sentence, chapters 1 to 4 without knowledge points, a knowledge point outside every chapter), when the formula layer is incomplete (no formula map, a box linking nowhere, a formula section missing from the map, an empty symbol table, a formula KaTeX could not typeset), when a formula card breaks its rules (none, before its demo, without a plain sentence whose coloured words match the formula, not live, or a control that does not change the substituted line), when a display formula appears outside the knowledge points and the appendix, when the formula map is not in the appendix, when a listed term is used before it is explained or capitalised jargon in the cards and chapter leads is not listed, when the cold read is missing, has a blocking item not marked fixed, or lacks the writer's 理解檢查 that the reader understood correctly, when a figure is a screenshot (other than a Weak spots text crop) or does not open, when no knowledge point runs a traditional approach, when a map entry has no section, when unconfirmed wording appears, or when the reading load is over its limits (the cards over 450 words, a paragraph over 5 sentences, a sentence over 25 words, a knowledge-point field over 2 sentences, a source inside a sentence, a name the page made up; Chinese pages: 900 and 40 characters). It also writes `_work/verify/reading_text.txt` for the cold read: run it as [references/cold-read.md](references/cold-read.md) describes, check the reader's 3-sentence understanding against the paper, fix and mark every [阻斷] item, fix the others when one sentence does it; run it again only when the understanding was wrong or the cards or chapters were rewritten (at most 3 rounds, then report what remains). Fix what fails and run it again. Copy its lines into the checks table, then fill the Report requirements table.

**Checking the drawing by hand.** `check_page.py` proves that controls change the output, not that the output can be read. After building or changing a demo, operate every control at its defaults and its extremes and confirm by values (positions of labels and boxes, read with the browser): no label, value or legend overlaps another or leaves the drawing; nothing goes outside the page width; a number that looks like a bug on screen (for example 100% false alarms, or 0% found) is either fixed or explained in the result line with its cause in the data (for example an overexposed photo). Check the desktop width only; phone width is not a target unless the user asks.

## Stage 5: cards and chapters

Write the six cards and the chapter text last, around the knowledge points that already exist, so every sentence of a card is backed by a chapter and every chapter by its points. Use the English card names on the page (the template has them; `data-toc-name` keeps the sidebar entries short).

| Card and chapter | The card says | The chapter adds, before its knowledge points |
|---|---|---|
| 1. Problem | The question in everyday words; one concrete failure (what was expected, what happened, the effect), with a small figure when the paper has one | Why it is hard, with an everyday example; the basics come as knowledge points right after the lead, before the failure is analysed |
| 2. Before | How it was done before and where it falls short, as a 3-step flow when it is a pipeline | Where the traditional approach fails and its effect; 1 or 2 sentences on the paper groups (how many papers, what they add) with a link to the paper-groups table |
| 3. This paper | The idea in one sentence and the method in 3 steps | The method end to end with the paper's own figure, which difficulty each step targets, each step linked to its knowledge point |
| 4. Result | The main finding with its number and scale, and the conditions | What is measured and what number counts as good; what the evidence supports; our recomputation kept apart from the paper's numbers |
| 5. Weak spots | The most important weakness in one sentence, then 3 to 5 confirmed problems, one line each | Each problem as an `ol.crit` item: what is wrong, stated as a fact, page and section, the text crop, and what it changes for reading the results; then the limits the authors state themselves |
| 6. Next steps | Where the work went next, in one sentence | What the authors published next and where the field went, each with its paper; the user's own work only when the user supplied it (results, code, data), each claim with its source |

The paper groups' details (each paper's role, evidence and gap) live only in the paper-groups table; the cards and chapters do not list papers one by one.

There is no section of open questions; see "What the page shows".

**Sections connect through their content, not through signposts.** Write "the traditional approach fails when …, so the paper …", not "next section: …". "Uses module X" is not a research rationale, and a higher average score does not mean every failure is gone.

**The speaker script, when the user asks for one.** Write `talk-script.md` once, following the page from top to bottom: an opening on the paper, then per card and chapter what to show, what to do on the page and what to say, each cue on its own line (Show:, Do:, Say:). After that it is the user's file: never overwrite it, and do not publish it.

## What the user sees at acceptance

`index.html` is the acceptance page and the page the user presents from. From it the user must be able to see, without opening other files, the six cards and their chapters, and in the backup material:

1. **Paper groups**: one heading row per group naming the chapter it supports, then one row per paper with its role, the difficulty it addresses, its core design, its evidence (with source location), what it leaves unsolved, and how much was read (已讀全文 / 已讀相關段落 / 部分閱讀 / 待讀).
2. **Formulas**: a live card for every formula inside its knowledge point, and in the appendix the formula map, the symbol table and every formula typeset with its location.
3. **Complete knowledge-point map**: every point, grouped by chapter and numbered in reading order, with its source location and a link to its section.
4. **Interactive material**: each knowledge-point section with its demo.
5. **Item-by-item check results**: one row per knowledge point with the controls that were operated, whether its formula animation steps, the hand calculation or reference it was checked against, the result (通過 / 未通過 / 未驗收), and any limitation. Totals alone ("279 controls passed") are not enough; each point must be traceable to its own row.
6. **Report requirements**: the Report requirements table from "Report requirements", one row per requirement with a link to where the page meets it.

## Output location

Never write to an Obsidian vault unless the user explicitly asks. The output folder is chosen in this order: a location the user specifies; a rule of the current project about where output goes (its `CLAUDE.md`, `AGENTS.md` or README, for example "write only under work/<project>/"), with the topic as a subfolder there; otherwise the current user's `Documents/claude/` (`~/Documents/claude/`; on Windows `%USERPROFILE%\Documents\claude\`), resolving the home directory at run time instead of assuming a user name. Stage 0 states the folder chosen and why. The default layout:

```
~/Documents/claude/paper-reading/<topic>/
  index.html            the one page: six cards, a chapter under each with its knowledge points and demos, then backup material
  talk-script.md        the speaker script, only when the user asks; written once, then the user's own file
  serve.py              opens the page at a local web address (`python serve.py`); starts studio/server.py instead when presentation has added it
  widgets.js            the plugin's shared widgets, copied unchanged
  katex/                formula typesetting (KaTeX, MIT), copied unchanged; works offline
  demos.js              the computation of each knowledge point's demo
  papers/<short>.md     one note per paper (the source)
  papers/<short>.html   the same note as a page, written by build_notes.py; index.html links here
  data/                 real samples and their sources; created only when the user approved a download
  studio/               the labs of paper-reading:presentation, when stage 0 approved them
  _work/                by-products; deleting it breaks none of the above
    extract/<short>/    text layer, figures and figures.tsv of each paper read
    .venv/              Python virtual environment
    tmp/                temporary files, emptied when done
    verify/             check_page.py results (check.json)
```

**All source files live inside the output folder.** Neither subagents nor the main flow may keep the source used to assemble pages, generate data or run checks outside it; material kept elsewhere can no longer be edited once that place is cleared.

**When done, open the result for the user; do not leave it for them to open.**

1. Start `python <topic>/serve.py` in the background: it serves the folder at `http://127.0.0.1:<port>/index.html` (standard library only, a free port from 8000) and opens it in the user's default browser. The reply gives the address, the port, how to stop it and the command that starts it again. **In a remote session** (`SSH_CONNECTION` is set, or the user works through VS Code Remote) the user's browser cannot open this machine's 127.0.0.1, so do not hand over that address alone: when `tailscale ip -4` gives an address, start with `--host <that address>` (reachable only from the user's own Tailscale devices) and give `http://<address>:<port>/index.html`; otherwise give the one-line `ssh -L <port>:127.0.0.1:<port> …` forwarding. `serve.py` prints this hint itself. Opening the service to a whole network is asked first, like any port. If it cannot start, open `index.html` directly (Windows: `Start-Process "<path>\index.html"`; macOS: `open`; Linux: `xdg-open`); the page also works as a file.
2. Start the final reply with clickable markdown links: `index.html`, then the note on the user's paper. Do not give plain-text paths only. Then give the 報告要求對照 table (requirement, where on the page, 符合 / 不符合), so the user can see what was delivered against each requirement without searching the page.
3. If the browser cannot be opened (for example a remote session without a desktop), say why, and still give the links.

Before writing a paper note, check by full title or DOI/arXiv id whether it already exists; if it does, update it and keep any comments the user wrote.

**Notes open as pages.** A browser shows a `.md` file as raw text, so after the notes are written (and after any later edit) run `python <plugin>/scripts/build_notes.py <topic>`; it writes `papers/<short>.html` next to each note, and the page links to the `.html`. The `.md` stays the source.

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

Downloading data or model weights, installing packages, and starting any service that occupies a port: each time, state what it is, the source and the size, and get approval before acting. Do not use external services that need an API key unless the user asks.

## After stage 5: labs with a real backend

Labs on real dataset samples with a Python backend are built by **paper-reading:presentation** from this skill's output folder. When stage 0 proposed labs and the user approved them, continue with that skill after stage 5 in the same run, and hand over the reading page and the labs together at one address (`python serve.py`). Otherwise it runs when the user asks.

## Publishing to GitHub Pages

Only when the user asks. Publishing is public, so first list what goes up and what stays out, and wait for approval.

- **Copy, do not `git init` the topic folder.** Copy the pages, the `.js` files, `katex/`, `figs/` and `papers/` into `<topic>/_work/gh-pages/`, add an empty `.nojekyll` so the notes are served as they are, then `gh repo create <user>/<name> --public --source . --push` and enable Pages from `main` at `/` (`gh api -X POST repos/<user>/<name>/pages -f 'source[branch]=main' -f 'source[path]=/'`).
- **Left out by default:** the paper's PDF, `_work/`, `serve.py`, and the speaker script (and any link to it in the published copy). Ask before publishing the paper's figures and extracted data.
- **QR codes in the header** of the published pages, top right, inside the header layout (a grid column, so the header grows with them and nothing overlaps): left, the site's address; right, the user's GitHub profile. Generate them as SVG with the `qrcode` package (installed into `_work/.venv/` with approval) into `figs/`, and decode each once (for example with OpenCV) to confirm the address.
- **Verify the live site**, not the local copy: wait until the Pages build reports `built` for the pushed commit, open the address, and confirm the pages load without errors and every image and formula appears. An update repeats the copy and the push.

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

**Every subagent uses `model: sonnet`.** This covers all subagents: reading papers, writing demos, acceptance checks.

**Never present precomputed results as live computation.** If part of a demo uses precomputed data, say so on screen.

**Stay within the task.** Do not rewrite the user's thesis outline, batch-reorganize whole folders, or add index generators unless asked.

## Sources

The user's original requirements, the lab's review points and the origin of each rule are in [references/sources.md](references/sources.md). Read it only when a rule needs checking.
