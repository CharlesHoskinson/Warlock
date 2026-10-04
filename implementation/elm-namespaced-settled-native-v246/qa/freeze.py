"""Freeze actual durable host admission, unread recovery, settlement and failures."""
import ast,hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def find(name,kind):return next((REPO/'implementation'/name/'qa').glob(kind+'-*/report.json'))
paths={'nativeUnread':find('elm-before-write-native-v213','native'),'nativeSettled':find('elm-admission-settled-native-v214','native'),'build':find('elm-before-write-fault-v211','build'),'admission':find('elm-before-write-fault-v211','admission'),'journal':find('elm-before-write-fault-v211','journal'),'model':find('elm-admission-model-v207','model'),'failedSelection':find('elm-unread-broker-native-v204','native'),'failedSelectionDiagnostic':find('elm-unread-broker-native-v205','native'),'failedEarlyStop':find('elm-unread-broker-native-v206','native'),'failedStaleProjectionStop':find('elm-before-read-native-v210','native'),'upstream':REPO/'implementation/elm-authenticated-recovery-native-v200/qa/slice-manifest.json'}
data={k:json.loads(p.read_text()) for k,p in paths.items()}
for k,d in data.items():assert d['passed']==(not k.startswith('failed')),k
for name,count in [('nativeUnread',57),('nativeSettled',43)]:
 n=data[name];assert n['cleanupPassed'] and len(n['checks'])==count and all(c['passed'] for c in n['checks'])
 for p,digest in n['inputs'].items():assert sha(Path(p))==digest,p
 assert sha(Path(n['buildReport']))==n['buildReportSHA256']==sha(paths['build'])
 assert len(n['supervisorEvents']['starts'])==2 and n['cohortCleanup'][-1]['remaining']==[]
 for part in ['core','plugin']:
  item=n['pair'][part];assert sha(Path(item['path']))==item['sha256']
n=data['nativeUnread'];fault=n['unreadBrokerFault'];marker=n['beforeWriteMarker'];assert fault['admitted']['status']=='Pending' and fault['priorBrokerRecord']['status']=='Committed' and int(fault['admitted']['intent']['request'])==int(fault['priorBrokerRecord']['intent']['request'])+1
assert marker['request']==fault['request'] and int(marker['brokerPID'])==fault['broker']['pid'] and marker['stage']=='after-durable-admission-and-publication-before-broker-write'
for name,count in [('admission',22),('journal',19)]:
 d=data[name];assert len(d['checks'])==count and all(c['passed'] for c in d['checks'])
 for p,digest in d['inputs'].items():assert sha(Path(p))==digest,p
b=data['build']
for relative,digest in b['inputs'].items():assert sha(REPO/'implementation/elm-before-write-fault-v211'/relative)==digest,relative
for stem,count in [('replay',20),('shell',27),('recovery',30)]:
 d=json.loads((paths['build'].parent/(stem+'-report.json')).read_text());assert d['passed'] and d['checks']==count
q=data['model'];assert q['namedScenarios']==8 and q['invariantSamples']==1000 and q['maxSteps']==40
assert sha(REPO/'implementation/elm-admission-model-v207/spec/recovery.qnt')==q['sourceSHA256']
capsule=json.loads((REPO/'implementation/elm-before-write-supervisor-v212/runtime-manifest.json').read_text());assert len(capsule['files'])==20 and sha(Path(capsule['host']))==b['binarySHA256']
for p,digest in capsule['files'].items():assert sha(Path(p))==digest,p
assert data['nativeUnread']['pair']['core']['sha256']==capsule['coreSHA256']
source=(REPO/'implementation/elm-before-write-fault-v211/native/host.c').read_text();start=source.index('    if (!admission_batch(req,authority_binding))');publish=source.index('    surface_gate.publication=publication;',start);forward=source.index('    write_next();',publish);assert start<publish<forward
original=REPO/'implementation/elm-renderer-recovery-v170/qa/native.py'
def fn(path,name):return next(v for v in ast.walk(ast.parse(path.read_text())) if isinstance(v,ast.FunctionDef) and v.name==name)
for campaign in ['elm-before-write-native-v213','elm-admission-settled-native-v214']:
 for name in ['check','wait','click','choose','press_key','key_recipient']:assert ast.dump(fn(original,name),include_attributes=False)==ast.dump(fn(REPO/'implementation'/campaign/'qa/native.py',name),include_attributes=False)
names=['elm-host-admission-v201','elm-bound-admission-v202','elm-admission-supervisor-v203','elm-unread-broker-native-v204','elm-unread-broker-native-v205','elm-unread-broker-native-v206','elm-admission-model-v207','elm-before-read-fault-v208','elm-before-read-supervisor-v209','elm-before-read-native-v210','elm-before-write-fault-v211','elm-before-write-supervisor-v212','elm-before-write-native-v213','elm-admission-settled-native-v214']
files=[p for name in names for p in sorted((REPO/'implementation'/name).rglob('*')) if p.is_file() and not p.is_symlink() and p!=ROOT/'qa/slice-manifest.json'];assert not any(p.is_symlink() for name in names for p in (REPO/'implementation'/name).rglob('*'))
result={'passed':True,'scope':'Actual durable bound host admission before Pending publication/broker read; unread replacement Unknown/no replay and exact settled commit suppression; full release open','nativeUnreadChecks':57,'nativeSettledChecks':43,'actualCAdmissionFilesystemChecks':22,'actualJournalChecks':19,'compiledRecoveryChecks':30,'compiledInheritedReducerChecksRerun':20,'compiledInheritedShellChecksRerun':27,'namedQuintScenarios':8,'quintInvariantSamples':1000,'frontendDurableAdmissionAcceptance':True,'singleInflightIntentOnly':True,'storageErrorUXAccepted':False,'journalInstanceMigrationAccepted':False,'originalHelpersAndDeadlinesUnchanged':True,'cleanupPassed':True,'completedRequirementIds':[],'performanceBudgetsAccepted':False,'sealedRuntimeFiles':20,'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p),'retainedNotRerun':k=='upstream'} for k,p in paths.items()},'files':{str(p.relative_to(REPO)):sha(p) for p in files}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['files','evidence']}))
