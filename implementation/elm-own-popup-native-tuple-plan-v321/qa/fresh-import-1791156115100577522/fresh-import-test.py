"""Fresh process helper closure; invalid supervisor refuses before native resources."""
import hashlib,json,os,pathlib,subprocess,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parents[1];out=ROOT/'qa'/('fresh-import-'+str(time.time_ns()));out.mkdir();r={'passed':False,'nativeAcceptance':False}
try:
 helper=str(ROOT/'qa/helpers')
 code='import sys;sys.path.insert(0,'+repr(helper)+');import owned_bus_host,private_bus,activation_import,cleanup,credentials,outcomes,protocol,journal,actor;assert callable(owned_bus_host.derivative);print("source-closed helper import PASS")'
 p=subprocess.run(['/usr/bin/python3','-B','-c',code],capture_output=True,text=True,timeout=6);(out/'import.stdout').write_text(p.stdout);(out/'import.stderr').write_text(p.stderr);assert p.returncode==0,p.stderr
 sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import owned_runtime
 with owned_runtime() as runtime:
  env=dict(os.environ);env['XDG_RUNTIME_DIR']=runtime
  p=subprocess.run(['/usr/bin/python3','-B',str(ROOT/'qa/helpers/activation-supervisor.py'),'--invalid-safe'],capture_output=True,text=True,env=env,timeout=6)
 (out/'supervisor.stdout').write_text(p.stdout);(out/'supervisor.stderr').write_text(p.stderr);assert p.returncode!=0 and 'descriptor/journal required' in p.stderr and not p.stdout
 r.update(passed=True,checks=['actual-fresh-source-import','actual-supervisor-invalid-before-resource-allocation'],helperHashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'qa/helpers').glob('*.py')})
except BaseException as e:r.update(error=repr(e),traceback=traceback.format_exc())
(out/'fresh-import-test.py').write_bytes(pathlib.Path(__file__).read_bytes());(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':r['passed'],'error':r.get('error')}));raise SystemExit(0 if r['passed'] else 1)
