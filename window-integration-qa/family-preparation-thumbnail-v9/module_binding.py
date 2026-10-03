"""Read-only actual loaded product source evidence; import starts no resources."""
import hashlib
import importlib
import inspect
import json
import os
import re
from copy import deepcopy
from pathlib import Path
import stat
import sys
import time

SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v24')
MANIFEST=SERVICE/'manifest-family-preparation-v24.json'
# Exact independently reviewed/frozen V24; GUI acceptance remains separate.
MANIFEST_SHA256='b017d8d2a126f76c637429fffc2d77d510161fb89d3f3826795abb47d30b9f2c'
MODULES=('native_runtime','service_runtime','native_desktop','scene_manager','scene_controller','pipe_transport','context_provider','recovery_runtime','recovery_resources','recovery_cancel','readonly_ipc','owned_commands','helper_supervisor','owned_launch','helper_policy','timeout_adapter','snapshot_cache','production_motion_6d9','batch_preview')
LINKS=(('native_runtime','NativeDesktop','native_desktop','NativeDesktop'),('native_runtime','PipeTransport','pipe_transport','PipeTransport'),('native_runtime','RuntimeService','service_runtime','RuntimeService'),('native_runtime','NativeContextProvider','context_provider','NativeContextProvider'),('service_runtime','SceneManager','scene_manager','SceneManager'),('scene_manager','SceneController','scene_controller','SceneController'),('native_desktop','BatchPreviews','batch_preview','BatchPreviews'),('native_desktop','OwnedCommands','owned_commands','OwnedCommands'),('batch_preview','key','scene_controller','key'),('batch_preview','rectangle','scene_controller','rectangle'),('batch_preview','PipeTransport','pipe_transport','PipeTransport'),('batch_preview','OwnedLaunch','owned_launch','OwnedLaunch'),('batch_preview','Keeper','helper_supervisor','Keeper'),('batch_preview','checked_renderer','recovery_resources','checked_renderer'),('batch_preview','verify_process','recovery_resources','verify_process'),('batch_preview','process_start','recovery_resources','process_start'))

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def identity(info):return {'device':info.st_dev,'inode':info.st_ino,'size':info.st_size,'mode':stat.S_IMODE(info.st_mode),'uid':info.st_uid,'gid':info.st_gid}

def read_source(path):
    p=Path(path)
    if not p.is_absolute() or p.resolve()!=p:raise ValueError('actual canonical absolute module source required')
    descriptor=os.open(p,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
    raw={'path':str(p),'fd':descriptor,'before':None,'after':None,'namedBefore':None,'namedAfter':None,'sha256':None,'error':None}
    try:
        before=os.fstat(descriptor);raw['before']=identity(before);raw['namedBefore']=identity(p.lstat())
        if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid() or before.st_mode&0o022 or before.st_size>1048576:raise ValueError('actual candidate source unsafe')
        chunks=[];size=0
        while part:=os.read(descriptor,65536):
            size+=len(part)
            if size>1048576:raise ValueError('actual candidate source exceeds bound')
            chunks.append(part)
        raw['sha256']=sha(b''.join(chunks));raw['after']=identity(os.fstat(descriptor));raw['namedAfter']=identity(p.lstat())
        if not(raw['before']==raw['after']==raw['namedBefore']==raw['namedAfter']) or size!=before.st_size:raise ValueError('actual module source replaced during observation')
    except BaseException as failure:raw['error']={'type':type(failure).__name__,'message':str(failure)}
    finally:os.close(descriptor)
    return raw

def functions(module):
    result=[]
    for name,value in vars(module).items():
        if inspect.isfunction(value) and value.__module__==module.__name__:result.append((name,value))
        elif inspect.isclass(value) and value.__module__==module.__name__:
            for method,fn in vars(value).items():
                if isinstance(fn,(classmethod,staticmethod)):fn=fn.__func__
                if inspect.isfunction(fn):
                    fn=inspect.unwrap(fn)
                    if fn.__module__==module.__name__ and not fn.__code__.co_filename.startswith('<'):result.append((name+'.'+method,fn))
    return [{'symbol':name,'objectID':id(fn),'filename':fn.__code__.co_filename} for name,fn in sorted(result)]

def _observe(phase,*,previous=None):
    raw={'version':1,'phase':phase,'observedNs':time.monotonic_ns(),'servicePID':os.getpid(),'serviceStart':None,'manifest':str(MANIFEST),'manifestExpectedSHA256':MANIFEST_SHA256,'manifestActualSHA256':None,'modules':[],'links':[],'errors':[],'usable':False}
    loaded={};packet=None
    try:
        if len(MODULES)!=19 or len(set(MODULES))!=19:raise ValueError('exact nineteen unique actual module observations required')
        blob=MANIFEST.read_bytes();raw['manifestActualSHA256']=sha(blob);packet=json.loads(blob)
        if raw['manifestActualSHA256']!=MANIFEST_SHA256:raise ValueError('exact frozen V24 manifest required')
        for name in MODULES:
            # Cached modules are inspected too. Adding candidate PATH never
            # substitutes for a stale module already present in sys.modules.
            module=importlib.import_module(name);loaded[name]=module
            entry={'name':name,'objectID':id(module),'actualFile':getattr(module,'__file__',None),'source':None,'callables':[],'error':None}
            try:
                entry['source']=read_source(entry['actualFile']);entry['callables']=functions(module)
                expected=str(SERVICE/(name+'.py'))
                if entry['actualFile']!=expected or entry['source']['error'] or entry['source']['sha256']!=packet['inputs'].get(expected) or entry['source']['before']['mode']!=packet['inputModes'].get(expected):raise ValueError('actual loaded module does not match frozen candidate: '+name)
                if not entry['callables'] or any(fn['filename']!=expected for fn in entry['callables']):raise ValueError('actual source-bearing callable path differs: '+name)
            except BaseException as failure:entry['error']={'type':type(failure).__name__,'message':str(failure)};raw['errors'].append(entry['error'])
            raw['modules'].append(entry)
        for left,symbol,right,target in LINKS:
            actual=getattr(loaded[left],symbol,None);expected=getattr(loaded[right],target,None)
            item={'left':left+'.'+symbol,'right':right+'.'+target,'actualObjectID':id(actual),'expectedObjectID':id(expected),'matched':actual is not None and actual is expected}
            raw['links'].append(item)
            if not item['matched']:raw['errors'].append({'type':'ValueError','message':'actual linked runtime object differs: '+item['left']})
        raw['serviceStart']=loaded['service_runtime'].process_start(os.getpid())
        if type(raw['serviceStart']) is not int or raw['serviceStart']<1:raise ValueError('actual service lifetime unavailable')
    except BaseException as failure:raw['errors'].append({'type':type(failure).__name__,'message':str(failure)})
    stable={'servicePID':raw['servicePID'],'serviceStart':raw['serviceStart'],'manifestSHA256':raw['manifestActualSHA256'],'modules':[{'name':m['name'],'objectID':m['objectID'],'actualFile':m['actualFile'],'source':None if m['source'] is None else {k:m['source'][k] for k in ('path','before','after','namedBefore','namedAfter','sha256','error')},'callables':m['callables'],'error':m['error']} for m in raw['modules']],'links':raw['links']}
    raw['moduleToken']=digest(stable)
    if previous is not None and (previous.get('errors') or previous.get('moduleToken')!=raw['moduleToken']):raw['errors'].append({'type':'ValueError','message':'fresh actual module/owner witness differs from captured proof'})
    raw['rawEvidenceOnly']=True
    return raw

def persist_raw(destination,raw):
    destination=Path(destination);data=(json.dumps(raw,indent=2)+'\n').encode()
    descriptor=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC|os.O_NOFOLLOW,0o600)
    with os.fdopen(descriptor,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
    parent=os.open(destination.parent,os.O_DIRECTORY|os.O_RDONLY|os.O_CLOEXEC)
    try:os.fsync(parent)
    finally:os.close(parent)
    before=destination.lstat();actual=destination.read_bytes();after=destination.lstat()
    if identity(before)!=identity(after) or actual!=data:raise ValueError('raw binding disk confirmation differs')
    return {'path':str(destination),'sha256':sha(data),'identity':identity(after)}


def capture(destination,phase,*,previous=None):
    raw=_observe(phase,previous=previous);disk=persist_raw(destination,raw)
    if raw['errors']:raise ValueError('actual loaded source refused; raw evidence: '+str(destination))
    fresh=_observe(phase+'-post-disk',previous=raw)
    fresh['capturedRaw']=disk
    confirmation=Path(destination).with_name(Path(destination).stem+'-confirmation.json')
    confirmed_disk=persist_raw(confirmation,fresh)
    if fresh['errors']:raise ValueError('actual post-disk source refused; raw evidence: '+str(confirmation))
    raw['confirmation']=confirmed_disk
    # This proves source observation only. A RuntimeLease is NOT yet bound.
    return raw


def owner_projection(factory,lease):
    if lease.owner.get('nonce')!=lease.nonce or lease.owner.get('session')!=lease.session:raise ValueError('actual lease owner token inconsistent')
    return {'pid':lease.owner['pid'],'start':lease.owner['start'],'uid':os.getuid(),'nonce':lease.nonce,'session':lease.session,'root':str(lease.root),'rootIdentity':list(lease.root_identity),'lockIdentity':list(lease.lock_identity),'compositorPID':factory.guard.pid,'compositorStart':factory.guard.start}


def callback(fn,packet):
    function=getattr(fn,'__func__',fn);code=getattr(function,'__code__',None)
    if code is None:raise ValueError('actual source-bearing callback required')
    material=read_source(code.co_filename)
    if material['error'] or material['sha256']!=packet['inputs'].get(material['path']) or material['before']['mode']!=packet['inputModes'].get(material['path']):raise ValueError('actual callback source differs from frozen package')
    return {'functionID':id(function),'boundOwnerID':id(getattr(fn,'__self__',None)),'filename':code.co_filename,'source':{k:material[k] for k in ('path','before','sha256')}}


def bind_owner(factory,verify,destination,initial,collector_digest):
    import native_runtime,service_runtime
    lease=getattr(verify,'__self__',None)
    raw={'version':1,'phase':'first-owner-bind','usable':False,'errors':[],'moduleToken':None,'owner':None,'ownerToken':None,'callbacks':{},'collectorSHA256':None}
    try:
        if type(lease) is not service_runtime.RuntimeLease or getattr(verify,'__func__',None) is not service_runtime.RuntimeLease.verify or not isinstance(factory,native_runtime.NativeFactory):raise ValueError('actual bound lease/factory required')
        if type(factory.guard) is not native_runtime.NativeSession:raise ValueError('actual linked NativeSession required')
        verify();modules=capture(Path(destination).with_name('actual-modules-at-owner-bind.json'),'owner-module-observation',previous=initial)
        raw['moduleToken']=modules['moduleToken'];raw['owner']=owner_projection(factory,lease);raw['ownerToken']=digest(raw['owner'])
        if raw['owner']['pid']!=os.getpid() or raw['owner']['start']!=service_runtime.process_start(os.getpid()) or lease.root!=factory.root or lease.session!=factory.guard.session:raise ValueError('actual lease root/lifetime differs')
        own=Path(__file__).parent/'frozen-inputs.json';blob=own.read_bytes();raw['collectorSHA256']=sha(blob)
        if raw['collectorSHA256']!=collector_digest:raise ValueError('exact collector frozen source required')
        packet=json.loads(blob);candidate=json.loads(MANIFEST.read_text())
        if not {'inputs','inputModes'}.issubset(packet):raise ValueError('complete collector source modes required')
        # Both source closures are independently pinned; actual callbacks must
        # come from one of these exact reviewed files, never arbitrary imports.
        for field in ('inputs','inputModes'):packet[field]={**candidate[field],**packet[field]}
        for name in ('__call__','bind_lease','context','helper_changed','readonly_changed'):
            raw['callbacks'][name]=callback(getattr(factory,name),packet)
        if hasattr(factory,'recover'):raw['callbacks']['recover']=callback(factory.recover,packet)
        raw['callbacks']['lease.verify']=callback(verify,packet)
        verify()
    except BaseException as failure:raw['errors'].append({'type':type(failure).__name__,'message':str(failure)})
    disk=persist_raw(destination,raw)
    if raw['errors']:raise ValueError('complete owner binding refused; raw evidence: '+str(destination))
    confirmation={'phase':'owner-post-disk','capturedRaw':disk,'errors':[],'owner':None,'callbacks':{},'usable':False}
    try:
        verify();confirmation['owner']=owner_projection(factory,lease)
        for name in raw['callbacks']:
            selected=verify if name=='lease.verify' else getattr(factory,name)
            confirmation['callbacks'][name]=callback(selected,packet)
        modules=capture(Path(destination).with_name('actual-modules-owner-post-disk.json'),'owner-post-disk',previous=initial)
        confirmation['moduleToken']=modules['moduleToken']
        if confirmation['owner']!=raw['owner'] or confirmation['callbacks']!=raw['callbacks'] or modules['moduleToken']!=raw['moduleToken']:raise ValueError('owner or linked callbacks changed after disk binding')
        verify()
    except BaseException as failure:confirmation['errors'].append({'type':type(failure).__name__,'message':str(failure)})
    raw['confirmation']=persist_raw(Path(destination).with_name('actual-owner-binding-confirmation.json'),confirmation)
    if confirmation['errors']:raise ValueError('complete post-disk owner binding refused; raw evidence retained')
    raw['usable']=True
    return raw


def source_packet():
    candidate=json.loads(MANIFEST.read_text());collector=json.loads((Path(__file__).parent/'frozen-inputs.json').read_text())
    return {field:{**candidate[field],**collector[field]} for field in ('inputs','inputModes')}


def typed_json(value):
    """Strict JSON types: comparing canonical bytes retains bool/int distinction."""
    def check(v):
        if type(v) is dict:
            if any(type(k) is not str for k in v):raise ValueError('exact string JSON keys required')
            for item in v.values():check(item)
        elif type(v) is list:
            for item in v:check(item)
        elif type(v) not in (str,int,bool,type(None)):raise ValueError('exact JSON scalar/container types required')
    check(value)
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def renderer_owner_types(owner,environment,packet):
    # Pure metadata decoding. No _closed, poll, /proc, source or material read.
    import recovery_resources,helper_policy
    expected={'pid','start','uid','producer','launcher','script','argv','scriptFD','producerFD','targetArgv','mode','interpreter','policy','policySHA256','environment'}
    if type(owner) is not dict or set(owner)!=expected:raise ValueError('complete modern renderer metadata required')
    typed_json(owner)
    if any(type(owner[k]) is not int or owner[k]<1 for k in ('pid','start'))or type(owner['uid']) is not int or owner['uid']!=os.getuid():raise ValueError('typed renderer lifetime/UID required')
    if any(type(owner[k]) is not int or owner[k]<0 for k in ('scriptFD','producerFD')):raise ValueError('typed renderer descriptor values required')
    for key,sealed in (('producer',True),('launcher',False),('script',True)):
        if type(owner[key]) is not dict:raise ValueError('exact renderer material metadata required')
        recovery_resources.checked_material(owner[key],sealed=sealed)
    if owner['mode']!='elf'or owner['interpreter']is not None or typed_json(owner['policy'])!=typed_json(helper_policy.POLICY)or owner['policySHA256']!=packet['inputs'][str(SERVICE/'helper_policy.py')]:raise ValueError('exact reviewed owned renderer metadata required')
    target=[f"/proc/self/fd/{owner['producerFD']}"]
    if type(owner['targetArgv'])is not list or owner['targetArgv']!=target:raise ValueError('default sealed renderer invocation required')
    argv=owner['argv']
    if type(argv)is not list or len(argv)!=8 or any(type(v)is not str for v in argv):raise ValueError('exact renderer launcher arguments required')
    if argv[1]!=f"/proc/self/fd/{owner['scriptFD']}"or not argv[2].isdigit()or not argv[3].isdigit()or argv[4]!=str(owner['producerFD'])or typed_json(json.loads(argv[5]))!=typed_json(target)or argv[6:]!=['elf','-1']:raise ValueError('exact owned renderer argument binding required')
    if type(owner['environment'])is not dict or typed_json(owner['environment'])!=typed_json(environment)or any(type(v)is not str or not v for v in owner['environment'].values()):raise ValueError('exact renderer session selectors required')


def renderer_observation(factory,number,desktop,transport,packet,*,terminal=False):
    """Immediate memory/source role observation; exec proof belongs to V24."""
    import subprocess,batch_preview,pipe_transport,owned_launch,helper_supervisor
    result={'stable':None,'lifecycle':None,'relations':{},'errors':[]}
    try:
        batch=desktop.preview_batch;binding=batch.renderer_binding
        fields={'transport','launch','process','keeper','job','actor','ownership','producerSHA256','environment'}
        result['relations']['bindingShape']=type(binding)is dict and set(binding)==fields
        if not result['relations']['bindingShape']:raise ValueError('exact renderer binding dictionary required')
        launch=transport.owned_launch;process=transport.process;keeper=desktop.commands.keeper
        result['relations']['rendererClasses']=(type(transport)is pipe_transport.PipeTransport and type(launch)is owned_launch.OwnedLaunch and type(process)is subprocess.Popen and type(keeper)is helper_supervisor.Keeper)
        if not result['relations']['rendererClasses']:raise ValueError('canonical actual renderer objects required')
        # No process/material/source IO is performed under this registry lock.
        with keeper.lock:
            environment={k:factory.guard.env[k]for k in ('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY')}
            owner=deepcopy(binding['ownership']);renderer_owner_types(owner,environment,packet)
            result['stable']={'bindingID':id(binding),'transportID':id(binding['transport']),'launchID':id(binding['launch']),'processID':id(binding['process']),'keeperID':id(binding['keeper']),
                'job':binding['job'],'actor':binding['actor'],'ownership':owner,'producerSHA256':binding['producerSHA256'],'environment':deepcopy(binding['environment']),
                'keeperRoot':str(keeper.root),'keeperRootIdentity':deepcopy(keeper.ownership['rootIdentity']),'keeperNonce':keeper.nonce,'keeperPID':keeper.ownership['pid'],'keeperStart':keeper.ownership['start']}
            typed_json(result['stable'])
            result['lifecycle']={'terminalObservation':terminal,'rendererReturncode':process.returncode,'transportClosed':transport.closed,'transportClosing':transport.closing,'transportFailed':transport.failed,'transportCloseError':transport.close_error,'launchClosed':launch.closed,'keeperClosed':keeper.closed,'keeperReturncode':keeper.process.returncode,'keeperPhase':keeper.ownership['phase'],'keeperTerminal':deepcopy(keeper.ownership.get('terminal'))}
            typed_json(result['lifecycle'])
            result['relations']['rendererObjectChain']=(binding['transport']is transport and binding['launch']is launch and binding['process']is process and binding['keeper']is keeper and factory.keeper is keeper and launch.keeper is keeper and launch.process is process and keeper.root==factory.root)
            result['relations']['rendererActorJob']=(type(number)is int and number>0 and type(binding['actor'])is int and binding['actor']==number==desktop.commands.actor and type(desktop.commands.actor)is int and type(binding['job'])is str and re.fullmatch('[0-9a-f]{32}',binding['job'])is not None and launch.job==binding['job'])
            result['relations']['rendererPopenPID']=(type(process.pid)is int and process.pid==owner['pid']and typed_json(process.args)==typed_json(owner['argv']))
            result['relations']['rendererSelectedMaterial']=(type(binding['producerSHA256'])is str and binding['producerSHA256']==factory.producer_hash==owner['producer']['sha256']and typed_json(binding['environment'])==typed_json(environment))
            result['relations']['rendererOwnership']=(typed_json(launch.ownership)==typed_json(owner))
            result['relations']['keeperOwnedContext']=(all(type(keeper.ownership[k])is int and keeper.ownership[k]>0 for k in ('pid','start','servicePID','serviceStart'))and type(keeper.nonce)is str and re.fullmatch('[0-9a-f]{32}',keeper.nonce)is not None and keeper.ownership['nonce']==keeper.nonce and keeper.ownership['servicePID']==factory.binding_owner['owner']['pid']and keeper.ownership['serviceStart']==factory.binding_owner['owner']['start']and keeper.ownership['root']==str(factory.root)and typed_json(keeper.ownership['rootIdentity'])==typed_json(factory.binding_owner['owner']['rootIdentity'])and typed_json(keeper.ownership['environment'])==typed_json(environment))
            if terminal:
                result['relations']['rendererNormalClose']=(transport.closed is True and transport.closing is True and transport.failed is False and transport.close_error is None and launch.closed is True and type(process.returncode)is int and process.returncode==0)
                result['relations']['rendererRegistrationRetired']=(not keeper.jobs and not keeper.children)
                result['relations']['keeperNormalStop']=(keeper.closed is True and type(keeper.process.returncode)is int and keeper.process.returncode==0 and keeper.ownership['phase']=='closed'and keeper.ownership['terminal']['normalStop']is True)
            else:
                expected={'job':binding['job'],'kind':'renderer','actor':number,'phase':'released','ownership':owner}
                own=[row for row in keeper.jobs.values()if row.get('actor')==number]
                result['relations']['rendererRegisteredOwner']=(len(own)==1 and typed_json(own[0])==typed_json(expected)and keeper.children.get(binding['job'])is process)
                result['relations']['rendererLiveRegistration']=(launch.closed is False and transport.closed is False and transport.closing is False and transport.failed is False and process.returncode is None)
        for name in ('bind_renderer','_closed','_renderer_matches'):
            fn=getattr(batch,name,None)
            result['relations']['rendererGuard.'+name]=(getattr(fn,'__func__',None)is getattr(batch_preview.BatchPreviews,name)and getattr(fn,'__self__',None)is batch)
        for name in ('_typed_equal','_renderer_witness'):
            result['relations']['rendererGuard.'+name]=(getattr(batch,name,None)is getattr(batch_preview.BatchPreviews,name))
        if not all(result['relations'].values()):raise ValueError('actual renderer binding role or ownership differs')
    except BaseException as failure:result['errors'].append({'type':type(failure).__name__,'message':str(failure)})
    return result



def actor_callbacks(factory,desktop,transport,controller):
    batch=desktop.preview_batch
    return [('controller.event',transport.callback),('controller.prepare',controller.prepare),('controller.commit_members',controller.commit_members),('controller.transport_failure',controller.transport_failure),('native.bind_controller',transport.qa_original_bind_controller),('failure.bind',transport.failure.bind),('desktop.commit',desktop.commit),('desktop.clients',desktop.clients),('commands.run',desktop.commands.run),('reader.query',factory.readonly.query),('runtime.persist',factory.resource_writer),('desktop.finish_capture_previews',desktop.finish_capture_previews),('batch.stage',batch.stage),('batch.finish',batch.finish),('batch.discard',batch.discard),('batch.require_releasable',batch.require_releasable),('batch.require_disposable',batch.require_disposable),('batch.bind_renderer',batch.bind_renderer),('batch._closed',batch._closed),('batch._renderer_matches',batch._renderer_matches),('batch._typed_equal',batch._typed_equal),('batch._renderer_witness',batch._renderer_witness)]


def batch_relations(factory,number,desktop):
    import batch_preview,native_desktop
    batch=desktop.preview_batch
    expected=Path(factory.guard.env['XDG_RUNTIME_DIR'])/'hypr-window-previews'
    result={
        'batchClass':type(batch) is batch_preview.BatchPreviews,
        'batchCommands':batch.commands is desktop.commands,
        'batchRoot':batch.root==desktop.root and desktop.root.parent==factory.root/'actors',
        'batchPreview':batch.preview==expected and desktop.production.RUNTIME==expected.parent,
        'batchActor':type(desktop.commands.actor) is int and desktop.commands.actor==number,
        'finisherFunction':getattr(desktop.finish_capture_previews,'__func__',None) is native_desktop.NativeDesktop.finish_capture_previews,
        'finisherOwner':getattr(desktop.finish_capture_previews,'__self__',None) is desktop,
    }
    for name in ('stage','finish','discard','require_releasable','require_disposable'):
        method=getattr(batch,name,None)
        result['batchCallback.'+name]=(getattr(method,'__func__',None) is getattr(batch_preview.BatchPreviews,name) and getattr(method,'__self__',None) is batch)
    return result


def batch_identity(desktop):
    batch=desktop.preview_batch
    return {'instanceID':id(batch),'commandsID':id(batch.commands),'root':str(batch.root),'preview':str(batch.preview)}


def terminal_batch_confirmation(factory,actors,packet):
    controllers=getattr(factory,'observed_controllers',[])
    if len(controllers)!=len(actors) or len({number for number,_ in controllers})!=len(controllers):raise ValueError('complete unique actual terminal actors required')
    result=[]
    for number,controller in controllers:
        selected=[row for row in actors if row['actor']==number]
        relations=batch_relations(factory,number,controller.desktop)
        instance=batch_identity(controller.desktop)
        callbacks={name:callback(fn,packet) for name,fn in actor_callbacks(factory,controller.desktop,controller.transport,controller)}
        if len(selected)!=1 or not all(relations.values()) or instance!=selected[0]['batch'] or callbacks!=selected[0]['callbacks']:raise ValueError('actual batch or callbacks replaced at terminal confirmation')
        renderer=renderer_observation(factory,number,controller.desktop,controller.transport,packet,terminal=True)
        if renderer['errors']or typed_json(renderer['stable'])!=typed_json(selected[0]['renderer']['stable']):raise ValueError('actual retained renderer identity or normal closure differs')
        result.append({'actor':number,'batch':instance,'relations':relations,'callbacks':callbacks,'renderer':renderer})
    return result


def linked_actor(factory,number,desktop,transport,controller,destination):
    """Observe the actual instances and installed callback, before preparation."""
    import native_runtime,scene_manager,scene_controller,pipe_transport,owned_commands
    raw={'phase':'actor-linked','actor':number,'errors':[],'callbacks':{},'relations':{},'usable':False}
    try:
        if not factory.binding_owner['usable']:raise ValueError('complete initial binding required')
        factory.lease_verify();factory.guard.verify();packet=source_packet()
        raw['relations']={
            'desktop':type(desktop) is native_runtime.PinnedNativeDesktop,
            'transport':type(transport) is pipe_transport.PipeTransport,
            'controller':type(controller) is scene_manager.ManagedController,
            'controllerDesktop':controller.desktop is desktop,
            'controllerTransport':controller.transport is transport,
            'eventOwner':getattr(transport.callback,'__self__',None) is controller,
            'eventFunction':getattr(transport.callback,'__func__',None) is scene_manager.ManagedController.event,
            'ownedCommands':type(desktop.commands) is owned_commands.OwnedCommands,
            'readonly':desktop.commands.readonly is factory.readonly,
            'productionCommands':desktop.production.subprocess is desktop.commands,
            'baseClass':type(desktop.base) is desktop.production.Desktop,
            'failureBinding':type(transport.failure) is native_runtime.FailureBinding,
            'failureClosure':inspect.getclosurevars(transport.qa_original_bind_controller).nonlocals.get('binding') is transport.failure,
        }
        raw['relations'].update(batch_relations(factory,number,desktop))
        raw['batch']=batch_identity(desktop)
        raw['renderer']=renderer_observation(factory,number,desktop,transport,packet)
        raw['relations'].update(raw['renderer']['relations'])
        if raw['renderer']['errors']:raise ValueError('actual renderer link refused; raw evidence retained')
        if not all(raw['relations'].values()):raise ValueError('actual actor/runtime links differ')
        def selected():return actor_callbacks(factory,desktop,transport,controller)
        for name,fn in selected():raw['callbacks'][name]=callback(fn,packet)
        source=read_source(desktop.production.__file__)
        raw['production']={'actualFile':desktop.production.__file__,'source':source,'callables':functions(desktop.production)}
        expected=str(SERVICE/'production_motion_6d9.py')
        if source['error'] or source['path']!=expected or source['sha256']!=packet['inputs'][expected] or source['before']['mode']!=packet['inputModes'][expected] or any(f['filename']!=expected for f in raw['production']['callables']):raise ValueError('actual independent production module differs')
        raw['ownerToken']=digest(owner_projection(factory,factory.lease_verify.__self__))
        if raw['ownerToken']!=factory.binding_owner['ownerToken']:raise ValueError('actor belongs to changed owner')
        factory.lease_verify()
    except BaseException as failure:raw['errors'].append({'type':type(failure).__name__,'message':str(failure)})
    raw['disk']=persist_raw(destination,raw)
    if raw['errors']:raise ValueError('actual linked actor refused; raw evidence retained')
    confirmation={'phase':'actor-post-disk','errors':[],'capturedRaw':raw['disk'],'callbacks':{},'ownerToken':None}
    try:
        factory.lease_verify();confirmation['ownerToken']=digest(owner_projection(factory,factory.lease_verify.__self__))
        confirmation['batch']=batch_identity(desktop)
        confirmation['batchRelations']=batch_relations(factory,number,desktop)
        confirmation['renderer']=renderer_observation(factory,number,desktop,transport,packet)
        if confirmation['renderer']['errors']or typed_json(confirmation['renderer']['stable'])!=typed_json(raw['renderer']['stable']):raise ValueError('actual renderer binding changed after disk')
        if confirmation['batch']!=raw['batch'] or not all(confirmation['batchRelations'].values()):raise ValueError('actual batch instance or links changed after disk')
        confirmation['callbacks']={name:callback(fn,packet) for name,fn in selected()}
        if confirmation['callbacks']!=raw['callbacks'] or confirmation['ownerToken']!=raw['ownerToken'] or functions(desktop.production)!=raw['production']['callables'] or read_source(desktop.production.__file__)['sha256']!=raw['production']['source']['sha256']:raise ValueError('actual actor changed after disk observation')
        factory.lease_verify()
    except BaseException as failure:confirmation['errors'].append({'type':type(failure).__name__,'message':str(failure)})
    raw['confirmation']=persist_raw(Path(destination).with_name(Path(destination).stem+'-confirmation.json'),confirmation)
    if confirmation['errors']:raise ValueError('actual actor confirmation refused; raw evidence retained')
    raw['usable']=True
    return raw


def archive_final(factory,service,destination,modules):
    """Terminal evidence has no live lease authority after normal close."""
    from readonly_ipc import checked_retained
    raw={'phase':'terminal-binding','errors':[],'usable':False,'moduleToken':modules['moduleToken'],'owner':None,'ownerToken':None,'ledger':None,'ledgerToken':None,'journal':None,'actors':getattr(factory,'observed_bindings',[])}
    try:
        lease=service.lease;raw['owner']=owner_projection(factory,lease);raw['ownerToken']=digest(raw['owner'])
        if modules['errors'] or raw['moduleToken']!=factory.binding_bootstrap['moduleToken'] or raw['ownerToken']!=factory.binding_owner['ownerToken']:raise ValueError('final module or owner token replaced')
        if not service.closed or service.failure or lease.fd is not None:raise ValueError('normal service lease closure required')
        with factory.readonly.lock:raw['ledger']=factory.readonly.snapshot()
        raw['journal']=service.store.read();raw['ledgerToken']=digest(raw['ledger'])
        validate_ledger(raw['ledger'],raw['owner'],raw['journal'])
        checked_retained(raw['ledger'],root=factory.root,environment={k:factory.guard.env[k] for k in ('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY')},keeper=raw['journal']['helperOwnership']['keeper'],guard=factory.guard)
        if factory.readonly.source!=raw['ledger']['issuer']['adapter'] or factory.readonly.issuer!=raw['ledger']['issuer'] or any(not row['usable'] or row['errors'] or row['ownerToken']!=raw['ownerToken'] for row in raw['actors']):raise ValueError('actual reader/actor bindings differ')
        packet=source_packet()
        raw['terminalBatchConfirmation']=terminal_batch_confirmation(factory,raw['actors'],packet)
        for number,controller in getattr(factory,'observed_controllers',[]):
            selected=[row for row in raw['actors'] if row['actor']==number]
            if len(selected)!=1 or {name:callback(fn,packet) for name,fn in actor_callbacks(factory,controller.desktop,controller.transport,controller)}!=selected[0]['callbacks']:raise ValueError('actual retained actor callbacks changed at terminal')
            if not all(batch_relations(factory,number,controller.desktop).values()) or batch_identity(controller.desktop)!=selected[0]['batch']:raise ValueError('actual batch instance or links changed at terminal')
            production=controller.desktop.production
            if production.__file__!=selected[0]['production']['actualFile'] or functions(production)!=selected[0]['production']['callables'] or production.subprocess is not controller.desktop.commands or type(controller.desktop.base) is not production.Desktop:raise ValueError('actual per-actor production links changed at terminal')
    except BaseException as failure:raw['errors'].append({'type':type(failure).__name__,'message':str(failure)})
    disk=persist_raw(destination,raw)
    confirmation={'phase':'terminal-post-disk','capturedRaw':disk,'errors':[],'owner':None,'ledgerToken':None,'moduleToken':None}
    try:
        confirmation['owner']=owner_projection(factory,service.lease)
        fresh=service.store.read();confirmation['ledgerToken']=digest(fresh['readonlyOwnership'])
        confirmation['moduleToken']=capture(Path(destination).with_name('actual-modules-final-confirm.json'),'terminal-post-disk',previous=modules)['moduleToken']
        packet=source_packet()
        confirmation['terminalBatchConfirmation']=terminal_batch_confirmation(factory,raw['actors'],packet)
        if raw['errors']:raise ValueError('terminal binding refused before post-disk acceptance')
        if confirmation['terminalBatchConfirmation']!=raw['terminalBatchConfirmation']:raise ValueError('actual terminal batch witness changed after disk')
        if fresh!=raw['journal'] or factory.readonly.snapshot()!=raw['ledger'] or confirmation['owner']!=raw['owner'] or confirmation['ledgerToken']!=raw['ledgerToken'] or confirmation['moduleToken']!=raw['moduleToken']:raise ValueError('terminal proof replaced after disk confirmation')
    except BaseException as failure:confirmation['errors'].append({'type':type(failure).__name__,'message':str(failure)})
    raw['confirmation']=persist_raw(Path(destination).with_name('actual-terminal-binding-confirmation.json'),confirmation)
    if raw['errors'] or confirmation['errors']:raise ValueError('actual terminal binding refused; raw evidence retained')
    raw['usable']=True
    return raw


def validate_ledger(ledger,owner,journal):
    if not isinstance(ledger,dict) or ledger.get('fault') is not False or not ledger.get('history') or journal.get('readonlyOwnership')!=ledger:raise ValueError('exact nonempty durable current ledger required')
    issuer=ledger['issuer']
    for field in ('pid','start','uid','root','rootIdentity','lockIdentity','nonce','session','compositorPID','compositorStart'):
        if issuer.get(field)!=owner.get(field):raise ValueError('actual ledger owner differs: '+field)
    seen=set();descriptors=set()
    requests={'j/clients','j/monitors','j/workspaces','j/activewindow','/repl print(hl.plugin.hyprbars.window_families())'}
    for row in ledger['history']:
        if type(row.get('id')) is not str or len(row['id'])!=32 or row['id'] in seen:raise ValueError('unique actual query ID required')
        seen.add(row['id']);descriptor=(row.get('fd'),tuple(row.get('fdIdentity',[])))
        if descriptor in descriptors or type(row.get('fd')) is not int or row['fd']<0 or len(descriptor[1])!=2:raise ValueError('unique typed actual descriptor identity required')
        descriptors.add(descriptor)
        evidence=row.get('evidence')
        if row.get('closed') is not True or row.get('published') is not True or row.get('outcome')!='complete' or row.get('error') is not None or row.get('issuerSHA256')!=digest(issuer) or row.get('request') not in requests or row.get('requestSHA256')!=sha(row['request'].encode()) or not isinstance(evidence,dict) or evidence.get('completeServerEOF') is not True or evidence.get('peer',{}).get('pid')!=owner['compositorPID'] or evidence.get('peer',{}).get('uid')!=owner['uid']:raise ValueError('complete closed actual query proof required')
    return True


def validate_evidence(evidence):
    before=evidence.get('moduleBindingBefore',{});after=evidence.get('actualTerminalBinding',{});bootstrap=evidence.get('moduleBindingBootstrap',{})
    if before.get('usable') is not True or after.get('usable') is not True or before.get('errors') or after.get('errors') or before.get('ownerToken')!=after.get('ownerToken') or bootstrap.get('moduleToken')!=after.get('moduleToken'):raise ValueError('actual current binding acceptance required')
    if before['ownerToken']!=digest(before['owner']) or after['ownerToken']!=digest(after['owner']) or after['ledgerToken']!=digest(after['ledger']):raise ValueError('concrete owner/ledger digest differs')
    validate_ledger(after['ledger'],after['owner'],after['journal'])
    probe=evidence.get('actualOwnedDataProbe',{})
    if probe.get('usable') is not True or probe.get('errors') or probe.get('ownerToken')!=after['ownerToken'] or probe.get('row') not in after['ledger']['history']:raise ValueError('fresh actual service-owned query evidence required')
    if probe.get('nativeAuthority') is not False or probe.get('replySHA256')!=probe['row']['evidence']['replySHA256'] or probe.get('replyBytes')!=probe['row']['evidence']['replyBytes']:raise ValueError('labelled actual probe reply differs')
    for field in ('disk','confirmation'):
        link=probe.get(field,{});path=Path(link.get('path',''))
        if not path.is_file() or path.is_symlink() or sha(path.read_bytes())!=link.get('sha256') or identity(path.stat())!=link.get('identity'):raise ValueError('actual data probe archive differs')
        observation=json.loads(path.read_text())
        if observation.get('errors') or observation.get('ownerToken')!=probe['ownerToken'] or observation.get('row')!=probe['row']:raise ValueError('actual data probe confirmation differs')
    for proof in (before,after):
        link=proof.get('confirmation',{});path=Path(link.get('path',''))
        if not path.is_file() or path.is_symlink() or sha(path.read_bytes())!=link.get('sha256') or identity(path.stat())!=link.get('identity'):raise ValueError('complete actual post-disk proof required')
        confirmation=json.loads(path.read_text());captured=confirmation.get('capturedRaw',{});captured_path=Path(captured.get('path',''))
        if confirmation.get('errors') or confirmation.get('owner')!=proof['owner'] or confirmation.get('moduleToken')!=proof['moduleToken'] or not captured_path.is_file() or captured_path.is_symlink() or sha(captured_path.read_bytes())!=captured.get('sha256') or identity(captured_path.stat())!=captured.get('identity'):raise ValueError('post-disk owner/source/captured witness differs')
        original=json.loads(captured_path.read_text())
        for field in ('owner','ownerToken','moduleToken','errors'):
            if original.get(field)!=proof.get(field):raise ValueError('archived proof differs from service evidence')
        if proof is before and (confirmation.get('callbacks')!=proof['callbacks'] or original.get('callbacks')!=proof['callbacks']):raise ValueError('actual initial callbacks changed')
        if proof is after and (confirmation.get('ledgerToken')!=proof['ledgerToken'] or original.get('ledger')!=proof['ledger'] or original.get('journal')!=proof['journal']):raise ValueError('actual final ledger changed')
    return {'accepted':True,'moduleToken':after['moduleToken'],'ownerToken':after['ownerToken'],'ledgerToken':after['ledgerToken'],'queryCount':len(after['ledger']['history'])}


def data_probe(factory,destination):
    """One genuine fixed service-owned read, before input; no semantic use."""
    from owned_commands import OwnedCommands
    from readonly_ipc import ReadonlyIPC
    raw={'phase':'QA-owned-data-probe','errors':[],'usable':False,'nativeAuthority':False,'ownerToken':None,'row':None,'replySHA256':None,'replyBytes':None}
    try:
        factory.lease_verify();raw['ownerToken']=digest(owner_projection(factory,factory.lease_verify.__self__))
        if not factory.binding_owner['usable'] or raw['ownerToken']!=factory.binding_owner['ownerToken'] or type(factory.readonly) is not ReadonlyIPC:raise ValueError('complete actual source/lease/adapter binding required before probe')
        before=factory.readonly.snapshot()
        commands=OwnedCommands(factory.keeper,factory.guard.env,readonly=factory.readonly)
        reply=commands.check_output(['hyprctl','clients','-j'],env=factory.guard.env,timeout=.6)
        raw['replySHA256']=sha(reply);raw['replyBytes']=len(reply)
        fresh=factory.readonly.snapshot();new=[row for row in fresh['history'] if row['id'] not in {r['id'] for r in before['history']}]
        if len(new)!=1:raise ValueError('one actual owned query row required')
        raw['row']=new[0]
        if raw['row']['actor'] is not None or raw['row']['request']!='j/clients' or raw['row']['outcome']!='complete' or not raw['row']['closed'] or raw['row']['evidence']['replySHA256']!=raw['replySHA256'] or raw['row']['evidence']['replyBytes']!=raw['replyBytes']:raise ValueError('actual returned data differs from owned durable row')
        factory.lease_verify()
    except BaseException as failure:raw['errors'].append({'type':type(failure).__name__,'message':str(failure)})
    raw['disk']=persist_raw(destination,raw)
    confirmation={'phase':'QA-owned-data-post-disk','errors':[],'capturedRaw':raw['disk'],'ownerToken':None,'row':None}
    try:
        factory.lease_verify();confirmation['ownerToken']=digest(owner_projection(factory,factory.lease_verify.__self__))
        confirmation['row']=next(row for row in factory.readonly.snapshot()['history'] if raw['row'] is not None and row['id']==raw['row']['id'])
        if confirmation['ownerToken']!=raw['ownerToken'] or confirmation['row']!=raw['row']:raise ValueError('actual owned data proof changed after disk')
        factory.lease_verify()
    except BaseException as failure:confirmation['errors'].append({'type':type(failure).__name__,'message':str(failure)})
    raw['confirmation']=persist_raw(Path(destination).with_name(Path(destination).stem+'-confirmation.json'),confirmation)
    if raw['errors'] or confirmation['errors']:raise ValueError('owned data probe refused; raw evidence retained')
    raw['usable']=True
    return raw


def bind_recovery(factory,coordinator,destination):
    from recovery_runtime import NativeRecovery
    raw={'phase':'recovery-linked','errors':[],'callbacks':{},'ownerToken':None,'usable':False}
    try:
        if type(coordinator) is not NativeRecovery or coordinator.factory is not factory:raise ValueError('actual linked recovery coordinator required')
        factory.lease_verify();packet=source_packet()
        raw['ownerToken']=digest(owner_projection(factory,factory.lease_verify.__self__))
        if not factory.binding_owner['usable'] or raw['ownerToken']!=factory.binding_owner['ownerToken']:raise ValueError('complete recovery owner binding required')
        raw['callbacks']['recover']=callback(coordinator.recover,packet)
        raw['callbacks']['factory.recover']=callback(factory.recover,packet)
        factory.lease_verify()
    except BaseException as failure:raw['errors'].append({'type':type(failure).__name__,'message':str(failure)})
    raw['disk']=persist_raw(destination,raw)
    if raw['errors']:raise ValueError('actual recovery binding refused; raw evidence retained')
    confirmation={'phase':'recovery-post-disk','errors':[],'capturedRaw':raw['disk'],'ownerToken':None,'callbacks':{}}
    try:
        factory.lease_verify();confirmation['ownerToken']=digest(owner_projection(factory,factory.lease_verify.__self__))
        confirmation['callbacks']={'recover':callback(coordinator.recover,packet),'factory.recover':callback(factory.recover,packet)}
        if confirmation['ownerToken']!=raw['ownerToken'] or confirmation['callbacks']!=raw['callbacks']:raise ValueError('actual recovery binding changed after disk')
        factory.lease_verify()
    except BaseException as failure:confirmation['errors'].append({'type':type(failure).__name__,'message':str(failure)})
    raw['confirmation']=persist_raw(Path(destination).with_name(Path(destination).stem+'-confirmation.json'),confirmation)
    if confirmation['errors']:raise ValueError('actual recovery confirmation refused; raw evidence retained')
    raw['usable']=True
    return raw


def validate_recovery_evidence(evidence):
    proof=evidence.get('actualRecoveryBinding',{})
    if proof.get('usable') is not True or proof.get('errors') or proof.get('ownerToken')!=evidence['moduleBindingBefore']['ownerToken']:raise ValueError('actual current recovery coordinator binding required')
    for field in ('disk','confirmation'):
        link=proof.get(field,{});path=Path(link.get('path',''))
        if not path.is_file() or path.is_symlink() or sha(path.read_bytes())!=link.get('sha256') or identity(path.stat())!=link.get('identity'):raise ValueError('actual recovery binding archive differs')
        raw=json.loads(path.read_text())
        if raw.get('errors') or raw.get('ownerToken')!=proof['ownerToken'] or raw.get('callbacks')!=proof['callbacks']:raise ValueError('actual recovery proof changed')
    return {'accepted':True,'ownerToken':proof['ownerToken']}


def archive_fault_binding(folder,journal,owner,guard,destination):
    """An old pending data row remains evidence and grants no current authority."""
    from readonly_ipc import checked_retained
    folder=Path(folder);raw={'phase':'expected-fault-old-binding','errors':[],'usable':False,'oldOwner':owner,'ledger':journal.get('readonlyOwnership'),'capturedBinding':None,'confirmation':None}
    try:
        raw['capturedBinding']=json.loads((folder/'actual-owner-binding.json').read_text())
        raw['confirmation']=json.loads((folder/'actual-owner-binding-confirmation.json').read_text())
        before=raw['capturedBinding'];confirm=raw['confirmation']
        if before.get('errors') or confirm.get('errors') or before.get('owner')!=confirm.get('owner') or before.get('moduleToken')!=confirm.get('moduleToken') or before.get('callbacks')!=confirm.get('callbacks'):raise ValueError('old exact completed source/lease binding absent')
        for field in ('pid','start','nonce','session'):
            if before['owner'].get(field)!=owner.get(field) or raw['ledger']['issuer'].get(field)!=owner.get(field):raise ValueError('old data belongs to another lifetime/lease')
        captured=confirm['capturedRaw'];path=Path(captured['path'])
        if path!=folder/'actual-owner-binding.json' or sha(path.read_bytes())!=captured['sha256'] or identity(path.stat())!=captured['identity']:raise ValueError('old first binding archive replaced')
        checked_retained(raw['ledger'],root=Path(before['owner']['root']),environment={k:guard.env[k] for k in ('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY')},keeper=journal['helperOwnership']['keeper'],guard=guard)
    except BaseException as failure:raw['errors'].append({'type':type(failure).__name__,'message':str(failure)})
    raw['disk']=persist_raw(destination,raw)
    if raw['errors']:raise ValueError('old expected-fault source/data evidence refused; raw persisted')
    return raw
