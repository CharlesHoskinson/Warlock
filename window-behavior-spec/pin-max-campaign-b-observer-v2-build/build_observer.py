"""Compile-only exact reviewed observer. Never run/load compositor or plugin."""
from pathlib import Path
import hashlib,json,os,shlex,shutil,subprocess,time
B=Path(__file__).resolve().parent
C=Path('/home/hoskinson/window-behavior-spec/pin-maximized-core-v3-hit-fallback')
PKGS=['hyprland','lua','libeis-1.0','libinput','xkbcommon','json-c']
def run(args):return subprocess.check_output(args,text=True).strip()
def file(p):
 p=Path(p).absolute();s=p.stat();return dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mode=oct(s.st_mode&0o7777),size=s.st_size,mtimeNs=s.st_mtime_ns,resolved=str(p.resolve()),literalLink=os.readlink(p)if p.is_symlink()else None)
def save(name,value):
 p=B/'build'/name
 with p.open('x')as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
 p.chmod(0o600)
def execute(args,name):
 log=B/'build'/(name+'.log');started=time.monotonic_ns()
 with log.open('xb')as f:r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT);f.flush();os.fsync(f.fileno())
 log.chmod(0o600);return dict(command=args,exitCode=r.returncode,startedNs=started,finishedNs=time.monotonic_ns(),log=file(log))
source=B/'src/campaign_b_observer.cpp';parent=B/'retained-reviewed-draft/campaign_b_observer.cpp'
assert source.read_bytes()==(B/'retained-first-build/proposed-source-correction-v2/campaign_b_observer.cpp').read_bytes()
rawFlags=shlex.split(run(['/usr/bin/pkg-config','--cflags',*PKGS]));flags=[f for f in rawFlags if not f.startswith('-I/usr/include/hyprland')];libs=shlex.split(run(['/usr/bin/pkg-config','--libs','json-c']))
selected=['-isystem',str(C/'core/src'),'-isystem',str(C/'core/protocols'),'-isystem',str(C/'build-core-make'),'-isystem',str(C/'build-inputs/glaze-src/include')]
compileArgs=['/usr/bin/c++','-std=c++26','-fPIC','-O2','-Wall','-Wextra','-Werror','-MD','-MF',str(B/'build/observer.d'),*selected,*flags,'-c',str(source),'-o',str(B/'build/observer.o')]
linkArgs=['/usr/bin/c++','-shared',str(B/'build/observer.o'),'-Wl,--build-id=sha1','-Wl,-Map='+str(B/'build/observer.map'),'-Wl,-t','-o',str(B/'build/libpin-campaign-b-observer.so'),*libs]
tools={}
for name in ['c++','g++','as','ld','pkg-config','readelf','nm','ldd']:
 p=shutil.which(name);assert p;tools[p]=file(p)
for name in ['cc1plus','collect2']:
 p=run(['/usr/bin/c++','-print-prog-name='+name]);tools[p]=file(p)
pc={}
for name in PKGS:
 d=Path(run(['/usr/bin/pkg-config','--variable=pcfiledir',name]));p=d/(name+'.pc')
 assert p.is_file(),p;pc[str(p)]=file(p)
save('build-before.json',dict(source=file(source),tools=tools,pkgConfig=pc,flags=flags,libs=libs,compilerVersion=run(['/usr/bin/c++','--version']),core=file(C/'build-core-make/Hyprland'),coreReady=file(C/'SOURCE_READY.json'),coreInputs=file(C/'SOURCE_READY_INPUTS.json'),nativeLoaded=False,coreExecuted=False))
comp=execute(compileArgs,'compile');save('compile-result.json',comp)
if comp['exitCode']:raise SystemExit(comp['exitCode'])
link=execute(linkArgs,'link');save('link-result.json',link)
if link['exitCode']:raise SystemExit(link['exitCode'])
# Actual compiler dependency list, including literal aliases and resolved owning headers.
raw=(B/'build/observer.d').read_text().replace('\\\n',' ');depPaths=shlex.split(raw.split(':',1)[1]);deps={str(Path(p).absolute()):file(p)for p in depPaths}
fixed=json.loads((C/'SOURCE_READY_INPUTS.json').read_text());matched={}
for p,row in deps.items():
 assert not p.startswith('/usr/include/hyprland/'),p
 q=Path(p)
 if q.is_relative_to(C):
  rel=str(q.relative_to(C));decl=fixed['files'].get(rel)
  assert decl is not None and row['sha256']==decl['sha256']and int(row['mode'],8)==decl['mode'],(rel,decl,row)
  matched[p]=dict(sha256=decl['sha256'],mode=decl['mode'])
assert matched
save('v3-selected-header-origin-conservation.json',dict(matched=matched,installedHyprlandHeaders=[],removedInstalledFlags=[f for f in rawFlags if f not in flags]))
save('dependency-closure.json',deps)
text=run(['/usr/bin/ldd',str(B/'build/libpin-campaign-b-observer.so')]);(B/'build/ldd.txt').write_text(text+'\n')
linkInputs={}
for line in (B/'build/link.log').read_text().splitlines():
 p=Path(line.strip())
 if p.is_file():linkInputs[str(p.absolute())]=file(p)
shared={}
for line in text.splitlines():
 for word in line.split():
  if word.startswith('/')and Path(word).is_file():shared[word]=file(word)
for args,name in [(['/usr/bin/readelf','-Ws',str(B/'build/libpin-campaign-b-observer.so')],'symbols.txt'),(['/usr/bin/readelf','-d',str(B/'build/libpin-campaign-b-observer.so')],'dynamic.txt'),(['/usr/bin/readelf','-n',str(B/'build/libpin-campaign-b-observer.so')],'elf-notes.txt')]:
 (B/'build'/name).write_text(run(args)+'\n')
# Version-sensitive dynamic imports. Select actual core transitive DT_NEEDED graph,
# then include newly linked observer JSON-C and its recursively captured dependencies.
prior=json.loads((C/'final-review/compiler-and-linked-library-closure.json').read_text())
sharedGraph={};pending=[str(C/'build-core-make/Hyprland')]
pluginNeeded=[]
import re
for line in (B/'build/dynamic.txt').read_text().splitlines():
 if '(NEEDED)'in line:pluginNeeded.append(re.search(r'\[(.+)\]',line).group(1))
def named(needed):
 matches=[p for p in prior['libraries'] if Path(p).name==needed]
 assert len(matches)==1,(needed,matches)
 return matches[0]
pending += [named(n)for n in pluginNeeded]
while pending:
 p=pending.pop()
 if p in sharedGraph:continue
 decl=prior['libraries'][p];current=file(p)
 assert current['sha256']==decl['metadata']['sha256']and int(current['mode'],8)==decl['metadata']['mode'],p
 sharedGraph[p]=current;pending += [named(n)for n in decl['needed']]
save('actual-core-plus-observer-library-closure.json',sharedGraph)
def symbols(p,flag):return run(['/usr/bin/nm','-D',flag,p]).splitlines()
def normalized(name):return name.replace('@@','@')
exports={}
for origin in sharedGraph:
 for line in symbols(origin,'--defined-only'):
  row=line.split()
  if len(row)<3:continue
  name=row[-1];exports.setdefault(normalized(name),[]).append(origin)
  if '@@'in name:exports.setdefault(name.split('@@')[0],[]).append(origin)
imports={};missing=[]
for line in symbols(str(B/'build/libpin-campaign-b-observer.so'),'--undefined-only'):
 row=line.split()
 if len(row)!=2:continue
 binding,name=row;providers=exports.get(normalized(name),[]);imports[name]=dict(providers=providers,binding=binding)
 if binding=='U'and not providers:missing.append(name)
save('elf-import-closure.json',dict(imports=imports,unresolvedStrong=missing,scope='actual version-sensitive dynamic nm imports resolved against exact core transitive DT_NEEDED plus observer DT_NEEDED graph',nativeLoaded=False))
assert not missing,missing
assert source.read_bytes()==(B/'retained-first-build/proposed-source-correction-v2/campaign_b_observer.cpp').read_bytes()
for p,row in deps.items():assert file(p)==row,p
save('BUILD_READY.json',dict(result='compile-link-only-pass',source=file(source),object=file(B/'build/observer.o'),binary=file(B/'build/libpin-campaign-b-observer.so'),depfile=file(B/'build/observer.d'),linkMap=file(B/'build/observer.map'),actualDependencyCount=len(deps),linkInputs=linkInputs,sharedLibraries=shared,imports=imports,core=file(C/'build-core-make/Hyprland'),nativeLoaded=False,coreExecuted=False,abiLiveAccepted=False))
print(json.dumps({'result':'compile-link-only-pass','dependencies':len(deps),'imports':len(imports),'sharedLibraries':len(shared),'binarySHA256':file(B/'build/libpin-campaign-b-observer.so')['sha256']}))
