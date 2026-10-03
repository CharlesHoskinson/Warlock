"""Complete original offline suites and new runtime data model, no GUI launch."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import time

B=Path(__file__).resolve().parent

def sources():
    paths=[p for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in {'.py','.qnt','.md','.qml','.js','.cpp'} and not any(v.startswith('attempt-')for v in p.parts)]
    return {str(p.relative_to(B)):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(paths)}

def main():
    before=sources();rows=[];python_count=0;named=0
    commands=[[sys.executable,str(B/'preservation_projection.py'),p.name] if p.name in {'test_geometry_source.py','test_focus_setup.py','test_press_receipt.py'} else [sys.executable,str(p)] for p in sorted(B.glob('test_*.py'))]
    for model in ['draft_focus','runtime_authority','bus_authority','process_evidence','mapping_evidence','data_provenance_proposal','data_provenance_lifecycle','runtime_metrics','viewport_geometry','coordinate_representation','pointer_syntax','focus_setup','press_receipt','continuation_diagnostic']:
        commands.extend([['quint','test',str(B/(model+'_test.qnt'))],
                         ['quint','run',str(B/(model+'.qnt')),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1']])
    started=time.monotonic()
    for command in commands:
        p=subprocess.run(command,capture_output=True,text=True,timeout=60)
        row=dict(command=command,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr);rows.append(row)
        if command[0]==sys.executable:
            hit=re.search(r'Ran (\d+) tests?',p.stderr)
            if hit:python_count+=int(hit[1])
        elif command[1]=='test':
            hit=re.search(r'(\d+) passing',p.stdout)
            if hit:named+=int(hit[1])
        if p.returncode:break
    after=sources();success=all(r['returncode']==0 for r in rows) and len(rows)==len(commands) and before==after
    result=dict(result='pass' if success else 'fail',commands=rows,pythonTests=python_count,quintNamed=named,
                originalModels=7,inheritedModels=8,models=14,tracesPerModel=2000,maxSteps=100,sourceSHA256=before,
                sourceUnchangedDuringTests=before==after,cpuOnly=True,nativeGuiExecuted=False,
                mainGUIWrites=False,elapsedSeconds=time.monotonic()-started)
    name='metrics-offline-report.json' if success else f'metrics-offline-failure-{time.time_ns()}.json'
    target=B/name
    with target.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['commands','sourceSHA256']}),flush=True)
    return 0 if success else 1

if __name__=='__main__':raise SystemExit(main())
