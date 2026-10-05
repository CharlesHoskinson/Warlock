import ast,hashlib,json,pathlib,resource,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('adoption-'+str(time.time_ns()));OUT.mkdir();r={'passed':False,'nativeAcceptance':False,'checks':[]}
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
try:
 origin=json.loads((ROOT/'index-origin.json').read_bytes());base=pathlib.Path(origin['ancestor']);assert sha(base/'component-manifest.json')==origin['manifestSHA256']
 for name in ('native.py','host_guard.py','stdlib_origin.py','selector.py','stamp.py','target.py','join.py','map_failure.py','ancestor-shell.py','ancestor-observer_endpoint.py'):
  assert (ROOT/'qa'/name).read_bytes()==(base/'qa'/name).read_bytes();r['checks'].append('byteexact351 '+name)
 for p in (base/'qa/helpers').glob('*.py'):assert p.read_bytes()==(ROOT/'qa/helpers'/p.name).read_bytes()
 for p in (base/'runtime').rglob('*'):
  if p.is_file():assert p.read_bytes()==(ROOT/'runtime'/p.relative_to(base/'runtime')).read_bytes()
 r['checks'].append('all351 helpers and owning runtime byteexact')
 old=(base/'qa/preflight.py').read_text();expected=old.replace('elm-own-popup-parallel-runtime-guard-bounded-v353','elm-own-popup-runtime-index-guard-v364').replace('held_runtime_guard353','held_runtime_guard364').replace('guard353','guard364').replace('5ac724fade372fd86af4238d642778449c3260cb8e635f51cd545998a2dac907','4d940d15d8f1cfe24d60c927939fdf9b9f5d5c7b0a778211992f067c43d9e1b6')
 assert (ROOT/'qa/preflight.py').read_text()==expected;r['checks'].append('only preflight guard source name/path/hash deltas')
 old=(base/'qa/origin-test.py').read_text();expected=old.replace('elm-own-popup-parallel-runtime-guard-bounded-v353','elm-own-popup-runtime-index-guard-v364');assert (ROOT/'qa/origin-test.py').read_text()==expected;r['checks'].append('same31 stdlib controls except owningguard pinpath')
 r.update(passed=True,inputs={str(p):sha(p) for p in [ROOT/'qa/adoption-test.py',ROOT/'qa/preflight.py',ROOT/'qa/native.py',ROOT/'qa/stdlib_origin.py']})
except BaseException as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
