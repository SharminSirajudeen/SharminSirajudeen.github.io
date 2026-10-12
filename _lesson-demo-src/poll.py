import json,time,urllib.request
key=open('.key').read().strip(); jid=json.load(open('job.json'))['job_id']; H={'api-subscription-key':key}
get=lambda p: json.load(urllib.request.urlopen(urllib.request.Request(f'https://api.sarvam.ai/dubbing/jobs/{jid}/{p}',headers=H),timeout=60))['data']
last=None
for _ in range(120):
    d=get('live-status'); now=(d['status'],d.get('current_step_label'),d.get('progress'))
    if now!=last: print(*now, flush=True); last=now
    if d['status'] in ('completed','partial_failure','failed','deleted'):
        if d.get('error_message'): print('error:',d['error_message'])
        break
    time.sleep(10)
for _ in range(60):
    ex=get('export-status')['exports']
    if ex and all(e['status'] in ('completed','failed') for e in ex): break
    time.sleep(10)
for e in ex:
    f=f"{e['target_language'][:2]}.{ {'video':'mp4','audio':'audio','srt':'srt'}[e['export_type']] }"
    if e['status']=='completed':
        with urllib.request.urlopen(e['download_url'],timeout=300) as r: data=r.read()
        if e['export_type']=='audio': f=f"{e['target_language'][:2]}-audio.{'wav' if data[:4]==b'RIFF' else 'mp3' if data[:3]==b'ID3' or data[:2]==b'\xff\xfb' else 'bin'}"
        open(f,'wb').write(data); print('saved',f,len(data))
    else: print('export',e['target_language'],e['export_type'],e['status'])
