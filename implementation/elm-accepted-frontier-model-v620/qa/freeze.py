import hashlib,json,pathlib,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((ROOT/'qa/report.json').read_text());assert r['passed'] and r['namedCount']==16 and r['typedMutants']==9 and r['selected']==r['executed']
for n,h in r['sourceHashes'].items():assert sha(ROOT/n)==h
for c in r['commands']:assert c['ok'] and c.get('actualAssertionFailure',True) and sha(ROOT/'qa'/(c['name']+'.log'))==c['outputSHA256']
assert '[ok] No violation found' in (ROOT/'qa/traces.log').read_text()
a=ROOT.parent/'elm-reconciliation-accepted-read-v619'
for src,dst in [('spec/accepted.qnt','accepted.qnt'),('SPEC.md','SPEC.md'),('component-manifest.json','component-manifest.json'),('src/ReconciliationTracking.elm','ReconciliationTracking.elm')]:assert sha(a/src)==sha(ROOT/'qa/ancestor619'/dst)
a=ROOT.parent/'elm-reconciliation-ready-model-v614'
for n in ['protocol.qnt','component-manifest.json']:assert sha(a/n)==sha(ROOT/'qa/ancestor614'/n)
rows=[]
for f in sorted(ROOT.rglob('*')):
 if f.is_file() and f not in [ROOT/'component-manifest.json',ROOT/'qa/freeze-receipt.json',ROOT/'qa/protected-freeze.log']:
  assert not f.is_symlink();rows.append({'path':str(f.relative_to(ROOT)),'sha256':sha(f),'size':f.stat().st_size})
m=ROOT/'component-manifest.json';m.write_text(json.dumps({'passed':True,'sourceHeld':True,'nativeAcceptance':False,'scope':r['scope'],'namedCount':16,'sampledTraces':1000,'maxTransitions':40,'typedMutants':9,'files':rows},indent=2)+'\n');out={'passed':True,'files':len(rows),'manifestSHA256':sha(m),'nativeAcceptance':False};(ROOT/'qa/freeze-receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
