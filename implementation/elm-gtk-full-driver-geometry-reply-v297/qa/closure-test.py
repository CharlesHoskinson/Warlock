import hashlib,json,os,resource,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'elm-gtk-full-driver-v260';BASE=ROOT.parent/'elm-gtk-privileged-helper-drain-v282';OUT=ROOT/'qa'/('closure-'+str(time.time_ns()));OUT.mkdir()
report={'passed':False,'nativeAcceptance':False,'checks':[]}
def check(n,b):assert b,n;report['checks'].append({'name':n,'passed':True})
try:
 names=['owned_bus_host.py','private_bus.py','activation-supervisor.py','activation_import.py','cleanup.py','placement.py','protocol.py','credentials.py','outcomes.py']
 for name in names:check('exact282-'+name,(ROOT/'qa/helpers'/name).read_bytes()==(BASE/'qa'/name).read_bytes())
 source_names=['driver.py','shell.py','popup.py','keyboard.py','native.py','fault-native.py','observer_endpoint.py','client_evidence.py']
 for name in source_names:
  expected=(OLD/'qa'/name).read_bytes()
  if name=='driver.py':expected=expected.replace(b"g['windows']",b"g['facts']['windows']").replace(b"geo['windows']",b"geo['facts']['windows']")
  check('original-full260-with-declared-geometry-delta-'+name,(ROOT/'qa'/name).read_bytes()==expected)
 code='import sys,pathlib;sys.path.insert(0,sys.argv[1]);import owned_bus_host,private_bus,activation_import,credentials,outcomes,cleanup,placement,protocol;mods=[owned_bus_host,private_bus,activation_import,credentials,outcomes,cleanup,placement,protocol];assert all(pathlib.Path(m.__file__).parent==pathlib.Path(sys.argv[1]) for m in mods);print("fresh-matching-local-modules")'
 p=subprocess.run(['/usr/bin/python3','-B','-c',code,str(ROOT/'qa/helpers')],capture_output=True,timeout=3);(OUT/'import.stdout').write_bytes(p.stdout);(OUT/'import.stderr').write_bytes(p.stderr);check('fresh-process-complete-import',p.returncode==0 and p.stdout==b'fresh-matching-local-modules\n')
 p=subprocess.run(['/usr/bin/python3','-B',str(ROOT/'qa/helpers/activation-supervisor.py'),'--invalid-safe'],env=dict(os.environ,XDG_RUNTIME_DIR='/tmp'),capture_output=True,timeout=3);(OUT/'invalid.stdout').write_bytes(p.stdout);(OUT/'invalid.stderr').write_bytes(p.stderr);check('actual-supervisor-reject-before-any-child',p.returncode!=0 and b'ModuleNotFoundError' not in p.stderr and b'verify_runtime' in p.stderr and not p.stdout)
 report['passed']=True
finally:
 report['inputs']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__)]+list((ROOT/'qa/helpers').glob('*.py'))+[ROOT/'qa'/n for n in source_names]};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
