"""Actual private toolkit case lifetimes and native intervention delegation."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import helper_observer
import helper_setup
from observations import exact,released,retired as validate_retired
from public_toolkit import actual_backend,backend_observation,PublicFixture

B=Path(__file__).resolve().parent

def wait(function,label,seconds=8):
    deadline=time.monotonic()+seconds;last=None
    while time.monotonic()<deadline:
        try:
            value=function()
            if value:return value
        except FileNotFoundError as error:last=repr(error)
        time.sleep(.05)
    raise TimeoutError(label+(': '+last if last else ''))

class CaseRoute:
    def __init__(self,session,env,folder,variant,config,pointer,keyboard,plugin,plugin_hash,host_api,closure,frontend,load_generation):
        self.session=session;self.env=env;self.folder=Path(folder);self.variant=variant;self.config=config;self.pointer=pointer;self.keyboard=keyboard;self.plugin=Path(plugin);self.plugin_hash=plugin_hash;self.host_api=host_api;self.closure=closure;self.frontend=frontend;self.evaluations=load_generation
        self.toolkit=variant['toolkit'];self.extents=[1600,1000];self.identities={};self.process=None;self.fixture=None;self.log=None;self.source_name='nested'
        self.report=dict(case=None,result='pending',gates=[],trace=[],cleanup={},nativeInputSource='owned Wayland virtual protocols',physicalInputAccepted=False)
    def record(self,label,value):self.report['trace'].append(dict(label=label,**value))
    def gate(self,name,value,**details):
        self.report['gates'].append(dict(name=name,passed=bool(value),**details))
        if not value:raise AssertionError(name)
    def guard(self):
        self.session.guard()
        if self.process is not None:
            if self.process.poll() is not None or not helper_observer.still_live(self.process_identity):raise RuntimeError('Exact public fixture lifetime exited')
            proc=Path('/proc')/str(self.process.pid)
            if (proc/'exe').resolve()!=self.executable or helper_observer.cmdline(self.process.pid)!=self.command or helper_observer.digest(self.executable)!=self.executable_hash:raise RuntimeError('Exact fixture executable/argv/source changed')
            values=dict(part.split(b'=',1) for part in (proc/'environ').read_bytes().split(b'\0') if b'=' in part)
            for key in ('HOME','XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY','DISPLAY','XAUTHORITY','QT_QPA_PLATFORM','GDK_BACKEND'):
                value=self.fixture_environment.get(key)
                if values.get(key.encode())!=(value.encode() if value is not None else None):raise RuntimeError('Actual fixture private/backend environment changed')
            for value in self.command:
                source=Path(value)
                if source.is_absolute() and source.suffix=='.py' and (self.closure.get(str(source)) is None or helper_observer.digest(source)!=self.closure[str(source)]):raise RuntimeError('Exact actual fixture Python source changed')
            if (proc/'cgroup').read_text()!=Path('/proc/self/cgroup').read_text():raise RuntimeError('Actual fixture QA scope changed')
    def native(self):
        self.guard();return json.loads(self.session.ctl('repl','print(hl.plugin.toolkit_held_probe.state())'))
    def window(self,role,pending=False):
        self.guard();name=self.source_name if role=='source' else role
        prefix='Qt WindowModal QA ' if self.toolkit=='QtWidgets' else 'Toolkit '+self.tag+' '
        matches=[row for row in self.session.data('clients') if row['pid']==self.process.pid and row['title']==prefix+name]
        if not matches and pending:return None
        if len(matches)!=1:raise RuntimeError('One exact actual mapped fixture window required: '+role)
        row=matches[0]
        if type(row['mapped']) is not bool:raise RuntimeError('Actual mapped state must be a native boolean')
        if bool(row['xwayland'])!=(self.variant['backend'] in ('xcb','x11')):raise RuntimeError('Actual mapped fixture native backend changed')
        if row['mapped'] is not True:
            if pending:return None
            raise RuntimeError('Actual fixture window is not mapped: '+role)
        identity={key:row[key] for key in ('address','stableId','pid')}
        if role in self.identities and not exact(identity,self.identities[role]):raise RuntimeError('Captured toolkit native lifetime changed')
        self.identities[role]=identity;return row
    def await_mapped(self,role):
        def paired():
            state=self.fixture.state()
            if role not in state['windows']:return None
            row=self.window(role,pending=True)
            if row is None:return None
            self.register_observed([row])
            return row
        return self.wait(paired,'Actual public/native mapped lifetime '+role)
    def register_observed(self,windows):
        self.guard()
        pending=[row for row in windows if helper_observer.operation(['forget-closed',row['address'],str(row['stableId']),str(row['pid'])]) not in self.config['allowed']]
        if pending:helper_setup.allow_closes(self.env,self.config,pending)
        self.report.setdefault('mappedLifetimeRegistrations',[]).append([dict((key,row[key]) for key in ('address','stableId','pid')) for row in pending])
    def register_partial(self):
        state=self.fixture.state();roles=[role for role in ('owner','peer','child','nested') if role in state['windows']]
        for role in roles:self.await_mapped(role)
        clients=[row for row in self.session.data('clients') if row['pid']==self.process.pid]
        prefix='Qt WindowModal QA ' if self.toolkit=='QtWidgets' else 'Toolkit '+self.tag+' '
        if any(row['title'] not in [prefix+role for role in roles] for row in clients):raise RuntimeError('Unknown exact fixture lifetime during partial quit')
        for row in clients:
            role=row['title'][len(prefix):]
            if row['mapped'] is not True or not exact(row,self.identities[role]):raise RuntimeError('Exact mapped fixture lifetime changed before partial quit')
        self.register_observed(clients)
    def arrange(self,role,rectangle):
        window=self.await_mapped(role);x,y,width,height=rectangle;address=json.dumps('address:'+window['address'])
        if not window['floating']:self.session.ctl('dispatch','hl.dsp.window.float({action="set",window='+address+'})')
        self.session.ctl('dispatch',f'hl.dsp.window.resize({{x={width},y={height},window={address}}})')
        self.session.ctl('dispatch',f'hl.dsp.window.move({{x={x},y={y},window={address}}})')
        return self.wait(lambda:self.window(role) if self.window(role)['at']==[x,y] and self.window(role)['size']==[width,height] else None,'Actual arranged '+role)
    def wait(self,*args,**kwargs):return wait(*args,**kwargs)
    def prepare(self,case,index):
        self.session.guard();released(json.loads(self.session.ctl('repl','print(hl.plugin.toolkit_held_probe.state())')))
        self.folder.mkdir(mode=0o700);self.report['case']=case['name'];self.tag='Held'+str(index);environment=dict(self.env)
        if self.variant['backend'] in ('xcb','x11'):
            if not self.session.env.get('DISPLAY') or not self.session.env.get('XAUTHORITY'):raise RuntimeError('Authenticated owned X11 selectors required before fixture')
            environment.update(DISPLAY=self.session.env['DISPLAY'],XAUTHORITY=self.session.env['XAUTHORITY'])
        else:environment.pop('DISPLAY',None);environment.pop('XAUTHORITY',None)
        if self.toolkit=='QtWidgets':
            environment.update(QT_QPA_PLATFORM=self.variant['backend'],QT_QPA_PLATFORMTHEME='',QT_STYLE_OVERRIDE='Fusion')
            command=[self.variant['fixture'],str(self.folder)]
        else:
            environment.update(GDK_BACKEND=self.variant['backend'])
            command=['/usr/bin/python3',self.variant['fixture'],'--state',str(self.folder/'state.json'),'--tag',self.tag,'--backend',self.variant['backend']]
        self.log=(self.folder/'fixture.log').open('x');self.fixture_environment=environment;self.command=command
        self.process=subprocess.Popen(command,env=environment,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,text=True,start_new_session=True)
        self.process_identity=helper_observer.process(self.process.pid);self.report['processIdentity']=self.process_identity;self.executable=Path(command[0]).resolve();self.executable_hash=helper_observer.digest(self.executable)
        self.source_name='owner' if case['name']=='genuine-group-release-positive' else 'nested'
        self.fixture=PublicFixture(self.process,self.toolkit,self.folder,self.guard,self.wait,aliases={'source':self.source_name})
        self.wait(lambda:(self.fixture.state() if len(self.session.data('clients'))>=2 else None),'Actual fresh public fixture mapped')
        self.arrange('owner',[100,250,460,300]);self.arrange('peer',[1000,300,460,300])
        if self.source_name=='nested':
            self.fixture.command('open');self.wait(lambda:'child' in self.fixture.state()['windows'],'Actual public child creation');self.arrange('child',[260,310,320,180])
            self.fixture.command('nested');self.wait(lambda:'nested' in self.fixture.state()['windows'],'Actual public nested creation');self.arrange('source',[330,350,240,140])
        windows=[self.window(role) for role in (('owner','child','source','peer') if self.source_name=='nested' else ('source','peer'))]
        self.guard();public=self.fixture.state();mapping=self.host_api.original.mapped_files(self.process.pid);self.guard()
        observation=backend_observation(public,windows,self.variant,self.process.pid,mapping['files'],self.closure)
        observation.update(processIdentity=self.process_identity,argv=self.command,executable=str(self.executable),executableSHA256=self.executable_hash,privateEnvironment={key:self.fixture_environment.get(key) for key in ('HOME','PATH','XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY','DISPLAY','XAUTHORITY','QT_QPA_PLATFORM','GDK_BACKEND')},rawMaps=mapping['maps'],guardedBeforeAfter=True)
        evidence=self.folder/'backend-observation.json';fd=os.open(evidence,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'w') as stream:json.dump(observation,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
        self.report['backendObservation']=dict(path=str(evidence),sha256=helper_observer.digest(evidence),candidateSetNonempty=observation['candidateSetNonempty'],allCandidateBytesExact=observation['allCandidateBytesExact'])
        backend=actual_backend(public,windows,self.variant,self.process.pid,mapping['files'],self.closure)
        self.gate('Actual public and native backend loaded exact frozen modules',True,authority=backend)
        if self.source_name=='nested':
            families=json.loads(self.session.ctl('repl','print(hl.plugin.hyprbars.window_families())'));rows={row['address']:row for row in families}
            owner,child,nested,_=windows
            self.gate('Actual public three-member modal family metadata matches exact native parent lifetimes',rows[child['address']]['modal'] and rows[nested['address']]['modal'] and rows[child['address']]['parent']==owner['address'] and str(rows[child['address']]['parentStableId'])==str(owner['stableId']) and rows[nested['address']]['parent']==child['address'] and str(rows[nested['address']]['parentStableId'])==str(child['stableId']),families=families)
        self.register_observed(windows)
        peer=self.window('peer');self.session.ctl('dispatch','hl.dsp.focus({window='+json.dumps('address:'+peer['address'])+'})')
        self.session.ctl('dispatch','hl.dsp.group.toggle()')
        self.wait(lambda: any(exact(group['head'],peer) and len(group['members'])==1 for group in self.native()['groups']),'Actual native peer target group')
        self.report['processIdentity']=self.process_identity;self.report['initialWindows']=windows
        return self
    def focus_peer(self,peer):
        self.guard();return self.session.ctl('dispatch','hl.dsp.focus({window='+json.dumps('address:'+peer['address'])+'})')
    def resize_point(self,target,native):
        matches=[row for row in native['windows'] if exact(row,target)]
        if len(matches)!=1 or not matches[0]['surfaceBox']:raise RuntimeError('Actual allocated resize client missing')
        x,y,width,height=matches[0]['surfaceBox'];return [x+width-2,y+height-2]
    def interrupt(self,end,target,current_geometry):
        self.guard()
        if end=='reload':
            ticket=self.evaluations.arm('reload',['reload'])
            result=self.session.ctl('reload');self.evaluations.complete(ticket)
            return dict(actualReloadReply=result,evaluationTicket=ticket,featureOutcomeNotInferred=True)
        if end=='unload-reload':
            before_unload=self.native();peer=self.window('peer')
            unload_ticket=self.evaluations.arm('native-unload',['plugin','unload',str(self.plugin)],self.plugin)
            result=self.session.ctl('plugin','unload',str(self.plugin))
            if result.strip()!='ok' or any(row['name']=='hyprbars' for row in self.session.data('plugin','list')):raise RuntimeError('Normal native unload refused')
            retired=json.loads(self.session.ctl('repl','print(hl.plugin.toolkit_held_probe.state())'))
            if retired['coreDragTarget'] is not None:raise RuntimeError('Normal native unload left controller active')
            validate_retired(before_unload,retired,peer)
            actual={key:self.window('source')[key] for key in self.press_geometry}
            if actual!=self.press_geometry:raise RuntimeError('Normal native unload did not restore original press geometry/pins')
            self.record('actual native state between unload/reload',dict(native=retired))
            self.evaluations.complete(unload_ticket)
            if helper_observer.digest(self.plugin)!=self.plugin_hash:raise RuntimeError('Reviewed native artifact source changed')
            load_ticket=self.evaluations.arm('native-load',['plugin','load',str(self.plugin)],self.plugin)
            if self.session.ctl('plugin','load',str(self.plugin)).strip()!='ok':raise RuntimeError('Exact native reload failed')
            self.evaluations.complete(load_ticket)
            reload_ticket=self.evaluations.arm('reload',['reload'])
            reload_reply=self.session.ctl('reload');self.evaluations.complete(reload_ticket)
            return dict(actualUnloadReply=result,actualConfigurationReloadAfterNativeReload=reload_reply,evaluationTickets=[unload_ticket,load_ticket,reload_ticket],featureOutcomeNotInferred=True)
        if end=='close-reopen':
            self.fixture.command('closeNested');self.wait(lambda:not any(exact(row,target) for row in self.session.data('clients')),'Exact old native source lifetime gone')
            return dict(publicCloseACK=True,oldIdentity=target,featureOutcomeNotInferred=True)
        if end=='minimize-preview':return self.frontend.minimize(self,target,current_geometry)
        raise ValueError('Unregistered held interruption')
    def next_generation(self):
        def register():
            try:return helper_setup.register_load_generation(self.env,self.config)
            except helper_setup.HelperBusy:return None
        return self.wait(register,'All prior exact helper lifetimes normally retire before generation')
    def reopen_source(self,previous):
        del self.identities['source'];self.fixture.command('nested');self.wait(lambda:'nested' in self.fixture.state()['windows'],'Actual new public nested lifetime')
        new=self.await_mapped('source')
        if exact(new,previous):raise RuntimeError('Native public reopen did not produce new lifetime')
        self.register_observed([new]);return new
    def restore_frontend(self,target,geometry):return self.frontend.restore(self,target,geometry)
    def close(self):
        if self.process is None:return
        self.session.guard()
        if self.pointer.down or self.keyboard.down:raise RuntimeError('Real held inputs must release before public toolkit shutdown')
        self.register_partial()
        self.fixture.command('quit')
        self.wait(lambda:not any(row['pid']==self.process.pid for row in self.session.data('clients')),'All exact toolkit windows gone normally')
        if helper_observer.still_live(self.process_identity):raise RuntimeError('Normal toolkit exit retained original PID/start')
        self.process.stdin.close();self.process.stdout.close();self.log.close()
        self.report['cleanup'].update(fixtureExitCode=self.process.returncode,normalPublicQuit=True,publicCommandAcknowledgements=self.fixture.acks,exactOriginalProcessGone=True)
