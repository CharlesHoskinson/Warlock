"""Record and apply the reviewed V7 source pairing; starts no GUI."""
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat

B=Path('/home/hoskinson/window-integration-qa/family-preparation-thumbnail-v7')
BASE=B.parent/'family-recovery-bootstrap-v5'
def sha(raw):return hashlib.sha256(raw).hexdigest()
changes={}
def change(name,old,new):
    current=changes.get(name,(B/name).read_text())
    assert current.count(old)==1,(name,old,current.count(old))
    changes[name]=current.replace(old,new)

change('module_binding.py',"service-readonly-ipc-v20')","service-family-preparation-v23')")
change('module_binding.py',"MANIFEST=SERVICE/'manifest-readonly-ipc-v20.json'","MANIFEST=SERVICE/'manifest-family-preparation-v23.json'")
change('module_binding.py',"MANIFEST_SHA256='d3d836eda0e2a25681df4ca80740ca94f8d2084ea1c48f8834293b740122c068'","# Deliberately refuses until root freezes/reviews the completed V23 packet.\nMANIFEST_SHA256='UNFROZEN_V23_NO_NATIVE_GRANT'")
change('module_binding.py',"'snapshot_cache','production_motion_6d9')","'snapshot_cache','production_motion_6d9','batch_preview')")
change('module_binding.py',"('scene_manager','SceneController','scene_controller','SceneController'))","('scene_manager','SceneController','scene_controller','SceneController'),('native_desktop','BatchPreviews','batch_preview','BatchPreviews'),('native_desktop','OwnedCommands','owned_commands','OwnedCommands'),('batch_preview','key','scene_controller','key'),('batch_preview','rectangle','scene_controller','rectangle'))")
change('module_binding.py',"exact frozen V20 manifest required","exact frozen V23 manifest required")
old="    return [('controller.event',transport.callback),('controller.prepare',controller.prepare),('controller.commit_members',controller.commit_members),('controller.transport_failure',controller.transport_failure),('native.bind_controller',transport.qa_original_bind_controller),('failure.bind',transport.failure.bind),('desktop.commit',desktop.commit),('desktop.clients',desktop.clients),('commands.run',desktop.commands.run),('reader.query',factory.readonly.query),('runtime.persist',factory.resource_writer)]"
new="""    batch=desktop.preview_batch
    return [('controller.event',transport.callback),('controller.prepare',controller.prepare),('controller.commit_members',controller.commit_members),('controller.transport_failure',controller.transport_failure),('native.bind_controller',transport.qa_original_bind_controller),('failure.bind',transport.failure.bind),('desktop.commit',desktop.commit),('desktop.clients',desktop.clients),('commands.run',desktop.commands.run),('reader.query',factory.readonly.query),('runtime.persist',factory.resource_writer),('desktop.finish_capture_previews',desktop.finish_capture_previews),('batch.stage',batch.stage),('batch.finish',batch.finish),('batch.discard',batch.discard),('batch.require_releasable',batch.require_releasable),('batch.require_disposable',batch.require_disposable)]


def batch_relations(factory,number,desktop):
    import batch_preview,native_desktop
    batch=desktop.preview_batch
    expected=Path(factory.guard.env['XDG_RUNTIME_DIR'])/'hypr-window-previews'
    return {
        'batchClass':type(batch) is batch_preview.BatchPreviews,
        'batchCommands':batch.commands is desktop.commands,
        'batchRoot':batch.root==desktop.root and desktop.root.parent==factory.root/'actors',
        'batchPreview':batch.preview==expected and desktop.production.RUNTIME==expected.parent,
        'batchActor':type(desktop.commands.actor) is int and desktop.commands.actor==number,
        'finisherFunction':getattr(desktop.finish_capture_previews,'__func__',None) is native_desktop.NativeDesktop.finish_capture_previews,
    }


def batch_identity(desktop):
    batch=desktop.preview_batch
    return {'instanceID':id(batch),'commandsID':id(batch.commands),'root':str(batch.root),'preview':str(batch.preview)}"""
change('module_binding.py',old,new)
change('module_binding.py',"        if not all(raw['relations'].values()):raise ValueError('actual actor/runtime links differ')","        raw['relations'].update(batch_relations(factory,number,desktop))\n        raw['batch']=batch_identity(desktop)\n        if not all(raw['relations'].values()):raise ValueError('actual actor/runtime links differ')")
change('module_binding.py',"        confirmation['callbacks']={name:callback(fn,packet) for name,fn in selected()}","        confirmation['batch']=batch_identity(desktop)\n        confirmation['batchRelations']=batch_relations(factory,number,desktop)\n        if confirmation['batch']!=raw['batch'] or not all(confirmation['batchRelations'].values()):raise ValueError('actual batch instance or links changed after disk')\n        confirmation['callbacks']={name:callback(fn,packet) for name,fn in selected()}")
change('module_binding.py',"            production=controller.desktop.production","            if not all(batch_relations(factory,number,controller.desktop).values()) or batch_identity(controller.desktop)!=selected[0]['batch']:raise ValueError('actual batch instance or links changed at terminal')\n            production=controller.desktop.production")

change('native_integration.py',"SERVICE = Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-readonly-ipc-v20')","from module_binding import SERVICE, MANIFEST as SERVICE_MANIFEST, MANIFEST_SHA256 as EXPECTED_SERVICE_MANIFEST")
change('native_integration.py',"    if sha(SERVICE/'manifest-readonly-ipc-v20.json')!='d3d836eda0e2a25681df4ca80740ca94f8d2084ea1c48f8834293b740122c068':raise ValueError('Reviewed corrected recovery V17 freeze changed')","    if sha(SERVICE_MANIFEST)!=EXPECTED_SERVICE_MANIFEST:raise ValueError('Reviewed V23 service freeze changed')")
change('native_integration.py',"json.loads((SERVICE / 'manifest-readonly-ipc-v20.json').read_text())","json.loads(SERVICE_MANIFEST.read_text())")
change('native_integration.py',"for p in (SERVICE/'checkpoint-readonly-ipc-v20.json',):","for p in (SERVICE_MANIFEST,):")
change('native_integration.py',"(SERVICE / 'manifest-readonly-ipc-v20.json', PRODUCER_PACKET, QT / 'frozen-inputs.json')","(SERVICE_MANIFEST, PRODUCER_PACKET, QT / 'frozen-inputs.json')")
change('native_integration.py',"report['actualV20Binding']","report['actualServiceBinding']")
insertion="""    # Preserve the exact V5 collector and its failed baseline, not only its name.
    retained_v5=QA/'family-recovery-bootstrap-v5'
    v5_manifest=retained_v5/'frozen-inputs.json'
    if sha(v5_manifest)!='bbd142db7116de7e076df508dcb6d9b57ceda4d6cc5035cec7da6a5867b2e492':raise ValueError('Reviewed V5 collector changed')
    v5_packet=json.loads(v5_manifest.read_text())
    for name,value in v5_packet['inputs'].items():
        mode=v5_packet['inputModes'][name]
        if sha(name)!=value or stat.S_IMODE(Path(name).stat().st_mode)!=mode:raise ValueError('V5 retained source or mode changed')
        if name in inputs and inputs[name]!=value or name in modes and modes[name]!=mode:raise ValueError('V5 retained source conflict')
        inputs[name]=value;modes[name]=mode
    for name,target in v5_packet['symlinks'].items():
        if not Path(name).is_symlink() or os.readlink(name)!=target or name in links and links[name]!=target:raise ValueError('V5 retained link changed')
        links[name]=target
    for path in [v5_manifest,*sorted((retained_v5/'attempt-baseline-1').rglob('*'))]:
        if path.is_file() and not path.is_symlink():inputs[str(path)]=sha(path);modes[str(path)]=stat.S_IMODE(path.stat().st_mode)
"""
change('native_integration.py',"    row = {'inputs': inputs, 'symlinks': links,",insertion+"    row = {'inputs': inputs, 'symlinks': links,")
change('native_faults.py',"SERVICE.name!='service-readonly-ipc-v20'","SERVICE.name!='service-family-preparation-v23'")
for old,new in [('actualV20Binding','actualServiceBinding'),('oldActualV20Binding','oldActualServiceBinding'),('actualV20RecoveryBinding','actualServiceRecoveryBinding')]:
    current=changes.get('native_faults.py',(B/'native_faults.py').read_text())
    assert old in current
    changes['native_faults.py']=current.replace(old,new)
change('native_faults.py','Same frozen packet actual V20 baseline binding required','Same frozen packet actual V23 baseline binding required')
change('service_recovery_observer.py','both observers must select exact frozen V20','both observers must select exact frozen V23')
change('test_actual_binding.py',"len(raw['modules']),18","len(raw['modules']),19")
change('test_actual_binding.py',"  controller=object.__new__(scene_manager.ManagedController);", "  from batch_preview import BatchPreviews\n  desktop.root=factory.root/'actors'/'actor-1-cpu';desktop.production.RUNTIME=Path(self.env['XDG_RUNTIME_DIR']);desktop.preview_batch=BatchPreviews(desktop.root,desktop.production.RUNTIME/'hypr-window-previews',desktop.commands)\n  controller=object.__new__(scene_manager.ManagedController);")
change('test_actual_binding.py',"desktop.production.subprocess=desktop.commands;desktop.base=object.__new__(desktop.production.Desktop)","desktop.production.subprocess=desktop.commands;desktop.production.RUNTIME=Path(self.env['XDG_RUNTIME_DIR']);desktop.base=object.__new__(desktop.production.Desktop)")
current=(B/'test_freezer_v2.py').read_text()
assert current.count("n.SERVICE/'manifest-readonly-ipc-v20.json'")==2
changes['test_freezer_v2.py']=current.replace("n.SERVICE/'manifest-readonly-ipc-v20.json'","n.SERVICE_MANIFEST")
for name in ('actual_service_binding.qnt','actual_service_binding_test.qnt'):
    current=(B/name).read_text()
    import re
    changes[name]=re.sub(r'\b20\b','23',current)

def check_calls(text):
    tree=ast.parse(text)
    result=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='check':
            result.append((node.lineno,ast.dump(node,include_attributes=False)))
    return [v for _,v in sorted(result)]
# Thirty syntactic baseline calls execute 38 gates through original loops.
for name,count in [('native_integration.py',30),('native_faults.py',34)]:
    old=check_calls((BASE/name).read_text());new=check_calls(changes[name])
    assert old==new and len(old)==count,(name,len(old),len(new))
for name,new in changes.items():
    if name.endswith('.py'):ast.parse(new)
plan={'formalBeforeRuntime':str(B/'batch-service-binding-formal-before-pairing-v1.json'),'formalSHA256':sha((B/'batch-service-binding-formal-before-pairing-v1.json').read_bytes()),'nativeGrant':False,'manifestStatus':'awaiting immutable V23 full proof/root freeze','deltas':{}}
for name,new in changes.items():
    old=(B/name).read_bytes()
    assert old==(BASE/name).read_bytes(),name
    plan['deltas'][name]={'beforeSHA256':sha(old),'afterSHA256':sha(new.encode()),'mode':stat.S_IMODE((B/name).stat().st_mode)}
patch=''.join(''.join(difflib.unified_diff((B/name).read_text().splitlines(True),new.splitlines(True),fromfile='V5/'+name,tofile='V7/'+name)) for name,new in changes.items())
def exclusive(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC,0o600)
    with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
exclusive(B/'intended-pairing-v7-v1.diff',patch.encode())
plan['intendedDiffSHA256']=sha(patch.encode())
exclusive(B/'source-pairing-v7-plan-v1.json',(json.dumps(plan,indent=2)+'\n').encode())
for name,new in changes.items():
    assert sha((B/name).read_bytes())==plan['deltas'][name]['beforeSHA256']
    (B/name).write_text(new)
    assert sha((B/name).read_bytes())==plan['deltas'][name]['afterSHA256']
print('Applied',len(changes),'reviewed source deltas; 30/34 original check-call ASTs exact (38 executed baseline gates); native grant false')
