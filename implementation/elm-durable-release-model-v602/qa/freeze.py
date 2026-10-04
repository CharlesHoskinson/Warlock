import hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((ROOT/'qa/report.json').read_text());assert r['passed'] and r['namedCount']==31 and r['executedNames']==r['selectedNames'] and r['mutants']==15
for name,h in r['sourceHashes'].items():assert sha(ROOT/name)==h
for row in r['commands']:
 assert row['ok'] and row.get('actualAssertionFailure',True);assert sha(ROOT/'qa'/(row['name']+'.log'))==row['outputSHA256']
assert '[ok] No violation found' in (ROOT/'qa/traces.log').read_text()
rows=[]
for f in sorted(ROOT.rglob('*')):
 if f.is_file() and f.name not in ('component-manifest.json','freeze-receipt.json'):
  assert not f.is_symlink();rows.append({'path':str(f.relative_to(ROOT)),'size':f.stat().st_size,'sha256':sha(f)})
m=ROOT/'component-manifest.json';m.write_text(json.dumps({'sourceHeld':True,'passed':True,'nativeAcceptance':False,'scope':'Bounded CPU Quint retirement-release model only','namedCount':31,'sampledTraces':2000,'maxTransitions':80,'typedMutants':15,'files':rows},indent=2)+'\n');out={'passed':True,'files':len(rows),'manifestSHA256':sha(m),'nativeAcceptance':False};(ROOT/'qa/freeze-receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
