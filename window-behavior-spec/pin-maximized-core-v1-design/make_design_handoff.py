#!/usr/bin/env python3
from pathlib import Path
import os,stat,json,hashlib,datetime,re
B=Path(__file__).resolve().parent
sourceHashes={str(p.relative_to(B)):hashlib.sha256(p.read_bytes()).hexdigest() for p in B.glob('*') if p.is_file() and p.suffix in ['.qnt','.md','.py']}
commands=[]
for job,expected in [('max_pin',4),('modal_focus',3)]:
 rows=json.loads((B/'proof'/f'{job}-commands.json').read_text());assert len(rows)==expected
 for r in rows:
  assert r['exitCode']==0
  p=B/r['log'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];commands.append(r)
counts={}
for module,expected in [('max_pin',61),('modal_focus',59),('naive_max_pin_counterexamples',4),('first_band_counterexample',1),('independent_family_test',4)]:
 name=f'{module}_test.qnt' if module in ['max_pin','modal_focus'] else f'{module}.qnt'
 src=B/name;count=len(re.findall(r'\brun\s+\w+',src.read_text()));assert count==expected;counts[module]=count
 log= B/'proof'/ {'max_pin':'max_pin-1.log','modal_focus':'modal_focus-1.log','naive_max_pin_counterexamples':'naive-counterexamples.log','first_band_counterexample':'first-band-counterexample.log','independent_family_test':'independent-family.log'}[module]
 assert f'{count} passing' in log.read_text()
sourceEvidence=json.loads((B/'source-counterexamples.json').read_text());assert len(sourceEvidence['checks'])==8
pres=json.loads((B/'proof/source-preservation.json').read_text());assert pres['result']=='PASS' and pres['sourceRecords']==180
checkpoint={'schema':1,'result':'DESIGN_PROOF_PASS','created':datetime.datetime.now(datetime.timezone.utc).isoformat(),'nativeAuthorized':False,'runtimeChanged':False,
 'namedDesignCases':counts,'totalNamed':sum(counts.values()),'traces':{'maxPinMixed':2000,'maxPinValid':2000,'focusMixed':2000},'maxStepsPerInvocation':100,
 'traceMeaning':'validStep composes several native model phases; its expanded state traces can exceed100 states. Simulation is bounded and not exhaustive proof.',
 'actualCommands':commands,'sourceHashes':sourceHashes,'primaryRecordsExact':180,'sourcePredicateCounterexamples':8,'modelsRetained':'Prior fixed-chain band/focus schemas and their completed proofs are retained as independent preimages. Four naive policy failures plus the first-band missing descendant case are executable model counterexamples.',
 'remaining':['Root design review of coexistence/mode restore/family/focus policy and exact intended implementation diff','Fresh isolated actual core/plugin/helper implementation plus CPU/source inverses and original regressions','Root-only matching private core native gates; no deployment/native acceptance from this packet']}
cp=B/'proof/formal-design-checkpoint.json';cp.write_text(json.dumps(checkpoint,indent=2)+'\n')
files={};links={}
for root,dirs,names in os.walk(B,followlinks=False):
 for n in list(dirs)+names:
  p=Path(root)/n;rel=str(p.relative_to(B));st=p.lstat()
  if p==B/'SOURCE_READY.json':continue
  if stat.S_ISLNK(st.st_mode):links[rel]={'target':os.readlink(p),'mode':st.st_mode&0o777}
  elif stat.S_ISREG(st.st_mode):files[rel]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':st.st_mode&0o777,'size':st.st_size}
  else:assert stat.S_ISDIR(st.st_mode),(rel,'unexpected file kind')
ready={'schema':1,'created':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':'SOURCE_DESIGN_READY','stage':str(B),'runtimeChanged':False,'nativeReady':False,'nativeAccepted':False,'fullParityAccepted':False,
 'checkpoint':'proof/formal-design-checkpoint.json','checkpointSHA256':hashlib.sha256(cp.read_bytes()).hexdigest(),'fileCount':len(files),'files':files,'links':links,
 'review':'DESIGN_REVIEW_REQUEST.md','coreRevision':'efb50993780079460b0cbed1363e2166a2de1d9f','copiedOriginalSourcesExact':180}
out=B/'SOURCE_READY.json'
with out.open('x') as f:json.dump(ready,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'stage':str(B),'sourceReadySHA256':hashlib.sha256(out.read_bytes()).hexdigest(),'files':len(files),'links':len(links),'named':sum(counts.values()),'checkpointSHA256':ready['checkpointSHA256']}))
