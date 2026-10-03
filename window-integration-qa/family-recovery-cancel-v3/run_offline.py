from pathlib import Path
import argparse,hashlib,io,json,os,resource,subprocess,sys,unittest
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent));import qa_launch as qa
parser=argparse.ArgumentParser();parser.add_argument('--report',default='offline-report.json');args=parser.parse_args();scope=qa.require_qa_scope();stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.discover(str(B),pattern='test*.py'))
probes=[]
with qa.owned_runtime() as runtime:
 env={k:v for k,v in os.environ.items() if k not in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')}
 env.update(XDG_RUNTIME_DIR=runtime,HOME=runtime,XDG_CONFIG_HOME=runtime,QT_QPA_PLATFORM='offscreen',QT_NO_XDG_DESKTOP_PORTAL='1')
 pid=2147483647;assert not Path(f'/proc/{pid}').exists()
 for extra in (['-p',runtime],[]):
  command=['/usr/bin/qs','kill','--pid',str(pid),*extra];r=subprocess.run(command,env=env,capture_output=True,text=True,timeout=5);probes.append({'command':command,'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'nativeShellLaunched':False,'mainIPCContacted':False})
 assert probes[0]['exitCode']==108 and probes[1]['exitCode']!=108 and 'No instance found for pid' in probes[1]['stdout']+probes[1]['stderr']
report={'result':'pass' if result.wasSuccessful() else 'fail','tests':result.testsRun,'output':stream.getvalue(),'qaScope':scope,'coreLimits':list(resource.getrlimit(resource.RLIMIT_CORE)),'actualQsParserProbes':probes,'nativeLaunch':False,'mainIPCContacted':False,'immutableV3Retained':True}
p=B/args.report;assert p.parent==B and p.name.endswith('.json');assert not p.exists();p.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'result':report['result'],'tests':result.testsRun,'CLIProbes':2,'reportSHA256':hashlib.sha256(p.read_bytes()).hexdigest()}));raise SystemExit(not result.wasSuccessful())
