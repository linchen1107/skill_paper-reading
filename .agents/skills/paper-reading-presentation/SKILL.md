---
name: paper-reading-presentation
description: Build a locally runnable paper teaching lab from paper-reading output, using real sourced samples and a Python backend that computes results on request. Use for a paper presentation requiring real data and an executable playground.
---

# Presentation: real data and a real backend

$paper-reading-reading explains the paper in the browser on generated data. This skill adds what it cannot: **real samples from a real dataset, and a Python backend that actually runs the method on them when the user asks.** It does not rebuild the reading page and it does not make slides.

Keep it small. One Python file, one lab page, a few labs. No frontend framework, no build step.

## Language

The lab page and code are in English, in short declarative sentences: give the number and its source instead of an adjective, no marketing words. Replies to the user in chat are in Traditional Chinese (Taiwan).

## Input

The output folder of $paper-reading-reading for the same topic (`index.html`, `widgets.js`, `papers/`). If it does not exist, tell the user and offer to run $paper-reading-reading first.

## Step 0: confirm the plan in chat

If this plan has not already been approved, write no files yet; prior user authorization counts. Read the reading output (the storyline, the knowledge points and the note on the user's paper), check what the machine has (`python --version`, and whether the packages the method needs import), then list in the chat. Continue if the user already authorized this scope; otherwise wait for one reply:

1. **Labs**, 2 to 5. Each lab starts from a failure or a claim in the user's paper, with its location, and names the knowledge points it exercises. For each: what the user picks (sample, method, parameters), what the backend computes, what the page shows.
2. **Data to download**: dataset, the exact files, source URL, licence, size. Prefer a few small files over a whole dataset; if only large files exist, download one, cut the short samples the labs need into `data/`, and delete the large file, saying how much space it takes meanwhile. Say plainly if the paper's dataset is not public, and propose an openly licensed substitute collected the same way, labelled as a substitute.
3. **Packages to install** into `studio/_work/.venv/`, with size; none if the machine already has them.
4. **What cannot be run** here (for example model weights, a GPU that does not load, a paid API) and what the lab does instead. Never plan a stored result shown as live.

## Build

```
<topic>/studio/
  server.py        the backend: serves lab.html, one JSON endpoint per lab
  lab.html         the lab page; links back to ../index.html for the explanations
  data/            the real samples, and SOURCES.md (source, licence, file ids, size, date)
  _work/           .venv/, tmp/; deleting it breaks nothing except packages to reinstall
```

- **`server.py`** uses the Python standard library's `http.server` unless the method needs more. It binds to `127.0.0.1` on a free port and prints the address. Start command: `python studio/server.py`.
- **Each lab** posts the chosen sample, method and parameters to its endpoint. The backend loads the real sample, runs the traditional approach and the paper's method, and returns the result and the metric. The page shows the input picture (for example the spectrogram or the image with its annotation), the output of both methods side by side, and the metric, and lets the user switch to a sample where the method does poorly.
- **Real means computed on request.** A result the backend did not compute for this request is not shown as live; if part of a lab uses precomputed data, the page says so.
- **Numbers keep their source**: reported by the paper (table, figure or section), computed by this backend (with the input and parameters), or measured on this machine.
- Reuse the computations already in the reading output where they fit.
- Cite papers by author and year (for example Wang et al. 2017), never by file ids such as `wang17`. Explain a technical term in one plain sentence the first time it appears on the page.

## Check, then hand over

1. Start the server for checking. For every lab, call its endpoint with at least two settings and confirm the results differ; compare one result with a reference (a hand calculation or a library such as librosa). Open `lab.html` in a headless browser and read the values off the page; no screenshots unless a layout question cannot be settled otherwise.
2. Stop the checking server and delete its browser profile.
3. Start the server once more for the user, open `lab.html` in the user's default browser, and begin the reply with a clickable link to it. Say the port, how to stop it, and the one command that starts it again.
4. Report per lab: what was operated, what it was checked against, 通過 / 未通過 / 未驗收.

## Usage budget

Keep use economical: read files once and search instead of rereading; check by values, not screenshots. Use the model selected by the user or Codex.

## Work only inside `studio/`

Write nothing outside `<topic>/studio/`: not the scratchpad, the current working directory, Downloads, the home directory, an Obsidian vault, or this skill's folder. Packages go into `studio/_work/.venv/` with `pip install --no-cache-dir`; nothing is installed globally. A headless browser's profile goes in `_work/tmp/` and is deleted after checking. The final reply says how to clean up: stop the server; delete `_work/` to free space (with its size); delete `studio/` to remove everything.

## Ask first

Before a download, install, or server start, check existing user authorization. If absent, state the source, size or port and ask once; an approved Step 0 covers the listed actions. Ask separately only when the action exceeds that scope. Do not use external services that need an API key unless the user asks.

## Hard rules

**Never present a stored or reconstructed result as live computation.**

**Never invent data, numbers or failures.** Missing data is stated as missing.

**Stay within the confirmed plan.** Anything else is proposed first.
