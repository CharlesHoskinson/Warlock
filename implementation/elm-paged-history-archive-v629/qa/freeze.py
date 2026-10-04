import hashlib,json,pathlib,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((ROOT/'qa/report.json').read_text());assert r['passed'] and r['namedCount']==32 and r['typedMutants']==10 and r['selected']==r['executed']
for n,h in r['sourceHashes'].items():assert sha(ROOT/n)==h
for c in r['commands']:assert c['ok'] and c.get('actualAssertionFailure',True) and sha(ROOT/'qa'/(c['name']+'.log'))==c['outputSHA256']
assert '[ok] No violation found' in (ROOT/'qa/traces.log').read_text()
for src,dst in [('elm-durable-reservation-release-v608/adapter/retirement_ledger.py','retirement_ledger608.py'),('elm-release-delivery-attestation-v624/adapter/delivery_ledger.py','delivery_ledger624.py')]:assert sha(ROOT.parent/src)==sha(ROOT/'qa/ancestry'/dst)
req=json.loads((ROOT/'requirements.json').read_text());assert len(req['requirements'])==14
for item in req['requirements']:assert all(name in r['selected'] for name in item['openspecScenarioWitnesses'])
rows=[]
for f in sorted(ROOT.rglob('*')):
 if f.is_file() and f not in [ROOT/'component-manifest.json',ROOT/'qa/freeze-receipt.json',ROOT/'qa/protected-freeze.log']:
  assert not f.is_symlink();rows.append({'path':str(f.relative_to(ROOT)),'sha256':sha(f),'size':f.stat().st_size})
m=ROOT/'component-manifest.json';m.write_text(json.dumps({'passed':True,'sourceHeld':True,'nativeAcceptance':False,'fullS15Accepted':False,'scope':r['scope'],'namedCount':32,'sampledTraces':1500,'maxTransitions':70,'typedMutants':10,'proposedEARSRequirements':14,'files':rows},indent=2)+'\n');out={'passed':True,'files':len(rows),'manifestSHA256':sha(m),'nativeAcceptance':False,'fullS15Accepted':False};(ROOT/'qa/freeze-receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
