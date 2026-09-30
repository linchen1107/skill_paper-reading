# paper-reading

從一篇論文出發，讀同一研究問題的論文群，找出前人方法的限制，並把知識點做成可操作的教學內容。提供 Claude Code plugin 與本機 Codex skills。

| Skill | 用途 |
| --- | --- |
| `reading` | 閱讀約 20–30 篇相關論文，整理研究脈絡、所有知識點與互動頁 |
| `annotate` | 逐段產生單篇論文的中英對照與註解 |
| `presentation` | 用真實資料、Python 後端與可操作的 lab 展示方法 |

## Claude Code

安裝：

```sh
claude plugin marketplace add linchen1107/skill_paper-reading
claude plugin install paper-reading@linchen-skills
```

或傳給 Claude Code agent：

```text
幫我安裝 https://github.com/linchen1107/skill_paper-reading，讓我可以調用。請用 Claude Code marketplace 安裝或更新，並確認 /paper-reading:reading、/paper-reading:annotate、/paper-reading:presentation 可用。
```

更新：

```sh
claude plugin marketplace update linchen-skills
claude plugin update paper-reading@linchen-skills
```

## Codex

在 repo 內使用時，Codex 會讀取 `.agents/skills/`。若要在所有專案使用，安裝到個人目錄 `~/.agents/skills/`。Windows PowerShell：

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

或傳給 Codex agent：

```text
幫我安裝 https://github.com/linchen1107/skill_paper-reading 裡的 3 個 Codex skills 到 ~/.agents/skills/，讓我可以在本機調用。若已安裝請更新，完成後確認 $paper-reading-reading、$paper-reading-annotate、$paper-reading-presentation 可用。
```

更新個人安裝：先執行 `git -C "$HOME/skill_paper-reading" pull --ff-only`，再重新執行上面的複製指令。

## 使用與成果

| Claude Code | Codex | 主要成果 |
| --- | --- | --- |
| `/paper-reading:reading` | `$paper-reading-reading` | `index.html`、`papers/`、逐項檢查結果 |
| `/paper-reading:annotate` | `$paper-reading-annotate` | `annotated.html` |
| `/paper-reading:presentation` | `$paper-reading-presentation` | `studio/lab.html`、`studio/server.py` |

提供 PDF、arXiv 連結或論文標題即可開始 `reading`。互動頁的示範計算不等於在真實資料上重現論文；需要真實資料與可執行後端時，再用 `presentation`。

驗證閱讀頁：`python .agents/skills/paper-reading-reading/scripts/check_page.py <topic>`。修改 Claude skill 或共用工具後，用 `python scripts/build_codex.py` 重新產生 Codex 版本。
