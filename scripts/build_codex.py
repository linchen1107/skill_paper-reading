"""Generate self-contained Codex skills from skills/ and the shared assets."""
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / '.agents' / 'skills'
DESCRIPTIONS = {
    'reading': 'Read a supplied paper and its related cluster; make visual, interactive explanations for readers with no field background. Also use for Discussion review or code search.',
    'annotate': 'Create an English–Traditional Chinese paragraph-by-paragraph reading of one paper, with aligned explanations, figures and tables.',
    'presentation': 'Build real-data paper experiments with a runnable Python backend and interactive controls, using paper-reading output.',
}


def codex_text(text):
    for name in DESCRIPTIONS:
        text = text.replace(f'paper-reading:{name}', f'$paper-reading-{name}')
        text = text.replace(f'../{name}/', f'../paper-reading-{name}/')
    text = text.replace('`<plugin>` is the directory above `skills/`.',
                        '`<skill>` is the directory containing this SKILL.md.')
    text = text.replace('<plugin>/', '<skill>/')
    text = text.replace('`Documents/claude/paper-reading/<topic>/` under the current user\'s home',
                        '`<workspace>/paper-reading/<topic>/`')
    text = text.replace('../../../ARCHIVE/reading-sources-2026-09-30.md',
                        'https://github.com/linchen1107/skill_paper-reading/blob/main/ARCHIVE/reading-sources-2026-09-30.md')
    return text


def build(name):
    source = ROOT / 'skills' / name
    destination = TARGET / f'paper-reading-{name}'
    original = (source / 'SKILL.md').read_text(encoding='utf-8')
    match = re.match(r'\A---\n.*?\n---\n(.*)\Z', original, re.S)
    if not match:
        raise ValueError(f'Missing frontmatter: {name}')
    destination.mkdir(parents=True, exist_ok=True)
    header = f'---\nname: paper-reading-{name}\ndescription: {DESCRIPTIONS[name]}\n---\n\n'
    (destination / 'SKILL.md').write_text(header + codex_text(match.group(1)).lstrip('\n'), encoding='utf-8', newline='\n')
    for reference in (source / 'references').rglob('*.md'):
        target = destination / reference.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(codex_text(reference.read_text(encoding='utf-8')), encoding='utf-8', newline='\n')
    return destination


def copy_files(source, destination, names):
    destination.mkdir(parents=True, exist_ok=True)
    for name in names:
        shutil.copy2(source / name, destination / name)


def main():
    folders = {name: build(name) for name in DESCRIPTIONS}
    copy_files(ROOT / 'scripts', folders['reading'] / 'scripts',
               ('extract_figures.py', 'fetch_papers.py', 'check_page.py', 'selftest.js', 'serve.py'))
    copy_files(ROOT / 'templates', folders['reading'] / 'templates', ('page.html', 'widgets.js'))
    shutil.copytree(ROOT / 'templates' / 'katex', folders['reading'] / 'templates' / 'katex', dirs_exist_ok=True)
    copy_files(ROOT / 'scripts', folders['presentation'] / 'scripts', ('check_lab.py', 'check_page.py', 'serve.py'))
    shutil.copytree(ROOT / 'templates' / 'studio', folders['presentation'] / 'templates' / 'studio',
                    dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    copy_files(ROOT / 'scripts', folders['annotate'] / 'scripts', ('extract_figures.py',))
    print('Generated reading, annotate, and presentation Codex skills.')


if __name__ == '__main__':
    main()
