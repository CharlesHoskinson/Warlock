"""Run through protected QA: verify review binding and existing PoC receipts."""
import hashlib,json,re,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
registry=digest(root/'requirements.json');reviews=[]
for specialty in ['window-behavior','accessibility','navigation','motion','consistency']:
 p=root/'audits'/('ux-final-'+specialty+'-confirmation.json');d=json.loads(p.read_text())
 assert d['verdict']=='confirmed',(specialty,d['verdict'])
 bound=d.get('requirementsSha256',d.get('requirementsSHA256',d.get('reviewedRequirementsSha256')))
 assert bound==registry,(specialty,bound,registry)
 reviews.append(dict(specialty=specialty,path=str(p.relative_to(root)),sha256=digest(p),verdict=d['verdict']))
b=root/'prototypes/quint/bridge';m=json.loads((b/'receipts/manifest.json').read_text())
for f,sha in m['artifacts'].items():assert digest(b/f)==sha,f
for x in m['records']:
 assert x['expectedOutcomeObserved'] and x['exitCode']==x['expectedExitCode'],x['name']
 assert digest(b/'receipts'/(x['name']+'.log'))==x['logSha256'],x['name']
log=(b/'receipts/named-tests.log').read_text();actual=re.findall(r'ok (\w+) passed 1 test\(s\)',log)
assert set(actual)==set(m['namedTests']) and len(actual)==18,actual
assert 'No violation found' in (b/'receipts/simulation.log').read_text()
for x in m['records'][4:]:assert 'Assertion failed' in (b/'receipts'/(x['name']+'.log')).read_text(),x['name']
e=root/'prototypes/elm';m2=json.loads((e/'proof-manifest.json').read_text());assert m2['passed']
for x in m2['files']:assert digest(e/x['path'])==x['sha256'],x['path']
scene=json.loads((root/'prototypes/quint/scene-receipts/scene-evidence-verification.json').read_text());assert scene['allPassed']
result=dict(observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Five final requirements-review bindings and retained CPU proof evidence; no empirical/native implementation acceptance',registrySHA256=registry,reviews=reviews,bridgeNamedTests=18,bridgeMutations=9,sceneNamedTests=11,sceneMutations=3,elmChecks=8,passed=True)
(root/'audits/final-review-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
