# paper-reading

從一篇論文展開同題文獻群，為沒有領域背景的讀者製作圖解與可操作教材。**圖優先、表其次、文字只補必要解釋。**

| 技能 | 用途 | 主要產出 |
|---|---|---|
| `reading` | 閱讀約 20–30 篇相關論文，串起問題、方法與證據，涵蓋全部知識點 | `index.html`、`papers/` |
| `annotate` | 主論文逐段中英對照與短註解 | `annotated.html` |
| `presentation` | 真實資料、Python 後端與可操作實驗 | `studio/lab.html`、`studio/server.py` |

## 安裝

Claude Code：

```sh
claude plugin marketplace add linchen1107/skill_paper-reading
claude plugin install paper-reading@linchen-skills
```

Codex：repository 內可直接使用 `.agents/skills/`；其他專案可複製這 3 個技能到個人的技能目錄。

Windows PowerShell：

```powershell
$repo = Join-Path $HOME 'skill_paper-reading'
git clone https://github.com/linchen1107/skill_paper-reading.git $repo
New-Item -ItemType Directory -Force (Join-Path $HOME '.agents\skills') | Out-Null
Copy-Item -Path (Join-Path $repo '.agents\skills\paper-reading-*') -Destination (Join-Path $HOME '.agents\skills') -Recurse -Force
```

macOS/Linux：

```sh
git clone https://github.com/linchen1107/skill_paper-reading.git "$HOME/skill_paper-reading"
mkdir -p "$HOME/.agents/skills"
cp -R "$HOME/skill_paper-reading/.agents/skills/." "$HOME/.agents/skills/"
```

## 使用與維護

| Claude Code | Codex |
|---|---|
| `/paper-reading:reading` | `$paper-reading-reading` |
| `/paper-reading:annotate` | `$paper-reading-annotate` |
| `/paper-reading:presentation` | `$paper-reading-presentation` |

提供 PDF、arXiv 連結或標題。`reading` 的小型示範解釋機制；需要真實資料與可執行 backend 時，使用 `presentation`。兩種結果都需標明來源與條件。

Claude 更新：`claude plugin marketplace update linchen-skills`，再執行 `claude plugin update paper-reading@linchen-skills`。Codex 個人安裝更新：repository 執行 `git pull --ff-only` 後，重新複製技能。

修改正式來源 `skills/` 後，執行 `python scripts/build_codex.py` 同步生成 `.agents/skills/`。檢查教材使用 `python scripts/check_page.py <topic>`；實驗使用 `python scripts/check_lab.py <topic>`。
