"""Artifact-only B14 replay. No desktop connection, process launch or mutation."""
import ast
import base64
import hashlib
import json
import os
from pathlib import Path
import stat

QA=Path('/home/hoskinson/window-integration-qa')
B=QA/'family-preparation-thumbnail-v14'
A=B/'attempt-baseline-1'
S=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-focus-transaction-v28')
HERE=Path(__file__).resolve().parent

def read(path):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode):raise ValueError('regular artifact required')
        data=b''
        while block:=os.read(fd,1048576):data+=block
        fields=lambda r:(r.st_dev,r.st_ino,r.st_size,r.st_mtime_ns,r.st_ctime_ns)
        if fields(before)!=fields(os.fstat(fd)) or fields(before)!=fields(path.lstat()):raise ValueError('artifact changed')
        return data,{'sha256':hashlib.sha256(data).hexdigest(),'mode':stat.S_IMODE(before.st_mode)}
    finally:os.close(fd)

def save(path,row):
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as stream:
        json.dump(row,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())

def main():
    sources={}
    def raw(path):
        data,stamp=read(path);sources[str(path)]=stamp;return data
    def load(path):return json.loads(raw(path))
    report=load(A/'report.json');packet=load(A/'service-retirement-2.json')
    evidence=load(A/'service-evidence.json');helpers=load(A/'completed-helpers.json')
    host=load(A/'host/host-evidence.json')
    audit=load(QA/'thumbnail-v14-root-failure-audit-v1.json')
    journal=load(A/'host/runtime-archive/hypr-window-motion/qa-family-service/journal.json')['body']
    raw(A/'terminal-helpers/helper-events.jsonl')
    raw(B/'frozen-inputs.json');raw(B/'capture_evidence.py')
    for name in ('native_desktop.py','production_motion_6d9.py','batch_preview.py','scene_controller.py'):raw(S/name)
    # Execute only the exact pure parser AST, without importing runtime modules.
    tree=ast.parse(raw(S/'owned_commands.py'))
    owner=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='OwnedCommands')
    parser=next(n for n in owner.body if isinstance(n,ast.FunctionDef) and n.name=='_focus_reply')
    parser.decorator_list=[]
    namespace={};exec(compile(ast.fix_missing_locations(ast.Module(body=[parser],type_ignores=[])),str(S/'owned_commands.py'),'exec'),namespace)
    record=packet['history'][0];profile=record['profile'];tx=profile['ownedDestinationTransaction']
    conversation=base64.b64decode(tx['stdoutBase64'],validate=True);receipts=[];offset=0
    for index,expression in enumerate(tx['expressions']):
        prefix=b'> '+expression.encode()+b'\n'
        if not conversation[offset:].startswith(prefix):raise ValueError('actual echo differs')
        line_end=conversation.index(b'\n',offset+len(prefix))
        frame=conversation[offset:line_end+3]
        parsed=namespace['_focus_reply'](frame,expression,tx['nonce'],6,2*(index+1))
        if parsed is None:raise ValueError('incomplete actual receipt')
        receipts.append(parsed[0]);offset=line_end+1
    if conversation[offset:]!=b'> ':raise ValueError('unexpected trailing conversation')
    if not tx['normalComplete'] or tx['completed']!=6 or tx['stderrBase64']!='':raise ValueError('actual transaction not normal')
    captures=[]
    for row in packet['retainedEpochSources']:
        data=raw(Path(row['retainedPath']))
        if hashlib.sha256(data).hexdigest()!=row['sha256'] or row['sha256']!=row['source']['digest']:raise ValueError('capture bytes differ')
        if row['captureCallbackDelegatedOnce'] is not True or row['sourceResultUnchanged'] is not True:raise ValueError('capture observer differs')
        captures.append({k:row['source'][k] for k in ('stableId','pid','digest','captureEpoch','pixels','insets')})
    if len(captures)!=3:raise ValueError('actual three captures missing')
    received=profile['receivedNs'];deadline=received+2000000000
    queries=[{k:r.get(k) for k in ('id','request','thread','registeredNs','finishedNs','outcome','closed','published','error','evidence')} for r in journal['readonlyOwnership']['history'] if r.get('registeredNs',0)>=received]
    # Source/helper timeNs is realtime; no mixed-clock duration inference.
    counts={}
    for row in packet['rendererEvents']:counts[row.get('event')]=counts.get(row.get('event'),0)+1
    assert not any(counts.get(n,0) for n in ('seeded','uploaded','ready','presented'))
    assert helpers['allNormal'] and helpers['allExactProcessesGone'] and helpers['allQueriesNormal']
    assert record['validated'] and not record['visual'] and not record['ready']
    result={'result':'pass','meaning':'read-only failure attribution replay; campaign remains fail',
        'campaignResult':report['result'],'recordedChecks':len(report['checks']),
        'passedChecks':sum(r['passed'] for r in report['checks']),
        'receipts':receipts,'transactionNormalComplete':True,'transactionJob':tx['job'],
        'transactionOwnership':tx['ownership'],'receivedNs':received,'originalDeadlineNs':deadline,
        'metadataValidatedMs':(profile['metadataValidatedNs']-received)/1e6,
        'capturedSources':captures,'rendererEventCounts':counts,
        'settlementReason':profile['settlementReason'],
        'results':[dict(r,fromReceiptMs=(r['committedNs']-received)/1e6) for r in record['results']],
        'allActualHelpersNormal':True,'allActualHelperLifetimesGone':True,
        'serviceQueries':helpers['serviceQueries'],'harnessQueries':helpers['harnessQueries'],
        'readonlyAfterReceipt':queries,'serviceClosed':evidence['serviceClosed'],
        'mainPreservation':report['mainPreservation'],'allFrozenInputsExact':report['allFrozenInputsExact'],
        'normalNativeUnload':report['normalNativeUnload'],'hostEvidence':host,
        'limitations':['Exact late capture/finisher blocking site not retained','No retrospective attribution to concurrent CPU scope','Realtime file/helper stamps are not monotonic span durations','Native effect returns alone do not prove pixels or seeding','Host normal exit status was not observed'],
        'sources':sources,'nativeLaunch':False,'sourceEdited':False,'runtimeEdited':False}
    for path,stamp in sources.items():
        if read(Path(path))[1]!=stamp:raise ValueError('source changed during replay')
    save(HERE/'report.json',result)
    print(json.dumps({k:result[k] for k in ('result','campaignResult','recordedChecks','passedChecks','metadataValidatedMs','rendererEventCounts','serviceQueries')}))

if __name__=='__main__':main()
