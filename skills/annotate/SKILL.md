---
name: annotate
model: sonnet
description: Produce a single-file bilingual annotated reading of the one paper the user is reading. Every paragraph shows the English original with its key phrases highlighted in five colours (claims, key terms, evidence, concessions, method), a Traditional Chinese (Taiwan) translation, and an aligned English annotation card (what the paragraph does, its place in the argument, what to notice). Figures and tables appear where the text discusses them. Ends with an English overview of the whole argument. Everything except the translation is in English. Main paper only; no paper cluster. Use when the user wants to read a paper closely, see its argument structure, or get a Chinese–English side-by-side reading.
---

# Annotate: a bilingual annotated reading of the main paper

The purpose is to help the user understand **the paper they are reading**: what each paragraph says, what it does in the argument, and how the argument holds together. It covers the main paper only; for the paper cluster and interactive units, use paper-reading:reading.

The output is one HTML file the user reads from top to bottom. Keep it plain: no extra panels, widgets or modules beyond what is described here.

## Language

- The purpose of this skill is the side-by-side reading: each paragraph shows the English original and its translation in **Traditional Chinese as used in Taiwan** (Taiwanese terminology, for example 資料 not 數據, 影片 not 視頻, 程式碼 not 代碼). Technical terms may stay in English in the translation, with the Chinese term on first use.
- Everything else the page contains is in **English**: the annotation cards, the argument notes, the overview, the section bar, the legend, headings and interface labels. Follow the wording rules of paper-reading:reading (complete sentences, conclusion first, no filler). Replies to the user in chat are in Traditional Chinese (Taiwan).
- The English original is quoted exactly; do not paraphrase or shorten it.
- The translation is idiomatic academic Traditional Chinese, not word-for-word, and must not add or drop content.

## Reading the paper

Read the paper by **"How to read a paper" in [../reading/SKILL.md](../reading/SKILL.md)**: extract with `scripts/extract_figures.py` into `<topic>/_work/extract/<short>/` (never the scratchpad), read the whole text, look at every figure, keep a reading log. Paragraph text, headings, tables and equations come from `text.txt` (fix hyphenation and line breaks; keep equations readable). Page images of text are not opened.

Cover the main text from the title and abstract through the conclusion. References are not translated. Appendices are included only if the user asks; otherwise the page says they were not included.

## The page

One file: `<topic>/annotated.html`, all CSS and JS inline, figures embedded, no external files except Google Fonts. It must still be readable if the fonts do not load.

### A. Top bar

Fixed at the top (`position: fixed; top: 0; z-index: 1000`, height 60px), navy `#1a2744` with white text. Left: paper title, authors, venue and year. Right: the colour legend.

| Colour | Marks |
|---|---|
| Yellow `#fff3b0` | Core claims and stated positions |
| Red `#ffd6d6` | Key concepts and terms, where they first appear |
| Blue `#d6e5ff` | Empirical evidence and numbers |
| Green `#d6f5d6` | Concessions, limitations and answers to objections |
| Purple `#e8d6ff` | Method descriptions |

### B. Section bar

Sticky directly below the top bar (`position: sticky; top: 60px; z-index: 900`). One button per section heading of the paper, jumping to it; the current section is highlighted while scrolling.

### C. The paragraphs

The body has `padding-top` large enough that neither bar covers content (about 120px). **Each paragraph is one row with two cells**, so the left text and its right card are always aligned:

- **Left: the paragraph.**
  - English original in Lora, with highlights on phrases or sentences, never a whole paragraph.
  - A 1px light-grey rule.
  - The Chinese translation on a beige background (`#f0ece2`) with a 3px left border (`#c4b99a`), no highlights.
  - The page number of the paragraph (for example `p.3`), so every statement can be found in the PDF.
- **Right: the annotation card** (light-grey `#f5f5f5`, 4px coloured left border matching the paragraph's main dimension):
  1. **Function**: a short label, such as Poses the problem, Provides evidence, Answers an objection, Transition, Summary.
  2. **Role in the argument**: where the paragraph sits in the chain and how it relates to the paragraphs before and after it.
  3. **What to notice**: a writing technique worth learning, or a possible gap in the logic, with the reason. Write "None" when there is nothing worth saying; do not invent observations.

**Figures, tables and equations** appear as their own rows, at the point where the text first discusses them:

- Figures: the left cell shows the figure as the paper holds it, `fig<N>-real.*` (the original bitmap or the vector SVG, never the screenshot copy `fig<N>.png`), with the caption in English and Chinese.
- Tables: rebuilt as an HTML table from the text layer, with the caption in English and Chinese; cells the text layer leaves unclear are marked "not yet confirmed".
- The right card says what it shows, which claim it supports, and whether the text's claim matches what the image actually shows.
- Equations are shown as images or typeset, and each symbol is explained in the card.

Interface and annotations use IBM Plex Sans, falling back to Noto Sans TC or Microsoft JhengHei for the Chinese translation. Page background `#faf8f4`.

### D. Argument overview (at the bottom)

1. Research problem.
2. The core claim in one sentence.
3. The chain of evidence: which figure or table supports which claim, in order.
4. How concessions and objections are handled.
5. Conclusion.
6. The strongest point and the weakest point of the argument, one each, with the reason and the page.

### E. Optional modules (only when the user asks)

- Discussion questions: 5–8 questions, each with a reference answer hidden in `<details>`, and the question number shown on the related annotation cards.
- Term cards: the red-highlighted concepts as flip cards.
- Concept map: the main concepts and their relations as SVG.

### Responsive

At 1024px and wider, two columns. Below 1024px, one column: each annotation card sits under its paragraph, collapsed, and opens on tap.

## Rules

**Faithful to the paper.** Every statement in a card or the overview is about the paper and traceable to a page. General knowledge is labelled "Background". If the paper does not say something, write "not stated in the paper". Possible problems in the logic are the reader's inference and are marked "Unverified inference".

**The whole paper.** No paragraph of the main text is skipped. If the paper is long, build the file section by section in the same file until it is complete; do not stop after the first sections.

**Work only inside the output folder**, as in paper-reading:reading: the page goes in `<topic>/annotated.html` (the same `<topic>` folder paper-reading:reading uses, or a location the user names); extracted text, figures and temporary files go in `<topic>/_work/`. Nothing is written anywhere else.

## Done when

- Every section and paragraph of the main text is present: compare the paragraph count and section headings with the PDF, and list any gap.
- Every figure and table of the main text appears once, next to the paragraph that first discusses it.
- Opened in a browser: the bars do not cover content, the section bar jumps and highlights correctly, paragraphs and cards line up, and the layout switches to one column below 1024px.
- Then open the page in the user's default browser, and start the reply with a clickable link to it and the reading log (figures viewed out of captioned figures; tables with their pages).
