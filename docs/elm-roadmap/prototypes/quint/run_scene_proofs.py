#!/usr/bin/env python3
"""Launch ONLY through protected qa_run.py. CPU formal/simulation evidence."""
import hashlib,json,pathlib,re,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'scene-receipts'
OUT.mkdir(exist_ok=True)
source=ROOT/'scene_model.qnt'; tests=ROOT/'scene_tests.qnt'
rows=[]
def run(name,args,expect=0):
    start=time.time(); p=subprocess.run(['quint',*args],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90)
    (OUT/(name+'.log')).write_text(p.stdout)
    row={'name':name,'command':['quint',*args],'exit':p.returncode,'expectedExit':expect,'expectationMet':p.returncode==expect,'seconds':round(time.time()-start,3),'outputSha256':hashlib.sha256(p.stdout.encode()).hexdigest()}; rows.append(row); return p
run('version',['--version'])
run('typecheck',['typecheck',str(tests)])
names=re.findall(r'run (\w+) =',tests.read_text()); selector='^('+'|'.join(names)+')$'
run('named-tests',['test',str(tests),'--main=scene_tests','--match='+selector,'--seed=610103','--max-samples=1','--backend=typescript','--out-itf='+str(OUT/'accepted_{test}_{seq}.itf.json')])
run('bounded-invariants',['run',str(source),'--main=scene','--invariants','noExcludedPaint','noExcludedInput','focusSafe','proxyInert','leaseValid','proxyValid','--seed=610104','--max-samples=1000','--max-steps=40','--backend=typescript'])
mutations=[('minimized-eligible',' and not(st.minimized.contains(id))','', 'minimizedFullscreenExcludedTest','noExcludedPaint'),('proxy-interactive','pure def proxyHit(st: Scene): bool = false','pure def proxyHit(st: Scene): bool = st.proxy','inertRestoreProxyTest','proxyInert'),('gpu-lease-survives','| DeviceLoss => {...s,gpuReady:false,lease:false,proxy:false,liveReady:false}','| DeviceLoss => {...s,gpuReady:false,proxy:false,liveReady:false}','gpuLossRevokesLeaseTest','leaseValid')]
for label,old,new,name,inv in mutations:
    text=source.read_text(); assert text.count(old)==1
    model=OUT/(label+'.qnt'); model.write_text(text.replace(old,new)); mt=OUT/(label+'_tests.qnt'); mt.write_text(tests.read_text().replace('"./scene_model"','"./'+label+'"'))
    run(label+'-named-counterexample',['test',str(mt),'--main=scene_tests','--match=^'+name+'$','--seed=610105','--max-samples=1','--backend=typescript','--out-itf='+str(OUT/(label+'_{test}_{seq}.itf.json'))],1)
    run(label+'-invariant-counterexample',['run',str(model),'--main=scene','--invariant='+inv,'--seed=610106','--max-samples=1000','--max-steps=40','--backend=typescript','--out-itf='+str(OUT/(label+'_invariant_{seq}.itf.json'))],1)
receipt={'schema':1,'scope':'CPU-only bounded Quint simulation and exact named scenarios; no exhaustive model checking, native rendering/input acceptance or desktop changes.','protectedLauncher':'/home/hoskinson/window-integration-qa/qa_run.py','seedByCampaign':{'named':610103,'invariants':610104,'mutationNamed':610105,'mutationInvariants':610106},'selectedNames':names,'expectedNamedCount':len(names),'boundedSamples':1000,'boundedMaxSteps':40,'inputSha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,tests,pathlib.Path(__file__)]},'commands':rows,'allExpectationsMet':all(r['expectationMet'] for r in rows)}
(OUT/'scene-proof-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
raise SystemExit(0 if receipt['allExpectationsMet'] else 1)
