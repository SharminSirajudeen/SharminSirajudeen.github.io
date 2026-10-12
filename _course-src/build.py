"""Build digital-marketing-course/index.html from the language files. One self-contained page; no outside requests."""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
LANGS = ['en', 'hi', 'ta', 'te', 'ml']
OUT = HERE.parent / 'digital-marketing-course' / 'index.html'

data = {code: json.loads((HERE / f'{code}.json').read_text()) for code in LANGS}
page = (HERE / 'page.html').read_text()
blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
assert page.count('/*DATA*/null') == 1, page.count('/*DATA*/null')
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(page.replace('/*DATA*/null', blob))
print(f'built {OUT.relative_to(HERE.parent)}: {len(LANGS)} languages, {OUT.stat().st_size:,} bytes')
