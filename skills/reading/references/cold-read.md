# Read as a newcomer

Use after `check_page.py` writes `_work/verify/reading_text.txt`. The review checks understanding, not just term registration. When independent delegation is authorized and available, give a reader only that file and the prompt below; otherwise review it without relying on outside knowledge and state that no independent review ran.

```text
你完全沒有這個領域的背景。只讀 <topic>/_work/verify/reading_text.txt，不查其他資料。
依序找出未解釋名詞、跳過的步驟、沒有尺度的數字、尚未介紹的概念，以及讀兩次仍不懂的句子。
出處與知識點編號只是查證和導覽資訊，不算理解障礙。
將結果寫入 <topic>/_work/verify/cold_read.md：

## 看不懂的地方
- 〔所在標題〕「卡住的片段」：原因
沒有問題時寫「（無）」，不要留下空白項目。

## 讀完後我理解的內容
用 3 句話說明問題、方法及證據顯示的效果。
最後只回覆問題數。
```

Check the reader's three-sentence understanding against the paper. Fix both reported obstacles and misleading explanations; rerun the checker and review the updated text. The review record must be newer than `index.html`. Stop after 3 unsuccessful rounds and report the remaining items. A completed checklist alone does not prove a human reader understands.
