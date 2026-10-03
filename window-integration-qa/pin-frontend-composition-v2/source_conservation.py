"""Source reconstruction, separate from actual unprojected CPU execution."""
from pathlib import Path
import ast,copy,difflib,hashlib,json,os
B=Path(__file__).resolve().parent;OLD=Path('/home/hoskinson/window-integration-qa/pin-frontend-qa-v1');V8=Path('/home/hoskinson/window-behavior-spec/qml-process-provider-v8-terminal-retire')
def dump(n):return ast.dump(n,include_attributes=False)
def named(tree,name):return next(n for n in ast.walk(tree)if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name==name)
def target(n,text):return isinstance(n,ast.Assign)and any(ast.unparse(t)==text for t in n.targets)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,value):
 checks.append({'name':name,'passed':bool(value)})
 if not value:raise AssertionError(name)
old=ast.parse((OLD/'frontend_cases.py').read_text());new=ast.parse((B/'frontend_cases.py').read_text())
o=named(old,'FrontendCases');n=named(new,'FrontendCases')
for f in o.body:
 if isinstance(f,ast.FunctionDef)and f.name not in('scope','toggle'):check('Unchanged controller '+f.name,dump(f)==dump(named(new,f.name)))
a=copy.deepcopy(named(new,'toggle'));b=named(old,'toggle')
a.body=[v for v in a.body if not target(v,"row['inputBefore']")]
index=next(i for i,v in enumerate(a.body)if isinstance(v,ast.FunctionDef)and v.name=='completed')
a.body.insert(index-1,ast.parse('case.release(True)').body[0])
completed=named(a,'completed');stop=next(i for i,v in enumerate(completed.body)if isinstance(v,ast.If)and "refused-or-uncertain"in ast.unparse(v.test))
completed.body=completed.body[:1]+completed.body[stop:]
check('Complete original toggle/effect AST reconstructs exactly',dump(a)==dump(b))
check('No external reader flag call',not any(isinstance(v,ast.Call)and isinstance(v.func,ast.Attribute)and v.func.attr=='scope_reader'for v in ast.walk(new)))
check('No boolean release in applied controller',not any(isinstance(v,ast.Call)and isinstance(v.func,ast.Attribute)and v.func.attr=='release'and v.args and isinstance(v.args[0],ast.Constant)and v.args[0].value is True for v in ast.walk(new)))
old=ast.parse((OLD/'frontend_authority.py').read_text());new=ast.parse((B/'frontend_authority.py').read_text())
for f in old.body:
 if isinstance(f,ast.FunctionDef)and f.name not in('binding','completion_current'):check('Unchanged acceptance '+f.name,dump(f)==dump(named(new,f.name)))
for name in ('__init__','invalidate','accept'):check('Unchanged FrontendCase '+name,dump(named(old,name))==dump(named(new,name)))
press=copy.deepcopy(named(new,'press'));press.body=[v for v in press.body if not target(v,'self.route')];check('Original press readiness AST conserved',dump(press)==dump(named(old,'press')))
completion=copy.deepcopy(named(new,'completion_current'));completion.body=completion.body[1:];check('Original completion predicates conserved',dump(completion)==dump(named(old,'completion_current')))
binding=copy.deepcopy(named(new,'binding'));ob=named(old,'binding');binding.body=copy.deepcopy(ob.body[:3])+binding.body[1:]
for v in ast.walk(binding):
 if isinstance(v,ast.Call)and isinstance(v.func,ast.Name)and v.func.id=='dict':v.keywords=[k for k in v.keywords if k.arg!='popupWitness']
check('Original native layer/row binding predicates conserved',dump(binding)==dump(ob))
check('Native authority exact', (B/'native_authority.py').read_bytes()==(OLD/'native_authority.py').read_bytes())
check('Root helper exact', (B/'root_pin_helper.py').read_bytes()==(OLD/'root_pin_helper.py').read_bytes())
check('Actual frozen driver exact', (B/'keyboard/physical-keyboard').read_bytes()==(OLD/'keyboard/physical-keyboard').read_bytes())
old=(V8/'frontend/PinWindowMenu.qml').read_text();new=(B/'frontend/PinWindowMenu.qml').read_text()
a=new.index('    function diagnosticState() {');b=new.index('    function sync()',a);c=old.index('    function diagnosticState() {');d=old.index('    function sync()',c)
check('V8 action/capture/retire/feedback QML exact outside diagnostic',new[:a]+old[c:d]+new[b:]==old)
for name in('Windows.qml','TaskbarPopup.qml','PinMenu.js'):check('V8 QML factory exact '+name,(B/'frontend'/name).read_bytes()==(V8/'frontend'/name).read_bytes())
old=(OLD/'native-probe/probe.cpp').read_text();new=(B/'native-probe/probe.cpp').read_text();inverse=new
inverse=inverse.replace('#include <hyprland/src/devices/IKeyboard.hpp>\n','',1)
inverse=inverse.replace('CHyprSignalListener keyboardListener;\nstd::vector<std::string> keyboardEvents;\nuint64_t keyboardSequence=0;\nuint64_t buttonSequence=0;\n','',1)
inverse=inverse.replace(' const auto keyboardResource=g_pSeatManager->m_state.keyboardFocusResource.lock();\n','',1)
inverse=inverse.replace('+",\\\"keyboardResourcePresent\\\":"+(keyboardResource?"true":"false")','',1)
a=inverse.index('int luaKeyboardEvents(');b=inverse.index('void authorize(){',a);inverse=inverse[:a]+inverse[b:]
inverse=inverse.replace('HyprlandAPI::addLuaFunction(handle,"toolkit_held_probe","keyboard_events",luaKeyboardEvents);observeKeyboard();','',1)
inverse=inverse.replace('R"({{\"sequence\":{},\"button\":','R"({{\"button\":',1).replace('++buttonSequence,e.button,','e.button,',1)
inverse=inverse.replace('keyboardListener.reset();keyboardEvents.clear();keyboardSequence=0;buttonSequence=0;','',1)
check('Existing readonly probe/listeners exact outside episode additions',inverse==old)
formal=json.loads((B/'formal-composition-v3-before-source.json').read_text());check('Model/contract before source still exact',all(sha(Path(p))==r['sha256']for p,r in formal['inputs'].items()))
plan=json.loads(Path('/home/hoskinson/window-behavior-spec/process-private-qs-route-plan-v1/source-plan-handoff.json').read_text());check('All1518 ancestry bytes unchanged',all(sha(Path(p))==h for p,h in plan['inputs'].items()))
inputs=json.loads((Path('/home/hoskinson/window-integration-qa')/'pin-input-episode-v2-component-handoff-v1.json').read_text())['componentSources'];check('All original A2 component protocol bytes unchanged',all(sha(Path(p))==v['sha256']for p,v in inputs.items()))
diffs=B/'diffs';diffs.mkdir(mode=0o700,exist_ok=True)
for oldroot,name in[(OLD,'frontend_cases.py'),(OLD,'frontend_authority.py'),(OLD,'native-probe/probe.cpp'),(V8,'frontend/PinWindowMenu.qml')]:
 target=diffs/(name.replace('/','_')+'.diff');assert not target.exists();target.write_text(''.join(difflib.unified_diff((oldroot/name).read_text().splitlines(True),(B/name).read_text().splitlines(True),fromfile=str(oldroot/name),tofile=str(B/name))))
report={'result':'pass','checks':checks,'sourceReconstructionOnly':True,'actualCPUProofSeparate':True,'GUI':False};target=B/'source-conservation-report.json';assert not target.exists();target.write_text(json.dumps(report,indent=2)+'\n');os.chmod(target,0o600);print(json.dumps({'result':'pass','checks':len(checks),'path':str(target)}))
