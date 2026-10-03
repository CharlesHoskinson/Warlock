"""Genuine candidate CLI minimize and unmodified widget preview native restore."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import helper_observer
import helper_setup
from observations import exact
from service_presentations import validate as validate_presentation
from preview_evidence import PreviewEvidence

B=Path(__file__).resolve().parent
SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-review-v12')
PRODUCER=SERVICE.parent/'producer-readback-v4/hypr-motion-renderer-staged'

def layer(state,pid,namespace):
    rows=[row for row in state['layers'] if row['pid']==pid and row['namespace']==namespace and row['mapped'] is True and row['visible'] is True and row['box'] is not None]
    if len(rows)!=1:raise ValueError('One exact mapped native taskbar layer required')
    return rows[0]

def item_point(item,layer_row):
    x,y,width,height=layer_row['box'];point=[x+item['x']+item['width']/2,y+item['y']+item['height']/2]
    if item['width']<=0 or item['height']<=0 or not(x<=point[0]<x+width and y<=point[1]<y+height):raise ValueError('Actual taskbar item outside native layer allocation')
    return point

class FrontendLifecycle:
    def __init__(self,session,env,output,config,shell,shell_command,launch,ipc,closure):
        self.session=session;self.env=env;self.output=Path(output);self.config=config;self.shell=shell;self.shell_command=shell_command;self.launch=launch;self.ipc=ipc;self.closure=closure
        self.service=None;self.setup=None;self.members=None;self.pairs=None;self.before=None;self.snapshot_used=False;self.snapshot_attempted=False;self.retirements=[]
        self.service_root=Path(env['XDG_RUNTIME_DIR'])/'hypr-window-motion/held-service'
        candidate=B/'frontend-candidate';sys.path.insert(0,str(candidate))
        spec=importlib.util.spec_from_file_location('_held_candidate_frontend_setup',candidate/'prepare_config.py');self.builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.builder)
    def install(self):
        source=B/'frontend-candidate/native_frontend.py';legacy=B/'payload/home/.local/bin/hypr-windowctl'
        if self.closure.get(str(source))!=helper_observer.digest(source) or self.closure.get(str(B/'frontend-candidate/prepare_config.py'))!=helper_observer.digest(B/'frontend-candidate/prepare_config.py'):raise RuntimeError('Exact reviewed frontend source closure required')
        self.entry=self.builder.install_entry(self.env,self.closure[str(source)],helper_observer.digest(legacy))
        return dict(entry=str(self.entry),entrySHA256=helper_observer.digest(self.entry),candidateOnly=True)
    def ensure_service(self,route):
        members=[route.window(role) for role in ('owner','child','source')];self.members=members;self.before={row['address']:copy.deepcopy(row) for row in members}
        if self.service is None:
            parent=self.service_root.parent;parent.mkdir(mode=0o700,exist_ok=True)
            command=['/usr/bin/python3',str(B/'service_observer.py'),'--root',str(self.service_root),'--session',self.env['HYPRLAND_INSTANCE_SIGNATURE'],'--pid',str(self.session.evidence['compositorPID']),'--start',str(self.session.evidence['compositorStart']),'--display',self.env['WAYLAND_DISPLAY'],'--producer',str(PRODUCER),'--producer-sha256',helper_observer.digest(PRODUCER),'--core',str(B/'payload/home/.local/bin/hypr-windowctl-core'),'--core-sha256',helper_observer.digest(B/'payload/home/.local/bin/hypr-windowctl-core'),'--evidence',str(self.output/'service-evidence.json')]
            def register(identity):helper_setup.register_service_root(self.env,self.config,identity,command,members,SERVICE)
            self.service=self.launch('held-service',command,self.env,register=register)
            route.wait(lambda:(self.service_root/'api.sock').exists() and self.service.poll() is None,'Exact gated native service API readiness')
            roots=[self.builder.capture_request_root('shell',helper_observer.process(self.shell.pid),self.shell_command),self.builder.capture_request_root('harness',helper_observer.process(os.getpid()),helper_observer.cmdline(os.getpid()))]
            compositor=dict(pid=self.session.evidence['compositorPID'],start=str(self.session.evidence['compositorStart']))
            self.setup=self.builder.create_config(self.env,self.entry,roots,compositor,helper_observer.process(self.service.pid),self.service_root,self.env['WINDOW_MOTION_NATIVE_CONFIG'])
        else:helper_setup.append_service_members(self.env,self.config,members)
    def retired(self,route,operation):
        def packet():
            body=json.loads((self.service_root/'journal.json').read_text())['body']
            if body['scenes'] or body['pending'] or body['liveActors'] or body['retiringActors']:return None
            if body['resourceErrors'] or body['housekeepingErrors']:raise RuntimeError('Actual native service resource retirement failed')
            path=self.output/('service-retirement-'+str(body['actorSerial'])+'.json')
            return json.loads(path.read_text()) if path.exists() else None
        value=route.wait(packet,'Actual '+operation+' actor/renderer normal retirement')
        if self.retirements and value['retirement']['actor']<=self.retirements[-1]['retirement']['actor']:raise RuntimeError('Fresh monotonic actor required')
        evidence=validate_presentation(value,operation,self.members)
        self.retirements.append(value)
        return value,evidence
    def minimize(self,route,target,current_geometry):
        self.ensure_service(route)
        route.record('real held inputs before product CLI minimize',dict(native=route.native(),pointerKnownDown=sorted(route.pointer.down),keyboardKnownDown=sorted(route.keyboard.down)))
        command=[str(self.entry),'minimize',target['address'],str(target['stableId']),str(target['pid'])]
        result=subprocess.run(command,env=self.env,capture_output=True,text=True,timeout=8)
        route.record('actual product CLI request',dict(command=command,exitCode=result.returncode,stdout=result.stdout,stderr=result.stderr))
        if result.returncode!=0:raise RuntimeError('Product frontend submission refused/unknown; no retry')
        answer=json.loads(result.stdout)
        if answer.get('ok') is not True or answer.get('accepted') is not True or answer.get('completed') is not False:raise RuntimeError('Genuine product durable acceptance receipt required')
        route.wait(lambda:all(route.window(role)['workspace']['name']=='special:win-minimized' for role in ('owner','child','source')),'Actual complete family minimize from genuine CLI')
        packet,evidence=self.retired(route,'minimize');self.pairs=evidence['cachePairs']
        route.gate('Real held minimize capture seed native presentation and cache retirement',True,receipt=answer,evidence=evidence,packet=packet)
        if not self.snapshot_used:
            self.snapshot_attempted=True
            snapshot=json.loads(subprocess.check_output([str(Path(self.env['HOME'])/'.local/bin/hypr-taskbar'),'snapshot'],env=self.env,text=True,timeout=5))
            windows=[row for group in snapshot['groups'] for row in group['windows'] if any(exact(row,member) for member in self.members)]
            route.gate('Exactly one genuine harness taskbar snapshot verifies real complete family previews',len(windows)==3 and all(row['previewReady'] for row in windows),windows=windows)
            self.snapshot_used=True
        return dict(answer=answer,actualProductCLI=True,nativeCompletionNotInferredFromACK=True,retirementActor=packet['retirement']['actor'])
    def restore(self,route,target,current_geometry):
        if route.pointer.down or route.keyboard.down:raise RuntimeError('Original genuine held input must release before taskbar action')
        shell_identity=helper_observer.process(self.shell.pid)
        with PreviewEvidence(route,shell_identity,target) as evidence:
            return self.restore_observed(route,target,current_geometry,shell_identity,evidence)
    def restore_observed(self,route,target,current_geometry,shell_identity,evidence):
        state=json.loads(self.ipc('hoskinson.windows','state'))
        icon_native=route.native();bar=layer(icon_native,self.shell.pid,'omarchy-bar');items=[row for row in state['taskbarItems'] if target['address'] in row['windows']]
        if len(items)!=1:raise RuntimeError('Exact genuine taskbar icon identity required')
        point=item_point(items[0],bar)
        evidence.emit('icon-proposed',dict(widgetState=state,item=items[0],layer=bar,native=icon_native,point=point,extents=route.extents,expectedMotion='absolute '+' '.join(format(v,'.12g') for v in [*point,*route.extents]),inputTraceIndex=len(route.pointer.trace)))
        route.pointer.absolute(point,route.extents)
        evidence.emit('icon-motion-synced',dict(inputTrace=route.pointer.trace[-2:]))
        def arrived(namespace):
            native=route.native();owner=native['pointerLayerOwner']
            widget=json.loads(self.ipc('hoskinson.windows','state'))
            value=native if all(abs(a-b)<=.5 for a,b in zip(native['cursor'],point)) and owner is not None and owner['pid']==self.shell.pid and owner['namespace']==namespace and owner['mapped'] else None
            evidence.emit('arrival-sample',dict(namespace=namespace,point=point,native=native,widgetState=widget,originalArrivalPredicate=bool(value)))
            return value
        hovered=route.wait(lambda:arrived('omarchy-bar'),'Actual pointer enters exact real icon layer')
        popup=route.wait(lambda:(value if (value:=json.loads(self.ipc('hoskinson.windows','state')))['popupOpen'] and not value['menuMode'] and any(row['address']==target['address'] for row in value['previewItems']) else None),'Real pointer hover opens genuine preview')
        preview_native=route.native();preview_layer=layer(preview_native,self.shell.pid,'hoskinson-taskbar-popup');previews=[row for row in popup['previewItems'] if row['address']==target['address']]
        if len(previews)!=1:raise RuntimeError('One actual source preview card required')
        point=item_point(previews[0],preview_layer)
        evidence.emit('preview-proposed',dict(widgetState=popup,item=previews[0],layer=preview_layer,native=preview_native,point=point,extents=route.extents,expectedMotion='absolute '+' '.join(format(v,'.12g') for v in [*point,*route.extents]),inputTraceIndex=len(route.pointer.trace)))
        route.pointer.absolute(point,route.extents)
        evidence.emit('preview-motion-synced',dict(inputTrace=route.pointer.trace[-2:]))
        before_click=route.wait(lambda:arrived('hoskinson-taskbar-popup'),'Actual pointer enters exact preview card layer')
        if not helper_observer.still_live(shell_identity):raise RuntimeError('Actual taskbar root lifetime changed before preview click')
        route.record('genuine widget preview native click authority',dict(widgetState=popup,iconHover=hovered,previewLayer=preview_layer,preview=previews[0],point=point,nativeBefore=before_click,shellIdentity=shell_identity))
        route.pointer.button(272,True);route.pointer.button(272,False)
        route.wait(lambda:all(route.window(role)['workspace']['name']==self.before[route.window(role)['address']]['workspace']['name'] for role in ('owner','child','source')),'Genuine preview click restores exact family')
        packet,evidence=self.retired(route,'restore')
        if evidence['cachePairs']!=self.pairs:raise RuntimeError('Genuine frontend restore changed original immutable cache pairs')
        rows=[json.loads(line) for line in Path(self.setup['log']).read_text().splitlines()]
        accepted=[row for row in rows if row.get('result')=='accepted' and row.get('request',{}).get('operation')=='restore' and row.get('request',{}).get('address')==target['address'] and row.get('request',{}).get('stableId')==str(target['stableId']) and row.get('request',{}).get('pid')==target['pid'] and row.get('authority',{}).get('root')=='shell']
        if len(accepted)!=1 or not accepted[0]['transport']['completeServerEOF'] or accepted[0]['answer'].get('completed') is not False:raise RuntimeError('Exact widget parent genuine frontend durable receipt required')
        deepest=route.window('source');focus=route.native()['nativeFocus']
        route.gate('Genuine preview frontend restored complete family with deepest modal focus',exact(focus,deepest) and all(route.window(role)['at']==self.before[route.window(role)['address']]['at'] and route.window(role)['size']==self.before[route.window(role)['address']]['size'] and route.window(role)['pinned']==self.before[route.window(role)['address']]['pinned'] for role in ('owner','child','source')),frontendReceipt=accepted[0],actualPresentation=evidence,retirement=packet)
