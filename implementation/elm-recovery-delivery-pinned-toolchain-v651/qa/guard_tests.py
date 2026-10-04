import hashlib,json,pathlib,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
import toolchain as guard
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'qa/guard-fixtures';OUT.mkdir();checks=[]
for name in ['valid','missing','changed','added','symlink','nonempty-lock','empty-lock','manifest-rewritten']:
 r=OUT/name;r.mkdir();(r/'qa/toolchain').mkdir(parents=True);p=r/'qa/toolchain/elm';p.write_bytes(b'synthetic compiler input');h=hashlib.sha256(p.read_bytes()).hexdigest();info={'compiler':'qa/toolchain/elm','elmHome':'qa/toolchain/elm-home','heldFiles':{'qa/toolchain/elm':{'sha256':h,'size':len(p.read_bytes())}}};manifest=r/'qa/toolchain.json';manifest.write_text(json.dumps(info));guard.ROOT=r;guard.MANIFEST_SHA256=guard.digest(manifest)
 if name=='missing':p.unlink()
 if name in ['changed','manifest-rewritten']:p.write_bytes(b'changed input')
 if name=='added':(r/'qa/toolchain/extra.elm').write_bytes(b'unknown source')
 if name=='symlink':p.rename(r/'outside');p.symlink_to(r/'outside')
 if name in ['nonempty-lock','empty-lock']:
  lock=r/'qa/toolchain/elm-home/0.19.2/packages/lock';lock.parent.mkdir(parents=True);lock.write_bytes(b'unsafe' if name=='nonempty-lock' else b'')
 if name=='manifest-rewritten':info['heldFiles']['qa/toolchain/elm']['sha256']=guard.digest(p);manifest.write_text(json.dumps(info))
 try:guard.verify();refused=False
 except AssertionError:refused=True
 ok=refused==(name not in ['valid','empty-lock']);checks.append({'name':name,'passed':ok,'refused':refused});assert ok,name
 if name=='valid':assert guard.command(['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Main.elm'])==[str(r/'qa/toolchain/elm'),'make','src/Main.elm']
report={'passed':True,'checks':checks,'scope':'Synthetic isolated fixtures execute exact provenance guard; no fixture compiler execution or actual held-file mutation'};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'guards':len(checks)}))
