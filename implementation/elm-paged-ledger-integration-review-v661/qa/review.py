import hashlib, importlib.util, json, pathlib, sys, tempfile
from unittest.mock import patch
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1]; REPO=ROOT.parents[1]
P=REPO/'implementation/elm-paged-history-storage-v647'
spec=importlib.util.spec_from_file_location('archive647', P/'adapter/archive.py'); a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
checks=[]
def check(n,v):
 if not v:raise AssertionError(n)
 checks.append(n)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((P/'component-manifest.json').read_bytes())
for name,row in m['files'].items():check('frozen647:'+name,digest(P/name)==row['sha256'] and (P/name).stat().st_size==row['size'])
for name,row in m['unchangedFrozen629Inputs'].items():check('frozen629:'+name,digest(REPO/'implementation/elm-paged-history-archive-v629'/name)==row['sha256'])
r=json.loads((P/m['report']).read_bytes());check('historical362_not_new_execution',r['passed'] and r['assertions']==362 and r['measuredLargeArchive']['retainedRecords']==1026)
real=a.hashlib.sha256
class Routed:
 def __init__(self,data,full=False):self.data=data;self.full=full
 def hexdigest(self):
  h=real(self.data).hexdigest()
  if self.data.startswith(b'{"collisionFixture":'):return '0'*64 if self.full else '0'*16+h[16:]
  return h
with tempfile.TemporaryDirectory(prefix='elm-review661-') as tmp:
 base=pathlib.Path(tmp)
 with a.Archive(base/'prefix') as store:
  with patch.object(a.hashlib,'sha256',side_effect=lambda data:Routed(data)):
   for n in range(32):store.append({'collisionFixture':n},'Unknown',a.canonical({'original':n}))
   check('shared64bit_route_32_distinct_fullkeys',all(store.lookup({'collisionFixture':n})==a.canonical({'original':n}) for n in range(32)))
   previous=dict(store.root_ref)
   try:store.append({'collisionFixture':32},'Unknown',b'{"original":32}')
   except a.Refused:check('33rd_shared64bit_route_refuses_before_publish',store.root_ref==previous)
   else:raise AssertionError('bucket should refuse')
   check('bucket_exhaustion_preserves_old32',store.root['count']==32 and store.lookup({'collisionFixture':0})==b'{"original":0}')
 with a.Archive(base/'fullcollision') as store:
  with patch.object(a.hashlib,'sha256',side_effect=lambda data:Routed(data,True)):
   store.append({'collisionFixture':1},'Unknown',b'{"first":true}')
   try:store.lookup({'collisionFixture':2})
   except a.Corrupt:check('synthetic256bit_collision_refuses_wrong_origin',True)
   else:raise AssertionError('full collision should refuse')
   check('full_collision_poisoned_no_positive_wrongkey',store.poisoned)
 with a.Archive(base/'opaque') as store:
  raw=b'{"request":18446744073709551616,"generation":true,"sequence":-1}'
  store.append({'origin':'opaque'},'Admission',raw)
  check('opaque_invalid_replay_counters_are_evidence_not_authority',store.lookup({'origin':'opaque'})==raw)
 # Deliberately invalid integration algorithm: independently append admission then watermark.
 # This tests the API's nontransactionality, not an error in its declared storage contract.
 path=base/'split'
 with a.Archive(path) as store:
  store.append({'origin':'A','event':'Admission'},'Admission',b'{"request":"7"}')
  def hook(edge):
   if edge=='before:quota:open':raise OSError('stop before separate watermark commit')
  store.hook=hook
  try:store.append({'binding':'B','event':'ReplayMaxima'},'Predecessor',b'{"request":"7"}')
  except OSError:check('split_ledger_transaction_failure_injected',True)
  else:raise AssertionError('fault not reached')
 with a.Archive(path) as store:
  check('split_transaction_admission_visible_watermark_absent',store.lookup({'origin':'A','event':'Admission'})==b'{"request":"7"}' and store.lookup({'binding':'B','event':'ReplayMaxima'}) is None)
  check('split_transaction_counterexample_requires_atomic_v7_commit',store.root['count']==1)
report={'passed':True,'checks':checks,'assertions':len(checks),'parentManifestSHA256':digest(P/'component-manifest.json'),'newExecutionScope':'read-only parent inventory plus isolated temporary actual647 primitive controls','historicalClaimsNotRerun':{'assertions':362,'records':1026,'cacheBound':64},'witnesses':['shared 64-bit route and bucket exhaustion','synthetic full-hash collision fail closed','opaque invalid replay counters accepted only as evidence','separate append commits do not form atomic ledger transaction'],'nativeAcceptance':False,'ledgerIntegrated':False,'S15Accepted':False,'powerLossQualified':False}
(ROOT/'qa/report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='checks'}))
