---
name: paper-reading-presentation
description: Build a locally runnable paper teaching lab from paper-reading output, using real sourced samples and a Python backend that computes results on request. Use for a paper presentation requiring real data and an executable playground.
---

# Presentation: real data and a real backend

$paper-reading-reading explains the paper in the browser on generated data. This skill adds what it cannot: **real samples from a real dataset, and a Python backend that runs the method on them when the user asks.** It does not rebuild the reading page and it does not make slides.

Keep it small: one Python file, one lab page, 2 to 5 labs, no frontend framework, no build step. The backend, the page and the checks come from the plugin; a run writes only the labs.

## Language

The lab page is in Traditional Chinese as used in Taiwan, like the reading page, so one report uses one language: lab titles, questions, control labels, summaries and notes; technical terms stay in English when that is clearer. Short declarative sentences: a number and its source instead of an adjective, no marketing words. Code and comments are in English. Replies to the user in chat are in Traditional Chinese (Taiwan).

## Input

The output folder of $paper-reading-reading for the same topic (`index.html`, `widgets.js`, `katex/`, `papers/`). If it does not exist, tell the user and offer to run $paper-reading-reading first. When reading's stage 0 already listed the labs and the user approved them, that approval is this skill's Step 0.

## Step 0: confirm the plan in chat

If this plan has not already been approved, write no files yet; prior user authorization counts. Read the reading output (the storyline, the knowledge points and the note on the user's paper) and check the machine: `python --version`, whether the packages the method needs import, whether a GPU is usable (`nvidia-smi`, and whether torch sees it), and free disk space. Then list in the chat. Continue if the user already authorized this scope; otherwise wait for one reply:

1. **Labs**, 2 to 5. Each starts from a claim or a failure in the user's paper, with its location, and names the knowledge points it exercises. For each: what the user picks (sample, method, parameters), what the backend computes, what the page shows.
2. **Data to download**: dataset, exact files, source URL, licence, size. Prefer a few small files over a whole dataset. If only large files exist, download one, cut the samples the labs need into `data/`, delete the large file, and say how much space it takes meanwhile. Say plainly when the paper's data is not public, and propose an openly licensed substitute collected the same way, labelled as a substitute. When no such data exists, a **substitute task** is allowed: real data from a related task the method also applies to (for example material detection instead of defect detection on the same kind of images). The lab's question then states which question it answers instead of the paper's, and its numbers are never compared with the paper's. Name any modality the labs cannot cover for lack of data (for example no polarised images), and say it on the lab page.
3. **Model weights and packages**, with source, licence and size; packages go into `studio/_work/.venv/`. Name what is already installed, so nothing is installed twice.
4. **What cannot run here** (gated weights, a paid API, not enough memory) and what the lab does instead. When a smaller model replaces the paper's, say that its numbers show the trend only and cannot be compared with the paper's tables.

## Build from the templates

`<skill>` is the directory containing this `SKILL.md`.

```
<topic>/studio/
  server.py        copied from <skill>/templates/studio/server.py; the run replaces the example lab
  lab.html         copied unchanged: the lab page
  lab.js           copied unchanged: controls, requests, results, states
  data/            the real samples, and SOURCES.md (source, licence, file ids, size, date)
  _work/           cache/, .venv/, tmp/, verify/; deleting it breaks nothing but costs recomputation
```

- **Write only the labs.** In `server.py`, below the `LABS` line, each lab is one function registered with `@lab(name, title, question, source, params, knowledge)`; its parameters become the page's controls (range, select, checkbox, sample picker). It returns the result documented in `server.py`: a one-sentence `summary`, the `input`, the `methods` (the traditional approach and the paper's method, each with its metric and plot), and the `failures`, the samples where the paper's method does worse, which the page loads with one click. Add at least one `@check` per lab: a hand calculation or a library value the backend must reproduce.
- **Use the project's backend when it has one.** If the project already has a working backend for the method (a package, a service on a local port, tests on real data), a lab calls it with `remote(url, payload, about)` or imports its package; do not copy or rewrite its code. The page states that those numbers come from that backend, with its address. Step 0 names the backend, how it is started and which of its tests pass; if it is not running when checking, `check_lab.py` fails that lab with a message naming its address.
- **Real means computed on request.** Each request runs the method on the chosen sample. An expensive intermediate result that does not depend on the controls, such as a model's hidden states, goes through `cached(key, compute, about)`: it is computed on this machine once, and the page states what was cached, when, and how long it took. Never show a stored result as live.
- **Numbers keep their source**: reported by the paper (table, figure or section), computed by this backend (with the input and parameters), or measured on this machine.
- **The page is already designed.** `lab.html` and `lab.js` give a lab list, a sticky settings panel, a one-sentence result, the input, both methods side by side with the better one marked, failure cases, where each number comes from, a computing state that keeps the last result visible, an error card with a retry, and an address that keeps the settings so a view can be shared. Do not restyle it per paper; improve the template instead.
- Reuse the computations already in the reading output where they fit. Cite papers by author and year (for example Wang et al. 2017), never by file ids. Explain a technical term in one plain sentence the first time it appears.

## Check, then hand over

1. Run `python <skill>/scripts/check_lab.py <topic>`. It starts the backend, lets the page run every lab with its defaults and with one changed setting, runs every `@check`, stops the backend and deletes its browser profile. Fix what fails and run it again.
2. Start the backend for the user with `python <topic>/serve.py` (it starts `studio/server.py`, which serves the reading page and the labs at one address) and open the lab page in the user's default browser.
3. Begin the reply with a clickable link to the lab page, then: the port, how to stop the backend, the command that starts it again, and per lab what was operated, what it was checked against, and 通過 / 未通過 / 未驗收.

## Usage budget

Keep use economical: read files once and search instead of rereading; check by values, not screenshots. Use the model selected by the user or Codex.

## Work only inside `studio/`

Write nothing outside `<topic>/studio/` except copying `serve.py` into `<topic>/` when it is missing. Not the scratchpad, the current working directory, Downloads, the home directory, an Obsidian vault, or this skill's folder. Model weights and caches go into `studio/_work/` (for Hugging Face, set `HF_HOME` there); packages into `studio/_work/.venv/` with `pip install --no-cache-dir`; nothing is installed globally. The final reply says how to clean up: stop the backend; delete `studio/_work/` to free space (give its size); delete `studio/` to remove the labs.

## Ask first

Before a download, install, or server start, check existing user authorization. If absent, state the source, size or port and ask once; an approved Step 0 covers the listed actions. Ask separately only when the action exceeds that scope. Do not use external services that need an API key unless the user asks.

## Hard rules

**Never present a stored or reconstructed result as live computation.**

**Never invent data, numbers or failures.** Missing data is stated as missing.

**Stay within the confirmed plan.** Anything else is proposed first.
