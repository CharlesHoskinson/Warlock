"""Formal-only stage. A failed initial model is retained; runtime must be absent."""
from pathlib import Path
import hashlib,json,stat,subprocess,time
B=Path(__file__).resolve().parent
FILES=[B/'CONTRACT.md',B/'SOURCE_API_REVIEW.md',B/'qml_lifetime.qnt',B/'prove_before.py',B/'initial-model.qnt',B/'initial-contract.md',B/'initial-prove-before.py',B/'formal-before-runtime.json']
HEADERS=[Path(n)for n in('/usr/include/qt6/QtQml/qqmlengine.h','/usr/include/qt6/QtQml/qqml.h','/usr/include/qt6/QtCore/qpointer.h','/usr/include/bits/dlfcn.h','/usr/lib/qt6/qml/Quickshell/quickshell-core.qmltypes')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if list(B.glob('*.cpp'))or list(B.glob('*.so')):raise ValueError('Root review must precede provider runtime implementation')
 before={str(p):dict(sha256=sha(p),mode=stat.S_IMODE(p.stat().st_mode))for p in FILES+HEADERS}
 commands=[['quint','test',str(B/'qml_lifetime.qnt')],['quint','run',str(B/'qml_lifetime.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']];rows=[]
 for c in commands:
  r=subprocess.run(c,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 unchanged=all(sha(Path(p))==v['sha256']and stat.S_IMODE(Path(p).stat().st_mode)==v['mode']for p,v in before.items());good=unchanged and all(r['exitCode']==0 for r in rows)
 row=dict(result='pass'if good else'fail',inputs=before,commands=rows,sourceUnchanged=unchanged,runtimeImplemented=False,runtimeLoaded=False,rootReviewRequiredBeforeRuntime=True,nativeLaunch=False,mainChanges=False,privateGUIAccepted=False,batchConsumerAccepted=False)
 path=B/('formal-refined-before-runtime.json'if good else f'model-failure-{time.time_ns()}.json')
 if path.exists():raise ValueError('Retain existing formal checkpoint')
 path.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({k:v for k,v in row.items()if k not in('inputs','commands')}));return int(not good)
if __name__=='__main__':raise SystemExit(main())
