import hashlib,json,os,pathlib,resource,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[2]
OUT=ROOT/'qa'/('validate-'+str(time.time_ns()));OUT.mkdir()
cli=pathlib.Path('/home/hoskinson/.npm/_npx/b05ce0373733faa6/node_modules/@fission-ai/openspec/bin/openspec.js')
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
inputs={str(p):sha(p) for p in ROOT.rglob('*.md')};inputs[str(cli)]=sha(cli);inputs[str(pathlib.Path(__file__))]=sha(__file__)
env=dict(os.environ,OPENSPEC_TELEMETRY='0')
argv=['node',str(cli),'validate','warlock-preview-shared-backdrop','--strict','--json','--no-interactive']
p=subprocess.run(argv,cwd=REPO,env=env,capture_output=True,text=True,timeout=120)
(OUT/'stdout.json').write_text(p.stdout);(OUT/'stderr.log').write_text(p.stderr)
r={'passed':p.returncode==0,'scope':scope,'argv':argv,'exitCode':p.returncode,'inputs':inputs,'artifacts':{name:sha(OUT/name) for name in ['stdout.json','stderr.log']},'nativeAcceptance':False,'fullReleaseAccepted':False}
assert all(sha(p)==h for p,h in inputs.items())
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'stderr':p.stderr[-1000:]}));raise SystemExit(p.returncode)
