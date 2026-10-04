"""Rebuild all actual XDG-header consumers, preserving current205 ordered archive."""
import hashlib,json,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];R=ROOT.parent;O=R/'maximized-stack-v1/native-core-v2'
sys.path.insert(0,str(R/'elm-core-keyboardless-focus-v205'));from archive import archive_payloads
CORE=R/'elm-core-keyboardless-focus-v205/build-1791139089126747676'
AUDIT=ROOT/'qa/audit-1791154009981036333/report.json'
OUT=ROOT/('build-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
r={'passed':False,'nativeAcceptance':False,'installed':False,'commands':[],'scope':'Actual19-TU owning XDG header consumer rebuild,414 unchanged ordered payloads, current205/AQ155 linker closure; native provenance consumer qualification pending'}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def run(name,cmd,cwd=O/'build'):
 p=subprocess.run(cmd,cwd=cwd,capture_output=True,timeout=240);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'command':cmd,'cwd':str(cwd),'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr.decode(errors='replace')[-4000:];return p.stdout
def dep_paths(path):
 names=shlex.split(Path(path).read_text().replace('\\\n',' ').split(':',1)[1]);names=names[:next((i for i,n in enumerate(names) if n.endswith(':')),len(names))];return [(Path(p) if Path(p).is_absolute() else O/'build'/p).resolve() for p in names]
try:
 a=json.loads(AUDIT.read_text());d=json.loads((CORE/'report.json').read_text());assert a['passed'] and d['passed'] and len(a['affected'])==19
 archive=CORE/'libhyprland_lib.a';assert sha(archive)==d['archiveSHA256']==a['archive']['sha256'];r['ancestor']=a['archive'];r['consumerAudit']={'path':str(AUDIT),'sha256':sha(AUDIT)}
 for x in a['objects']:
  assert sha(x['source'])==x['sourceSHA256'] and sha(x['object'])==x['objectSHA256']
  if 'dependencyFile' in x:assert sha(x['dependencyFile'])==x['dependencySHA256']
  for p,w in x.get('dependencyInventory',{}).items():assert sha(p)==w,p
 r['inputs']={}
 for p in [Path(__file__),ROOT/'qa/compile.py',ROOT/'qa/consumer-audit.py',ROOT/'REQUIREMENTS.md',*sorted((ROOT/'candidate').rglob('*'))]:
  if p.is_file():
   rel=str(p.relative_to(ROOT));q=OUT/'inputs'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);q.chmod(0o444);r['inputs'][rel]=sha(q)
 tree=OUT/'owning-headers';r['owningHeaders']={};r['owningHeaderOrigins']={}
 for rel,w in d['owningHeaders'].items():
  p=CORE/'owning-headers'/rel;assert sha(p)==w;q=tree/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);q.chmod(0o600)
  if rel=='src/protocols/XDGShell.hpp':shutil.copy2(ROOT/'candidate'/rel,q)
  q.chmod(0o444);r['owningHeaders'][rel]=sha(q);r['owningHeaderOrigins'][rel]={'path':str(p),'sha256':w}
 assert sum(r['owningHeaders'][rel]!=w for rel,w in d['owningHeaders'].items())==1
 policy=OUT/'inputs/candidate';policy.mkdir(parents=True,exist_ok=True);r['retainedPolicyHeaders']={}
 for p,w in d['retainedPolicyHeaders'].items():
  assert sha(p)==w;q=policy/Path(p).name;shutil.copy2(p,q);q.chmod(0o444);r['retainedPolicyHeaders'][str(q)]=sha(q)
 r['dependencies']={};r['translationUnits']=[];objects=[]
 for x in a['affected']:
  source=Path(x['source']);rel='src/'+str(source).split('/src/',1)[1];q=tree/rel;q.parent.mkdir(parents=True,exist_ok=True)
  selected=ROOT/'candidate'/rel if (ROOT/'candidate'/rel).exists() else source
  if q.exists():q.chmod(0o600)
  shutil.copy2(selected,q);q.chmod(0o444);obj=OUT/x['member']['name'];dep=OUT/(obj.name+'.d');old=x['command'];cmd=[];i=0
  while i<len(old):
   arg=old[i]
   if arg=='-include':i+=2;continue
   if arg in ['-MF','-o','-c']:
    cmd.extend([arg,str({'-MF':dep,'-o':obj,'-c':q}[arg])]);i+=2;continue
   if arg.startswith('-I'):
    inc=arg[2:]
    if '/owning-headers' in inc:inc=str(tree)+inc.split('/owning-headers',1)[1]
    elif '/inputs/candidate' in inc:inc=str(policy)+inc.split('/inputs/candidate',1)[1]
    elif inc.startswith(str(O)) and not inc.startswith(str(O/'build')):inc=str(tree)+inc[len(str(O)):]
    arg='-I'+inc
   cmd.append(arg);i+=1
  cmd[1:1]=['-I'+str(policy),'-MD','-MF',str(dep)]
  run(Path(rel).stem+'-compile',cmd)
  ds={str(p):sha(p) for p in dep_paths(dep)};r['dependencies'].update(ds)
  assert not any(p.startswith(str(O/'src')+'/') or p.startswith('/usr/include/hyprland/') for p in ds)
  r['translationUnits'].append({'source':str(q),'sourceSHA256':sha(q),'origin':x,'selectedSource':str(selected),'selectedSourceSHA256':sha(selected),'command':cmd,'object':str(obj),'objectSHA256':sha(obj),'dependencies':ds});objects.append(obj)
 target=OUT/'libhyprland_lib.a';shutil.copy2(archive,target);run('archive',['/usr/bin/ar','r',str(target),*map(str,objects)])
 before=archive_payloads(archive);after=archive_payloads(target);changed={p.name:sha(p) for p in objects};assert len(before)==len(after)==433
 for b,c in zip(before,after):
  assert b['name']==c['name']
  if c['name'] in changed:assert c['sha256']==changed[c['name']]
  else:assert b==c
 r['rebuiltArchiveMembers']=changed;r['unchangedArchiveMembers']=414
 (OUT/'ancestor-archive-payloads.json').write_text(json.dumps(before,indent=2)+'\n');(OUT/'new-archive-payloads.json').write_text(json.dumps(after,indent=2)+'\n')
 original=list(next(x['command'] for x in d['commands'] if x['name']=='link'));cmd=[]
 for i,arg in enumerate(original):
  if i and original[i-1]=='-o':arg=str(OUT/'Hyprland')
  elif arg==str(archive):arg=str(target)
  elif arg.startswith('-Wl,--dependency-file='):arg='-Wl,--dependency-file='+str(OUT/'link.d')
  cmd.append(arg)
 for p,w in d['linkDependencies'].items():assert sha(p)==w,p
 run('link',cmd);r['linkDependencies']={str(p):sha(p) for p in dep_paths(OUT/'link.d')}
 for p,w in d['linkDependencies'].items():
  if p!=str(archive):assert r['linkDependencies'][p]==w,p
 symbols=run('symbols',['/usr/bin/nm','-D','--defined-only',str(OUT/'Hyprland')]);oldsyms=run('ancestor-symbols',['/usr/bin/nm','-D','--defined-only',d['binary']]);new={l.split()[-1] for l in symbols.splitlines()};previous={l.split()[-1] for l in oldsyms.splitlines()};assert previous<=new
 demangled=run('demangled-symbols',['/usr/bin/nm','-D','-C','--defined-only',str(OUT/'Hyprland')]);assert b'CXDGShellProtocol::currentActiveGrab() const' in demangled
 r['exportClosure']={'ancestor':len(previous),'retained':len(previous&new),'new':sorted(x.decode() for x in new-previous)}
 r['tools']={str(Path(shutil.which(n)).resolve()):sha(Path(shutil.which(n)).resolve()) for n in ['c++','ar','ld','nm','ldd']}
 output=run('ldd',['/usr/bin/ldd',str(OUT/'Hyprland')]);r['linkedLibraries']={}
 for line in output.decode().splitlines():
  for word in line.split():
   if word.startswith('/') and Path(word).is_file():r['linkedLibraries'][word]=sha(word)
 r['binary']=str(OUT/'Hyprland');r['binarySHA256']=sha(r['binary']);r['archiveSHA256']=sha(target);r['owningVersionHeaderSHA256']=d['owningVersionHeaderSHA256'];r['passed']=True
except Exception as e:r['error']=repr(e)
finally:
 (OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');print('PASS' if r['passed'] else r.get('error'))
if not r['passed']:raise SystemExit(1)
