"""Real protected supervisor CLI refuses unsafe subjects before child launch."""
import hashlib,json,os,pathlib,resource,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');sup=repo/'implementation/warlock-window-restart-supervisor-v2';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
out=pathlib.Path(__file__).with_name('supervisor-qa-guards-v2-'+str(time.time_ns()));out.mkdir(mode=0o700)
pre=json.loads((repo/'implementation/warlock-client-provider-native-v204/qa/preflight.json').read_text())
manifest=sup/'runtime-manifest.json';inputs={str(p):sha(p) for p in [sup/'supervisor.py',sup/'cohort.py',manifest,pathlib.Path(__file__)]}
authority=out/'authority.json';authority.write_text(json.dumps({'runtime':str(out),'instance':'qa_guard','pid':1,'expected_start':1,'binary_sha256':pre['pair']['core']['sha256']}));authority.chmod(0o600)
# Even a guard regression cannot use a display in this CPU-only child.
env=dict(os.environ,XDG_RUNTIME_DIR=str(out),WAYLAND_DISPLAY=str(out/'no-display'),GSETTINGS_BACKEND='memory',GTK_A11Y='none',NO_AT_BRIDGE='1');env.pop('DISPLAY',None)
cases=[('nonQA',False,'1'),('zero',True,'0'),('leadingZero',True,'01'),('negative',True,'-1'),('nondigits',True,'1x'),('nonascii',True,'٢'),('overflow',True,'18446744073709551616')]
report={'passed':False,'inputs':inputs,'checks':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual protected Python supervisor CLI rejects seven invalid/non-QA controlled-preview subjects before any host, reader or generation log is created. CPU-only no-display environment; no native behavior claim.'}
try:
 for name,qa,subject in cases:
  directory=out/name;directory.mkdir(mode=0o700)
  args=['/usr/bin/python3','-B',str(sup/'supervisor.py'),'--manifest',str(manifest),'--authority-config',str(authority),'--qa-preview-subject='+subject]
  if qa:args+=['--qa','--qa-log-directory',str(directory)]
  p=subprocess.run(args,capture_output=True,text=True,timeout=5,env=env);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
  passed=p.returncode==2 and 'Shell supervisor refused: ValueError' in p.stdout and 'supervisor-host-start:' not in p.stdout and not list(directory.iterdir())
  report['checks'].append({'name':name,'passed':passed,'exitCode':p.returncode,'childLaunchObserved':False if passed else None});assert passed,name
 assert all(sha(p)==h for p,h in inputs.items());report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(out/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
