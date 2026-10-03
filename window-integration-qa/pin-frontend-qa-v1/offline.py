"""Focused CPU/source/formal evidence only; never invoke a private desktop."""
from pathlib import Path
import hashlib,json,subprocess,time
B=Path(__file__).resolve().parent
excluded=('source-controller-inputs-v1.json','source-controller-handoff-v1.json','offline-report.json')
def sources():return {str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted(B.rglob('*'))if p.is_file()and not p.is_symlink()and '__pycache__'not in p.parts and not any(s.startswith('attempt-')for s in p.parts)and p.name not in excluded}
def main():
 before=sources();commands=[]
 for model in ('pin_case.qnt','frontend_case.qnt','keyboard/chord.qnt'):
  commands+=[(B,['quint','test',str(B/model)]),(B,['quint','run',str(B/model),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1'])]
 commands += [(B,['/usr/bin/python3','-m','unittest','-v','test_frontend_authority','test_frontend_controller']),(B/'keyboard',['/usr/bin/python3','-m','unittest','-v','test_chord_keyboard']),(B/'frontend-candidate',['/usr/bin/python3','-m','unittest','-v','test_frontend']),(B,['/usr/bin/python3',str(B/'check_source.py')])]
 rows=[]
 for cwd,command in commands:
  r=subprocess.run(command,cwd=cwd,capture_output=True,text=True,timeout=120);rows.append(dict(cwd=str(cwd),command=command,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 unchanged=sources()==before;good=unchanged and all(r['exitCode']==0 for r in rows)
 row=dict(result='pass'if good else'fail',commands=rows,sourceSHA256=before,sourceUnchanged=unchanged,sourceReconstructionSeparateFromRuntimeTests=True,CPUControlledObservationsNotNativeAuthority=True,nativeLaunch=False,mainChanges=False,engineAuthorityImplemented=False,nativeRunnable=False)
 path=B/('offline-report.json'if good else f'offline-failure-{time.time_ns()}.json');path.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({k:v for k,v in row.items()if k not in('commands','sourceSHA256')}));return int(not good)
if __name__=='__main__':raise SystemExit(main())
