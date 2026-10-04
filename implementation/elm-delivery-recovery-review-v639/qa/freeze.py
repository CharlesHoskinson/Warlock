import hashlib,json,pathlib,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];SOURCE=ROOT.parent/'elm-recovery-delivery-integration-v630'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((ROOT/'qa/report.json').read_text());assert r['passed'] and r['assertions']==12 and all(c['passed'] for c in r['checks'])
for p,h in r['sourceHashes'].items():assert sha(pathlib.Path(p))==h
m=json.loads((SOURCE/'component-manifest.json').read_text());pins=m['unchangedProductionFiles']
for n,v in pins.items():assert sha(SOURCE/n)==v['sha256']
for n in ['adapter/reconciliation.py','adapter/recovery_store.py','adapter/delivery_ledger.py']:assert sha(SOURCE/n)==m['files'][n]['sha256']
assert sha(SOURCE/'adapter/delivery_ledger.py')==sha(ROOT.parent/'elm-release-delivery-attestation-v624/adapter/delivery_ledger.py')
rows=[]
for p in sorted(ROOT.rglob('*')):
 if p.is_file() and p not in [ROOT/'component-manifest.json',ROOT/'qa/freeze-receipt.json',ROOT/'qa/protected-freeze.log']:rows.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'size':p.stat().st_size})
out=ROOT/'component-manifest.json';out.write_text(json.dumps({'sourceHeld':True,'passed':True,'reviewVerdict':'changes-required','finding':'RECOVERY-639-001','source630ManifestSHA256':sha(SOURCE/'component-manifest.json'),'verified630Pins':len(pins),'assertions':12,'nativeAcceptance':False,'files':rows},indent=2)+'\n');receipt={'passed':True,'files':len(rows),'manifestSHA256':sha(out),'reviewVerdict':'changes-required'};(ROOT/'qa/freeze-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
