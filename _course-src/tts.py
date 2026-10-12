"""Narrate every lesson in every language: one MP3 per lesson, served from this site (no outside request at play time).
Needs SARVAM_API_KEY. Sarvam Bulbul v3, max 2,500 characters a request, so a lesson is sent in blocks and joined."""
import base64
import json
import os
import pathlib
import sys
import urllib.request

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / 'digital-marketing-course' / 'audio'
LANGS = {'en': 'en-IN', 'hi': 'hi-IN', 'ta': 'ta-IN', 'te': 'te-IN', 'ml': 'ml-IN'}
LIMIT = 2500


def blocks(m):
    parts = [m['title'], m['intro'], *m['points'], m['example'], m['mistake'], *m['takeaways']]
    out, cur = [], ''
    for p in parts:
        if len(p) > LIMIT:
            sys.exit(f'a paragraph is over {LIMIT} characters: {p[:60]}')
        if len(cur) + len(p) + 1 > LIMIT:
            out.append(cur)
            cur = ''
        cur = (cur + '\n' + p).strip()
    return out + [cur]


def speak(text, code, key):
    body = json.dumps({'text': text, 'language_code': code, 'model': 'bulbul:v3', 'output_audio_codec': 'mp3'}).encode()
    req = urllib.request.Request('https://api.sarvam.ai/text-to-speech', body,
                                 {'api-subscription-key': key, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return b''.join(base64.b64decode(a) for a in json.load(r)['audios'])


key = os.environ.get('SARVAM_API_KEY') or sys.exit('SARVAM_API_KEY is not set')
OUT.mkdir(exist_ok=True)
for lang, code in LANGS.items():
    for i, m in enumerate(json.loads((HERE / f'{lang}.json').read_text())['modules'], 1):
        path = OUT / f'{lang}-{i}.mp3'
        if not path.exists():
            path.write_bytes(b''.join(speak(t, code, key) for t in blocks(m)))
        print(f'{path.name}: {path.stat().st_size:,} bytes')
