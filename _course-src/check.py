"""Every translation has the English structure, the same answers and minutes, and the same numbers in every field."""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
NUM = re.compile(r'\d+(?:,\d+)*(?:\.\d+)?')
ACRO = ['CAC', 'LTV', 'CPA', 'CPC', 'ROAS', 'RFM', 'A/B']
# may stay in English: the letters of RFM are English words
KEEP = {f'.modules[4].quiz[1].options[{i}]' for i in range(3)}
QUOTE = 'free, specific, informed, unconditional and unambiguous with a clear affirmative action'
en = json.loads((HERE / 'en.json').read_text())
fails = []


def walk(a, b, path):
    if isinstance(a, dict):
        if set(a) != set(b):
            fails.append(f'{path}: keys differ')
            return
        for k in a:
            walk(a[k], b[k], f'{path}.{k}')
    elif isinstance(a, list):
        if not isinstance(b, list) or len(a) != len(b):
            fails.append(f'{path}: list length differs')
            return
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f'{path}[{i}]')
    elif isinstance(a, int):
        if a != b:
            fails.append(f'{path}: {a} != {b}')
    elif path not in ('.lang', '.langName'):
        if sorted(NUM.findall(a)) != sorted(NUM.findall(b)):
            fails.append(f'{path}: numbers {sorted(NUM.findall(a))} != {sorted(NUM.findall(b))}')
        prose = re.search(r'[A-Za-z]{3}', a) and not any(path.endswith(p) for p in KEEP)
        if b.strip() == '' or (a == b and prose):
            fails.append(f'{path}: empty or untranslated')
        fails.extend(f'{path}: acronym {x} dropped' for x in ACRO if x in a and x not in b)


codes = sys.argv[1:] or ['hi', 'ta', 'te', 'ml']
for code in codes:
    d = json.loads((HERE / f'{code}.json').read_text())
    n = len(fails)
    walk(en, d, f'{code}')
    if d['lang'] != code:
        fails.append(f'{code}: lang is {d["lang"]}')
    if QUOTE not in json.dumps(d, ensure_ascii=False):
        fails.append(f'{code}: the exact Section 6(1) phrase is missing')
    print(f'{code}: {"ok" if len(fails) == n else f"{len(fails) - n} problem(s)"}')
for f in fails:
    print('FAIL', f)
sys.exit(1 if fails else 0)
