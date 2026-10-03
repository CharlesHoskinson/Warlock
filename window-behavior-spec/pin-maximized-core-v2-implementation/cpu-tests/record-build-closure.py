import hashlib,json,os,shlex,stat,subprocess,time
from pathlib import Path
B=Path(__file__).resolve().parents[1]
O=B/'final-review';O.mkdir(exist_ok=True)
def meta(path):
 s=path.stat();return dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),mode=stat.S_IMODE(s.st_mode),size=s.st_size,mtimeNs=s.st_mtime_ns)
def save(name,value):
 p=O/name
 with p.open('x') as f:json.dump(value,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
fixed=json.loads((B/'final-build-source-fixed-v2-before.json').read_text());errors=[]
for rel,m in fixed['sources'].items():
 current=meta(B/rel)
 if any(current[k]!=m[k] for k in ['sha256','mode','mtimeNs']):errors.append(rel)
for rel,target in fixed['links'].items():
 if not (B/rel).is_symlink() or os.readlink(B/rel)!=target:errors.append(rel)
identity=json.loads((B/'core-policy-source-identity-final-v2.json').read_text())
for rel,digest in identity['sourceSHA256'].items():
 if meta(B/'core'/rel)['sha256']!=digest:errors.append('core identity:'+rel)
save('source-fixed-post-build.json',dict(beforeSHA256=meta(B/'final-build-source-fixed-v2-before.json')['sha256'],checked=len(fixed['sources']),identityChecked=len(identity['sourceSHA256']),errors=errors,nativeExecuted=False))
if errors:raise SystemExit(str(errors))
dependencies={};objects=[];freshness=[]
for dep in sorted((B/'build-core-make').rglob('*.o.d')):
 text=dep.read_text().replace('\\\n',' ')
 lhs,rhs=text.split(':',1)
 obj=(B/'build-core-make'/shlex.split(lhs)[0]).resolve()
 if not obj.exists():raise SystemExit('missing object '+str(obj))
 om=meta(obj);resolved=[]
 for entry in shlex.split(rhs):
  path=Path(entry)
  if not path.is_absolute():path=B/'build-core-make'/path
  path=path.resolve();key=str(path);resolved.append(key)
  if key not in dependencies:dependencies[key]=meta(path)
  if dependencies[key]['mtimeNs']>om['mtimeNs']:freshness.append(dict(object=str(obj),dependency=key))
 objects.append(dict(path=str(obj.relative_to(B)),metadata=om,dependencyFile=str(dep.relative_to(B)),dependencyFileSHA256=meta(dep)['sha256'],dependencies=resolved))
save('core-object-freshness.json',dict(objects=objects,dependencies=dependencies,newerDependencies=freshness,method='compiler emitted .o.d; every resolved dependency hash/mode recorded and mtime no newer than object'))
if freshness:raise SystemExit('stale objects '+str(freshness[:5]))
flags=subprocess.check_output(['pkg-config','--cflags','pixman-1','libdrm','hyprland','libinput','libudev','wayland-server','xkbcommon','libeis-1.0'],text=True).split()
pluginDeps={};commands=[]
sources=['main.cpp','barDeco.cpp','BarPassElement.cpp','dragBridge.cpp','familyBridge.cpp','ancestorHit.cpp','snapshotBridge.cpp','atlasRenderer.cpp','atlasAdapter.cpp','pinBridge.cpp']
for source in sources:
 args=['g++','-M','-std=c++26','-I../include','-I../core/src','-I../core/protocols','-I../build-core-make']+flags+[source]
 start=time.monotonic();r=subprocess.run(args,cwd=B/'plugin',text=True,capture_output=True)
 dep=O/('plugin-'+source+'.d');dep.write_text(r.stdout);(O/('plugin-'+source+'.stderr')).write_text(r.stderr)
 commands.append(dict(argv=args,cwd=str(B/'plugin'),exitCode=r.returncode,elapsed=time.monotonic()-start,dependencyFile=str(dep.relative_to(B))))
 if r.returncode:raise SystemExit(r.stderr)
 for entry in shlex.split(r.stdout.replace('\\\n',' ').split(':',1)[1]):
  path=Path(entry)
  if not path.is_absolute():path=B/'plugin'/path
  path=path.resolve();pluginDeps[str(path)]=meta(path)
plugin=B/'plugin/hyprbars-native-max-core-v2-candidate.so';pm=meta(plugin)
newer=[path for path,m in pluginDeps.items() if m['mtimeNs']>pm['mtimeNs']]
save('plugin-dependency-freshness.json',dict(commands=commands,dependencies=pluginDeps,newerDependencies=newer,metadata=pm,method='actual compiler -M same c++ standard/includes/pkg-config flags; source fixed before logged actual make compile'))
if newer:raise SystemExit('plugin dependencies newer '+str(newer))
toolPaths=['/usr/bin/c++','/usr/bin/g++','/usr/bin/as','/usr/bin/ld','/usr/bin/cmake','/usr/bin/make','/usr/bin/pkg-config']
toolMeta={str(Path(path).resolve()):meta(Path(path).resolve()) for path in toolPaths}
externalLibs={}
for entry in shlex.split((B/'build-core-make/CMakeFiles/Hyprland.dir/link.txt').read_text()):
 path=Path(entry)
 if path.is_absolute() and path.is_file():externalLibs[str(path.resolve())]=meta(path.resolve())
buildInputs={}
for path in (B/'build-core-make').rglob('*'):
 if path.is_file() and path.name in {'flags.make','link.txt','CMakeCache.txt','compile_commands.json','CompilerIdCXX','CMakeCXXCompiler.cmake'}:buildInputs[str(path.relative_to(B))]=meta(path)
outputs={rel:meta(B/rel) for rel in ['build-core-make/Hyprland','build-core-make/libhyprland_lib.a','plugin/hyprbars-native-max-core-v2-candidate.so']}
for rel in outputs:
 if rel.endswith('.a'):continue
 for label,args in [('elf-note',['readelf','-n',rel]),('exported-symbols',['nm','-D','-C',rel]),('elf-needed',['readelf','-d',rel])]:
  r=subprocess.run(args,cwd=B,text=True,capture_output=True);(O/(Path(rel).name+'-'+label+'.log')).write_text(r.stdout+r.stderr)
  if r.returncode:raise SystemExit('ELF inspection failed')
save('build-input-output-closure.json',dict(corePolicyBuild=identity['sha256'],tools=toolMeta,linkInputs=externalLibs,buildInputs=buildInputs,outputs=outputs,coreCommand=['cmake','--build','build-core-make','--parallel','2'],pluginCommand=['make'],coreSession=52687,pluginSession=50669,coreExit=0,pluginExit=0,nativeExecuted=False))
print(json.dumps(dict(sourceChecked=len(fixed['sources']),objects=len(objects),coreDependencies=len(dependencies),pluginDependencies=len(pluginDeps),newerDependencies=0,outputs=outputs),indent=2))
