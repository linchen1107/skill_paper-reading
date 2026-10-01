"""Build the three self-contained Codex skills from the Claude skill sources.

Usage: python scripts/build_codex.py
The generated .agents/skills folders can be copied together into ~/.agents/skills.
"""

from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / ".agents" / "skills"

DESCRIPTIONS = {
    "reading": (
        "Read a supplied research paper with its same-problem paper cluster, "
        "explain prior failures and evidence, map every knowledge point, and build "
        "an interactive teaching page. Also use for paper Discussion review or code search."
    ),
    "annotate": (
        "Create a bilingual paragraph-by-paragraph annotated reading of one research "
        "paper, with figures, tables, argument notes, and a Traditional Chinese translation. "
        "Use for close reading of the main paper; not for a paper cluster."
    ),
    "presentation": (
        "Build a locally runnable paper teaching lab from paper-reading output, using "
        "real sourced samples and a Python backend that computes results on request. "
        "Use for a paper presentation requiring real data and an executable playground."
    ),
}


def frontmatter(name: str) -> str:
    return f"---\nname: paper-reading-{name}\ndescription: {DESCRIPTIONS[name]}\n---\n\n"


def source_body(name: str) -> str:
    original = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\n.*?\n---\n(.*)\Z", original, re.S)
    if not match:
        raise ValueError(f"Missing frontmatter: {name}")
    return match.group(1)


def replace_required(body: str, old: str, new: str, name: str) -> str:
    if old not in body:
        raise ValueError(f"Expected source text missing in {name}: {old[:60]}")
    return body.replace(old, new)


def build_reading() -> str:
    name = "reading"
    body = source_body(name)
    body = body.replace("paper-reading:presentation", "$paper-reading-presentation")
    body = body.replace("paper-reading:reading", "$paper-reading-reading")
    body = replace_required(
        body,
        "**Do not start stage 1 until the user replies to stage 0.**",
        "**Do not start stage 1 until the user has authorized the full scope; prior authorization in the conversation counts.**",
        name,
    )
    body = replace_required(
        body,
        "wait for the user's approval",
        "use the user's existing approval or wait for approval",
        name,
    )
    body = replace_required(
        body,
        "Full reading, downloads, subagent dispatch and code wait until the user approves.",
        "Full reading, downloads, agent dispatch and code wait until the user authorizes the full run; reuse authorization already given. If the user has approved it, show the proposal briefly and continue; otherwise wait for a reply.",
        name,
    )
    body = replace_required(
        body,
        "List the following and wait for the user's reply.",
        "List the following. Wait only if the full run has not already been authorized.",
        name,
    )
    body = replace_required(
        body,
        "- **Sonnet throughout.** This skill runs on Sonnet, and every subagent is dispatched with `model: sonnet`.",
        "- Use the model selected by the user or Codex; do not assume a Claude-specific model is available.",
        name,
    )
    body = replace_required(
        body,
        "the run writes only the content and `demos.js`.",
        "the run writes only the content and `demos.js`. Resolve a Python executable on this host before running the bundled scripts.",
        name,
    )
    body = body.replace("from the plugin (`templates/`, `scripts/`)",
                        "from this skill (`templates/`, `scripts/`)")
    body = body.replace("the plugin's templates", "this skill's templates")
    body = replace_required(
        body,
        "**Every subagent uses `model: sonnet`.** This covers all subagents: reading papers, writing demos, acceptance checks.",
        "**Agent work follows the host and user settings.** Delegate only when authorized and available; verify each agent's source claims.",
        name,
    )
    body = replace_required(
        body,
        "Assume the user is on a small plan: a whole run, stages 0 to 5, should use no more than about 10% of a Pro plan's weekly usage (about 1% on Max 20x).",
        "Keep the workflow economical without claiming a known quota or token cost; estimate scope before a full run.",
        name,
    )
    body = replace_required(
        body,
        "- **Split the reading across subagents.**",
        "- **When agent delegation is authorized and available, split the reading across subagents.**",
        name,
    )
    body = replace_required(
        body,
        "`<plugin>` is the folder of this plugin (the parent of `skills/`).",
        "`<skill>` is the directory containing this `SKILL.md`.",
        name,
    )
    body = body.replace("<plugin>/", "<skill>/")
    body = replace_required(
        body,
        "otherwise the current user's `Documents/claude/` (`~/Documents/claude/`; on Windows `%USERPROFILE%\\Documents\\claude\\`), resolving the home directory at run time instead of assuming a user name.",
        "otherwise the current workspace.",
        name,
    )
    body = replace_required(body, "~/Documents/claude/paper-reading/<topic>/", "<workspace>/paper-reading/<topic>/", name)
    body = replace_required(
        body,
        "Downloading data or model weights, installing packages, and starting any service that occupies a port: each time, state what it is, the source and the size, and get approval before acting.",
        "For material downloads, package installs, model weights, or a server start, check the user's existing authorization first. If absent, state the source, size or port and ask; an approved plan covers the actions it listed without repeated requests.",
        name,
    )
    return frontmatter(name) + body.lstrip("\n")


def build_annotate() -> str:
    name = "annotate"
    body = source_body(name)
    body = body.replace("paper-reading:reading", "$paper-reading-reading")
    body = replace_required(body, "[../reading/SKILL.md](../reading/SKILL.md)",
                            "[../paper-reading-reading/SKILL.md](../paper-reading-reading/SKILL.md)", name)
    body = replace_required(body, "`scripts/extract_figures.py`", "`<skill>/scripts/extract_figures.py`", name)
    body = replace_required(
        body,
        "Read the paper by **\"How to read a paper\"",
        "`<skill>` is the directory containing this `SKILL.md`. Read the paper by **\"How to read a paper\"",
        name,
    )
    return frontmatter(name) + body.lstrip("\n")


def build_presentation() -> str:
    name = "presentation"
    body = source_body(name)
    body = body.replace("paper-reading:reading", "$paper-reading-reading")
    body = replace_required(
        body,
        "Write no files yet.",
        "If this plan has not already been approved, write no files yet; prior user authorization counts.",
        name,
    )
    body = replace_required(
        body,
        "Then list in the chat and wait for one reply:",
        "Then list in the chat. Continue if the user already authorized this scope; otherwise wait for one reply:",
        name,
    )
    body = replace_required(
        body,
        "`<plugin>` is the folder of this plugin (the parent of `skills/`).",
        "`<skill>` is the directory containing this `SKILL.md`.",
        name,
    )
    body = body.replace("<plugin>/", "<skill>/")
    body = replace_required(
        body,
        "Same as $paper-reading-reading: a whole run within about 10% of a Pro plan's weekly usage (about 1% on Max 20x). Sonnet throughout, every subagent `model: sonnet`; read files once and search instead of rereading; check by values, not screenshots.",
        "Keep use economical: read files once and search instead of rereading; check by values, not screenshots. Use the model selected by the user or Codex.",
        name,
    )
    body = replace_required(
        body,
        "Before each download, install, or server start, state what it is, the source and the size, and wait for approval. Step 0 covers what it listed; anything new is asked separately.",
        "Before a download, install, or server start, check existing user authorization. If absent, state the source, size or port and ask once; an approved Step 0 covers the listed actions. Ask separately only when the action exceeds that scope.",
        name,
    )
    return frontmatter(name) + body.lstrip("\n")


def main() -> None:
    for name, build in (("reading", build_reading), ("annotate", build_annotate),
                        ("presentation", build_presentation)):
        folder = TARGET / f"paper-reading-{name}"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "SKILL.md").write_text(build(), encoding="utf-8")

    reading = TARGET / "paper-reading-reading"
    for script in ("extract_figures.py", "fetch_papers.py", "check_page.py", "selftest.js", "serve.py", "build_notes.py"):
        dest = reading / "scripts"
        dest.mkdir(exist_ok=True)
        shutil.copy2(ROOT / "scripts" / script, dest / script)
    for template in ("page.html", "widgets.js"):
        dest = reading / "templates"
        dest.mkdir(exist_ok=True)
        shutil.copy2(ROOT / "templates" / template, dest / template)
    shutil.copytree(ROOT / "templates" / "katex", reading / "templates" / "katex", dirs_exist_ok=True)
    sources = reading / "references"
    sources.mkdir(exist_ok=True)
    for ref in ("sources.md", "cold-read.md"):
        shutil.copy2(ROOT / "skills" / "reading" / "references" / ref, sources / ref)

    presentation = TARGET / "paper-reading-presentation"
    (presentation / "scripts").mkdir(exist_ok=True)
    for script in ("check_lab.py", "check_page.py", "serve.py"):
        shutil.copy2(ROOT / "scripts" / script, presentation / "scripts" / script)
    shutil.copytree(ROOT / "templates" / "studio", presentation / "templates" / "studio", dirs_exist_ok=True)

    annotate_scripts = TARGET / "paper-reading-annotate" / "scripts"
    annotate_scripts.mkdir(exist_ok=True)
    shutil.copy2(ROOT / "scripts" / "extract_figures.py",
                 annotate_scripts / "extract_figures.py")
    print("Generated reading, annotate, and presentation Codex skills.")


if __name__ == "__main__":
    main()
