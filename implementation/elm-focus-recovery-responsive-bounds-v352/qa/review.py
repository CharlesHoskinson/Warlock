import ast,hashlib,importlib.util,json,resource,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=ROOT/'qa/native.py';code=source.read_text();tree=ast.parse(code)
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='geometry_effect' for n in ast.walk(tree)),'GUI campaign cannot dispatch native effects directly'
assert 'gui.apply' in code and 'gui.click(item,272,deadline)' in code and 'gui.pixels' in code
for exact in ["if time.monotonic()>=deadline:raise RuntimeError('Original six-second deadline')","client.wait(timeout=5)","session.data('clients')==[]", "not report.get('profileCleanupErrors')", "not report.get('finalCleanupErrors')"]:assert exact in code
assert (ROOT/'profiles.json').read_bytes()==(REPO/'implementation/elm-keyboardless-bounds-regression-v215/profiles.json').read_bytes()
profiles=json.loads((ROOT/'profiles.json').read_text())['profiles'];assert len(profiles)==22 and len({p['id'] for p in profiles})==22
original=json.loads((REPO/'implementation/elm-keyboardless-bounds-regression-v215/profiles.json').read_text());assert profiles==original['profiles']
for p in profiles:
 w,h=p['physicalMode'];scale=p['monitorScale'];assert w%scale==0 and h%scale==0 and h//scale>48
 # Independent expected GUI workarea retains normative48 bar; producer snapshot must agree.
 area=[0,48,w//scale,h//scale-48];proposal=[area[2]-2,area[3]-2];expected=p['origin']==[0,0] and p['minimum']!=p['maximum'] and all(lo<=v and (hi==0 or v<=hi) for lo,hi,v in zip(p['minimum'],p['maximum'],proposal))
 assert expected==p['expectedMAX'],'This22-profile matrix happens to retain support classification after actual48px reservation'
spec=importlib.util.spec_from_file_location('current_gui_bounds_preflight',source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);host,meta,client,Endpoint,start,journal,inputs=module.preflight();inputs[str(source)]=sha(source);inputs[str(Path(__file__))]=sha(Path(__file__));inputs[str(ROOT/'qa/observation-amendment.json')]=sha(ROOT/'qa/observation-amendment.json');inputs[str(ROOT/'qa/observation_tests.py')]=sha(ROOT/'qa/observation_tests.py')
bus_report=REPO/'implementation/elm-gui-bounds-native-v272/qa/bus-1791146957045683792/report.json'
bus=json.loads(bus_report.read_text())
assert bus['passed'] and bus['privateBusRuntimeGone'] and not bus['nativeAcceptance']
assert bus['checks']==['no service directory or includes','actual socket credential and owned daemon',*[name+' actual unavailable without child activation' for name in ('org.a11y.Bus','org.freedesktop.portal.Desktop','org.freedesktop.portal.Documents')],'owned daemon has no activated children','normal daemon termination']
inputs[str(bus_report)]=sha(bus_report);inputs[str(ROOT/'qa/bus_test.py')]=sha(ROOT/'qa/bus_test.py')
for name,digest in bus['artifacts'].items():
 artifact=bus_report.parent/name;assert sha(artifact)==digest
 inputs[str(artifact)]=digest
failure=REPO/'implementation/elm-gui-bounds-failure-v273/failure-manifest.json'
assert sha(failure)=='d72a3fe4afa983ab8aa6cccdeb079b149f884d8ba35d23bd041c984fbb4bfa2e'
inputs[str(failure)]=sha(failure)
for name in ('bus_test.py','bus_policy.py'):
 prior=REPO/'implementation/elm-gui-bounds-native-v272/qa'/name
 assert prior.read_bytes()==(ROOT/'qa'/name).read_bytes()
 inputs[str(prior)]=sha(prior)
compiled=json.loads((module.GUI_BUILD/'report.json').read_text());assert compiled['passed'] and len(compiled['commands'])==21 and all(c['exitCode']==0 for c in compiled['commands'])
producer=REPO/'implementation/elm-focus-recovery-pinned-toolchain-v349'
for name,digest in compiled['inputs'].items():
 assert sha(producer/name)==digest
 inputs[str(producer/name)]=digest
for name,digest in compiled['artifacts'].items():
 assert sha(module.GUI_BUILD/name)==digest
 inputs[str(module.GUI_BUILD/name)]=digest
for name in ('SPEC.md','parents.json','qa/toolchain.json','component-manifest.json'):
 inputs[str(producer/name)]=sha(producer/name)
# Original physical input, view joining, receipt/ACK/RGB helpers stay exact.
for name in ['gui.py','inspection.py']:
 original=REPO/'implementation/elm-gui-bounds-native-v279/qa'/name
 expected=original.read_text()
 if name=='gui.py':
  for before,after in json.loads((ROOT/'qa/observation-amendment.json').read_text()):
   assert expected.count(before)==1;expected=expected.replace(before,after)
 assert expected==(ROOT/'qa'/name).read_text()
actual=ast.parse(code);original=ast.parse((REPO/'implementation/elm-gui-bounds-native-v279/qa/native.py').read_text())
get_run=lambda t: next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='run')
a,b=get_run(original),get_run(actual)
# Scope text is descriptive; all behavioral calls and nested bodies must match.
for n in ast.walk(a):
 if isinstance(n,ast.Constant) and isinstance(n.value,str):n.value=n.value.replace('on278/Core205/206/AQ155','on349(same333)/Core205/594/AQ155')
assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False),'Original22-profile execution/oracles/deadlines drift'
report={'passed':True,'sourceHeld':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Reviewed additive22 actualGUI matrix: no direct effect dispatch, exact profiles, original deadlines, real input/receipts/ACK+pixels and ordered cleanup; source/build/runtime closure only','profileCount':22,'inputs':inputs,'currentScopedNativeChecks':626,'rendererCohort40StillPending':True}
with (ROOT/'qa/preflight.json').open('x') as f:f.write(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':True,'profiles':22,'inputs':len(inputs)}))
