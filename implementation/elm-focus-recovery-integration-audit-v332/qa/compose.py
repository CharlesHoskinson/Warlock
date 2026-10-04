import hashlib,json,os,resource,shutil,time,traceback
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/'qa'/('review-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 refs={}
 def inventory(path,digest):
  assert sha(path)==digest,path
  m=json.loads(path.read_text());rows=m['files'];rows=rows if isinstance(rows,list) else [dict(path=k,**v) for k,v in rows.items()]
  for row in rows:
   p=REPO/row['path']
   if 'symlink' in row:assert p.is_symlink() and os.readlink(p)==row['symlink'],p
   else:assert sha(p)==row['sha256'] and p.stat().st_size==row['size'],p
  refs[str(path)]=digest;return len(rows)
 report['reviewed331Files']=inventory(REPO/'implementation/elm-focus-recovery-held-v331/acceptance-manifest.json','7600fa859fc2e41a054a646de9a4cf3953a977c9562f87aaff07e635258b5b51')
 report['reviewed648Files']=inventory(REPO/'implementation/elm-reconciliation-scoped-general-reviewed-v648/component-manifest.json','bcd53d5abc424cae817372b715084837b8eaa2d37a69d27adad95c24ee7e1b99')
 primary=REPO/'implementation/elm-recovery-delivery-integrated-gui-v640';presentation=REPO/'implementation/elm-focus-visible-surfaces-gui-v327';base=REPO/'implementation/elm-reconciliation-startup-order-v626'
 build=primary/'qa/build-1791153819143987946/report.json';b=json.loads(build.read_text());assert b['passed'] and all(c['exitCode']==0 for c in b['commands'])
 production={str(p.relative_to(primary)):sha(p) for root in ['src','native','adapter','assets'] for p in (primary/root).glob('*') if p.is_file()}
 for name,d in production.items():assert b['inputs'][name]==d,(name,'current640 changed after build')
 changes=sorted(name for name,d in production.items() if not (base/name).exists() or sha(base/name)!=d)
 assert changes==['adapter/delivery_ledger.py','adapter/reconciliation.py','adapter/recovery_store.py','src/ReconciliationTracking.elm','src/SurfaceController.elm'],changes
 assert (presentation/'src/SurfaceRenderer.elm').read_text().split('view :')[0]==(primary/'src/SurfaceRenderer.elm').read_text().split('view :')[0],'renderer API/action mapping changed'
 for name in ['src/SurfaceRenderer.elm','assets/shell.css','assets/context.js','assets/bar-adapter.js']:assert sha(primary/name)==sha(base/name),name
 target=REPO/'implementation/elm-focus-recovery-integrated-gui-v333';target.mkdir()
 for root in ['src','native','adapter','assets']:
  (target/root).mkdir()
  for p in (primary/root).glob('*'):
   if p.is_file():shutil.copy2(p,target/root/p.name)
 shutil.copy2(primary/'elm.json',target/'elm.json');(target/'qa').mkdir()
 for name in ['build.py','run.py','drain.py','controls.py','Probe.elm','probe.cjs']:shutil.copy2(primary/'qa'/name,target/'qa'/name)
 for name in ['src/SurfaceRenderer.elm','assets/shell.css','assets/context.js','assets/bar-adapter.js']:shutil.copy2(presentation/name,target/name)
 # Exercise this candidate's actual Python authority/store, retaining630 captured fixture.
 drain=target/'qa/drain.py';text=drain.read_text();assert text.count("sys.path.insert(0,str(SOURCE/'adapter'))")==1;drain.write_text(text.replace("sys.path.insert(0,str(SOURCE/'adapter'))","sys.path.insert(0,str(ROOT/'adapter'))"))
 (target/'SPEC.md').write_text('Coherent333 retains every640 production source except four explicit327 presentation files: view-only SurfaceRenderer label/detail/title, bounded complete confirmation CSS, guarded recovery keyboard scope, and already-admitted native bar-focus nearest reveal.640 fixes historical informational/released-scope recovery. All native C/authority/schema/Elm reducer/adapter sources are exact640; no replay or fabricated outcome change. Current production compilation/public51 and actual own adapter drain21 must rerun. Parent626135/473 and327synthetic104 are ancestry only; current333 native qualification is required. No installed actions, full roadmap/release/ATIME/hardware/budgets/rollback remain open.
')
 captured={name:sha(primary/name) for name in production};assert captured==production,'source changed while composing'
 effective={name:sha(target/name) for name in production}
 changed=sorted(name for name in production if effective[name]!=production[name]);assert changed==['assets/bar-adapter.js','assets/context.js','assets/shell.css','src/SurfaceRenderer.elm'],changed
 refs[str(build)]=sha(build)
 for name in ['tests-1791153820316433749','drain-1791153891368556594','controls-1791153924910941912']:
  p=primary/'qa'/name/'report.json';m=json.loads(p.read_text());assert m['passed'];refs[str(p)]=sha(p)
 report.update(passed=True,primaryProductionPins={str(primary/name):d for name,d in production.items()},candidateProductionPins=effective,primaryChangesFrom626=changes,candidateChangesFrom640=changed,references=refs,candidate=str(target),scope='Source/API composition closure only; current333 native effects and full release unaccepted')
 (target/'lineage.json').write_text(json.dumps(report,indent=2)+'\n')
except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(OUT/'report.json'),'passed':report['passed'],'error':report.get('error'),'candidate':report.get('candidate')}));raise SystemExit(not report['passed'])
