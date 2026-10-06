import hashlib,json,pathlib,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];owner=REPO/'implementation/warlock-family-crop-capture-v2';OUT=ROOT/'qa'/('test-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
paths=[pathlib.Path(__file__),ROOT/'SPEC.md',*ROOT.joinpath('native').glob('*.cpp'),*owner.joinpath('native').glob('*.hpp')];inputs={str(p):sha(p) for p in paths}
for p in paths:shutil.copy2(p,OUT/p.name)
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'qaScope':scope,'inputs':inputs,'commands':[]}
try:
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gio-2.0'],text=True));evidence={}
 for name in ['legacy','qualify']:
  argv=['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror','-I'+str(OUT),str(OUT/(name+'.cpp')),*flags,'-MD','-MF',str(OUT/(name+'.d')),'-o',str(OUT/name)]
  for stage,command in [('compile',argv),('run',[str(OUT/name)])]:
   p=subprocess.run(command,capture_output=True,text=True,timeout=180 if stage=='compile' else 5);(OUT/(name+'-'+stage+'.stdout')).write_text(p.stdout);(OUT/(name+'-'+stage+'.stderr')).write_text(p.stderr);r['commands'].append({'name':name+'-'+stage,'argv':command,'exitCode':p.returncode});print(name,stage,p.returncode,flush=True);assert p.returncode==0,p.stderr
  evidence[name]=json.loads(p.stdout);assert evidence[name]['passed'] and all(evidence[name][k] for k in ['physicalFDClosed','physicalMappingClosed','chargeReleasedAfterClose'])
 assert evidence['legacy']['checks']==150
 assert all(sha(p)==h for p,h in inputs.items());r.update(passed=True,evidence=evidence)
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};report=OUT/'report.json';report.write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:(ROOT/'qa/test-report.json').write_text(json.dumps({'path':str(report),'sha256':sha(report)},indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(report),'error':r.get('error')}),flush=True);raise SystemExit(not r['passed'])
