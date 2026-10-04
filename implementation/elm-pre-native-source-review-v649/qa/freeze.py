import hashlib,json,pathlib,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((ROOT/'qa/report.json').read_text());assert r['passed'] and r['checks']==8425 and len(r['pins'])==6499 and all(v['passed'] for v in r['rows'])
for p,row in r['pins'].items():assert sha(pathlib.Path(p))==row['sha256'] and pathlib.Path(p).stat().st_size==row['size']
rows=[]
for p in sorted(ROOT.rglob('*')):
 if p.is_file() and p not in [ROOT/'component-manifest.json',ROOT/'qa/freeze-receipt.json',ROOT/'qa/protected-freeze.log']:rows.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'size':p.stat().st_size})
m=ROOT/'component-manifest.json';m.write_text(json.dumps({'sourceHeld':True,'passed':True,'verdict':r['verdict'],'sourceChecks':r['checks'],'externalPins':len(r['pins']),'nativeAcceptance':False,'newBuildOrBehaviorExecution':False,'scope':r['scope'],'files':rows},indent=2)+'\n');out={'passed':True,'files':len(rows),'manifestSHA256':sha(m),'nativeAcceptance':False};(ROOT/'qa/freeze-receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
