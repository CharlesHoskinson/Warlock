"""Run unchanged current GUI regressions in independent protected CPU workers."""
import concurrent.futures,hashlib,json,pathlib,resource,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
root=repo/'implementation/warlock-preview-provider-v86'
out=pathlib.Path(__file__).parent/('regressions86-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
scripts=['next-intent-check.py','feedback-check.py','resume-enrollment-check.py',
 'receipt-check.py','metadata-check.py','catalog-check.py','check.py',
 'delivery-check.py','resume-model-check.py','intent-check.py','enrollment-check.py','next-resume-check.py']
inputs={str(root/'qa'/name):sha(root/'qa'/name) for name in scripts}
builds=list(root.glob('qa/build-*/report.json'));assert len(builds)==1
build=builds[0];proof=json.loads(build.read_text());assert proof['passed'] and len(proof['commands'])==95
for name,value in proof['inputs'].items():assert sha(root/name)==value,name
def run(name):
 result=subprocess.run(['/usr/bin/python3','-B',str(root/'qa'/name)],capture_output=True,text=True,timeout=1200)
 (out/(name+'.stdout')).write_text(result.stdout);(out/(name+'.stderr')).write_text(result.stderr)
 print(name,result.returncode,flush=True)
 return {'script':name,'exitCode':result.returncode,'stdoutSHA256':sha(out/(name+'.stdout')),'stderrSHA256':sha(out/(name+'.stderr'))}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(run,scripts))
assert all(sha(pathlib.Path(name))==value for name,value in inputs.items())
passed=all(row['exitCode']==0 for row in results)
(out/'report.json').write_text(json.dumps({'passed':passed,'inputs':inputs,'results':results,
 'fullBuild':{'path':str(build),'sha256':sha(build)},'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
print(json.dumps({'passed':passed,'report':str(out/'report.json')}),flush=True);sys.exit(not passed)
