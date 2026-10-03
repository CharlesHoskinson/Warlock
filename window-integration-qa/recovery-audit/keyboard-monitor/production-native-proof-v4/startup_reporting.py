"""Owned live evidence and immutable first-error reporting; no input/publishers."""
import hashlib,json,time,traceback
from pathlib import Path
import host_acceptance

def live_transport(paths,guard,report,seconds=12,clock=time.monotonic,pause=time.sleep):
    deadline=clock()+seconds
    while True:
        guard();logs=[];files=[]
        for path in paths:
            path=Path(path)
            try:
                blob=path.read_bytes();logs.append(blob.decode());files.append(dict(path=str(path),bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest()))
            except OSError as error:logs.append('');files.append(dict(path=str(path),readError=repr(error)))
        result=host_acceptance.transport(logs)
        report['lastStartupTransport']=dict(**result,files=files)
        if result['forbiddenDiagnostics']:raise RuntimeError('actual startup parent transport failure: '+repr(result['forbiddenDiagnostics']))
        if result['pass_']:return result
        if clock()>=deadline:raise TimeoutError('actual startup mandatory-parent/configure proof unavailable before deadline')
        pause(.08)

def failure(report,error,stage):
    entry=dict(stage=stage,type=type(error).__name__,error=repr(error),traceback=traceback.format_exc())
    report.setdefault('failures',[]).append(entry);report['result']='failed'
    report.setdefault('error',entry['error']);report.setdefault('traceback',entry['traceback']);report.setdefault('firstFailureStage',stage)

def archive_terminal(received,folder,report):
    if received is None or not received.exists():report['terminalReceiverBytesAvailable']=False;return
    blob=received.read_bytes();target=Path(folder)/'native-terminal.bin';target.write_bytes(blob);target.chmod(0o600)
    report['terminalReceiverBytesAvailable']=True;report['terminalBytes']=blob.hex()

def summary(report,path):
    checks=report.get('checks',[]);preservation=report.get('restoration',{})
    return dict(result=report.get('result'),checks=len(checks),passed=sum(bool(row['pass_']) for row in checks),
        preservation=len(preservation),preserved=sum(bool(ok) for ok in preservation.values()),
        failedPreservation=[name[:80] for name,ok in preservation.items() if not ok][:32],
        phases=[dict(name=row['name'],pass_=row.get('pass_',False),checks=row.get('checks',0)) for row in report.get('phases',[])][:3],
        error=str(report.get('error',''))[:1024],failureStage=report.get('firstFailureStage'),failureCount=len(report.get('failures',[])),
        report=str(path),reportSHA256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        privateCompositorPID=report.get('hostEvidence',{}).get('compositorPID'),runtimeGone=report.get('hostEvidence',{}).get('runtimeGone'),
        nativePointerProved=report.get('nativePointerProved',False),nativeInputProved=report.get('nativeInputProved',False))
