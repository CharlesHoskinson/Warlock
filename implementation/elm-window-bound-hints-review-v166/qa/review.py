"""Read-only extraction/ABI review; no test binary or native process execution."""
import ast,hashlib,json,re,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];PACKET=REPO/'implementation/elm-window-bound-hints-characterization-v165/qa/characterization-1791124527444957441';OUT=ROOT/'qa'/('review-'+str(time.time_ns()));OUT.mkdir();checks=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
r={'passed':False,'nativeAcceptance':False,'scope':'Exact owning CWindow methods with stub converted observations/rules and actual Hyprutils; no protocol conversion, rule applicability, eligibility or native mutation qualification','checks':checks}
try:
 report=json.loads((PACKET/'report.json').read_text());check('protected actual13 characterization passed',report['passed'] is True and report['compileExit']==0 and report['testExit']==0 and report['checks']==13)
 owning=REPO/'implementation/elm-core-parent-first-anchor-v89/build-1791107301396755104/inputs/candidate/src/desktop/view/Window.cpp';check('owning89 Window exact hash',sha(owning)=='ef8e7fc7f2bd9ffa8f0b99b486ca9ea3bc80f8906aa214277ab7b16faf0b445d' and sha(owning)==sha(PACKET/'owning-Window.cpp'))
 text=owning.read_text();methods=[]
 for name in ['minSize','maxSize']:
  start=text.index('std::optional<Vector2D> CWindow::'+name+'()');body=text.index('{',start);end=body+1;depth=1
  while depth:
   depth+=(text[end]=='{')-(text[end]=='}');end+=1
  methods.append(text[start:end])
 check('byte-identical exact extracted methods', ('\n\n'.join(methods)+'\n').encode()==(PACKET/'methods.cpp.inc').read_bytes());check('compiled source includes exact methods', '\n\n'.join(methods) in (PACKET/'characterization.cpp').read_text());check('extraction report hash exact',sha(PACKET/'methods.cpp.inc')==report['extractedMethodsSHA256'])
 old=REPO/'implementation/elm-window-bound-hints-characterization-v164/qa/test.py';new=REPO/'implementation/elm-window-bound-hints-characterization-v165/qa/test.py';before=old.read_text();after=new.read_text();check('only QA numeric constructor correction',before.replace('quiet_NaN(),4}','quiet_NaN(),4.0}')==after)
 tree=ast.parse(after);literals={n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ['prefix','tests']};check('actual generated compiled test source exact', (literals['prefix']+'\n'+'\n\n'.join(methods)+'\n'+literals['tests'])==(PACKET/'characterization.cpp').read_text())
 pair=json.loads((REPO/'implementation/elm-parent-first-anchor-pair-v90/qa/build-1791107369559431070/report.json').read_text());check('owning90 native pair report passed',pair['passed'] is True)
 for path,digest in pair['dependencies'].items():
  if '/hyprutils/math/' in path:check('actual owning Hyprutils header '+path,sha(path)==digest)
 deps=shlex.split((PACKET/'dependencies.d').read_text().replace('\\\n',' ').split(':',1)[1]);r['compilerDependencies']={str(Path(p).resolve()):sha(p) for p in deps}
 linked=subprocess.run(['ldd',str(PACKET/'characterization')],capture_output=True,text=True,check=True);(OUT/'ldd.txt').write_text(linked.stdout);check('actual helper link closure resolves','not found' not in linked.stdout);libs={}
 for line in linked.stdout.splitlines():
  match=re.search(r'(?:=>\s+)?(/[^\s]+)\s+\(',line)
  if match:
   p=Path(match.group(1)).resolve(strict=True);libs[str(p)]=sha(p)
 library='/usr/lib/libhyprutils.so.0.14.2';check('actual loader-resolved Hyprutils equals actual90 owning library',library in libs and libs[library]==pair['linkedLibraries'][library]==report['linkedLibrarySHA256'])
 r.update(passed=True,linkedLibraries=libs,artifacts={str(p):sha(p) for p in [PACKET/'report.json',PACKET/'characterization',PACKET/'characterization.cpp',PACKET/'methods.cpp.inc',old,new]},sourceSHA256=sha(Path(__file__)),limitations=['Already converted stub XDG vectors; no actual client or conversion run','Rule outputs stubbed; no actual rule resolution/runtime applicability','Tiny positive maximum endpoints1and4 only; branch is actual threshold5','Existing zero-min toplevel yields1x1; missing toplevel is separate nullopt','No live target, geometry policy, Quint model, command mutation or release qualification'])
 for p in [PACKET/'report.json',PACKET/'characterization.cpp',PACKET/'methods.cpp.inc',old,new]:shutil.copy2(p,OUT/(str(len(list(OUT.iterdir())))+'-'+p.name))
except Exception as error:r['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
