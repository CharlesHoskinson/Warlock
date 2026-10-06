import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];owner=REPO/'implementation/warlock-family-style-revisions-v2';OUT=ROOT/'qa'/('test-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
paths=[pathlib.Path(__file__),ROOT/'SPEC.md',ROOT/'native/controls.cpp',owner/'native/style_revision.hpp',owner/'native/source_epoch.hpp'];inputs={str(p):sha(p) for p in paths}
for p in paths:shutil.copy2(p,OUT/p.name)
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'qaScope':scope,'inputs':inputs,'commands':[]}
try:
 assert sha(owner/'native/style_revision.hpp')==sha(REPO/'implementation/warlock-family-style-source-v3/native/style_revision.hpp')
 argv=['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','-I'+str(OUT),str(OUT/'controls.cpp'),'-o',str(OUT/'controls')]
 for stage,command in [('compile',argv),('run',[str(OUT/'controls')])]:
  p=subprocess.run(command,capture_output=True,text=True,timeout=180 if stage=='compile' else 5);(OUT/(stage+'.stdout')).write_text(p.stdout);(OUT/(stage+'.stderr')).write_text(p.stderr);r['commands'].append({'stage':stage,'argv':command,'exitCode':p.returncode});assert p.returncode==0,p.stderr
 assert all(sha(p)==h for p,h in inputs.items());evidence=json.loads(p.stdout);assert evidence['passed'];r.update(passed=True,evidence=evidence)
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};report=OUT/'report.json';report.write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:(ROOT/'qa/test-report.json').write_text(json.dumps({'path':str(report),'sha256':sha(report)},indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(report),'error':r.get('error')}),flush=True);raise SystemExit(not r['passed'])
