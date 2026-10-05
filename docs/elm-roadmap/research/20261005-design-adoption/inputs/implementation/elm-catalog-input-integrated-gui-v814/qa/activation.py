import hashlib,json,pathlib,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
from toolchain import verify
r=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
o=r/'qa'/('activation-'+str(time.time_ns()));o.mkdir()
source={str(p.relative_to(r)):sha(p) for folder in ('src','assets') for p in (r/folder).glob('*') if p.is_file()}
source.update({name:sha(r/name) for name in ('qa/activation.py','qa/activation.cjs')})
for name in source:
 p=o/'source'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((r/name).read_bytes())
report={'cpuHarnessPassed':False,'productQualified':False,'nativeAcceptance':False,'sourceSHA256':source}
try:
 build=sorted((r/'qa').glob('build-*/report.json'))[-1];b=json.loads(build.read_text());assert b['passed']
 for name,digest in b['inputs'].items():assert sha(r/name)==digest,('buildSourceChanged',name)
 command=['node',str(r/'qa/activation.cjs'),str(build.parent/'inputs/assets'),str(o/'rows.json')]
 verify();p=subprocess.run(command,capture_output=True,text=True,timeout=90);verify()
 (o/'command.log').write_text(p.stdout+p.stderr);report['command']=command;report['exitCode']=p.returncode
 assert p.returncode==0,p.stderr
 rows=json.loads((o/'rows.json').read_text());assert rows['cpuHarnessPassed'] and not rows['productQualified'] and len(rows['openCounterexamples'])==5
 report.update({'cpuHarnessPassed':True,'build':str(build.relative_to(r)),'buildSHA256':sha(build),'checks':len(rows['checks']),'openCounterexamples':rows['openCounterexamples'],'sourceHeld':all(sha(r/name)==digest for name,digest in source.items()),'cliTimeoutSeconds':90,'productDeadlinesUnchanged':True,'loadedNodeDependenciesHeld':rows['loadedNodeDependenciesHeld']})
 assert report['sourceHeld']
except BaseException as e:
 report['error']=repr(e);(o/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(o/'report.json');raise
(o/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(o/'report.json')
