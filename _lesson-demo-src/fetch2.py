import json,time,urllib.request
key=open('.key').read().strip(); jid=json.load(open('job.json'))['job_id']; H={'api-subscription-key':key}
get=lambda p: json.load(urllib.request.urlopen(urllib.request.Request(f'https://api.sarvam.ai/dubbing/jobs/{jid}/{p}',headers=H),timeout=60))['data']
for i in range(60):
    ex=get('export-status')['exports']
    if i%6==0: print(i, sorted((e['target_language'],e['export_type'],e['status']) for e in ex), flush=True)
    if len(ex)==9 and all(e['status'] in ('completed','failed') for e in ex): break
    time.sleep(10)
for e in ex:
    if e['status']!='completed' or e['target_language']=='ta-IN': continue
    with urllib.request.urlopen(e['download_url'],timeout=300) as r: data=r.read()
    l=e['target_language'][:2]; f={'video':f'{l}.mp4','srt':f'{l}.srt','audio':f'{l}-audio.wav'}[e['export_type']]
    open(f,'wb').write(data); print('saved',f,len(data))
