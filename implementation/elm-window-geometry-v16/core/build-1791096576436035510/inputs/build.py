"""Replace exactly two owning TUs, preserving every other V7 archive member."""
import hashlib,json,resource,shlex,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[2]
OWNER=REPO/'implementation/maximized-stack-v1/native-core-v2'
PREVIOUS=REPO/'implementation/elm-native-buffer-size-v7/build-1791090562611157328'
WINDOW_ORIGIN=REPO/'implementation/elm-native-minimize-v13/build-1791057748334299238'
OUT=ROOT/('build-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def payloads(p):
 entries=[];longnames=b''
 with Path(p).open('rb') as f:
  assert f.read(8)==b'!<arch>\n'
  while True:
   header=f.read(60)
   if not header:break
   assert len(header)==60 and header[58:60]==b'`\n';name=header[:16].decode().strip();size=int(header[48:58]);remaining=size
   if name=='//':longnames=f.read(size);assert len(longnames)==size;remaining=0
   elif name not in ['/','/SYM64/']:
    if name.startswith('/'):
     start=int(name[1:]);end=longnames.index(b'/\n',start);name=longnames[start:end].decode()
    else:name=name.rstrip('/')
    h=hashlib.sha256()
    while remaining:
     part=f.read(min(remaining,1024*1024));assert part;remaining-=len(part);h.update(part)
    entries.append({'name':name,'size':size,'sha256':h.hexdigest()})
   if remaining:f.seek(remaining,1)
   if size%2:assert f.read(1)==b'\n'
 return entries
r={'passed':False,'installed':False,'nativeAcceptance':False,'scope':'Actual two-TU core compile/link and complete ordered ancestor archive preservation; no GUI/window roundtrip acceptance','commands':[]}
def run(name,command,cwd=None):
 p=subprocess.run(list(map(str,command)),cwd=cwd,capture_output=True,timeout=240)
 (OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr)
 r['commands'].append({'name':name,'command':list(map(str,command)),'cwd':str(cwd) if cwd else None,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr.decode(errors='replace')[-5000:]
 return p.stdout
try:
 previous=json.loads((PREVIOUS/'report.json').read_text());assert previous['passed'] and sha(previous['binary'])==previous['binarySHA256']
 archive=PREVIOUS/'libhyprland_lib.a';archiveHash=sha(archive);before=payloads(archive)
 oldWindow=run('ancestor-window-object',['/usr/bin/ar','p',str(archive),'Window.cpp.o']);assert hashlib.sha256(oldWindow).hexdigest()==sha(WINDOW_ORIGIN/'Window.cpp.o')
 oldController=run('ancestor-controller-object',['/usr/bin/ar','p',str(archive),'FullscreenController.cpp.o'])
 ownerObj=OWNER/'build/CMakeFiles/hyprland_lib.dir/src/managers/fullscreen/FullscreenController.cpp.o';assert hashlib.sha256(oldController).hexdigest()==sha(ownerObj)
 r['ancestor']={'report':str(PREVIOUS/'report.json'),'reportSHA256':sha(PREVIOUS/'report.json'),'binary':previous['binary'],'binarySHA256':previous['binarySHA256'],'archive':str(archive),'archiveSHA256':archiveHash,'windowSource':str(WINDOW_ORIGIN/'inputs/src/desktop/view/Window.cpp'),'windowSourceSHA256':sha(WINDOW_ORIGIN/'inputs/src/desktop/view/Window.cpp'),'windowObjectSHA256':hashlib.sha256(oldWindow).hexdigest(),'controllerSource':str(OWNER/'src/managers/fullscreen/FullscreenController.cpp'),'controllerSourceSHA256':sha(OWNER/'src/managers/fullscreen/FullscreenController.cpp'),'controllerObjectSHA256':sha(ownerObj)}
 rels=['src/desktop/view/Window.cpp','src/managers/fullscreen/FullscreenController.cpp']
 sources=[ROOT/'build.py',ROOT/'qa/callback-test.py',*[ROOT/'candidate'/rel for rel in rels]]
 r['inputs']={str(p.relative_to(ROOT)):sha(p) for p in sources}
 for p in sources:
  dest=OUT/'inputs'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);dest.chmod(0o444)
 for name in ['WindowPolicy.hpp','SceneModal.hpp','SceneTrace.hpp']:shutil.copy2(PREVIOUS/'inputs/candidate'/name,OUT/'inputs/candidate'/name)
 r['retainedPolicyHeaders']={str(p):sha(p) for p in (OUT/'inputs/candidate').glob('*.hpp')}
 db=OWNER/'build/compile_commands.json';commands=json.loads(db.read_text());r['compileDatabaseSHA256']=sha(db);r['dependencies']={};objects=[]
 for rel in rels:
  row=next(c for c in commands if c['file']==str(OWNER/rel));command=shlex.split(row['command']);obj=OUT/(Path(rel).name+'.o');dep=OUT/(Path(rel).name+'.d');source=OUT/'inputs/candidate'/rel
  for i,arg in enumerate(command):
   if i and command[i-1]=='-c':command[i]=str(source)
   elif i and command[i-1]=='-o':command[i]=str(obj)
   elif i and command[i-1] in ['-MF','-MT']:command[i]=str(dep if command[i-1]=='-MF' else obj)
  if '-MF' not in command:command[1:1]=['-MMD','-MF',str(dep)]
  command[1:1]=['-I'+str(OUT/'inputs/candidate'),'-I'+str((OWNER/rel).parent)]
  run(Path(rel).stem+'-compile',command,OWNER/'build')
  deps=shlex.split(dep.read_text().replace(chr(92)+chr(10),' ').split(':',1)[1])
  for name in deps:
   p=Path(name);p=p if p.is_absolute() else OWNER/'build'/p;p=p.resolve();r['dependencies'][str(p)]=sha(p)
  objects.append(obj)
 assert not any(p.startswith('/usr/include/hyprland') for p in r['dependencies'])
 target=OUT/'libhyprland_lib.a';shutil.copy2(archive,target);run('archive',['/usr/bin/ar','r',str(target),*map(str,objects)])
 after=payloads(target);assert len(before)==len(after)==433
 changed={obj.name:sha(obj) for obj in objects};seen=set()
 for b,a in zip(before,after):
  assert b['name']==a['name']
  if a['name'] in changed:assert a['sha256']==changed[a['name']];seen.add(a['name'])
  else:assert b==a,b['name']
 assert seen==set(changed)
 (OUT/'ancestor-archive-payloads.json').write_text(json.dumps(before,indent=2)+'\n');(OUT/'new-archive-payloads.json').write_text(json.dumps(after,indent=2)+'\n')
 link=list(previous['commands'][-1]['command'])
 for i,arg in enumerate(link):
  if i and link[i-1]=='-o':link[i]=str(OUT/'Hyprland')
  elif arg==str(archive):link[i]=str(target)
  elif arg.startswith('-Wl,--dependency-file='):link[i]='-Wl,--dependency-file='+str(OUT/'link.d')
 run('link',link)
 assert sha(archive)==archiveHash and sha(previous['binary'])==previous['binarySHA256']
 for rel,digest in r['inputs'].items():assert sha(ROOT/rel)==digest,rel
 for path,digest in r['dependencies'].items():assert sha(path)==digest,path
 r.update(passed=True,binary=str(OUT/'Hyprland'),binarySHA256=sha(OUT/'Hyprland'),archiveSHA256=sha(target),unchangedArchiveMembers=431,changedArchiveMembers=changed,owningVersionHeaderSHA256=sha(OWNER/'src/version.h'))
except Exception as error:r['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}),flush=True);raise SystemExit(not r['passed'])
