---
name: paper-reading-presentation
description: Build real-data paper experiments with a runnable Python backend and interactive controls, using paper-reading output.
---

# Run the method on real data

Use the same beginner-friendly, visual-first teaching approach as $paper-reading-reading. **Show the sample, compare the methods, and add only the explanation needed to interpret the result.** The interface and replies use Taiwanese Traditional Chinese.

```text
Choose a real sample → choose method and parameters
                    → backend computes → inspect and compare
```

| Step | Required result |
|---|---|
| Plan | Read the existing reading output; check packages, hardware, data and weights; propose 2–5 labs tied to claims or failures |
| Build | Use the supplied backend and page; reuse a working project backend; compute on the selected sample |
| Verify | Operate every lab with default and changed settings; check against a hand calculation or trusted implementation; inspect failures |
| Deliver | Open the lab, link it, and briefly give its execution status and start/stop commands |

The plan lists samples, sources, licences, sizes, packages and any substitutions. Reuse approval already given in the reading plan; ask only for missing authorization or a scope change.

- Display sourced real data, inputs, outputs, metrics and failure cases. State unavailable data or weights plainly.
- Identify substitute data, tasks or smaller models; do not compare their numbers with the paper's tables as if conditions matched.
- Each request computes the selected method. Label cached intermediates and existing backend results; never present stored output as live execution.
- Keep all lab files, data and dependencies in `<topic>/studio/`. Use existing authorization for downloads, installs and server starts; never alter another running service.

Read [Backend implementation and checks](references/backend.md) when building or verifying. Its API and file layout are maintained there.
