"""Require actual non-input producer roundtrip; preserve PID/exit/stderr errors."""
import json,select,subprocess,time
from pathlib import Path

def ready(process,report,stderr_path=None,label='native producer',timeout=6):
    row=dict(label=label,pid=process.pid,request='sync',inputSent=False,started=time.monotonic())
    report.setdefault('producerReadiness',[]).append(row)
    try:
        if process.poll() is not None:raise RuntimeError('producer exited before readiness')
        process.stdin.write('sync\n');process.stdin.flush()
        readable,_,_=select.select([process.stdout],[],[],timeout)
        if not readable:raise TimeoutError('producer readiness timed out')
        response=process.stdout.readline();row['response']=response.strip()
        if response!='ready\n' or process.poll() is not None:raise RuntimeError('producer returned invalid readiness or exited')
        row.update(pass_=True,exitCode=None,completed=time.monotonic());return row
    except Exception as error:
        try:process.wait(timeout=.2)
        except subprocess.TimeoutExpired:pass
        row.update(pass_=False,error=repr(error),exitCode=process.poll(),completed=time.monotonic())
        if stderr_path is not None:
            path=Path(stderr_path);row['stderrPath']=str(path)
            if path.exists():row['stderrTail']=path.read_bytes()[-4096:].decode(errors='replace')
        elif process.poll() is not None and process.stderr is not None:
            data=process.stderr.read(4096);row['stderrTail']=data.decode(errors='replace') if isinstance(data,bytes) else data
        raise RuntimeError('producer startup failed: '+json.dumps(row)) from error
