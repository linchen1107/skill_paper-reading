# paper-reading

從一篇論文出發，讀懂它要解決的問題、前人方法在什麼條件下不足，以及實驗證據實際支持到哪裡。這個 repo 提供 Claude Code plugin，也提供本機 Codex／ChatGPT 桌面版可安裝的 3 個 skill。

| Skill | 用途 | 主要成果 |
| --- | --- | --- |
| `reading` | 以主論文為核心，閱讀同一研究問題的論文群，補齊所有知識點 | 繁體中文的論文筆記與互動教學頁；預設完整報告約讀 20–30 篇相關論文 |
| `annotate` | 逐段細讀單篇主論文 | 英文原文、繁體中文翻譯及論證註解並排的單頁 HTML |
| `presentation` | 用真實資料展示方法與傳統作法 | 可執行的 Python 後端與互動 lab 頁面 |

`reading` 的互動頁會依控制項重新計算示範結果，先以同一份資料執行傳統作法，再展示論文方法；涉及公式的知識點可逐步播放當次數值的計算。這與在真實資料上跑模型是不同驗收項目。需要真實資料與後端時，接著使用 `presentation`。報告頁只放可追溯的「原論文報告」或「本次實際重現」；待驗證的推論與未確認資料留在論文筆記。

## Install：Claude Code

在終端機執行：

```sh
claude plugin marketplace add linchen1107/skill_paper-reading
claude plugin install paper-reading@linchen-skills
claude plugin list
```

也可以直接把以下文字傳給 Claude Code agent，請它完成安裝與確認：

```text
幫我安裝 https://github.com/linchen1107/skill_paper-reading 這個 Claude Code plugin，讓我可以調用。請用 marketplace 安裝：先加入 linchen1107/skill_paper-reading，再安裝 paper-reading@linchen-skills。完成後確認 /paper-reading:reading、/paper-reading:annotate、/paper-reading:presentation 可以調用；如果已有安裝，請更新而不是重複安裝。
```

在 Claude Code 中使用：

```text
/paper-reading:reading       給主論文 PDF、arXiv 連結或標題
/paper-reading:annotate      逐段閱讀同一篇主論文
/paper-reading:presentation  以 reading 的成果製作真實資料 lab
```

更新 marketplace 清單與已安裝的 plugin：

```sh
claude plugin marketplace update linchen-skills
claude plugin update paper-reading@linchen-skills
```

這是依照 [Claude Code 官方更新指令](https://code.claude.com/docs/en/discover-plugins#keep-plugins-updated) 寫的；`fankeel` 是其他 marketplace 的名稱，這個 repo 使用 `linchen-skills`。新的 repo 版本須先推送到 GitHub，以上更新指令才會取得它。

若你先前用 `git clone` 把這個 repo 直接放在 `~/.claude/skills/paper-reading`，請繼續用下列指令更新那份 checkout；不用同時安裝 marketplace 版本，以免出現重複 skill：

```sh
git -C "$HOME/.claude/skills/paper-reading" pull --ff-only
```

## Install：Codex／ChatGPT 桌面版

Codex 會搜尋目前 repo 的 `.agents/skills/`，也會搜尋個人目錄的 `~/.agents/skills/`。若只在這個 repo 使用，clone 後從 repo 根目錄或其子目錄開啟 Codex 即可。若要在其他專案使用，將 3 個完整 skill 資料夾複製到個人目錄；請連同其 `scripts/`、`templates/`、`references/` 一起保留。[Codex 官方說明](https://learn.chatgpt.com/docs/build-skills)

Windows PowerShell：

```powershell
$repo = Join-Path $HOME 'skill_paper-reading'
git clone https://github.com/linchen1107/skill_paper-reading.git $repo
New-Item -ItemType Directory -Force (Join-Path $HOME '.agents\skills') | Out-Null
Copy-Item -Path (Join-Path $repo '.agents\skills\paper-reading-*') -Destination (Join-Path $HOME '.agents\skills') -Recurse -Force
```

macOS／Linux：

```sh
git clone https://github.com/linchen1107/skill_paper-reading.git "$HOME/skill_paper-reading"
mkdir -p "$HOME/.agents/skills"
cp -R "$HOME/skill_paper-reading/.agents/skills/." "$HOME/.agents/skills/"
```

也可以直接把以下文字傳給 Codex agent，請它完成安裝與確認：

```text
幫我安裝 https://github.com/linchen1107/skill_paper-reading 裡的 Codex skills，讓我可以在本機 Codex／ChatGPT 桌面版調用。請把 repo 的 .agents/skills/paper-reading-reading、paper-reading-annotate、paper-reading-presentation 安裝到我的 ~/.agents/skills/；如果已有安裝，請更新。完成後確認這 3 個 skill 都能被找到，並告訴我如何用 $paper-reading-reading 開始讀論文。
```

更新個人安裝時，先執行 `git -C "$HOME/skill_paper-reading" pull --ff-only`，再重新執行上面對應作業系統的複製指令。Codex 通常會自動偵測 skill 變更；若清單尚未更新，重新啟動 Codex。

在 Codex 模式中使用 `$` 明確指定；在 ChatGPT 桌面版的 ChatGPT 模式中，輸入 `@` 並從技能選單選取同名 skill。[OpenAI 官方說明](https://learn.chatgpt.com/docs/build-skills#how-chatgpt-and-codex-use-skills)

```text
$paper-reading-reading 讀這篇 PDF，整理相關論文、研究缺口與所有知識點。
$paper-reading-annotate 逐段註解這篇論文，提供中英對照。
$paper-reading-presentation 依 reading 的成果製作真實資料與後端 lab。
```

Codex 也可依請求內容自動選用相符的 skill。這裡的「ChatGPT 桌面版」指本機 skill；ChatGPT 網頁版 plugin 發布不在這份安裝流程內。

例如，要用一篇論文測完整的閱讀流程，可輸入：

```text
$paper-reading-reading 以 arXiv:2310.14211v2（LUNA）為主論文，整理同一研究問題的論文群，從舊方法有證據的不足開始，逐一呈現所有知識點與互動驗收。
```

## 流程與驗收

`reading` 先讀主論文全文及每張真正的圖，提出論文群、知識點與互動設計；完整報告再閱讀約 20–30 篇直接相關論文。文字、表格及可辨識的公式由 PDF 文字層讀取；模糊處才裁圖核對。每個知識點都要有來源、頁面位置、可操作的示範與逐項驗收結果；傳統作法需在相同資料上實際運算，公式需逐步呈現當次計算。`annotate` 只處理主論文。`presentation` 在 `reading` 成果上加入真實資料、能依使用者輸入計算的後端，以及可操作的 lab。

Claude Code 預設將成果放在 `~/Documents/claude/paper-reading/<topic>/`。Codex 預設放在目前可寫工作區的 `paper-reading/<topic>/`；使用者指定的位置優先。下載資料、安裝套件或啟動服務前，依已取得的授權與執行環境規則處理。未取得的論文、未執行的模型與未通過的驗收都要明確標示。

完整閱讀成果的主要入口是 `<topic>/index.html`；`papers/` 存逐篇筆記，`widgets.js` 與 `demos.js` 驅動互動單元，`_work/verify/check.json` 留下逐項檢查結果。論文群的每篇筆記會區分已讀全文、已讀相關段落、部分閱讀與待讀。`annotate` 產生 `<topic>/annotated.html`；`presentation` 產生 `<topic>/studio/lab.html` 與 `server.py`。

驗證閱讀頁時，從 repo 根目錄執行：

```sh
python .agents/skills/paper-reading-reading/scripts/check_page.py <topic>
```

它會操作每個知識點的控制項、逐步操作公式動畫、核對手算例子，並檢查是否有傳統作法示範、知識點地圖缺項或未確認文字。檢查失敗時指令會回傳非 0 狀態；檢查只證明頁面可操作，研究論證與傳統方法是否真的使用相同資料仍須人工核對。`presentation` 還須以真實樣本呼叫後端，核對不同參數的輸出與失敗案例；頁面能開啟或 `/health` 成功，不能單獨證明模型與方法已執行。

## 維護 Codex 版本

Claude skill 位於 `skills/`；Codex 可安裝版位於 `.agents/skills/`。修改 Claude skill 或共用工具後，從 repo 根目錄執行 `python scripts/build_codex.py`，再檢查產生的 3 個 Codex skill 與變更內容。這個腳本只使用 Python 標準函式庫；閱讀論文時使用的 PyMuPDF 仍依 skill 指示於成果資料夾安裝。

```text
.claude-plugin/     Claude plugin 與 marketplace 設定
skills/             Claude Code 的 reading、annotate、presentation
scripts/            論文擷取、頁面驗收與 Codex 版本產生腳本
templates/          reading 的共用頁面與互動元件
.agents/skills/     可直接安裝的 3 個 Codex skill
```
