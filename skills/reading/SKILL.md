---
name: reading
model: sonnet
description: Read a supplied paper with its related paper cluster and build visual, interactive teaching material for a reader with no field background. Also use for paper Discussion review or code search.
---

# Understand a paper through its research problem

Assume the reader knows nothing about the field. Use **pictures first, tables second, short text third**. This is a presentation priority, not a fixed number of pictures or tables. Apply the same economy to these instructions: each rule has one home.

```text
Concrete failure → necessary background → traditional method
                 → paper's idea → experiment → improvement and limits
```

## Teach for a newcomer

| Use | Show | Text adds only |
|---|---|---|
| Pictures and interaction | A real case, method flow, changing inputs and outputs | What to look at and why it matters |
| Tables | Methods, conditions, results and limits side by side | How to interpret the difference |
| Short text | The connection between steps | Necessary definitions and sources |

- Introduce each concept before using it; explain what it means, why it is needed and how it works. Build on already explained concepts.
- Start with a concrete example. Let the reader manipulate or inspect it before seeing the general formula; explain every symbol when it appears.
- Give numbers a scale, unit and comparison. Show what changed under which conditions.
- Write user-facing material in natural Taiwanese Traditional Chinese. Keep useful English terms, explain them on first use, and cite papers by author and year.

## Workflow

| Step | Do | Read when needed |
|---|---|---|
| 0. Agree on scope | Read the main paper in full, including its figures; reuse existing material; propose the cluster, knowledge points, demos and feasible real-data labs | [Reading](references/reading.md) |
| 1. Read the cluster | Process about 20–30 directly related papers, even for a 5-page main paper; record each paper's role, evidence and reading depth | [Reading](references/reading.md), [Notes](references/notes.md) |
| 2. Establish the problem | Show a sourced failure and its effect; explain the needed background and traditional method before the new method | — |
| 3. Map the knowledge | Cover every knowledge point, ordered by prerequisites and linked to the main paper and its teaching unit | — |
| 4. Build and check | Use the supplied page and widgets; compute demos, animate formula steps, then check every unit | [Page](references/page.md), [Cold read](references/cold-read.md) |
| 5. Hand over | Link the reading page, main-paper note and any approved real-data labs; briefly state what remains incomplete | [Page](references/page.md) |

Existing user approval covers its stated scope. Ask only for missing authorization or work beyond it. Follow an explicit request to limit sources or outputs; report the actual coverage.

## Evidence and completeness

- Open with an observed failure or documented limitation. For theory or surveys, use the unresolved question or restricted assumption; never invent a failure.
- Link important claims and numbers to a page, section, figure, table or theorem. Distinguish **原論文報告**, **本次實際重現** and **待驗證的推論**; the last belongs in notes. A small demo explains a mechanism, not the paper's dataset result.
- Separate an observed failure from its cause. Compare numbers only under compatible conditions; preserve precision, units and the authors' stated limits.
- Use the user's complete knowledge-point list, or derive one from the paper and its required background. Each point has a source and a working link. Use a computed demo where meaningful; otherwise show a figure or table and explain why computation does not apply.
- Verify each point and operation. Report missing papers, data, resources and failed checks; counts, buttons and screenshots alone do not establish completion.

## Scope and other tasks

| Request | Action |
|---|---|
| Real data and an executable backend | Propose feasible labs in step 0; after approval, use paper-reading:presentation in the same run |
| Paragraph-by-paragraph bilingual reading | Use paper-reading:annotate |
| Discussion, code search or experiment reproduction | Read [Other tasks](references/other-tasks.md) |

Keep output in the user- or project-designated folder; otherwise use `Documents/claude/paper-reading/<topic>/` under the current user's home. Keep temporary files and project dependencies in `<topic>/_work/`; write to an Obsidian vault only on request. Resolve available tools and models on the host; delegate only when authorized and available. Reuse existing code and the supplied templates.

Rule origins: [Sources](references/sources.md), only when provenance is needed.
