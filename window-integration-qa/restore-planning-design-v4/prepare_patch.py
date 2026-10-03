"""Produce proposed files only; immutable selected runtime never written."""
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat

HERE=Path(__file__).resolve().parent
SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-housekeeping-admission-v26')

METHOD='''    def plan_destinations(self,members,*,current,reservation_lock,deadline_ns):
        """Bounded read-only plans; ordered complete results, no native effects."""
        from concurrent.futures import ThreadPoolExecutor
        import time
        if not isinstance(members,list) or not 1<=len(members)<=64:
            raise ValueError('complete bounded destination planning scope required')
        identities=[checked_identity(member) for member in members]
        if len(set(identities))!=len(identities) or type(deadline_ns) is not int:
            raise ValueError('exact unique destination identities and receipt deadline required')
        windows=deepcopy(members)
        stopped=threading.Event()
        def guard():
            with reservation_lock:
                if stopped.is_set() or not current():
                    raise ValueError('destination planning superseded or failed')
                if time.monotonic_ns()>=deadline_ns:
                    raise TimeoutError('original scene receipt deadline during destination planning')
        def plan(window):
            try:
                guard()
                result=self.plan_destination(window)
                guard()
                return result
            except BaseException:
                stopped.set()
                raise
        pool=ThreadPoolExecutor(max_workers=min(3,len(windows)),thread_name_prefix='destination-observation')
        futures=[]
        try:
            futures=[pool.submit(plan,window) for window in windows]
            results=[future.result() for future in futures]
        except BaseException:
            stopped.set()
            for future in futures:future.cancel()
            raise
        finally:
            # Drain every already registered read-only call with no receipt
            # lock held. This grants no extension of scene/effect authority.
            pool.shutdown(wait=True,cancel_futures=True)
        guard()
        if any(result.get('identity')!=list(identity) for result,identity in zip(results,identities,strict=True)):
            raise ValueError('ordered destination observation identity differs')
        return list(zip(members,results,strict=True))
'''


def stamp(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}


def main():
    names=('native_desktop.py','scene_controller.py')
    originals={name:(SERVICE/name).read_text() for name in names}
    proposed=dict(originals)
    marker='    def apply_destination(self,window,plan):\n'
    assert proposed['native_desktop.py'].count(marker)==1
    proposed['native_desktop.py']=proposed['native_desktop.py'].replace(marker,METHOD+marker)
    old='''                for member in members:
                    if member.get('workspace',{}).get('name')!='special:win-minimized':continue
                    with self.lock:
                        if not self.owns(record):return
                    plan=planner(member)
                    with self.lock:
                        if not self.owns(record):return
                    plans.append((member,plan))
'''
    new='''                parallel=getattr(self.desktop,'plan_destinations',None)
                if callable(parallel):
                    hidden=[member for member in members if member.get('workspace',{}).get('name')=='special:win-minimized']
                    if hidden:
                        plans=parallel(hidden,current=lambda:self.owns(record),reservation_lock=self.lock,
                            deadline_ns=record.profile['receivedNs']+2000000000)
                else:
'''+''.join('    '+line if line.strip() else line for line in old.splitlines(keepends=True))
    assert proposed['scene_controller.py'].count(old)==1
    proposed['scene_controller.py']=proposed['scene_controller.py'].replace(old,new)
    focus_old='''                    if planner is not None:
                        for member,plan in plans:self.desktop.apply_destination(member,plan)
'''
    focus_new='''                    if planner is not None:
                        if callable(parallel) and plans and time.monotonic_ns()>=record.profile['receivedNs']+2000000000:
                            raise TimeoutError('original scene receipt deadline before destination focus')
                        for member,plan in plans:self.desktop.apply_destination(member,plan)
'''
    assert proposed['scene_controller.py'].count(focus_old)==1
    proposed['scene_controller.py']=proposed['scene_controller.py'].replace(focus_old,focus_new)
    patches=[];mapping={}
    for name in names:
        ast.parse(proposed[name])
        inverse=proposed[name].replace(METHOD,'') if name=='native_desktop.py' else proposed[name].replace(new,old).replace(focus_new,focus_old)
        assert inverse==originals[name]
        path=HERE/(name+'.proposed');path.write_text(proposed[name])
        mapping[name]={'original':str(SERVICE/name),'old':stamp(SERVICE/name),'proposed':str(path),'new':stamp(path),'wholeInverseExact':True}
        patches.extend(difflib.unified_diff(originals[name].splitlines(True),proposed[name].splitlines(True),fromfile=name,tofile=name))
    (HERE/'intended.patch').write_text(''.join(patches))
    with os.fdopen(os.open(HERE/'intended-source-map.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:
        json.dump({'result':'pass','files':mapping,'nativeEffectApplyBodyByteExact':True,'refreshBodyByteExact':True,
            'OwnedCommandsByteExact':stamp(SERVICE/'owned_commands.py'),'entireOriginalBodyInverseExact':True},f,indent=2);f.write('\n')


if __name__=='__main__':main()
