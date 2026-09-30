# paper-reading

Start with one paper, read the related research, identify where earlier methods fall short, and turn every knowledge point into interactive teaching material. Available as a Claude Code plugin and local Codex skills.

| Skill | Purpose |
| --- | --- |
| `reading` | Read about 20–30 related papers; build the research narrative, knowledge-point map, and interactive page |
| `annotate` | Create a paragraph-by-paragraph English–Chinese annotated reading of one paper |
| `presentation` | Demonstrate the method with real data, a Python backend, and interactive labs |

## Claude Code

Install:

```sh
claude plugin marketplace add linchen1107/skill_paper-reading
claude plugin install paper-reading@linchen-skills
```

Or send this to your Claude Code agent:

```text
Install or update https://github.com/linchen1107/skill_paper-reading through the Claude Code marketplace so I can use it. Confirm that /paper-reading:reading, /paper-reading:annotate, and /paper-reading:presentation are available.
```

Update:

```sh
claude plugin marketplace update linchen-skills
claude plugin update paper-reading@linchen-skills
```

## Codex

Codex loads `.agents/skills/` when working in this repository. To use the skills in any project, copy them to `~/.agents/skills/`.

Windows PowerShell:

```powershell
$repo = Join-Path $HOME 'skill_paper-reading'
git clone https://github.com/linchen1107/skill_paper-reading.git $repo
New-Item -ItemType Directory -Force (Join-Path $HOME '.agents\skills') | Out-Null
Copy-Item -Path (Join-Path $repo '.agents\skills\paper-reading-*') -Destination (Join-Path $HOME '.agents\skills') -Recurse -Force
```

macOS/Linux:

```sh
git clone https://github.com/linchen1107/skill_paper-reading.git "$HOME/skill_paper-reading"
mkdir -p "$HOME/.agents/skills"
cp -R "$HOME/skill_paper-reading/.agents/skills/." "$HOME/.agents/skills/"
```

Or send this to your Codex agent:

```text
Install or update the three Codex skills from https://github.com/linchen1107/skill_paper-reading in ~/.agents/skills/ so I can use them locally. Confirm that $paper-reading-reading, $paper-reading-annotate, and $paper-reading-presentation are available.
```

To update a personal install, run `git -C "$HOME/skill_paper-reading" pull --ff-only`, then repeat the copy command above.

## Usage and output

| Claude Code | Codex | Main output |
| --- | --- | --- |
| `/paper-reading:reading` | `$paper-reading-reading` | `index.html`, `papers/`, per-point checks |
| `/paper-reading:annotate` | `$paper-reading-annotate` | `annotated.html` |
| `/paper-reading:presentation` | `$paper-reading-presentation` | `studio/lab.html`, `studio/server.py` |

Give `reading` a PDF, arXiv link, or paper title. Its interactive examples do not reproduce the paper on real data; use `presentation` when you need real data and a runnable backend.

Check a reading page with `python .agents/skills/paper-reading-reading/scripts/check_page.py <topic>`. After changing a Claude skill or shared tool, regenerate the Codex skills with `python scripts/build_codex.py`.
