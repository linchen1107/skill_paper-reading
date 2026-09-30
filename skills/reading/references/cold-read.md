# Cold read: a reader who knows nothing about the field

The writer of a page already knows the field, so they cannot see which words and steps a newcomer lacks. The cold read hands the page to a reader who has only the page.

## How to run it

1. Run `check_page.py`; it writes `<topic>/_work/verify/reading_text.txt`, the page's headings and prose in reading order.
2. Dispatch one subagent (the same model setting as the other subagents) with the prompt below, filling in the absolute paths. Give it nothing else: no paper, no notes, no summary of the topic.
3. Fix every item it lists on the page (explain the term where it first appears, add the missing step, give the number its scale, move the passage after what it needs), run `check_page.py` again, and run a new cold read on the new text. `check_page.py` accepts only a cold read newer than `index.html` with an empty list.
4. After 3 rounds that still list items, stop and report the remaining items to the user instead of looping.

## Prompt

```
你是一位聰明、但從來沒有學過這個領域的讀者，例如別的實驗室的研究生。
只讀這個檔案：<topic>/_work/verify/reading_text.txt。不要開啟任何其他檔案，不要上網查。
不要用你自己對這個領域的知識補空缺：頁面沒有解釋的東西，就當作你不知道。
括號裡的出處（例如「原論文報告，Section III-B」「Table V」）和知識點編號（例如 A4、C1）是給查證與跳轉用的，看不懂它們本身不算卡住。

依順序讀完，找出所有讓你卡住的地方：
- 沒有解釋就使用的名詞或縮寫（包括模型、資料集、方法的名稱）
- 跳過的步驟：前一句到後一句之間少了什麼
- 沒有尺度的數字：不知道這個數字算好還是算差
- 提到還沒介紹過的東西
- 讀了兩次仍然看不懂的句子

把結果用繁體中文寫進 <topic>/_work/verify/cold_read.md，格式如下（沒有卡住的地方就在清單位置寫「（無）」）：

## 看不懂的地方
- 〔所在的標題〕「原句中卡住的片段」：卡住的原因

## 讀完後我理解的內容
用 3 句話說明：這篇論文要解決什麼問題、它怎麼做、證據顯示效果如何。

最後只回覆一行：看不懂的地方共幾處。
```

The 讀完後我理解的內容 part lets the main flow check that the reader understood the page correctly, not only that nothing was flagged; if those 3 sentences are wrong, the page misleads and is fixed like any listed item.
