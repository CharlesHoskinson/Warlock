"""Original/current all-visible late metadata comparison; genuine CPU peer only."""
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import time

OUT=Path(__file__).resolve().parent
QA=OUT.parent
CURRENT=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-planning-v27')
OLD=CURRENT.with_name('service-housekeeping-admission-v26')
sys.path[:0]=[str(CURRENT),str(QA)]
from qa_launch import require_qa_scope
from fixture_restore_planning import KernelFixture
from scene_controller import SceneController

def stamp(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}

def main():
 scope=require_qa_scope()
 paths=[Path(__file__),OLD/'scene_controller.py',CURRENT/'scene_controller.py',CURRENT/'native_desktop.py',CURRENT/'fixture_restore_planning.py']
 paths += [CURRENT/name for name in ('owned_commands.py','owned_launch.py','helper_supervisor.py','readonly_ipc.py','native_runtime.py','service_runtime.py','production_motion_6d9.py')]
 sources={str(p):stamp(p) for p in paths}
 spec=importlib.util.spec_from_file_location('original_v26_visible_scene',OLD/'scene_controller.py');module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
 cases=[]
 for label,cls in [('original-v26',module.SceneController),('current-v27',SceneController)]:
  k=KernelFixture()
  try:
   k.controller.workers.shutdown(wait=True)
   k.controller=cls(k.desktop,k.transport);k.controller.lock=k.ipc.lock
   for w in k.fixture.windows:w['workspace']['name']='1'
   for w in k.fixture.native:w['workspace']['name']='1'
   family=k.desktop.family;calls=[]
   def delayed_family(*args,**kwargs):
    calls.append(time.monotonic_ns())
    if len(calls)==1:time.sleep(2.05)
    return family(*args,**kwargs)
   k.desktop.family=delayed_family
   record=k.request();k.wait_worker()
   row={'label':label,'profile':deepcopy(record.profile),'validated':record.validated,'results':deepcopy(record.results),
    'focus':k.focus(),'refresh':[r for r in k.requests if r['wire']=='CPU_REFRESH'],
    'messages':deepcopy(k.transport.sent),'readonly':k.ipc.reader.snapshot(),
    'cpuCommitMarkers':deepcopy(k.fixture.commits),'noWatchdogCalled':True,'workersDrained':not any(j for j in k.keeper.jobs.values())}
   k.assert_drained()
  finally:
   k.close()
   row['actualKeeperTerminal']=deepcopy(k.terminal)
   row['normalStop']=k.terminal['normalStop']
   row['fixtureRuntimeGone']=not k.ipc.runtime.exists()
  cases.append(row)
 original,current=cases
 assert original['validated'] and original['profile']['nativeEndpointAlreadySatisfied'] is True
 assert 'failure' not in original['profile']
 assert current['validated'] is False and current['profile']['failure']=='original scene receipt deadline before destination focus'
 assert all(c['focus']==c['refresh']==c['messages']==[] and c['normalStop'] is True and c['fixtureRuntimeGone'] for c in cases)
 assert all(r['closed'] and r['published'] and r['outcome']=='complete' and r['evidence']['completeServerEOF'] for c in cases for r in c['readonly']['history'])
 assert sources=={str(p):stamp(p) for p in paths}
 row={'result':'counterexample-confirmed','GUI':False,'scope':scope,'cases':cases,'sources':sources,'sourceUnchanged':True,
 'limits':['Actual old/current SceneController with actual selected NativeDesktop adapter and genuine ReadonlyIPC/RuntimeLease/JournalStore/Keeper.',
           'All-visible family and explicit first CPU family observation delay2.05s; no watchdog or deadline extension.',
           'CPU family/pixels/native settlement boundaries unchanged; native core effects/PNG acceptance not claimed.',
           'Zero focus/refresh/seed in both; original endpoint no-op metadata accepted, added empty-plan guard refuses before validation.']}
 with os.fdopen(os.open(OUT/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({'result':row['result'],'report':str(OUT/'report.json')}))

if __name__=='__main__':main()
