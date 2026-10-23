"""Generate the Game Center cards without touching game files (Python stdlib only)."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import argparse
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
START, END = '<!-- GAMES:START -->', '<!-- GAMES:END -->'

def render(root):
    games = sorted((p for p in root.rglob('*') if p.is_file()
        and p.suffix.lower() in {'.html', '.htm'}
        and p != root / 'index.html'
        and not any(part.startswith('.') or part in {'node_modules', 'scripts', '_site'}
                    for part in p.relative_to(root).parts)),
        key=lambda p: unicodedata.normalize('NFC', p.relative_to(root).as_posix()).casefold())
    cards = []
    for i, path in enumerate(games):
        name = unicodedata.normalize('NFC', path.stem).replace('_', ' ')
        relative = path.relative_to(root).as_posix()
        cards.append(f'<a class="game" style="--hue:{(i * 47 + 165) % 360}" href="{quote(relative, safe="/")}">'
            f'<span class="art" aria-hidden="true"><span>{escape(name[:2].upper())}</span></span>'
            f'<span class="game-info"><small>BROWSER GAME · {i+1:02d}</small>'
            f'<h3>{escape(name)}</h3><span class="play">Jetzt spielen <span aria-hidden="true">↗</span></span></span></a>')
    return '\n'.join(cards)

def build(root=ROOT, check=False):
    index = root / 'index.html'
    source = index.read_text(encoding='utf-8')
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError('index.html needs exactly one pair of catalog markers')
    before, rest = source.split(START)
    _, after = rest.split(END)
    updated = before + START + '\n' + render(root) + '\n' + END + after
    if check:
        if source != updated:
            raise SystemExit('Catalog is out of date. Run python3 scripts/build_catalog.py')
    else:
        index.write_text(updated, encoding='utf-8')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    build(check=parser.parse_args().check)
