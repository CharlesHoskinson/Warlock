import hashlib,json,resource,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];PRIOR=ROOT.parent/'elm-nested-input-status-v30'
OUT=ROOT/'qa'/('replay-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sources={'original':PRIOR/'candidate/src/backend/Wayland.cpp'}
if (ROOT/'candidate/src/backend/Wayland.cpp').exists():sources['candidate']=ROOT/'candidate/src/backend/Wayland.cpp'
r={'passed':False,'nativeAcceptance':False,'scope':'Actual initSeat body compiled with real Hyprutils shared/weak ownership and typed protocol/event fixtures; no native transport or whole compositor refinement','commands':[],'inputs':{str(p):sha(p) for p in [Path(__file__),ROOT/'qa/template.cpp',*sources.values()]}}
def run(name,cmd,expected):
 p=subprocess.run(cmd,capture_output=True,timeout=90);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True);assert p.returncode==expected,p.stderr.decode(errors='replace');return p
try:
 template=(ROOT/'qa/template.cpp').read_text();extracted={}
 for name,path in sources.items():
  text=path.read_text();start=text.index('void Aquamarine::CWaylandBackend::initSeat() {');end=text.index('\nvoid Aquamarine::CWaylandBackend::initShell()',start);body=text[start:end].replace('Aquamarine::CWaylandBackend::initSeat','CWaylandBackend::initSeat');extracted[name]=body
  cpp=OUT/(name+'.cpp');cpp.write_text(template.replace('@@BODY@@',body));exe=OUT/name
  run(name+'-compile',['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror','-Wno-unused-parameter',str(cpp),'-lhyprutils','-o',str(exe)],0)
  p=run(name+'-run',[str(exe)],1 if name=='original' else 0)
  if name=='original':assert b'FAIL retired pointer not published' in p.stderr
  else:r['candidateChecks']=int(p.stdout.decode().split('checks: ')[1])
 r.update(passed=True,originalViolation='retired pointer not published',candidateValidated='candidate' in sources)
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
