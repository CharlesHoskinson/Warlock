"""Couple eight selected receipt-correlation scenarios to actual optimized Elm."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v71')
s=(r/'qa/metadata-check.py').read_text().replace('metadata','receipt')
s=s.replace('compiled=build.parent/"inputs/assets/receipt-replay.js"','compiled=build.parent/"inputs/assets/preview-replay.js"')
start=s.index('"projection":');end=s.index('}\ndef run',start)
s=s[:start]+'"projection":"Exact known-job terminal correlation, single retained terminal(job,sequence) replay, next request and emitted ACKs against current compiled Elm for one fixed own binding/scope and Refused receipts. Later jobs are controlled typed messages; no native ownership/pixels or whole policy refinement."'+s[end:]
marker=' report["passed"]=True';assert s.count(marker)==1
added=''' parent=ROOT.parent/'warlock-preview-provider-v70';oldBuild=next(parent.glob('qa/build-*/report.json'));old=json.loads(oldBuild.read_text());assert old['passed'];oldElm=oldBuild.parent/'inputs/assets/preview-replay.js';assert sha(oldElm)==old['compiledAssetPackage']['files']['preview-replay.js']
 caught=[]
 for name in ['futureAfterOriginalFinal','alteredSequenceRefused']:
  paths=list(OUT.glob('named-'+name+'-*.itf.json'));assert len(paths)==1
  states=[row['s'] for row in decode(json.loads(paths[0].read_text()))['states']];history=states[-1]['history'];expected=[];count=0
  for state in states:
   if len(state['history'])==count:continue
   count=len(state['history']);expected.append({**state,'history':[]})
  actual=json.loads(run('retained-unsafe-'+name,['node',str(OUT/'inputs/qa/receipt-replay.js'),str(oldElm),str(OUT/'inputs/qa/native-source-fixture.json'),'--replay'],input=json.dumps(history)))
  assert actual!=expected,(name,'retained actual unsafe Elm escaped oracle');caught.append({'name':name,'observableMismatch':True})
 report.update(unsafeCounterexamplesDetected=len(caught),retainedUnsafeProgram={'buildReport':str(oldBuild),'sha256':sha(oldBuild),'compiledElmSHA256':sha(oldElm)},counterexamples=caught)
'''
s=s.replace(marker,added+marker)
target=r/'qa/receipt-check.py';assert not target.exists();target.write_text(s);print(str(target))
