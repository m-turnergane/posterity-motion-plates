import json, sys
from pathlib import Path
D = Path(__file__).parent
al = json.load(open(D / sys.argv[1]))
LINES = [l.strip() for l in (D.parent / 'raw/script-vo-v3.txt').read_text().splitlines() if l.strip()]
DISP = [(w, li + 1) for li, l in enumerate(LINES) for w in l.split()]
ch, st, en = al['characters'], al['character_start_times_seconds'], al['character_end_times_seconds']
text = ''.join(ch); b0 = text.find('<break'); b1 = text.find('/>', b0) + 2
toks = []; cur = None
for i, c in enumerate(ch):
    if b0 <= i < b1:
        if cur: toks.append(cur); cur = None
        continue
    if c.isspace():
        if cur: toks.append(cur); cur = None
    else:
        if cur is None: cur = dict(word='', start=st[i], end=en[i])
        cur['word'] += c; cur['end'] = en[i]
if cur: toks.append(cur)
assert [t['word'] for t in toks] == [w for w, _ in DISP], 'token mismatch'
for t, (_, li) in zip(toks, DISP): t['line'] = li
json.dump(dict(words=toks), open(D / sys.argv[2], 'w'), indent=0)
for a, b in zip(toks, toks[1:]):
    g = b['start'] - a['end']
    if g > 0.25: print(f"{a['end']:7.2f} gap {g:.2f}  L{a['line']}->{b['line']}  {a['word']} | {b['word']}")
print('first', toks[0]['start'], 'last', toks[-1]['end'])
