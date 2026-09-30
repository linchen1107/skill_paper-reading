# Read and prepare

`<skill>` is the directory containing this SKILL.md. Resolve a working Python executable before running scripts.

## Scope proposal

Read the main paper completely before proposing: text, equations, tables and every figure. Inspect existing notes, inventories and the paper folder first. The short proposal lists the reading log, candidate papers and their roles, draft knowledge points, demos, output location, and any real-data labs with resource needs. Reuse existing authorization; an approved plan covers its listed actions.

When the user asks which paper to report, compare candidates by length, understandable opening example, runnable traditional method, accessible real data and related local literature. Recommend one with a reason; wait for the user's choice.

## Extraction

```sh
python <skill>/scripts/extract_figures.py <paper.pdf> <topic>/_work/extract/<short>/
python <skill>/scripts/fetch_papers.py <list.tsv> <topic>
```

The batch list has `<short><TAB><arXiv id, PDF URL or local path>` per line. Scripts produce `text.txt`, `sections.tsv`, `figures.tsv`, captioned reading images `fig<N>.png`, and publication images `fig<N>-real.*`. Use existing local PDFs before downloading. If PyMuPDF is missing, install it only within an authorized project environment; name the missing dependency if installation is unavailable.

| Material | Read from | Check |
|---|---|---|
| Prose and tables | Text layer, in argument order | Row/column alignment, values and units |
| Equations | Text layer; crop only unreadable equations | Every symbol and derivation step used by the method |
| Figures | Captioned image plus citing paragraphs | What it shows and whether it supports the claim |

Read the main paper and direct predecessors/main comparison methods in full. Read other papers' relevant sections and cited figures. Use section offsets and search instead of repeated full-file reads. Check titles, authors and versions against the PDF, including mismatched local filenames.

Each added paper explains a specific passage, comparison or required background of the main paper. Each note records text coverage, figures viewed, tables read and cropped equations. Mark 已讀全文, 已讀相關段落, 部分閱讀 or 待讀. Titles and abstracts alone do not count as read.

Process about 20–30 relevant papers; do not pad the cluster. If fewer are available, report the count and missing context. Check follow-up work before calling a gap unsolved. Synthesize the relationships after reading, rather than stacking summaries.

## Real-data feasibility

For requested labs, check Python, required imports, available GPU and memory, free space, public weights and data. Propose only computations the machine can run; state missing resources and downloads with sources, licences and sizes. The reading page can explain the mechanism even when a full real-data experiment is unavailable, labelled accordingly.
