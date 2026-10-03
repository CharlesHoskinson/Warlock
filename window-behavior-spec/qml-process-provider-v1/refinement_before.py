from pathlib import Path
import hashlib,json,subprocess,time
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 inherited=json.loads((B/'base-inherited.json').read_text());unchanged=all(sha(B/p)==h for p,h in inherited['baseSourceBeforePopup'].items());assert unchanged,'Popup runtime must remain inherited base before formal review'
 files=[B/'pin_popup.qnt',B/'CONTEXT_REFINEMENT.md',B/'refinement_before.py',B/'qt-semantics-before-popup-runtime.json'];before={str(p):sha(p)for p in files};rows=[]
 for c in [['quint','test',str(B/'pin_popup.qnt')],['quint','run',str(B/'pin_popup.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']]:
  r=subprocess.run(c,capture_output=True,text=True,timeout=180);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 stable=all(sha(p)==h for p,h in before.items());good=stable and all(r['exitCode']==0 for r in rows)
 row=dict(result='pass'if good else'fail',inputs=before,sourceUnchanged=stable,commands=rows,popupRuntimeStillExactBase=True,popupRuntimeImplemented=False,GUI=False,rootReviewRequiredBeforeRuntime=True)
 p=B/('formal-context-before-popup-runtime.json'if good else f'context-model-failure-{time.time_ns()}.json');p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(p))));return int(not good)
if __name__=='__main__':raise SystemExit(main())
