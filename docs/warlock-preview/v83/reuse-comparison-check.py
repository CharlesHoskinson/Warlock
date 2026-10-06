"""Qualify new audit against archived real traces and unsafe evidence mutations."""
import copy, hashlib, importlib.util, json, pathlib, re, resource, sys, time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parent;repo=root.parents[2]
module=repo/'implementation/warlock-client-provider-native-v121/qa/reuse_comparison.py'
spec=importlib.util.spec_from_file_location('reuse_comparison',module);audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
paths=[next((repo/'implementation'/('warlock-client-provider-native-v'+str(n))).glob('qa/native-*/report.json')) for n in [118,120]]
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
out=root/('reuse-comparison-check-'+str(time.time_ns()));out.mkdir()
proofs=[json.loads(path.read_text()) for path in paths]
readonly={'styleDimPendingNativeReadonlyScope','styleAgainDimPendingNativeReadonlyScope','styleRestoreIntermediateReadonlyScope','styleCropDimIntermediateReadonlyScope'}
def stable(rows):return [re.sub(r'^opacityPrivateForeignWindowMoved-0x[0-9a-f]+$','opacityPrivateForeignWindowMoved-<native-address>',row['name']) for row in rows if row['name'] not in readonly]
report={'passed':False,'inputs':{str(path):sha(path) for path in [module,pathlib.Path(__file__),*paths]},'nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 report['actualComparison']=audit.compare(proofs[0],proofs[1],stable)
 assert report['actualComparison']['fixedOrderedControls']==2437
 assert report['actualComparison']['prior']['attempts']==9 and report['actualComparison']['current']['attempts']==1
 mutants=[]
 def caught(name,change):
  current=copy.deepcopy(proofs[1]);change(current)
  try:audit.compare(proofs[0],current,stable)
  except (AssertionError,KeyError):mutants.append({'name':name,'caught':True});return
  raise AssertionError('Unsafe evidence mutation escaped: '+name)
 caught('missing-attempt-clock',lambda d:d['checks'].__setitem__(slice(None),[row for row in d['checks'] if row['name']!='reuseAttempt1OriginalClockBeforeExpiry']))
 caught('late-attempt',lambda d:d['addressReuseAttempts'][0]['scope'].__setitem__('now',d['addressReuseEvidence']['originalFrame']['expires']))
 caught('wrong-attempt-normal-exit',lambda d:next(row for row in d['ownedExitCodes'] if row['name']=='reuse-replacement-1').__setitem__('exitCode',1))
 caught('native-address-not-reused',lambda d:d['addressReuseAttempts'][0].__setitem__('newAddress','0x0000'))
 caught('replayed-incarnation',lambda d:d['addressReuseAttempts'][0].__setitem__('newSubject',d['addressReuseEvidence']['oldSubject']))
 caught('missing-fixed-oracle',lambda d:d['checks'].__setitem__(slice(None),[row for row in d['checks'] if row['name']!='reuseHeldAndFreshURIRefusedBeforeElmNativeEffects']))
 caught('failed-fixed-oracle',lambda d:next(row for row in d['checks'] if row['name']=='reuseHeldAndFreshURIRefusedBeforeElmNativeEffects').__setitem__('passed',False))
 caught('reordered-attempt-oracles',lambda d:d['checks'].reverse())
 assert len(mutants)==8
 report.update(passed=True,unsafeMutantsDetected=8,mutants=mutants,scope='Actual archived118 nine conditional allocator trials versus120 one; each real attempt and all2437 fixed ordered identities verified. No original predicate/deadline change or new native acceptance.')
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}));sys.exit(not report['passed'])
