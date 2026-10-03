#!/usr/bin/env python3
from pathlib import Path
import subprocess,json,hashlib
B=Path(__file__).resolve().parent
E=B/'independent-model-evidence'
def run(name,cmd):
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
    (E/(name+'.stdout')).write_text(proc.stdout)
    (E/(name+'.stderr')).write_text(proc.stderr)
    return {'name':name,'command':cmd,'exitCode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr}
results=[]
for name,invariant,count in [('configure_lifecycle','safe',15),('nested_selection','safe',12),('version_guard','validBinding and truthfulRefusal',5)]:
    result=run(name+'-named',['quint','test',str(B/(name+'.qnt'))]);assert result['exitCode']==0,result;result['expectedNamedCount']=count;results.append(result)
    result=run(name+'-random',['quint','run',str(B/(name+'.qnt')),'--invariant',invariant,'--max-steps','100','--max-samples','2000','--seed','20260930','--verbosity','1']);assert result['exitCode']==0,result;results.append(result)
lifecycle=(B/'configure_lifecycle.qnt').read_text();selection=(B/'nested_selection.qnt').read_text()
def action_mutation(source,action):
    lines=source.splitlines(True)
    matches=[i for i,line in enumerate(lines) if line.startswith('  action '+action+' =')]
    assert len(matches)==1
    i=matches[0];assert lines[i].count('if (ready)')==2
    lines[i]=lines[i].replace('if (ready)','if (true)');return ''.join(lines)
mutants=[
 ('unguarded-buffer',action_mutation(lifecycle,'buffer')),
 ('unguarded-frame',action_mutation(lifecycle,'frame')),
 ('publication-before-ack',lifecycle.replace('val allowed = queued and ack and not(dead) and not(published)','val allowed = not(dead) and not(published)')),
 ('late-gpu-drm',selection.replace('| NewGpu => if (not(s.chosen) or s.rejected or s.mode!="unset")','| NewGpu => if (not(s.chosen) or s.rejected or s.mode=="invalid")')),
 ('parentloss-aux-fallback',selection.replace('ready:if(s.mode=="wayland")false else s.headlessAlive or s.drmAlive','ready:s.headlessAlive or s.drmAlive')),
]
mutation_results=[]
for name,source in mutants:
    original=selection if name in ('late-gpu-drm','parentloss-aux-fallback') else lifecycle
    assert source!=original
    path=E/(name+'.qnt');assert not path.exists();path.write_text(source)
    trace=E/(name+'.itf.json')
    result=run(name,['quint','run',str(path),'--invariant','safe','--max-steps','100','--max-samples','2000','--seed','20260930','--out-itf',str(trace),'--verbosity','1'])
    assert result['exitCode']!=0 and trace.exists(),result
    assert 'Invariant violated' in result['stdout'] or 'Invariant violated' in result['stderr'],result
    result['counterexample']=str(trace);result['counterexampleSha256']=hashlib.sha256(trace.read_bytes()).hexdigest();mutation_results.append(result)
wiring=subprocess.run(['python3',str(B/'check_wiring.py')],capture_output=True,text=True,check=True)
(E/'wiring-report.json').write_text(wiring.stdout)
scoped=json.loads((E/'scoped-cpp-report.json').read_text())
report={'result':'pass','namedScenarios':32,'randomizedModels':3,'samplesPerModel':2000,'stepsPerSample':100,'requestedSeed':20260930,'formal':results,'mutationCounterexamples':mutation_results,'sourceWiring':json.loads(wiring.stdout),'scopedCpp':scoped,'nativeGuiLaunched':False,'boundaries':['Models and actual compiled internal helper execution do not prove live parent transport loss, callback reentrancy, or native window correctness.','Fourteen source checks inspect actual source ordering and guards without executing those native callbacks.','C++ executable tests use the dedicated QA scope and inherited core soft/hard limit 1.','Unset backend policy retains upstream optional behavior; mandatory-parent invariants apply only to explicit Wayland selection.']}
paths=[B/name for name in ('configure_lifecycle.qnt','nested_selection.qnt','version_guard.qnt','test_lifecycle.cpp','test_version.cpp','check_wiring.py','run_scoped_cpp.py','run_independent_formal.py','candidate/src/backend/NestedLifecycle.hpp','candidate/src/backend/Wayland.cpp','candidate/src/backend/Backend.cpp','prefix/lib/libaquamarine.so.0.15.0')]
report['sourceHashes']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
path=E/'report.json';assert not path.exists();path.write_text(json.dumps(report,indent=2)+'\n');path.chmod(0o600)
print(json.dumps({'result':report['result'],'namedScenarios':32,'randomModels':3,'mutations':len(mutation_results),'sourceChecks':len(report['sourceWiring']['checks']),'report':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))
