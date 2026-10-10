"""quint-llm-kit additive appearance transaction gates; not native acceptance."""
import pathlib,subprocess,json,time,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/runs'/('layer-appearance-model-'+str(time.time_ns()));OUT.mkdir(parents=True)
spec=ROOT/'qa/layer-appearance.qnt';tests=ROOT/'qa/layer-appearance_test.qnt'
commands=[('typecheck',['quint','typecheck',str(tests)]),('named',['quint','test',str(tests),'--backend=typescript','--match=^(draftDoesNotApplyTest|bothFlagsCommitTest|unknownKeepsOldAppearanceTest|readReconcilesWithoutReplayTest|staleSaveCannotOverwriteTest)$','--max-samples=1','--seed=79401']),('witnesses',['quint','run',str(spec),'--backend=typescript','--witnesses','bothCommitted','unknownHeld','staleRefused','--max-samples=1000','--max-steps=30','--seed=79402']),('safety',['quint','run',str(spec),'--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=30','--seed=79403'])]
rows=[];counts={}
for name,args in commands:
 p=subprocess.run(args,text=True,capture_output=True);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);rows.append({'name':name,'command':args,'exitCode':p.returncode});assert p.returncode==0,p.stdout+p.stderr
 if name=='witnesses':
  import re
  counts={key:int(count) for key,count in re.findall(r'(bothCommitted|unknownHeld|staleRefused) was witnessed in (\d+) trace',p.stdout)}
  assert set(counts)=={'bothCommitted','unknownHeld','staleRefused'} and all(counts.values()),p.stdout
report={'passed':True,'scope':'Bounded appearance CAS/draft/committed/lost/refused/read state; no native presentation, timing, schema codec or transport refinement.','commands':rows,'witnessCounts':counts,'modelSHA256':hashlib.sha256(spec.read_bytes()).hexdigest(),'nativeAcceptance':False};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'report':str(OUT/'report.json'),'witnessCounts':counts}))
