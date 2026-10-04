"""Read-only live observer check, including bounded idle rate and normal close."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import select
import subprocess
import sys
import time

sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope, verify_parent
BASE=Path(__file__).resolve().parents[1]

def clients():
    values=json.loads(subprocess.check_output(['hyprctl','clients','-j'],text=True,timeout=3))
    return sorted([(w.get('address'),w.get('stableId'),w.get('pid'),w.get('at'),w.get('size'),w.get('workspace'),w.get('pinned')) for w in values])

def main():
    require_qa_scope()
    parser=argparse.ArgumentParser()
    parser.add_argument('--seconds',type=float,default=18)
    args=parser.parse_args()
    parent=verify_parent(os.environ)
    before=clients()
    proc=subprocess.Popen([str(BASE/'hypr-taskbar'),'observe'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    data=b'';rows=[];errors=b'';failure=None;closed=False
    start=time.monotonic()
    try:
        while time.monotonic()-start<args.seconds:
            ready,_,_=select.select([proc.stdout,proc.stderr],[],[],.2)
            for stream in ready:
                chunk=os.read(stream.fileno(),65536)
                if stream==proc.stderr:
                    errors+=chunk
                    if len(errors)>65536:raise ValueError('Diagnostic output exceeded bound')
                else:
                    if not chunk:raise ValueError('Observer exited before smoke end')
                    data+=chunk
                    if len(data)>4*1024*1024:raise ValueError('Unframed observer output exceeded bound')
                    while b'\n' in data:
                        line,data=data.split(b'\n',1)
                        value=json.loads(line)
                        if value.get('protocolVersion')!=1 or value.get('sequence')!=len(rows)+1 or rows and value.get('epoch')!=rows[0]['epoch']:raise ValueError('Stream ordering changed')
                        rows.append(dict(epoch=value['epoch'],sequence=value['sequence'],atSeconds=time.monotonic()-start,
                                         groupKeys=[g['key'] for g in value['groups']],windowIdentities=sorted((w['address'],w.get('stableId'),w.get('pid')) for g in value['groups'] for w in g['windows'])))
                        if len(rows)>20:raise ValueError('Observed idle refresh feedback loop')
        if not rows:raise ValueError('No actual selected-instance observation')
        proc.stdin.close();proc.stdin=None;closed=True
        tail,diagnostics=proc.communicate(timeout=8)
        if len(tail)>4*1024*1024:raise ValueError('Closing output exceeded bound')
        errors+=diagnostics
        if proc.returncode!=0:raise ValueError('Observer did not close normally')
    except Exception as error:
        failure=repr(error)
    finally:
        if not closed and proc.stdin is not None:proc.stdin.close()
        if proc.poll() is None:
            proc.terminate()
            try:proc.wait(timeout=8)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
    after=clients()
    preserved=before==after
    report=dict(result='pass' if failure is None and preserved else 'fail',error=failure,seconds=time.monotonic()-start,
                observations=rows,stderr=errors.decode(errors='replace'),returncode=proc.returncode,
                windowIdentityGeometryWorkspacePinPreserved=preserved,before=before,after=after,
                helperSHA256=hashlib.sha256((BASE/'hypr-taskbar').read_bytes()).hexdigest(),parent=parent,
                scope='read-only observation only; no popup/input/minimize/restore acceptance')
    path=BASE/'tests'/('native-observer-report.json' if report['result']=='pass' else 'native-observer-failure-'+str(time.time_ns())+'.json')
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(result=report['result'],snapshots=len(rows),seconds=report['seconds'],report=str(path),error=failure)))
    return int(report['result']!='pass')

if __name__=='__main__':raise SystemExit(main())
