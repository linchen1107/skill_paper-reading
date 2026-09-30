---
name: annotate
model: sonnet
description: Make a paragraph-by-paragraph English–Traditional Chinese reading of one paper, with aligned explanations, figures and tables.
---

# Read the main paper closely

Help a reader with no field background understand each paragraph and how it connects to the argument. Preserve the original text; keep added explanations short. Use figures first, tables second, and text for meaning and connections.

| Material | Present |
|---|---|
| Paragraph | Exact English, faithful Taiwanese Traditional Chinese, page number |
| Annotation | The paragraph's purpose, relation to neighbouring paragraphs, and any necessary concept explanation |
| Figure or table | At its first discussion, with a bilingual caption and the claim it supports |
| Equation | Readable formula, symbols and the role of the calculation |
| Overview | Problem → idea → evidence → conclusion and limits |

- Read the full main text and every figure; record the scope. References are not translated; include appendices only on request.
- Introduce unfamiliar concepts when needed. Do not assume a translated technical term explains itself.
- Keep background, author statements and reader interpretations distinct. Cite page locations; mark unclear table cells and unsupported interpretations.
- Cover every main-text paragraph, figure and table. Check alignment, navigation and narrow-screen reading.
- Write `<topic>/annotated.html`; keep intermediate extraction files in `<topic>/_work/`. Link and open the result for the user.

Read [Paper extraction](../reading/references/reading.md) for text and figures, and [Annotated page](references/page.md) when building the HTML. Use paper-reading:reading for the wider paper cluster.
