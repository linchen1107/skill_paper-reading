# Cold read: a reader who knows nothing about the field

The writer of a page already knows the field, so they cannot see which words and steps a newcomer lacks. The cold read hands the page to a reader who has only the page.

## How to run it

1. Run `check_page.py`; it writes `<topic>/_work/verify/reading_text.txt`, the page's headings and prose in reading order.
2. Dispatch one subagent (the same model setting as the other subagents) with the prompt below, filling in the absolute paths. Give it nothing else: no paper, no notes, no summary of the topic.
3. **Check the reader's understanding.** Compare its 3 sentences under "After reading, what I understood" with the paper, and add to `cold_read.md`:
   ```
   ## Understanding check
   Correct
   ```
   or, when a sentence is wrong, what it got wrong. A wrong understanding means the page misleads: fix the page and run one new cold read.
4. **Fix every [blocking] item** on the page (explain the term where it first appears, add the missing step, give the number its scale, move the passage after what it needs), and end its line in `cold_read.md` with `→ fixed: <what changed>`. Fix a [minor] or "Can be cut" item when one sentence does it (delete what is repeated or noise, replace a made-up name with the paper's or the standard term); list the rest in the final reply.
5. Run `check_page.py` again. It fails while a [blocking] line lacks "→ fixed" or the "Understanding check" does not start with "Correct".

**One cold read, not a loop.** A fresh reader always finds something new: on one run three successive readers listed 19, 41 and 14 unclear items, and with severity marks 2, 1 and 2 blocking items, each time different ones. So the cold read runs once, its blocking items are fixed and marked, and it is repeated only when the reader's understanding was wrong or the cards or chapters were rewritten after it.

## Prompt

```
You are an intelligent reader who has never studied this field, for example a graduate student from another lab.
Read only this file: <topic>/_work/verify/reading_text.txt. Do not open any other file and do not search the web.
Do not fill gaps with your own knowledge of the field: whatever the page does not explain, treat as something you do not know.
The file holds only the teaching part of the page: the 6 cards at the start (Problem, Before, This paper, Result, Weak spots, Next steps), and under each card its chapter and the chapter's knowledge points. Source lines, the knowledge-point map, the paper-groups table and the appendix have been removed; ignore them. Answer in English.
Knowledge-point numbers (for example A4, C1) are for jumping; not understanding them is not a problem. A source placed in the middle of a sentence that interrupts the reading is a problem.
"[formula: …]" and "[number card]" mark where a page widget sits; they are not noise.
The everyday example (Example) that opens each knowledge point is deliberate, to give a picture first; it is not noise.

Read in order and find every place where you got stuck:
- A term or abbreviation used without explanation (including names of models, datasets and methods)
- A skipped step: something missing between one sentence and the next
- A number without a scale: you cannot tell whether it is good or bad
- Something mentioned before it has been introduced
- A sentence you still cannot understand after reading it twice
- A name the author made up: not the paper's or a textbook's term, so you cannot look it up (for example "this page calls …")
- Repetition: the same thing said a second time at the same depth (the card states the conclusion, the chapter expands it, and a knowledge point restates it in one sentence before going further; this is deliberate structure, not repetition)
- Noise: a sentence that can be cut without hurting understanding, side facts, a source in the middle of a sentence

A term counts as explained once the page says in plain words what it is or does, even if the full name of an abbreviation is not spelled out.

Mark the severity of every place where you got stuck:
- [blocking] cannot follow the main line without it (Problem -> why Before is not enough -> how This paper does it -> what Result shows -> Weak spots), or it would make you misunderstand a result
- [minor] a detail inside one knowledge point is unclear, but the main line is still readable

Write the result in English to <topic>/_work/verify/cold_read.md in this format (when nothing got you stuck, write "(none)" in place of the list):

## Unclear
- [blocking] [heading it is under] "the stuck fragment of the original sentence": why you got stuck
- [minor] [heading it is under] "the stuck fragment of the original sentence": why you got stuck

## Can be cut
- [heading it is under] "fragment": repetition / noise / made-up name, and why

## After reading, what I understood
In 3 sentences: what problem this paper solves, how it does it, and what the evidence shows about how well it works.

Finally reply with one line only: how many blocking, how many minor, how many can be cut.
```

The [minor] items and "Can be cut" items are printed as counts by `check_page.py` and do not block acceptance.
