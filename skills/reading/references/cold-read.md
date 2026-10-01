# Cold read: a reader who knows nothing about the field

The writer of a page already knows the field, so they cannot see which words and steps a newcomer lacks. The cold read hands the page to a reader who has only the page.

## How to run it

1. Run `check_page.py`; it writes `<topic>/_work/verify/reading_text.txt`, the page's headings and prose in reading order.
2. Dispatch one subagent (the same model setting as the other subagents) with the prompt below, filling in the absolute paths. Give it nothing else: no paper, no notes, no summary of the topic.
3. **Check the reader's understanding.** Compare its 3 sentences under 讀完後我理解的內容 with the paper, and add to `cold_read.md`:
   ```
   ## 理解檢查
   正確
   ```
   or, when a sentence is wrong, what it got wrong. A wrong understanding means the page misleads: fix the page and run one new cold read.
4. **Fix every [阻斷] item** on the page (explain the term where it first appears, add the missing step, give the number its scale, move the passage after what it needs), and end its line in `cold_read.md` with `→ 已修正：<what changed>`. Fix a [輕微] or 可以刪掉 item when one sentence does it (delete what is repeated or noise, replace a made-up name with the paper's or the standard term); list the rest in the final reply.
5. Run `check_page.py` again. It fails while a [阻斷] line lacks 已修正 or the 理解檢查 does not start with 正確.

**One cold read, not a loop.** A fresh reader always finds something new: on one run three successive readers listed 19, 41 and 14 unclear items, and with severity marks 2, 1 and 2 blocking items, each time different ones. So the cold read runs once, its blocking items are fixed and marked, and it is repeated only when the reader's understanding was wrong or the storyline was rewritten after it.

## Prompt

```
你是一位聰明、但從來沒有學過這個領域的讀者，例如別的實驗室的研究生。
只讀這個檔案：<topic>/_work/verify/reading_text.txt。不要開啟任何其他檔案，不要上網查。
不要用你自己對這個領域的知識補空缺：頁面沒有解釋的東西，就當作你不知道。
這份文字只有教學的部分：出處行、知識點地圖、論文群比較表和附錄都已拿掉，不必理會它們。
知識點編號（例如 A4、C1）是給跳轉用的，看不懂它們本身不算卡住；但出處如果夾在句子中間、打斷了閱讀，就算一處問題。
「[公式：……]」「[數字卡]」是頁面元件的位置標記，不算雜訊。
每個知識點開頭的「生活例子」是刻意放的，用來先給畫面，不算雜訊。

依順序讀完，找出所有讓你卡住的地方：
- 沒有解釋就使用的名詞或縮寫（包括模型、資料集、方法的名稱）
- 跳過的步驟：前一句到後一句之間少了什麼
- 沒有尺度的數字：不知道這個數字算好還是算差
- 提到還沒介紹過的東西
- 讀了兩次仍然看不懂的句子
- 作者自己取的名字：不是論文或教科書的說法，你沒辦法拿去查（例如「本頁稱為……」）
- 重複：同一件事用同樣的深度講了第二次（知識點用一句話接回導讀的結論、再往下講細節，不算重複）
- 雜訊：刪掉之後不影響理解的句子、旁支知識、夾在句子中間的出處

一個名詞只要頁面用白話說了它是什麼或做什麼，就算解釋過，即使縮寫的全名沒有展開。

每一處看不懂的地方標上嚴重程度：
- 〔阻斷〕不解決就跟不上主線（問題 → 傳統作法為什麼不夠 → 作者怎麼做 → 證據顯示什麼），或會讓人誤解一個結果
- 〔輕微〕某個知識點裡的細節不清楚，但主線仍然讀得懂

把結果用繁體中文寫進 <topic>/_work/verify/cold_read.md，格式如下（沒有卡住的地方就在清單位置寫「（無）」）：

## 看不懂的地方
- [阻斷]〔所在的標題〕「原句中卡住的片段」：卡住的原因
- [輕微]〔所在的標題〕「原句中卡住的片段」：卡住的原因

## 可以刪掉的地方
- 〔所在的標題〕「片段」：重複／雜訊／自己取的名字，以及為什麼

## 讀完後我理解的內容
用 3 句話說明：這篇論文要解決什麼問題、它怎麼做、證據顯示效果如何。

最後只回覆一行：阻斷幾處，輕微幾處，可以刪掉的地方幾處。
```

The [輕微] items and 可以刪掉的地方 are printed as counts by `check_page.py` and do not block acceptance.
