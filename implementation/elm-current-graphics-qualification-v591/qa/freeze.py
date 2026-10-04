import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((ROOT/'qa/preflight.json').read_text());assert p['passed'] and len(p['checks'])==1842
for name,h in p['inputs'].items():assert sha(pathlib.Path(name))==h,name
claims=json.loads((ROOT/'qa/claims-report.json').read_text());assert claims['passed'] and len(claims['checks'])==12 and sha(ROOT/'qa/webgpu_claim.py')==claims['sourceSHA256']
rows=[]
for f in sorted(ROOT.rglob('*')):
 if f.name in ['component-manifest.json','freeze-receipt.json']:continue
 if f.is_symlink():rows.append({'path':str(f.relative_to(ROOT)),'symlink':str(f.readlink())})
 elif f.is_file():rows.append({'path':str(f.relative_to(ROOT)),'sha256':sha(f),'size':f.stat().st_size})
m=ROOT/'component-manifest.json';m.write_text(json.dumps({'schema':1,'sourceHeld':True,'nativeAcceptance':False,'scope':'Current205/206/AQ155/runtime216 GUI521-derived QA graphics source/build readiness only','cpuPreflightChecks':1842,'cpuClaimsChecks':12,'mainDesktopActions':False,'files':rows},indent=2)+'\n');r={'passed':True,'manifestSHA256':sha(m),'files':len(rows),'nativeAcceptance':False};(ROOT/'qa/freeze-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
