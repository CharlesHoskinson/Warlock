from pathlib import Path
import subprocess,re,json,time,sys,os
BASE=Path(__file__).resolve().parent
listing=subprocess.check_output(['qs','-p',str(BASE/'qa-app'),'list','--any-display'],text=True)
pids=[re.search(r'Process ID: (\d+)',block).group(1) for block in listing.split('Instance ')[1:] if 'Display connection: unk' in block];assert len(pids)==1,listing
pid=pids[0]
def ipc(fn,*args):
 return subprocess.check_output(['qs','ipc','--pid',pid,'call','files-responsive-qa',fn,*map(str,args)],text=True).strip()
def probe():return json.loads(ipc('probe'))
def wait_ready(w,h):
 for _ in range(80):
  p=probe()
  if p['width']==w and p['height']==h and not p['loading']:return p
  time.sleep(.05)
 raise AssertionError((w,h,p))
def overlap(a,b):return min(a['x']+a['w'],b['x']+b['w'])-max(a['x'],b['x'])>.1 and min(a['y']+a['h'],b['y']+b['h'])-max(a['y'],b['y'])>.1
results=[];fail=[]
shots=BASE/'offscreen-shots';shots.mkdir(exist_ok=True)
for w,h in [(330,320),(487,320),(500,320),(533,320),(600,320),(800,320),(900,320),(1000,320),(1320,800),(487,487),(533,1000),(800,1000)]:
 ipc('resize',w,h);wait_ready(w,h);time.sleep(.25)
 for scenario in ['home','folder-list','folder-grid','details','sidebar','menu','prompt','long-prompt','preview','path']:
  ipc('scenario',scenario);time.sleep(.3);p=wait_ready(w,h);r=p['rects'];bad=[]
  if p['negative']:bad.append('negative visible item: '+str(p['negative']))
  for key in ['nav','tools','extraTools','filter','path','main','status']:
   b=r[key]
   if not (b['w']>0 and b['h']>0 and b['x']>=-.01 and b['y']>=-.01 and b['x']+b['w']<=w+.01 and b['y']+b['h']<=h+.01):bad.append('unbounded '+key+' '+str(b))
  if min(r['filter']['w'],r['path']['w'])<100:bad.append('editable fields below100')
  controls=['nav','tools','extraTools','filter','path']
  for i,a in enumerate(controls):
   for b in controls[i+1:]:
    if overlap(r[a],r[b]):bad.append('toolbar overlap '+a+' '+b)
  if scenario!='home' and (r['files']['w']<330-.1 or r['files']['h']<100):bad.append('file area too small '+str(r['files']))
  if scenario=='folder-grid' and (p['cellWidth']<=0 or p['fileColumns']<1):bad.append('invalid grid cell')
  if scenario=='folder-grid' and p['thumbHeight']+52>p['named']['FileArea.gridList']['h']+.1:bad.append('grid filename/meta escapes short viewport')
  if scenario=='details' and not p['detailDocked'] and r['files']['w']!=r['main']['w']:bad.append('overlay steals file width')
  if scenario=='folder-list' and not p['detailDocked'] and p['detailVisible']:bad.append('details appears automatically compact')
  for key in ['Prompt.card','ContextMenu.card']:
   if key in p['named']:
    b=p['named'][key]
    if min(b['x'],b['y'])<-.01 or b['x']+b['w']>w+.01 or b['y']+b['h']>h+.01:bad.append('modal escapes '+key+str(b))
  p.update(scenario=scenario,errors=bad);results.append(p)
  if bad:fail.append({'size':[w,h],'scenario':scenario,'errors':bad})
  if (w,h) in [(330,320),(500,320),(800,320),(1320,800)] and scenario in ['home','folder-list','details','menu','prompt','preview']:
   ipc('shot','explorer',shots/f'{w}x{h}-{scenario}.png')
(BASE/'offscreen-report.json').write_text(json.dumps({'cases':len(results),'failures':fail,'results':results},indent=2))
print(json.dumps({'cases':len(results),'failedCases':len(fail),'failures':fail[:16]},indent=2));sys.exit(bool(fail))
