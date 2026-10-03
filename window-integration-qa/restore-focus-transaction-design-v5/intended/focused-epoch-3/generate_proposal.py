"""Materialize an UNAPPLIED three-file source proposal; never edit predecessor."""
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat

HERE=Path(__file__).resolve().parent
BASE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-planning-v27')

def stamp(path):return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mode':stat.S_IMODE(path.stat().st_mode)}
def save(path,value):
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as stream:stream.write(value)
def methods(source):
    tree=ast.parse(source)
    return {(cls.name,node.name):ast.get_source_segment(source,node) for cls in tree.body if isinstance(cls,ast.ClassDef) for node in cls.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}

def main():
    old={name:(BASE/name).read_text() for name in ('native_desktop.py','owned_commands.py','scene_controller.py')}
    new=dict(old)
    new['native_desktop.py']=new['native_desktop.py'].replace('    def apply_destination(self,window,plan):', (HERE/'native_methods.py.proposed').read_text()+'    def apply_destination(self,window,plan):',1)
    classify_old="argv[1]=='repl' and 'retire_gesture_current' in argv[2]"
    classify_new="argv[1]=='repl' and (len(argv)==2 or 'retire_gesture_current' in argv[2])"
    assert new['owned_commands.py'].count(classify_old)==1
    new['owned_commands.py']=new['owned_commands.py'].replace(classify_old,classify_new)
    new['owned_commands.py']=new['owned_commands.py'].replace('    def check_output(self,args,**options):',(HERE/'owned_methods.py.proposed').read_text()+'    def check_output(self,args,**options):',1)
    focus_old='                        for member,plan in plans:self.desktop.apply_destination(member,plan)\n'
    focus_new='''                        transaction=getattr(self.desktop,'apply_destinations',None)
                        if plans and callable(transaction):
                            transaction(plans,current=lambda:self.owns(record),reservation_lock=self.lock,
                                deadline_ns=record.profile['receivedNs']+2000000000,record=record)
                        else:
                            for member,plan in plans:self.desktop.apply_destination(member,plan)
'''
    refresh_old='''            for member,plan in plans:
                with self.lock:
                    if not self.owns(record):return
                self.desktop.refresh_destination(member,plan)
                with self.lock:
                    if not self.owns(record):return
'''
    refresh_new='''            refresh_many=getattr(self.desktop,'refresh_destinations',None)
            if plans and callable(refresh_many):
                refresh_many(plans,current=lambda:self.owns(record),reservation_lock=self.lock,
                    deadline_ns=record.profile['receivedNs']+2000000000)
            else:
                for member,plan in plans:
                    with self.lock:
                        if not self.owns(record):return
                    self.desktop.refresh_destination(member,plan)
                    with self.lock:
                        if not self.owns(record):return
'''
    assert new['scene_controller.py'].count(focus_old)==1 and new['scene_controller.py'].count(refresh_old)==1
    new['scene_controller.py']=new['scene_controller.py'].replace(focus_old,focus_new).replace(refresh_old,refresh_new)
    conservation={}
    for name,source in new.items():
        compile(source,name,'exec');before=methods(old[name]);after=methods(source)
        changed=[list(key) for key in before if before[key]!=after[key]]
        expected={'native_desktop.py':[], 'owned_commands.py':[['OwnedCommands','classify']], 'scene_controller.py':[['SceneController','prepare']]}[name]
        assert changed==expected,(name,changed)
        conservation[name]={'original':stamp(BASE/name),'proposedSHA256':hashlib.sha256(source.encode()).hexdigest(),
            'originalMethodCount':len(before),'unchangedMethods':len(before)-len(changed),'changedMethods':changed,
            'addedMethods':[list(key) for key in after if key not in before]}
        save(HERE/(name+'.proposed'),source)
    inverse=new['scene_controller.py'].replace(focus_new,focus_old).replace(refresh_new,refresh_old)
    assert inverse==old['scene_controller.py']
    inverse=new['owned_commands.py'].replace(classify_new,classify_old).replace((HERE/'owned_methods.py.proposed').read_text(),'')
    assert inverse==old['owned_commands.py']
    inverse=new['native_desktop.py'].replace((HERE/'native_methods.py.proposed').read_text(),'')
    assert inverse==old['native_desktop.py']
    guard=methods(new['native_desktop.py'])[('NativeDesktop','_guard_destination')].split('\n',2)[2]
    apply=methods(old['native_desktop.py'])[('NativeDesktop','apply_destination')]
    original_guard=apply.split('\n',2)[2].split('        for expression in ')[0].rstrip()
    assert guard.rstrip()==original_guard
    patch=''.join(''.join(difflib.unified_diff(old[name].splitlines(True),new[name].splitlines(True),fromfile='a/'+name,tofile='b/'+name)) for name in old)
    save(HERE/'intended.patch',patch)
    report={'result':'pass','unapplied':True,'wholeFileInverses':True,'originalGuardByteExact':True,
        'allOriginalPreparationTailAndCaptureBodiesExact':True,'conservation':conservation,
        'patchSHA256':hashlib.sha256(patch.encode()).hexdigest(),'inputs':{str(path):stamp(path) for path in [Path(__file__),HERE/'native_methods.py.proposed',HERE/'owned_methods.py.proposed']}}
    save(HERE/'source-conservation.json',json.dumps(report,indent=2)+'\n')
    print(json.dumps({'result':'pass','patch':str(HERE/'intended.patch'),'sha256':report['patchSHA256']}))

if __name__=='__main__':main()
