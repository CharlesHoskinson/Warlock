"""Read-only closure collection repair; never compiles/loads/runs candidate."""
from pathlib import Path
import hashlib,json,os,re,subprocess
B=Path(__file__).resolve().parent;C=Path('/home/hoskinson/window-behavior-spec/pin-maximized-core-v3-hit-fallback')
def file(p):
 p=Path(p).absolute();s=p.stat();return dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mode=oct(s.st_mode&0o7777),size=s.st_size,mtimeNs=s.st_mtime_ns,resolved=str(p.resolve()),literalLink=os.readlink(p)if p.is_symlink()else None)
def run(args):return subprocess.check_output(args,text=True).strip()
def save(name,value):
 with (B/'build'/name).open('x')as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
 (B/'build'/name).chmod(0o600)
assert json.loads((B/'build/compile-result.json').read_text())['exitCode']==0
assert json.loads((B/'build/link-result.json').read_text())['exitCode']==0
prior=json.loads((C/'final-review/compiler-and-linked-library-closure.json').read_text());named={};dynamic={}
for path,decl in prior['libraries'].items():
 current=file(path);assert current['sha256']==decl['metadata']['sha256']and int(current['mode'],8)==decl['metadata']['mode'],path
 text=run(['/usr/bin/readelf','-d',path]);soname=re.findall(r'\(SONAME\).*\[(.+)\]',text);needed=re.findall(r'\(NEEDED\).*\[(.+)\]',text)
 assert needed==decl['needed'],path
 dynamic[path]=dict(raw=text,metadata=current,soname=soname,needed=needed)
 for name in [Path(path).name,*soname]:named.setdefault(name,set()).add(path)
save('actual-library-soname-inputs.json',dynamic)
def resolve(name):
 matches=named.get(name,set());assert matches,(name,matches)
 resolved={str(Path(p).resolve())for p in matches};assert len(resolved)==1,(name,matches)
 return sorted(matches)[0]
pluginText=(B/'build/dynamic.txt').read_text();pluginNeeded=re.findall(r'\(NEEDED\).*\[(.+)\]',pluginText)
pending=[str(C/'build-core-make/Hyprland')]+[resolve(n)for n in pluginNeeded];graph={}
while pending:
 p=pending.pop()
 if p in graph:continue
 graph[p]=dynamic[p];pending += [resolve(n)for n in dynamic[p]['needed']]
save('actual-core-plus-observer-library-closure-v2.json',graph)
exports={}
for origin in graph:
 for line in run(['/usr/bin/nm','-D','--defined-only',origin]).splitlines():
  row=line.split()
  if len(row)<3:continue
  name=row[-1];exports.setdefault(name.replace('@@','@'),[]).append(origin)
  if '@@'in name:exports.setdefault(name.split('@@')[0],[]).append(origin)
imports={};missing=[]
for line in run(['/usr/bin/nm','-D','--undefined-only',str(B/'build/libpin-campaign-b-observer.so')]).splitlines():
 row=line.split()
 if len(row)!=2:continue
 binding,name=row;providers=exports.get(name.replace('@@','@'),[]);imports[name]=dict(providers=providers,binding=binding)
 if binding=='U'and not providers:missing.append(name)
save('elf-import-closure-v2.json',dict(imports=imports,unresolvedStrong=missing,method='actual version-sensitive nm-D names, actual readelf SONAME DT_NEEDED graph from exact V3 accepted linked libraries and new observer',nativeLoaded=False))
assert not missing,missing
for path,row in json.loads((B/'build/dependency-closure.json').read_text()).items():assert file(path)==row,path
for path,row in json.loads((B/'build/build-before.json').read_text())['tools'].items():assert file(path)==row,path
source=B/'src/campaign_b_observer.cpp';assert source.read_bytes()==(B/'retained-first-build/proposed-source-correction-v2/campaign_b_observer.cpp').read_bytes()
save('POST_BUILD_READY.json',dict(result='compile-link-dependency-versioned-ABI-only-pass',source=file(source),object=file(B/'build/observer.o'),binary=file(B/'build/libpin-campaign-b-observer.so'),depfile=file(B/'build/observer.d'),linkMap=file(B/'build/observer.map'),actualDependencies=len(json.loads((B/'build/dependency-closure.json').read_text())),core=file(C/'build-core-make/Hyprland'),libraryGraphCount=len(graph),strongUndefined=sum(v['binding']=='U'for v in imports.values()),unresolvedStrong=missing,elfNotes=(B/'build/elf-notes.txt').read_text(),nativeLoaded=False,coreExecuted=False,abiLiveAccepted=False,priorCheckerErrorRetained=True))
print(json.dumps({'result':'compile-link-dependency-versioned-ABI-only-pass','dependencies':len(json.loads((B/'build/dependency-closure.json').read_text())),'libraryGraph':len(graph),'strongUndefined':sum(v['binding']=='U'for v in imports.values()),'binarySHA256':file(B/'build/libpin-campaign-b-observer.so')['sha256']}))
