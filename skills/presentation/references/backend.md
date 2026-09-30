# Backend implementation and checks

`<plugin>` is the directory above `skills/`. Resolve Python and read the existing topic's storyline, knowledge points and main-paper note.

## Plan

Check required imports, usable GPU/memory and disk space. List 2–5 feasible labs with the claim/failure location, knowledge-point ids, selectable samples/methods/parameters, and expected output. List data, weights and packages with source, licence and size; keep samples small. Reuse installed resources and approved actions.

If original data or weights are unavailable, name the substitute and the different question it tests. Show missing modalities and limits on the page. Use an existing project backend or package when it works; identify its address, start procedure and verified tests.

## Build

| File | Action |
|---|---|
| `studio/server.py` | Copy `templates/studio/server.py`; replace only the example below `LABS` with lab functions and checks |
| `studio/lab.html`, `studio/lab.js` | Copy supplied templates unchanged |
| `studio/data/` | Real samples and `SOURCES.md`: source, licence, file/sample ids, size and date |
| `studio/_work/` | Cache, project `.venv`, temporary files and verification evidence |
| `<topic>/serve.py` | Copy `scripts/serve.py` if absent |

Register each lab with `@lab(name, title, question, source, params, knowledge)`. The function receives the selected parameters and returns the `RESULT` documented in `server.py`: `summary`, `input`, two `methods` with metric/plot, and `failures`. Use short plain labels; explain technical terms at first use. Register at least one `@check` returning expected value, actual value and tolerance.

| Computation | Use | Display |
|---|---|---|
| Per request | Run selected method on selected sample | Input, parameters, result, units and execution time |
| Expensive fixed intermediate | `cached(key, compute, about)` | What was cached, when and computation time |
| Existing backend | Import its package or `remote(url, payload, about)` | Backend address and provenance |

The supplied UI builds controls from the registration and displays results, failures and errors. Keep cached and live results distinct; retain cases where the new method loses. Store weights and dependencies locally; do not install globally. When an authorized large download must be reduced, extract the required samples and remove only that run's temporary download.

## Verify and hand over

```sh
python <plugin>/scripts/check_lab.py <topic>
```

The checker starts its own backend, runs each lab through the page with default and changed settings, checks references, then stops its backend and removes its temporary browser profile. Inspect missing-resource and execution errors too. Stop only processes created by this run.

Record per lab what was operated, its reference comparison and 通過／未通過／未驗收. Start the approved handover server with `python <topic>/serve.py` and open the lab through available host tools. Link the result; briefly state the port, start/stop commands and incomplete items. Describe cleanup only for this run's `studio/` and `_work/` resources.
