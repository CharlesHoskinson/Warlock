#!/usr/bin/env python3
"""Run through protected QA. Verify executed identities, not selector intent."""
import hashlib,json,pathlib,re
root=pathlib.Path(__file__).resolve().parent; out=root/'scene-receipts'
r=json.loads((out/'scene-proof-receipt.json').read_text())
log=(out/'named-tests.log').read_text(); actual=re.findall(r'ok (\w+) passed 1 test\(s\)',log)
checks={'exactNamesExecuted':actual==r['selectedNames'],'elevenPassing':'11 passing' in log,'quintPinned':(out/'version.log').read_text().strip()=='0.33.0','simulationSuccess':'[ok] No violation found' in (out/'bounded-invariants.log').read_text(),'allDeclaredCommandExits':r['allExpectationsMet']}
for row in r['commands']:
 p=out/(row['name']+'.log'); checks['hash-'+row['name']]=hashlib.sha256(p.read_bytes()).hexdigest()==row['outputSha256']
for name in ['minimized-eligible','proxy-interactive','gpu-lease-survives']:
 checks[name+'-actual-invariant-counterexample']='error: Invariant violated' in (out/(name+'-invariant-counterexample.log')).read_text()
 checks[name+'-actual-named-assertion']='Assertion failed' in (out/(name+'-named-counterexample.log')).read_text()
 checks[name+'-saved-counterexample']=len(list(out.glob(name+'_invariant_*itf.json')))>=1
for name,digest in r['inputSha256'].items(): checks['source-'+name]=hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
result={'scope':'Evidence integrity and executed scenario identities only','checks':checks,'allPassed':all(checks.values()),'proofReceiptSha256':hashlib.sha256((out/'scene-proof-receipt.json').read_bytes()).hexdigest(),'checkerSha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
(out/'scene-evidence-verification.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2)); raise SystemExit(0 if result['allPassed'] else 1)
