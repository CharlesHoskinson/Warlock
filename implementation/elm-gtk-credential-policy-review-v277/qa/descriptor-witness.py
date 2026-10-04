import importlib.util,json,resource,time,hashlib
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];n=r.parent/'elm-gtk-native-acquisition-fix-v268/qa/native-1791146650894471270/native-evidence'
spec=importlib.util.spec_from_file_location('captured_initial_outcomes',r/'initial/outcomes.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
inventory=json.loads((n/'activation-inventory.json').read_text());record=next(x for x in inventory['services'] if x['name']=='org.a11y.Bus');p=next((n/'activation-journals/org.a11y.Bus').glob('*.jsonl'));rows=[json.loads(x) for x in p.read_text().splitlines()];assert rows[-1]['error'] is None and not rows[-1]['fallback']
assert not Path(record['descriptor']).exists()
try:m.classify(record,rows)
except FileNotFoundError as error:failure=repr(error)
else:raise AssertionError('captured initial code must fail at removed runtime descriptor')
out=r/'qa'/('descriptor-witness-'+str(time.time_ns()));out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(out/'report.json').write_text(json.dumps({'passed':True,'sourceReviewPassed':False,'nativeAcceptance':False,'actualNormalJournal':str(p),'actualRuntimeDescriptorMissing':record['descriptor'],'error':failure,'inputs':{str(p):sha(p),str(n/'activation-inventory.json'):sha(n/'activation-inventory.json'),str(r/'initial/outcomes.py'):sha(r/'initial/outcomes.py')}},indent=2)+'\n');print(out/'report.json')
