"""Actual owning XDG accessor compile; no complete archive/native claim."""
import hashlib,json,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
CORE=REPO/'implementation/elm-core-keyboardless-focus-v205/build-1791139089126747676'
SOURCE=REPO/'implementation/elm-geometry-monitor-core-v73/core/build-1791106255338249967'
OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2'
OUT=ROOT/'qa'/('compile-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
r={'passed':False,'nativeAcceptance':False,'fullArchiveClosure':False,'commands':[]}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
try:
 d=json.loads((CORE/'report.json').read_text());s=json.loads((SOURCE/'report.json').read_text());assert d['passed'] and s['passed']
 r['ancestor']={'report':str(CORE/'report.json'),'sha256':sha(CORE/'report.json'),'archiveSHA256':d['archiveSHA256']}
 r['owningHeaders']={};tree=OUT/'owning-headers'
 for rel,want in d['owningHeaders'].items():
  p=CORE/'owning-headers'/rel;assert sha(p)==want
  q=tree/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);q.chmod(0o600)
  if rel=='src/protocols/XDGShell.hpp':shutil.copy2(ROOT/'candidate'/rel,q)
  q.chmod(0o444);r['owningHeaders'][rel]=sha(q)
 assert len(r['owningHeaders'])==694
 for rel in ['src/protocols/XDGShell.cpp']:
  q=tree/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/'candidate'/rel,q);q.chmod(0o444)
 policy=OUT/'inputs/candidate';policy.mkdir(parents=True)
 for p,want in d['retainedPolicyHeaders'].items():
  assert sha(p)==want;q=policy/Path(p).name;shutil.copy2(p,q);q.chmod(0o444)
 r['inputs']={}
 for p in [Path(__file__),ROOT/'REQUIREMENTS.md',*sorted((ROOT/'candidate').rglob('*'))]:
  if not p.is_file():continue
  rel=str(p.relative_to(ROOT));q=OUT/'inputs'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);q.chmod(0o444);r['inputs'][rel]=sha(q)
 original=SOURCE/'owning-headers/src/protocols/XDGShell.cpp';base=original.read_text();candidate=(ROOT/'candidate/src/protocols/XDGShell.cpp').read_text();assert candidate.startswith(base)
 r['originalSource']={'path':str(original),'sha256':sha(original)}
 old=list(next(x['command'] for x in s['commands'] if x['name']=='XDGShell-compile'));cmd=[]
 for i,a in enumerate(old):
  if a.startswith('-I'+str(SOURCE/'owning-headers')):a=a.replace(str(SOURCE/'owning-headers'),str(tree),1)
  elif a=='-I'+str(SOURCE/'inputs/candidate'):a='-I'+str(policy)
  elif i and old[i-1]=='-MF':a=str(OUT/'xdg.d')
  elif i and old[i-1]=='-o':a=str(OUT/'XDGShell.cpp.o')
  elif i and old[i-1]=='-c':a=str(tree/'src/protocols/XDGShell.cpp')
  cmd.append(a)
 p=subprocess.run(cmd,cwd=OWNER/'build',capture_output=True,timeout=240);(OUT/'compile.stdout').write_bytes(p.stdout);(OUT/'compile.stderr').write_bytes(p.stderr);r['commands'].append({'command':cmd,'cwd':str(OWNER/'build'),'exitCode':p.returncode});assert p.returncode==0,p.stderr.decode(errors='replace')[-5000:]
 r['dependencies']={}
 for n in shlex.split((OUT/'xdg.d').read_text().replace('\\\n',' ').split(':',1)[1]):
  p=Path(n);p=(p if p.is_absolute() else OWNER/'build'/p).resolve();r['dependencies'][str(p)]=sha(p)
 assert not any(p.startswith(str(OWNER/'src')+'/') or p.startswith('/usr/include/hyprland/') for p in r['dependencies'])
 r['tools']={n:sha(n) for n in ['/usr/bin/c++','/usr/bin/nm']}
 p=subprocess.run(['/usr/bin/nm','-C',str(OUT/'XDGShell.cpp.o')],capture_output=True,timeout=10);(OUT/'symbols.stdout').write_bytes(p.stdout);assert p.returncode==0 and b'CXDGShellProtocol::currentActiveGrab() const' in p.stdout
 r['object']=str(OUT/'XDGShell.cpp.o');r['objectSHA256']=sha(r['object']);r['passed']=True
except Exception as e:r['error']=repr(e)
finally:
 (OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json',flush=True);print('PASS' if r['passed'] else r.get('error'),flush=True)
if not r['passed']:raise SystemExit(1)
