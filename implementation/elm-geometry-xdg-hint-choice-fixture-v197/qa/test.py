"""Protected CPU parsing/map/callback tests; never opens a Wayland connection."""
import hashlib,json,os,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
selected=ROOT/'qa/client-build-1791129575587800319/report.json'
b=json.loads(selected.read_text());assert b['passed']
for p,d in b['inputs'].items():assert sha(p)==d,p
for p,d in b['dependencies'].items():assert sha(p)==d,p
for p,d in b['linkedLibraries'].items():assert sha(p)==d,p
binary=Path(b['client']);assert sha(binary)==b['clientSHA256']
out=ROOT/'qa'/('test-'+str(time.time_ns()));out.mkdir(mode=0o700)
inputs=out/'inputs';inputs.mkdir(mode=0o700)
for p in [ROOT/'native/xdg-origin-client.c',ROOT/'qa/helper-test.c',Path(__file__),ROOT/'REQUIREMENTS.md']:
 shutil.copyfile(p,inputs/p.name)
gen=selected.parent/'generated'
r={'passed':False,'scope':'CPU only: actual fixture helpers/callbacks and CLI; no compositor/GTK/presentation proof','qaScope':scope,'buildReport':str(selected),'buildReportSHA256':sha(selected),'commands':[],'runs':{},'cli':[]}
def run(name,args,expected=0):
 v=subprocess.run(list(map(str,args)),cwd=out,capture_output=True,text=True,timeout=30,env={**os.environ,'WAYLAND_DISPLAY':'elm-no-display-cpu-only'})
 (out/(name+'.stdout')).write_text(v.stdout);(out/(name+'.stderr')).write_text(v.stderr)
 r['commands'].append({'name':name,'command':list(map(str,args)),'exitCode':v.returncode})
 assert v.returncode==expected,(name,v.returncode,v.stderr)
 return v
try:
 cc='/usr/bin/cc';flags=['-std=c11','-O2','-Wall','-Wextra','-Werror','-Wl,-z,defs','-Wl,--wrap=wl_display_connect','-I'+str(inputs),'-I'+str(gen)]
 libs=shlex.split(subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','wayland-client'],text=True))
 for name,mutation in [('actual',None),('unsafe-buffer-no-scale',('*bw=*lw*p->scale; *bh=*lh*p->scale;','*bw=*lw; *bh=*lh;')),('unsafe-origin-missing',('int x=lx-p->x,y=ly-p->y;','(void)p;int x=lx,y=ly;')),('unsafe-foreign-recipient',('c->pointer_owned=s==c->surface;','(void)s;c->pointer_owned=true;')),('unsafe-MAX-clamp',('if(exact && proposed>0 &&','if(false && exact && proposed>0 &&')),('unsafe-ordinary-no-max',('upper=maximum>0 && maximum<4096?maximum:4096','upper=4096+maximum*0'))]:
  target=out/name;target.mkdir();source=target/'xdg-origin-client.c';text=(inputs/'xdg-origin-client.c').read_text()
  if mutation:assert text.count(mutation[0])==1;text=text.replace(*mutation)
  source.write_text(text);shutil.copyfile(inputs/'helper-test.c',target/'helper-test.c')
  dep=target/'helper.d';ex=target/'helper'
  run(name+'-build',[cc,*flags,'-I'+str(target),'-MD','-MF',dep,target/'helper-test.c',gen/'xdg-shell-protocol.c',*libs,'-o',ex])
  # Local quoted include searches helper's own directory first, so mutation drives actual fixture code.
  v=run(name,[ex],0 if mutation is None else 1)
  tail=json.loads(v.stdout.splitlines()[-1]);assert tail['connections']==0
  r['runs'][name]={**tail,'exitCode':v.returncode,'sourceSHA256':sha(source),'binarySHA256':sha(ex)}
 cases=[([],0),(['--origin-x','0','--origin-y','0','--right-pad','0','--bottom-pad','0'],0),(['--scale','2'],0),(['--origin-x','256','--origin-y','256'],0),(['--min-width','108','--min-height','42','--max-height','42','--height','42'],0),(['--max-width','1'],64),(['--scale','0'],64),(['--scale','3'],64),(['--origin-x','-1'],64),(['--origin-x','257'],64),(['--origin-x','01'],64),(['--origin-x','+1'],64),(['--origin-x',' 1'],64),(['--origin-x','1.0'],64),(['--origin-x','99999999999999999'],64),(['--width','0'],64),(['--width','31'],64),(['--width','4097'],64),(['--width','4096','--height','4096','--scale','2'],64),(['--scale','1','--scale','2'],64),(['--max-width','7','--min-width','8'],64),(['--origin-x'],64),(['--unknown','1'],64),(['--validate'],64),(['--min-height','42','--max-height','41'],64)]
 for i,(args,status) in enumerate(cases):
  v=run('cli-'+str(i),[binary,'--validate',*args],status);row={'arguments':args,'exitCode':v.returncode}
  if status==0:row['profile']=json.loads(v.stdout);assert row['profile']['valid']
  r['cli'].append(row)
 assert r['runs']['actual']['failures']==0 and all(r['runs'][n]['failures']>0 for n in r['runs'] if n!='actual')
 r['passed']=True
except Exception as e:r['error']=repr(e)
r['sourceInputs']={str(p):sha(p) for p in inputs.iterdir()}
r['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(out/'report.json'),'runs':r['runs'],'cliCases':len(r['cli']),'error':r.get('error')}))
raise SystemExit(0 if r['passed'] else 1)
