import hashlib,json,pathlib,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
r=json.loads((ROOT/'qa/report.json').read_text());assert r['passed'] and r['namedCount']==55 and r['typedMutants']==7 and r['selected']==r['executed']
for n,h in r['sourceHashes'].items():assert sha(ROOT/n)==h
for c in r['commands']:assert c['ok'] and c.get('actualAssertionFailure',True) and sha(ROOT/'qa'/(c['name']+'.log'))==c['outputSHA256']
assert '[ok] No violation found' in (ROOT/'qa/traces.log').read_text()
ancestor=ROOT.parent/'elm-durable-release-model-v605'
for n in ['release.qnt','tests.qnt','component-manifest.json']:assert sha(ancestor/n)==sha(ROOT/'qa/ancestor605'/n)
for n in ['release.qnt','tests.qnt']:assert sha(ROOT/n)==sha(ancestor/n)
rows=[]
for f in sorted(ROOT.rglob('*')):
 if f.is_file() and f not in [ROOT/'component-manifest.json',ROOT/'qa/freeze-receipt.json',ROOT/'qa/protected-freeze.log']:
  assert not f.is_symlink();rows.append({'path':str(f.relative_to(ROOT)),'sha256':sha(f),'size':f.stat().st_size})
m=ROOT/'component-manifest.json';m.write_text(json.dumps({'passed':True,'sourceHeld':True,'scope':r['scope'],'nativeAcceptance':False,'namedCount':55,'sampledTraces':2000,'maxTransitions':80,'typedMutants':7,'files':rows},indent=2)+'\n')
out={'passed':True,'files':len(rows),'manifestSHA256':sha(m),'nativeAcceptance':False};(ROOT/'qa/freeze-receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
