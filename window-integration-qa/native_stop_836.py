#!/usr/bin/env python3
"""Actual installed actor shutdown; no window requests or GUI input."""
from pathlib import Path
import hashlib,json,os,subprocess,time
from deploy_motion_stop_836 import state
H=Path.home();helper=H/'.local/bin/hypr-window-motion'
root=Path(os.environ['XDG_RUNTIME_DIR'])/'hypr-window-motion'/hashlib.sha256(os.environ['HYPRLAND_INSTANCE_SIGNATURE'].encode()).hexdigest()[:20]
report={'helperSHA256':hashlib.sha256(helper.read_bytes()).hexdigest(),'windowRequests':0,'checks':{}}
assert report['helperSHA256']=='6d9a21114cfc9d8ed4a4669bb4c1a585375abd56bf27de2783e203926dcecbaa'
assert not (root/'control.sock').exists() and not (root/'daemon.pid').exists()
assert not (root/'pending.json').exists() or json.loads((root/'pending.json').read_text())==[]
before=state();actor=None
try:
 for index in range(3):
  result=subprocess.run([str(helper),'stop'],capture_output=True,text=True,timeout=5)
  assert result.returncode==0,result.stderr
 report['checks']['repeatedIdleStopSucceeded']=True
 report['checks']['idleStopNeverStartedActor']=not (root/'daemon.pid').exists() and not (root/'control.sock').exists()
 actor=subprocess.Popen([str(helper),'daemon'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,start_new_session=True)
 deadline=time.monotonic()+5
 while not (root/'control.sock').exists() and time.monotonic()<deadline:
  assert actor.poll() is None,'fixture actor exited before listening'
  time.sleep(.03)
 assert (root/'control.sock').exists() and int((root/'daemon.pid').read_text())==actor.pid
 result=subprocess.run([str(helper),'diagnostics'],capture_output=True,text=True,timeout=5)
 diagnostics=json.loads(result.stdout);assert result.returncode==0 and diagnostics.get('ok')
 report['diagnostics']=diagnostics
 assert not diagnostics.get('events'), 'no native window commit or pixel request expected'
 report['checks']['exactReadonlyActorStarted']=True
 result=subprocess.run([str(helper),'stop'],capture_output=True,text=True,timeout=5)
 assert result.returncode==0,result.stderr
 actor.wait(timeout=5);assert actor.returncode==0
 report['checks']['liveShutdownExitedNormally']=True
 report['checks']['listenerAndPIDRemoved']=not (root/'control.sock').exists() and not (root/'daemon.pid').exists()
 assert subprocess.run([str(helper),'stop'],capture_output=True,timeout=5).returncode==0
 report['checks']['idleStopAfterLiveShutdownSucceeded']=True
 report['checks']['acceptedJournalEmpty']=json.loads((root/'pending.json').read_text())==[]
 report['preservation']={name:value==state()[name] for name,value in before.items()}
 assert all(report['checks'].values()) and all(report['preservation'].values())
 report['passed']=True
except Exception as error:
 report.update(passed=False,error=repr(error));raise
finally:
 if actor and actor.poll() is None:
  subprocess.run([str(helper),'stop'],capture_output=True,timeout=5)
  try:actor.wait(timeout=5)
  except subprocess.TimeoutExpired:actor.terminate();actor.wait(timeout=5)
 (H/'window-integration-qa/minimize-motion-deployment-stop-836-v65/native-stop-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':report['checks'],'preservation':report['preservation']},indent=2))
