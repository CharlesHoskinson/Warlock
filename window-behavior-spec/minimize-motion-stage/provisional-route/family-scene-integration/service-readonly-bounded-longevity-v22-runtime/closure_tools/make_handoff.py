"""O_EXCL source handoff after complete final proofs; no native or freeze authority."""
from pathlib import Path
import hashlib,json,os,stat
from freeze_bounded import exclusive,sha,B,MANIFEST,CHECKPOINT,HANDOFF,READY21,READY21_SHA,DESIGN_READY,DESIGN_READY_SHA

def main():
 if HANDOFF.exists() or MANIFEST.exists() or CHECKPOINT.exists():raise SystemExit('fresh unfrozen handoff destination required')
 proof=B/'bounded-source-typed-final-offline-checkpoint.json';measurement=B/'v22-source-typed-history-measurement-final.json'
 full=json.loads(proof.read_text());metrics=json.loads(measurement.read_text())
 if (full['pythonTests'],full['quintNamedScenarios'],full['quintModels'])!=(388,383,33) or not full['sourceUnchangedDuringProof']:raise ValueError('complete final gate required')
 for n,h in full['sourceSHA256'].items():
  if sha(n)!=h:raise ValueError('final proof source replaced: '+n)
 if metrics['failure'] is not None or metrics['genuineQueries']!=1031 or metrics['actualPeerDataRequests']!=1031 or not metrics['sourceUnchanged'] or not metrics['normalCurrentFDsClosed']:raise ValueError('actual final-source history measurement required')
 for n,item in metrics['sourceSHA256'].items():
  if sha(n)!=item['sha256'] or stat.S_IMODE(Path(n).stat().st_mode)!=item['mode']:raise ValueError('final measurement source replaced: '+n)
 if sha(READY21)!=READY21_SHA or sha(DESIGN_READY)!=DESIGN_READY_SHA:raise ValueError('approved ancestry/design replaced')
 inverse=B/'closure_tools/source-inverse-final.json';inv=json.loads(inverse.read_text())
 if not inv['passed'] or set(inv['existingChangedFiles'])!={'readonly_ipc.py','test_readonly_longevity.py'} or inv['inheritedTopSourceCount']!=131:raise ValueError('complete source inverse required')
 for n,h in inv['sources'].items():
  if sha(n)!=h:raise ValueError('reviewed inverse source replaced: '+n)
 local={str(f):{'sha256':sha(f),'mode':stat.S_IMODE(f.stat().st_mode)} for f in sorted(B.rglob('*')) if f.is_file() and '__pycache__' not in f.parts and f not in (HANDOFF,MANIFEST,CHECKPOINT)}
 record={'version':'service-readonly-bounded-v22-source-ready','stage':str(B),'nativeLaunch':False,'nativeAccepted':False,'productionDeployed':False,'mainChanged':False,'sourceReady':True,'frozen':False,
  'approvedDesignHandoff':str(DESIGN_READY),'approvedDesignSHA256':DESIGN_READY_SHA,'ancestorV21Handoff':str(READY21),'ancestorV21SHA256':READY21_SHA,
  'offline':{'path':str(proof),'sha256':sha(proof),'pythonTests':388,'quintNamedScenarios':383,'quintModels':33,'samplesPerModel':2000,'steps':100,'extraBoundedValidPathSamples':2000},
  'measurement':{'path':str(measurement),'sha256':sha(measurement),'genuineQueries':1031,'archivedRows':1024,'originalQueryTimeoutSeconds':1,'actualMaintenanceTimeoutSeconds':1,'sourceUnchanged':True,'fullAuditAndNormalClose':True,'concurrentFullCPUSuite':True,'unlimitedHistoryAccepted':False},
  'inverses':{'path':str(inverse),'sha256':sha(inverse),'checks':len(inv['checks']),'inheritedTopSources':131,'existingChangedFiles':inv['existingChangedFiles'],'allOriginalAssertionsAndDeadlinesUnchanged':True,'nativeEffectRecoveryFilesExact':True},
  'formalBeforeRuntime':[{ 'path':str(B/n),'sha256':sha(B/n)} for n in ('reviewed-design-v22/formal-design-before-runtime.json','normal-close-formal-before-runtime.json','current-shape-formal-before-runtime.json','current-source-shape-formal-before-runtime.json')],
  'newFields':'CURRENT_TYPED_FIELD_AUDIT.md','reviewRequest':'V22_RUNTIME_REVIEW_REQUEST.md','scope':'typed current-owner fresh readonly data only; full startup/recovery/audit/normal-close history retained',
  'remaining':['independent source review and root immutable freeze/pairing','original38 native baseline/fault campaign','current-user cancellation ingress','actor-ledger longevity','reduction/preview/actor integration','physical cadence and deployment'],
  'rootReviewCommands':['PYTHONDONTWRITEBYTECODE=1 python3 -B closure_tools/check_source_inverse.py','PYTHONDONTWRITEBYTECODE=1 python3 -B closure_tools/test_freeze_bounded.py','PYTHONDONTWRITEBYTECODE=1 python3 -B closure_tools/freeze_bounded.py'],
  'localSources':local}
 exclusive(HANDOFF,record)
 print(json.dumps({'handoff':str(HANDOFF),'sha256':sha(HANDOFF),'localSources':len(local),'nativeLaunch':False,'frozen':False}))
if __name__=='__main__':main()
