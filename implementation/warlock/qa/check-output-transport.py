"""Protected UI-019 zero-output transport model and one owning Aquamarine TU; native recovery separate."""
import hashlib,json,pathlib,re,shlex,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1];repo=root.parents[1]
assert sys.argv[1:] in ([],['--init'])
initial=bool(sys.argv[1:]);out=root/'qa/runs'/('output-transport-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r=dict(passed=False,scope=__doc__,nativeAcceptance=False,installed=False,protectedScope=scope,commands=[])
def run(name,args,cwd=None):
 p=subprocess.run(list(map(str,args)),cwd=cwd,capture_output=True,timeout=240)
 (out/(name+'.stdout')).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr)
 r['commands'].append(dict(name=name,command=list(map(str,args)),exitCode=p.returncode))
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-4000:]+p.stdout.decode(errors='replace')[-1000:])
 return p.stdout.decode()
try:
 model=root/'qa/output-transport.qnt';tests=root/'qa/output-transport_test.qnt'
 r['modelInputs']={str(p.relative_to(root)):sha(p) for p in (model,tests)}
 run('typecheck',['quint','typecheck',model])
 run('init',['quint','run',model,'--backend=typescript','--invariants=safety','--max-samples=1','--max-steps=1','--seed=85000'])
 if not initial:
  run('named',['quint','test',tests,'--backend=typescript','--match=Test$','--max-samples=1','--seed=85001'])
  witness=run('witnesses',['quint','run',model,'--backend=typescript','--witnesses','returned','failed','--max-samples=1000','--max-steps=20','--seed=85002'])
  r['witnessCounts']={n:int(c) for n,c in re.findall(r'(\w+) was witnessed in (\d+) trace',witness)}
  assert all(r['witnessCounts'].get(n,0)>0 for n in ('returned','failed'))
  run('safety',['quint','run',model,'--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=20','--seed=85003'])
  ancestor=repo/'implementation/elm-keyboard-focus-cancellation-v155/build-1791128575548525187'
  prior=json.loads((ancestor/'report.json').read_text());assert prior['passed']
  for p,h in prior['dependencies'].items():assert sha(p)==h,p
  oldlib=pathlib.Path(prior['library']);assert sha(oldlib)==prior['librarySHA256']
  source=root/'native/aquamarine/Wayland.cpp';r['sourceHashes']={'native/aquamarine/Wayland.cpp':sha(source)}
  compiled=out/'Wayland.cpp';compiled.write_bytes(source.read_bytes())
  cmake=ancestor/'cmake';flags=(cmake/'CMakeFiles/aquamarine.dir/flags.make').read_text()
  args=['/usr/bin/c++']
  for key in ('CXX_DEFINES','CXX_INCLUDES','CXX_FLAGS'):
   args+=shlex.split(next(l.split(' = ',1)[1] for l in flags.splitlines() if l.startswith(key+' = ')))
  owner=ancestor/'inputs/candidate/src/backend';args+=['-I'+str(owner)]
  obj=out/'Wayland.cpp.o';dep=out/'Wayland.cpp.d'
  run('compile',args+['-MD','-MF',dep,'-o',obj,'-c',compiled])
  names=shlex.split(dep.read_text().replace('\\\n',' ').split(':',1)[1]);deps={str(pathlib.Path(n).resolve()):sha(n) for n in names}
  baseline_source=owner/'Wayland.cpp'
  allowed=set(prior['dependencies'])-{str(baseline_source)}
  assert set(deps)-{str(compiled)}<=allowed,'New unreviewed compile dependency'
  link=shlex.split((cmake/'CMakeFiles/aquamarine.dir/link.txt').read_text());binary=out/oldlib.name;retained={};linkdeps={};i=0
  while i<len(link):
   a=link[i]
   if a=='-o':link[i+1]=str(binary);i+=2;continue
   if a.startswith('-Wl,--dependency-file='):link[i]='-Wl,--dependency-file='+str(out/'link.d')
   elif a.endswith('.o'):
    p=cmake/a;link[i]=str(obj) if a.endswith('/backend/Wayland.cpp.o') else str(p)
    if link[i]!=str(obj):retained[str(p)]=sha(p)
   elif a.startswith('/') and pathlib.Path(a).is_file():linkdeps[a]=sha(a)
   i+=1
  assert len(retained)==29,len(retained)
  run('link',link,cwd=cmake)
  loader=out/'libaquamarine.so.14';loader.symlink_to(binary.name)
  symbols=lambda text:{line.split()[-1] for line in text.splitlines() if line.split()}
  old=symbols(run('ancestor-exports',['nm','-D','--defined-only',oldlib]));new=symbols(run('candidate-exports',['nm','-D','--defined-only',binary]))
  assert old<=new,sorted(old-new)
  for p,h in {**deps,**retained,**linkdeps}.items():assert sha(p)==h,p
  assert sha(source)==r['sourceHashes']['native/aquamarine/Wayland.cpp']
  r.update(library=str(binary),librarySHA256=sha(binary),loaderSymlink={'path':str(loader),'target':binary.name},ancestor=dict(report=str(ancestor/'report.json'),reportSHA256=sha(ancestor/'report.json'),librarySHA256=sha(oldlib)),dependencies=deps,retainedObjects=retained,linkLibraries=linkdeps,missingParentSymbols=[],publicHeadersUnchanged=True)
 r['passed']=True
except Exception as e:r['error']=repr(e)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=r['passed'],report=str(out/'report.json'),error=r.get('error'))));raise SystemExit(not r['passed'])
