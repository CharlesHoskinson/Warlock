import hashlib,json,resource,time
from pathlib import Path
from archive import archive_payloads
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];owner=r.parent/'elm-own-popup-xdg-grab-provenance-v307';base=r.parent/'elm-core-keyboardless-focus-v205/build-1791139089126747676'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
assert sha(owner/'component-manifest.json')=='335b15fb98e6276d55d011ceecf6450c9a81e19df2ef72db97377698b8029a13'
m=json.loads((owner/'component-manifest.json').read_text());count=0
for section,root in [('files',owner),('externalFiles',None)]:
 for name,row in m[section].items():
  p=root/name if root else Path(name);assert sha(p)==row['sha256'] and p.stat().st_size==row['size'],name;count+=1
b=json.loads(Path(m['buildReport']).read_text());assert b['passed'] and len(b['translationUnits'])==19 and len(b['rebuiltArchiveMembers'])==19 and b['unchangedArchiveMembers']==414
assert len(b['owningHeaders'])==694 and b['exportClosure']['ancestor']==b['exportClosure']['retained']==13412
old=json.loads((base/'report.json').read_text());changed=[k for k,v in b['owningHeaders'].items() if old['owningHeaders'][k]!=v];assert changed==['src/protocols/XDGShell.hpp']
path=Path(m['buildReport']).parent
before=archive_payloads(base/'libhyprland_lib.a');after=archive_payloads(path/'libhyprland_lib.a');assert len(before)==len(after)==433
kept=0;rebuilt=0
for a,z in zip(before,after):
 assert a['name']==z['name']
 if z['name'] in b['rebuiltArchiveMembers']:assert z['sha256']==b['rebuiltArchiveMembers'][z['name']];rebuilt+=1
 else:assert a==z;kept+=1
assert kept==414 and rebuilt==19
g=json.loads((owner/'qa/getter-1791154267456611843/report.json').read_text());assert g['passed'] and not g['nativeAcceptance'] and len(g['controls'])==4
assert g['controls'][0]['exitCode']==0 and all(x['exitCode']!=0 for x in g['controls'][1:])
assert sha(g['source'])==g['sourceSHA256']
assert not m['nativeAcceptance'] and not m['installed']
report={'passed':True,'sourceReviewPassed':True,'nativeAcceptance':False,'rows':count,'archiveMembers':433,'rebuilt':19,'retained':414,'ownerManifestSHA256':sha(owner/'component-manifest.json'),'blocker':None}
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps(report,indent=2))
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size} for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
p=r/'component-manifest.json';p.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'sourceReviewPassed':True,'nativeAcceptance':False,'ownerManifestSHA256':report['ownerManifestSHA256'],'files':files,'verificationReport':str((out/'report.json').relative_to(r))},indent=2));print(json.dumps({'rows':count,'manifestSHA256':sha(p)}))
