"""Own fresh original capture-resource reconciliation and native protocol sources."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[('warlock-preview-provider-v104','warlock-preview-provider-v105'),('warlock-family-style-crop-capture-v18','warlock-family-style-crop-capture-v19')]
for old,new in rows:
 root=repo/'implementation'/old;target=repo/'implementation'/new;assert not target.exists(),target
 m=root/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed']
 for rel,row in d['files'].items():assert sha(root/rel)==row['sha256'],rel
 def ignore(path,names):
  p=pathlib.Path(path)
  if p==root:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','native-build-report.json','__pycache__'}]
  if p==root/'qa':return [n for n in names if (p/n).is_dir() and n!='toolchain']
  return [n for n in names if n in {'elm-stuff','__pycache__'}]
 shutil.copytree(root,target,ignore=ignore)
 (target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(root),'parentManifestSHA256':sha(m),'purpose':'Actual original native capture/export resource observation and scoped idempotent cleanup, including lost export-release acknowledgment, lock/expiry/revocation and pre-mapping capture Unknown. Original capture intent/counter/context/deadline remain retained; original local FD/readers/Broker proofs and control confirmation independently gate reclamation. Never recapture Unknown or retire another capture/window incarnation. Core16 remains owning ABI; new plugin19 and GUI105 are inactive until qualification.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2','implementation/warlock-preview-provider-v105',['PROGRESS ownGUI105/plugin19 actual original capture/export resource state and scoped idempotent cleanup; retain exact original capture request across response/FD failures, do not recapture or erase independent local FD/readers/proof/control obligations. Held10451capture+22sealed-FD controls,14/66/816/three native capture model variants,10190controlled C/260actors/1041tickets,full95. Original failed unused-fixture-function compile retained. Current public71 verified359f68251029daf00f15fa2a927614ff5bc5401e;localreceiptc6c8be67921938947fe106ced58d6b8bf0f8ba8f. Qualified runtimeGUI92/native128/core16/plugin18 and original real-capture/turnover/release gates remain unchanged. No installed/main desktop/draft changes.'],'progress',['implementation/warlock-preview-provider-v104/component-manifest.json','implementation/warlock-preview-provider-v105/ANCESTRY.json','implementation/warlock-family-style-crop-capture-v19/ANCESTRY.json']))
