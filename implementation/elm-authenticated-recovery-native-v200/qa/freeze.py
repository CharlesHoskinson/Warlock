"""Freeze real receipt-loss and same-authenticated-sender native proof."""
import ast,hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def find(name,kind):return next((REPO/'implementation'/name/'qa').glob(kind+'-*/report.json'))
paths={'nativeLostReceipt':find('elm-lost-receipt-native-v197','native'),'nativeOriginalSender':find('elm-authenticated-recovery-native-v200','native'),'buildLostReceipt':find('elm-window-fault-v195','build'),'buildOriginalSender':find('elm-authenticated-fault-v198','build'),'filesystemLostReceipt':find('elm-window-fault-v195','journal'),'filesystemOriginalSender':find('elm-authenticated-fault-v198','journal'),'upstream':REPO/'implementation/elm-journal-native-v193/qa/slice-manifest.json'}
data={k:json.loads(p.read_text()) for k,p in paths.items()}
assert all(d['passed'] for d in data.values())
for native,count in [('nativeLostReceipt',52),('nativeOriginalSender',55)]:
 n=data[native];assert n['cleanupPassed'] and len(n['checks'])==count and all(c['passed'] for c in n['checks'])
 for p,digest in n['inputs'].items():assert sha(Path(p))==digest,p
 marker=n['lostReceiptMarker'];assert marker['outcome']['status']=='Committed' and marker['durableRecord']['status']=='Pending' and marker['outcome']['intent']==marker['durableRecord']['intent']
 assert n['cohortCleanup'][-1]['remaining']==[] and len(n['supervisorEvents']['starts'])==2
 assert n['supervisorEvents']['exits'][0]['exitCode']==3 and n['supervisorEvents']['exits'][1]['exitCode']==1
 buildkey='buildOriginalSender' if count==55 else 'buildLostReceipt'
 assert sha(Path(n['buildReport']))==n['buildReportSHA256']==sha(paths[buildkey])
 for part in ['core','plugin']:
  item=n['pair'][part];assert sha(Path(item['path']))==item['sha256']
for name,sources,sup in [('buildLostReceipt','elm-window-fault-v195','elm-fault-supervisor-v196'),('buildOriginalSender','elm-authenticated-fault-v198','elm-authenticated-supervisor-v199')]:
 b=data[name]
 for relative,digest in b['inputs'].items():assert sha(REPO/'implementation'/sources/relative)==digest,relative
 for stem,count in [('replay',20),('shell',27),('recovery',30)]:
  r=json.loads((paths[name].parent/(stem+'-report.json')).read_text());assert r['passed'] and r['checks']==count
 capsule=json.loads((REPO/'implementation'/sup/'runtime-manifest.json').read_text());assert len(capsule['files'])==20
 assert sha(Path(capsule['host']))==b['binarySHA256']
 for p,digest in capsule['files'].items():assert sha(Path(p))==digest,p
for name in ['filesystemLostReceipt','filesystemOriginalSender']:
 d=data[name];assert len(d['checks'])==19 and all(c['passed'] for c in d['checks'])
 for p,digest in d['inputs'].items():assert sha(Path(p))==digest,p
n=data['nativeOriginalSender'];marker=n['lostReceiptMarker'];sender=marker['senderProof']
assert sender['pid']==marker['pid'] and sender['start']==marker['start'] and sender['originalBinding']==marker['binding']
assert sender['request']['binding']==sender['originalBinding'] and sender['request']['intent']==marker['outcome']['intent']
assert sender['renewedBinding']['session']==sender['originalBinding']['session'] and int(sender['renewedBinding']['frontend'])==int(sender['originalBinding']['frontend'])+1
assert sender['result']=={'kind':'authenticated-native-refusal','reason':'binding-mismatch'}
assert sender['before']['facts']==sender['after']['facts'] and sender['before']['revision']==sender['after']['revision']
original=REPO/'implementation/elm-renderer-recovery-v170/qa/native.py'
def fn(path,name):return next(v for v in ast.walk(ast.parse(path.read_text())) if isinstance(v,ast.FunctionDef) and v.name==name)
for campaign in ['elm-lost-receipt-native-v197','elm-authenticated-recovery-native-v200']:
 for name in ['check','wait','click','choose','press_key','key_recipient']:assert ast.dump(fn(original,name),include_attributes=False)==ast.dump(fn(REPO/'implementation'/campaign/'qa/native.py',name),include_attributes=False)
names=['elm-window-fault-v195','elm-fault-supervisor-v196','elm-lost-receipt-native-v197','elm-authenticated-fault-v198','elm-authenticated-supervisor-v199','elm-authenticated-recovery-native-v200']
files=[p for name in names for p in sorted((REPO/'implementation'/name).rglob('*')) if p.is_file() and not p.is_symlink() and p!=ROOT/'qa/slice-manifest.json'];assert not any(p.is_symlink() for name in names for p in (REPO/'implementation'/name).rglob('*'))
result={'passed':True,'scope':'Actual native committed action/lost receipt and same-sender rehandshake refusal; existing/replacement actual Unknown DOM, no automatic replay and fresh explicit action; frontend admission/global revocation/full release open','nativeLostReceiptChecks':52,'nativeOriginalSenderChecks':55,'filesystemSubprocessChecksPerCandidate':19,'compiledRecoveryChecksPerCandidate':30,'compiledInheritedReducerChecksRerunPerCandidate':20,'compiledInheritedShellChecksRerunPerCandidate':27,'nativeInterruptedEffectAcceptance':True,'sameAuthenticatedSenderRehandshakeReplayRefused':True,'formerLiveSenderGlobalRevocationAcceptance':False,'frontendDurableAdmissionAcceptance':False,'sealedRuntimeFilesPerCandidate':20,'noAutomaticResubmissionObservedMilliseconds':500,'originalHelpersAndDeadlinesUnchanged':True,'cleanupPassed':True,'completedRequirementIds':[],'performanceBudgetsAccepted':False,'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p),'retainedNotRerun':k=='upstream'} for k,p in paths.items()},'files':{str(p.relative_to(REPO)):sha(p) for p in files}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['files','evidence']}))
