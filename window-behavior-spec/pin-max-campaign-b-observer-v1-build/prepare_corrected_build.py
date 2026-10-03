from pathlib import Path
import shutil
B=Path(__file__).resolve().parent;N=Path('/home/hoskinson/window-behavior-spec/pin-max-campaign-b-observer-v2-build')
N.mkdir(mode=0o700);(N/'src').mkdir(mode=0o700);(N/'build').mkdir(mode=0o700)
shutil.copytree(B,N/'retained-first-build',copy_function=shutil.copy2)
for name in ['campaign_b_observer.cpp','decode_observation.py']:shutil.copy2(B/'proposed-source-correction-v2'/name,N/'src'/name)
shutil.copytree(B/'retained-reviewed-draft',N/'retained-reviewed-draft',copy_function=shutil.copy2)
shutil.copytree(B/'tests',N/'tests',copy_function=shutil.copy2)
s=(B/'build_observer.py').read_text()
s=s.replace("assert source.read_bytes()==parent.read_bytes()", "assert source.read_bytes()==(B/'retained-first-build/proposed-source-correction-v2/campaign_b_observer.cpp').read_bytes()")
s=s.replace("flags=shlex.split(run(['/usr/bin/pkg-config','--cflags',*PKGS]));libs", "rawFlags=shlex.split(run(['/usr/bin/pkg-config','--cflags',*PKGS]));flags=[f for f in rawFlags if not f.startswith('-I/usr/include/hyprland')];libs")
s=s.replace("selected=['-isystem',str(C/'include'),'-isystem',str(C/'core/src')", "selected=['-isystem',str(C/'core/src')")
s=s.replace("fixed=json.loads((C/'SOURCE_READY_INPUTS.json').read_text());save('dependency-closure.json',deps)","""fixed=json.loads((C/'SOURCE_READY_INPUTS.json').read_text());matched={}
for p,row in deps.items():
 assert not p.startswith('/usr/include/hyprland/'),p
 q=Path(p)
 if q.is_relative_to(C):
  rel=str(q.relative_to(C));decl=fixed['files'].get(rel)
  assert decl is not None and row['sha256']==decl['sha256']and int(row['mode'],8)==decl['mode'],(rel,decl,row)
  matched[p]=dict(sha256=decl['sha256'],mode=decl['mode'])
assert matched
save('v3-selected-header-origin-conservation.json',dict(matched=matched,installedHyprlandHeaders=[],removedInstalledFlags=[f for f in rawFlags if f not in flags]))
save('dependency-closure.json',deps)""")
a=s.index('# Never call dlopen/PLUGIN_INIT.');b=s.index("assert not missing,missing",a)
s=s[:a]+'''# Version-sensitive dynamic imports. Select actual core transitive DT_NEEDED graph,
# then include newly linked observer JSON-C and its recursively captured dependencies.
prior=json.loads((C/'final-review/compiler-and-linked-library-closure.json').read_text())
sharedGraph={};pending=[str(C/'build-core-make/Hyprland')]
pluginNeeded=[]
import re
for line in (B/'build/dynamic.txt').read_text().splitlines():
 if '(NEEDED)'in line:pluginNeeded.append(re.search(r'\\[(.+)\\]',line).group(1))
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
''' + s[b:]
(N/'build_observer.py').write_text(s)
print(str(N))
