"""Explicit Quint projection, compiled actual FamilyRevision replay, no native claim."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir()
TOOL='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
owner=ROOT
paths=[pathlib.Path(__file__),ROOT/'spec/style.qnt',ROOT/'native/replay.cpp',ROOT/'SPEC.md',owner/'native/style_revision.hpp',owner/'native/source_epoch.hpp']
inputs={str(p):sha(p) for p in paths}
for p in paths:shutil.copy2(p,OUT/p.name)
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'qaScope':scope,'inputs':inputs,'commands':[],'scope':'Selected style-channel/membership/unavailable projection replayed through actual StyleRevision; native collection, full renderer coverage and crop/Elm fidelity remain separate.'}
try:
 names=['stableStyleTest','nativeDimStyleTest','nativeAlphaStyleTest','nativeBorderAngleTest','nativeGradientStyleTest','familyContentStyleTest','familyMembershipStyleTest','unavailableStyleTest','recoveredStyleTest']
 for name,args in [('compile',['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','-I'+str(OUT),str(OUT/'replay.cpp'),'-o',str(OUT/'replay')]),('typecheck',[TOOL,'typecheck',str(OUT/'style.qnt')]),('selected',[TOOL,'test',str(OUT/'style.qnt'),'--main=style','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=730013','--max-samples=1','--out-itf='+str(OUT/'named-{test}-{seq}.itf.json')])]:
  p=subprocess.run(args,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);r['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});assert p.returncode==0,p.stdout+p.stderr
 traces=sorted(OUT.glob('named-*.itf.json'));assert len(traces)==9
 replay=[]
 for trace in traces:
  states=json.loads(trace.read_text())['states'];number=lambda row,k:int(row[k]['#bigint'])
  projection=OUT/(trace.stem+'.tsv');projection.write_text(''.join(' '.join(map(str,[number(row,'family'),number(row,'tint'),number(row,'alpha'),number(row,'angle'),number(row,'color'),number(row,'count'),int(row['complete']),number(row,'epoch')]))+'\n' for row in states))
  p=subprocess.run([str(OUT/'replay'),str(projection)],capture_output=True,text=True,timeout=5);(OUT/(trace.stem+'.stdout')).write_text(p.stdout);(OUT/(trace.stem+'.stderr')).write_text(p.stderr);assert p.returncode==0,p.stderr
  result=json.loads(p.stdout);assert result['passed'] and result['states']==len(states);replay.append({'trace':str(trace),'states':len(states),'result':result})
 assert all(sha(p)==h for p,h in inputs.items())
 r.update(passed=True,selectedNames=names,traces={str(p):sha(p) for p in traces},states=sum(len(json.loads(p.read_text())['states']) for p in traces),implementationReplay=replay)
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
report=OUT/'report.json';report.write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:(ROOT/'qa/model-report.json').write_text(json.dumps({'path':str(report),'sha256':sha(report)},indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(report),'error':r.get('error')}),flush=True)
raise SystemExit(not r['passed'])
