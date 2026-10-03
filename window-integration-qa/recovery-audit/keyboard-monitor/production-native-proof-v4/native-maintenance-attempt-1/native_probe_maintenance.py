#!/usr/bin/env python3
"""Prepared private compositor/official Orca/Foot probe. Requires root GUI slot."""
import argparse,base64,hashlib,json,os,select,shutil,signal,socket,subprocess,tempfile,time,traceback
from pathlib import Path
import sys
import importlib.util
import lifecycle_preservation as preservation
from main_observer import MainObserver
import host_acceptance
import startup_reporting
import producer_control
import private_helpers
from gi.repository import GLib
STAGE=Path(__file__).resolve().parent
HERE=STAGE
HOME=Path.home()
READER=HOME/'window-integration-qa/orca-reader'
LIB=HERE/'payload/native/libomarchy-a11y-prod-v2.so'
EXPECTED='913cbc06c6f16a001a3726b24ee8009af24629051822a3344f97ee0a7b181b43'
REPORT=HERE/'native-maintenance-report.json'
QA_ROOT=Path('/home/hoskinson/window-integration-qa')
HOST_ROOT=QA_ROOT/'private-weston-aq-host-v4'
def exact_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
HOST=exact_module('_pointer_reviewed_private_host',HOST_ROOT/'weston_host.py')
qa=exact_module('_pointer_shared_qa_launch',QA_ROOT/'qa_launch.py')
PRIVATE_SESSION=None
DENY_DEVICE='hl-virtual-keyboard-native-input'
CATALOG=[HOME/'.config/omarchy'/p for p in ('virtual-desktops.json','taskbar-settings.json','taskbar-order.json','taskbar-session-order.json')]

def command(*args,env=None):return subprocess.check_output(list(map(str,args)),env=env,text=True,stderr=subprocess.PIPE,timeout=10).strip()
def ctl(env,*args):
    if PRIVATE_SESSION is None:raise RuntimeError('private IPC requires active owned host context')
    for key in ('HYPRLAND_INSTANCE_SIGNATURE','XDG_RUNTIME_DIR','WAYLAND_DISPLAY','DBUS_SESSION_BUS_ADDRESS'):
        if env.get(key)!=PRIVATE_SESSION.env.get(key):raise RuntimeError('private IPC routing mismatch '+key)
    return PRIVATE_SESSION.ctl(*args).strip()
def data(env,*args):return json.loads(ctl(env,*args,'-j'))
def identity(w):return [w.get('address'),w.get('pid'),w.get('stableId')]
def client_state(w):return {k:w.get(k) for k in preservation.CLIENT_FIELDS}
def rpc(env,dest,path,method,*args):
    values=GLib.Variant.parse(None,command('gdbus','call','--session','--dest',dest,'--object-path',path,'--method',method,*args,env=env),None,None).unpack()
    return values[0] if values else None

def observation(env):return json.loads(rpc(env,'org.gnome.Orca.Service','/org/gnome/Orca/Service/QAObservation','org.gnome.Orca.Module.ExecuteRuntimeGetter','State'))
def wait(fn,label,seconds=12):
    end=time.monotonic()+seconds;last=None
    while time.monotonic()<end:
        try:
            result=fn()
            if result:return result
        except (ValueError,subprocess.SubprocessError,OSError) as e:last=repr(e)
        time.sleep(.08)
    raise AssertionError(label+': '+str(last))
def check(report,name,ok,**details):
    report['checks'].append(dict(name=name,pass_=bool(ok),**details))
    if not ok:raise AssertionError(name)
def pid_stop(process):
    if process.poll() is None:
        try:os.killpg(process.pid,signal.SIGTERM)
        except ProcessLookupError:pass
        try:process.wait(timeout=8)
        except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=4)
def finish_fixture(process):
    # Native keyboard producer EOF emits real paired releases. Give it that
    # chance before any process signal or quiescent plugin maintenance check.
    if process.poll() is None and process.stdin is not None:
        try:
            if not process.stdin.closed:process.stdin.close()
            process.wait(timeout=5)
        except (OSError,subprocess.TimeoutExpired):pass
    pid_stop(process)
def finish_scenario(processes,checkpoint):
    assert 0<=checkpoint<=len(processes),'invalid scenario process checkpoint'
    for process in reversed(processes[checkpoint:]):finish_fixture(process)
def retire_private_plugin(control,report):
    report['cleanupNormalRetirement']=control.unload();report['cleanupNormalUnloadResult']='ok'
    report['cleanupCalibratedArtifactMapping']=control.mapping_observation
    return True

def save_json(path,row):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as stream:stream.write(json.dumps(row,indent=2)+'\n')
def verify_manifest(manifest,root=None):
    root=HERE if root is None else Path(root)
    for name,value in manifest['dependencies'].items():
        path=root/name
        assert not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest()==value,name
        assert path.stat().st_mode&0o7777==manifest['dependencyModes'][name],name+' mode'
    for name,value in manifest['externalDependencies'].items():
        path=Path(name)
        assert hashlib.sha256(path.read_bytes()).hexdigest()==value,name
        assert path.stat().st_mode&0o7777==manifest['externalModes'][name],name+' mode'
    for name,value in manifest.get('externalSymlinks',{}).items():assert Path(name).is_symlink() and str(Path(name).readlink())==value,name
def manifest_unchanged(manifest):
    try:
        verify_manifest(manifest)
        verify_manifest(manifest,STAGE)
        return True
    except (OSError,AssertionError):return False
def process_identity(pid):
    path=Path('/proc')/str(pid);assert path.stat().st_uid==os.getuid()
    fields=(path/'stat').read_text().rsplit(')',1)[1].split()
    return dict(pid=pid,start=fields[19],pgid=int(fields[2]))
def fixture_parent_env(main):return {**main,'HYPR_A11Y_BRIDGE_PRIVATE':'1'}

class ProcessList(list):
    def __init__(self,records):super().__init__();self.records=records
    def append(self,p):
        row=process_identity(p.pid);row['command']=list(map(str,p.args)) if isinstance(p.args,(list,tuple)) else str(p.args)
        self.records.append(row);super().append(p)

def profile_tree(env):
    roots=[Path(env[key]) for key in ('XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME')]
    result={}
    for root in roots:
        for p in [root,*sorted(root.rglob('*'))]:
            row={'mode':p.lstat().st_mode&0o7777}
            if p.is_symlink():row.update(kind='symlink',target=str(p.readlink()))
            elif p.is_dir():row.update(kind='directory')
            elif p.is_file():row.update(kind='file',sha256=hashlib.sha256(p.read_bytes()).hexdigest())
            else:raise RuntimeError('unexpected profile object '+str(p))
            result[str(p)]=row
    return result

def make_context(env,report,session,control,received,foot_window,processes,logs):
    from control import Refused,reader_intent
    def pipe(args,extra=None,label='fixture'):
        target={**env,**(extra or {})};session.guard()
        log=(HERE/(label+'-'+str(len(processes))+'.log')).open('w');logs.append(log)
        p=subprocess.Popen(list(map(str,args)),env=target,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=log,text=True,start_new_session=True);processes.append(p);return p
    def keyboard():
        log=HERE/('native-input-'+str(len(processes))+'.log')
        p=pipe([HERE/'native-fixture/native-input'],label='native-input')
        producer_control.ready(p,report,stderr_path=log,label='maintenance actual keyboard');return p
    def set_private_intent(value):
        session.guard();assert env['DBUS_SESSION_BUS_ADDRESS']=='unix:path='+env['XDG_RUNTIME_DIR']+'/bus'
        rpc(env,'org.a11y.Bus','/org/a11y/bus','org.freedesktop.DBus.Properties.Set','org.a11y.Status','ScreenReaderEnabled','<true>' if value else '<false>')
    def reader(mode):
        payload=HERE/'payload';sys.path.insert(0,str(payload))
        from launch_reader import environment
        reader_env=environment(env,payload)
        # Only the owned fixture telemetry/silent factory path is appended.
        reader_env['PYTHONPATH']+=':'+str(HERE)
        reader_env.update(PROOF_READER_MODE=mode,PROOF_READER_RESULT=str(HERE/(mode+'-reader-result.json')),PROOF_READER_STATE=str(HERE/(mode+'-reader-state.json')),ORCA_QA_UTTERANCES=str(HERE/'owned-utterances.jsonl'))
        arguments=['python3',HERE/'proof_reader_entry.py','--manifest',payload/'package.json','--instance',env['HYPRLAND_INSTANCE_SIGNATURE']]
        if mode=='enabled':arguments+=['--','--speech-system','silent_factory','--debug-file',HERE/'owned-reader.debug']
        return pipe(arguments,reader_env,mode+'-reader')
    def maintenance_action(action):
        # Actual product CLI main(), lock and intent reads; only its acceptance
        # constructor is injected for this owned unaccepted private candidate.
        p=pipe(['python3',HERE/'proof_control_entry.py',action,'--manifest',HERE/'payload/package.json','--instance',env['HYPRLAND_INSTANCE_SIGNATURE']],label='actual-control-'+action)
        output,_=p.communicate(timeout=20)
        assert len(output)<=65536 and p.returncode==0,'actual product maintenance action failed: '+str(p.returncode)
        value=json.loads(output)
        check(report,'actual product CLI '+action+' preserves explicit reader intent',value['readerEnabledBefore']==value['readerEnabledAfter']==reader_intent(env),output=value)
        return value['result']
    def stop_reader(process):
        # Orca's installed SIGINT handler performs normal public shutdown.
        if process.poll() is None:process.send_signal(signal.SIGINT);process.wait(timeout=12)
        check(report,'owned reader exits through normal signal handler',process.poll()==0,exitCode=process.poll())
    def pointer_target():
        layout=HERE/'owned-gtk-layout.json'
        gtk=pipe(['python3',HERE/'native-fixture/gtk_peer.py','A',layout],{'GTK_A11Y':'atspi','GDK_BACKEND':'wayland'},'owned-gtk')
        window=wait(lambda:next((w for w in data(env,'clients') if w['pid']==gtk.pid),None),'actual GTK pointer target')
        ctl(env,'dispatch','hl.dsp.window.resize({x=360,y=240,window='+json.dumps('address:'+window['address'])+'})')
        ctl(env,'dispatch','hl.dsp.window.move({x=48,y=80,window='+json.dumps('address:'+window['address'])+'})')
        row=wait(lambda:r if (r:=json.loads(layout.read_text())).get('windows',[{}])[0].get('button') else None,'actual GTK child allocation')
        window=next(w for w in data(env,'clients') if w['pid']==gtk.pid)
        button=row['windows'][0]['button'];transform=row['windows'][0]['surfaceTransform']
        target=[window['at'][0]+transform[0]+button['x']+button['width']/2,window['at'][1]+transform[1]+button['y']+button['height']/2]
        ctl(env,'dispatch','hl.dsp.focus({window='+json.dumps('address:'+foot_window['address'])+'})')
        pointer=pipe([HERE/'native-fixture/native-pointer'],label='native-pointer');producer_control.ready(pointer,report,stderr_path=HERE/('native-pointer-'+str(len(processes)-1)+'.log'),label='maintenance actual pointer')
        rpc(env,'org.gnome.Orca.Service','/org/gnome/Orca/Service/MouseReviewer','org.gnome.Orca.Module.ExecuteRuntimeSetter','IsEnabled','<true>')
        pointer.stdin.write(f'absolute {target[0]:.17g} {target[1]:.17g} 1024 640\nsync\n');pointer.stdin.flush()
        ready,_,_=select.select([pointer.stdout],[],[],8);assert ready and pointer.stdout.readline().strip()=='ready'
        raw=ctl(env,'repl',"local p=hl.get_cursor_pos(); return string.format('%.17g,%.17g',p.x,p.y)")
        actual=list(map(float,raw.split(',')))
        check(report,'actual private pointer reaches observed GTK child coordinates',all(abs(a-b)<0.02 for a,b in zip(actual,target)),actual=actual,target=target)
        return gtk,pointer,target,row
    def close_gtk(process):
        process.stdin.write('{"operation":"exit"}\n');process.stdin.flush()
        ready,_,_=select.select([process.stdout],[],[],6);assert ready
        reply=json.loads(process.stdout.readline());process.wait(timeout=6)
        check(report,'owned actual GTK acknowledges normal exit',reply.get('pass_') and process.returncode==0)
    def guard_negatives():
        import control as product
        refused=[]
        for label,changed,target in (
            ('unknown explicit instance',env,'missing-exact-instance'),
            ('wrong own bus',{**env,'DBUS_SESSION_BUS_ADDRESS':'unix:path='+env['XDG_RUNTIME_DIR']+'/unavailable'},env['HYPRLAND_INSTANCE_SIGNATURE']),
            ('unaccepted main runtime',{**env,'XDG_RUNTIME_DIR':'/run/user/'+str(os.getuid())},env['HYPRLAND_INSTANCE_SIGNATURE'])):
            try:product.Control(HERE/'payload/package.json',explicit=target,env=changed,approved=False)
            except product.Refused as error:refused.append(dict(name=label,error=str(error)))
            else:raise AssertionError(label+' incorrectly accepted')
        temporary=Path(env['XDG_RUNTIME_DIR'])/'source-guard-package';temporary.mkdir(mode=0o700)
        source=HERE/'payload/package.json';value=json.loads(source.read_text())
        library=temporary/value['library'];library.parent.mkdir();shutil.copyfile(LIB,library);library.chmod(0o755)
        for label,fields in (('actual ABI mismatch',{'hyprlandABI':'wrong'}),('actual hash mismatch',{'sha256':'0'*64})):
            (temporary/'package.json').write_text(json.dumps({**value,**fields}))
            try:product.Control(temporary/'package.json',explicit=env['HYPRLAND_INSTANCE_SIGNATURE'],env=env,approved=False)
            except product.Refused as error:refused.append(dict(name=label,error=str(error)))
            else:raise AssertionError(label+' incorrectly accepted')
        (temporary/'package.json').write_text(json.dumps(value))
        unmapped=product.Control(temporary/'package.json',explicit=env['HYPRLAND_INSTANCE_SIGNATURE'],env=env,approved=False)
        try:unmapped.native_identity()
        except product.Refused as error:refused.append(dict(name='actual distinct unmapped artifact',error=str(error)))
        else:raise AssertionError('unmapped artifact incorrectly accepted')
        check(report,'actual production source/target guards fail before activation',len(refused)==6,refusals=refused)
    def introspection():
        xml=rpc(env,'org.freedesktop.a11y.Manager','/org/freedesktop/a11y/Manager','org.freedesktop.DBus.Introspectable.Introspect')
        if 'org.omarchy.KeyboardMonitorProbe' in xml:return False
        result=subprocess.run(['gdbus','call','--session','--dest','org.freedesktop.a11y.Manager','--object-path','/org/freedesktop/a11y/Manager','--method','org.omarchy.KeyboardMonitorProbe.State'],env=env,capture_output=True,text=True,timeout=5)
        check(report,'actual production D-Bus rejects old private Probe',result.returncode!=0 and 'UnknownInterface' in result.stderr,error=result.stderr)
        return all(name in xml for name in ('org.freedesktop.a11y.KeyboardMonitor','org.freedesktop.a11y.PointerLocator'))
    return dict(here=HERE,env=env,runtime=Path(env['XDG_RUNTIME_DIR']),control=control,Refused=Refused,received=received,ctl=lambda *args:ctl(env,*args),check=lambda name,ok,**fields:check(report,name,ok,**fields),wait=wait,pipe=pipe,keyboard=keyboard,reader=reader,
                finish=finish_fixture,stop_reader=stop_reader,introspection=introspection,profile_tree=lambda:profile_tree(env),set_private_intent=set_private_intent,private_intent=lambda:reader_intent(env),guard_negatives=guard_negatives,pointer_target=pointer_target,close_gtk=close_gtk,maintenance_action=maintenance_action)

def import_preflight(root):
    import ast
    source=Path(root)/'proof_cases.py';ast.parse(source.read_text())
    cases=exact_module('_maintenance_actual_cases_preflight',source)
    assert callable(cases.run)
    for name in ('proof_reader_entry.py','proof_control_entry.py','production_client.py','native_probe_maintenance.py','native_refusal.py','payload/control.py','payload/mapping_artifact.py','payload/reader_bootstrap.py'):
        compile((Path(root)/name).read_text(),str(Path(root)/name),'exec')
    return dict(pass_=True,GUI=False,nativeCalled=False,actualProductControl=str(Path(root)/'payload/control.py'),cases=str(source),privateInjection='approved=False factory only',actualHelpers={name:str(Path(__file__).resolve().parent/(name+'.py')) for name in ('main_observer','lifecycle_preservation','host_acceptance','startup_reporting','producer_control','private_helpers')})

def config_bytes():
    return ('hl.monitor({output="WAYLAND-1",mode="1280x800@60",position="0x0",scale=1.25})\n'
        'hl.config({animations={enabled=false},input={follow_mouse=0,repeat_delay=1000,virtualkeyboard={release_pressed_on_close=false}},ecosystem={enforce_permissions=true},misc={name_vk_after_proc=true},debug={disable_logs=false,enable_stdout_logs=true}})\n'
        'hl.on("window.open",function(w) if not w.floating then hl.dispatch(hl.dsp.window.float({action="set",window="address:"..w.address})) end end)\n'
        'hl.permission({binary='+json.dumps(str(LIB))+',type="plugin",mode="allow"})\n'
        'hl.permission({binary='+json.dumps(str(READER/'physical-commands/evdev-keyboard'))+',type="keyboard",mode="allow"})\n'
        'hl.permission({binary='+json.dumps(str(HERE/'native-fixture/native-input'))+',type="keyboard",mode="allow"})\n'
        'hl.bind("F12",function() local f=io.open(os.getenv("XDG_RUNTIME_DIR").."/shortcut-count","a");f:write("shortcut\\n");f:close() end)\n').encode()

def execute():
    global PRIVATE_SESSION
    qa.require_qa_scope()
    main=dict(os.environ);observer=MainObserver(main)
    report=dict(kind='private actual production maintenance/reader-intent proof',checks=[],restoration={},nativeInputProved=False,nativePointerProved=False,widerPolicyInputProved=False,physicalHardwareProved=False,mainInputWrites=False,mainRestorationWrites=False)
    before=observer.capture()
    assert 'false' in before['reader'],'original reader must remain disabled'
    save_json(HERE/'main-before.json',before);report['before']=before
    manifest=json.loads((HERE/'proof-frozen-stage-report.json').read_text());verify_manifest(manifest)
    assert manifest['hostAdapter']==str(HOST_ROOT),'actual host differs from reviewed dependency packet'
    assert hashlib.sha256(LIB.read_bytes()).hexdigest()==EXPECTED
    report['fixtureParentEnvDelta']={'HYPR_A11Y_BRIDGE_PRIVATE':'1'}
    fixture_parent=fixture_parent_env(main)
    records=[];processes=ProcessList(records);logs=[];session=None;received=None;phase_checkpoint=0;control=None
    try:
        session=HOST.PrivateHyprSession(output=HERE/'owned-host',main_env=fixture_parent,width=1280,height=800,nested_lua=config_bytes(),dri_prime='pci-0000_00_02_0',mesa_vendor=True)
        with session:
            PRIVATE_SESSION=session;runtime=Path(session.env['XDG_RUNTIME_DIR']);config=Path(session.evidence['compositorConfig']);effective=config.read_bytes()
            env={**session.env,'HYPR_WINDOWCTL_MOTION':'0','GSETTINGS_BACKEND':'memory','PYTHONDONTWRITEBYTECODE':'1','GDK_DEBUG':'no-portals','GIO_USE_VFS':'local','PYTHONPATH':str(HERE),'ORCA_QA_READER_ROOT':str(READER),'POINTER_QA_COMPOSITOR_PID':str(session.evidence['compositorPID']),'POINTER_QA_COMPOSITOR_START':session.evidence['compositorStart']}
            report['private']=session.evidence
            report['privateClientEnvironmentDelta']={'GDK_DEBUG':'no-portals','GIO_USE_VFS':'local'}
            for name in ('config','data','cache'):
                source=HERE/'owned-profile-template'/name
                if source.exists():shutil.copytree(source,Path(env['XDG_'+name.upper()+'_HOME']),dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
            def launch(args,launch_env=env,label='fixture'):
                session.guard()
                assert launch_env['XDG_RUNTIME_DIR']==str(runtime) and launch_env['WAYLAND_DISPLAY']==env['WAYLAND_DISPLAY'] and launch_env['DBUS_SESSION_BUS_ADDRESS']==env['DBUS_SESSION_BUS_ADDRESS']
                log=(HERE/(label+'.log')).open('w');logs.append(log)
                p=subprocess.Popen(list(map(str,args)),env=launch_env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);processes.append(p);return p
            try:
                monitor=wait(lambda:data(env,'monitors')[0],'private output')
                check(report,'private physical1280x800 fractional logical1024x640 established',monitor['width']==1280 and monitor['height']==800 and monitor['scale']==1.25 and monitor['width']/monitor['scale']==1024 and monitor['height']/monitor['scale']==640,monitor=monitor)
                check(report,'private config errors absent',not ctl(env,'configerrors'))
                check(report,'private Xwayland disabled',data(env,'getoption','xwayland:enabled')['bool'] is False)
                check(report,'private complete IPC readiness reply has exact peer and unchanged socket',host_acceptance.ipc_complete(session.evidence),readiness=session.evidence.get('ipcReadiness'))
                maps=HOST.original.mapped_files(session.evidence['compositorPID'])
                aq=str(QA_ROOT/'aquamarine-nested-lifecycle-v1/prefix/lib/libaquamarine.so.0.15.0')
                check(report,'actual private mandatory-Wayland Aquamarine mapped',maps['files'].get(aq)==host_acceptance.AQ_SHA,mappedSHA256=maps['files'].get(aq))
                stdout_log=Path(session.evidence['hyprland']['log'])
                assert stdout_log==HERE/'owned-host/hyprland.log','actual registered child stdout path required'
                weston_log=HERE/'owned-host/weston-renderer.log'
                startup_transport=startup_reporting.live_transport([stdout_log,weston_log],session.guard,report)
                check(report,'actual startup parent configure transport is healthy',startup_transport.pop('pass_'),**startup_transport,logHashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (stdout_log,weston_log)})
                receiver=runtime/'terminal_receiver.py';received=runtime/'terminal.bin';marker=runtime/'shortcut-count'
                receiver.write_text('import os,sys,termios,tty\nold=termios.tcgetattr(0)\ntty.setraw(0)\nprint("Private native Foot byte receiver",flush=True)\ntry:\n with open(sys.argv[1],"ab",buffering=0) as f:\n  while True:\n   b=os.read(0,256)\n   if not b:break\n   f.write(b)\nfinally:termios.tcsetattr(0,termios.TCSANOW,old)\n');receiver.chmod(0o600)
                foot=launch(['/usr/bin/foot','--app-id=org.omarchy.keyboardnativeqa','--title=Private full pointer keyboard QA','/usr/bin/python3',receiver,received],env,'native-foot')
                foot_window=wait(lambda:next((w for w in data(env,'clients') if w['pid']==foot.pid),None),'private Foot receiver')
                ctl(env,'dispatch','hl.dsp.focus({window='+json.dumps('address:'+foot_window['address'])+'})')
                wait(lambda:received.exists(),'private byte receiver ready')
                accessibility_launcher=launch(['/usr/lib/at-spi-bus-launcher','--launch-immediately'],env,'private-a11y-launcher')
                ax_address=wait(lambda:rpc(env,'org.a11y.Bus','/org/a11y/bus','org.a11y.Bus.GetAddress'),'own accessibility bus')
                assert ax_address.startswith('unix:path='+str(runtime)+'/');ax_socket=Path(ax_address[10:].split(',')[0]);assert ax_socket.resolve().is_relative_to(runtime) and not ax_socket.is_symlink() and ax_socket.stat().st_uid==os.getuid()
                env['AT_SPI_BUS_ADDRESS']=ax_address
                registry=launch(['/usr/lib/at-spi2-registryd'],env,'private-a11y-registry')
                wait(lambda:command('gdbus','call','--address',ax_address,'--dest','org.freedesktop.DBus','--object-path','/org/freedesktop/DBus','--method','org.freedesktop.DBus.GetNameOwner','org.a11y.atspi.Registry',env=env),'actual private AX Registry')
                report['privateAccessibility']=dict(address=ax_address,socket=str(ax_socket),registryPID=registry.pid,launcherPID=accessibility_launcher.pid)
                sys.path.insert(0,str(HERE/'payload'))
                import control as product_control
                def trace_transport(arguments,target_env):
                    started=time.monotonic();row=dict(start=started,arguments=arguments)
                    try:
                        value=product_control.run(arguments,target_env);row['result']=value;return value
                    except Exception as error:row['error']=repr(error);raise
                    finally:
                        row['end']=time.monotonic()
                        with (HERE/'actual-control-transport.jsonl').open('a') as stream:stream.write(json.dumps(row)+'\n')
                control=product_control.Control(HERE/'payload/package.json',explicit=env['HYPRLAND_INSTANCE_SIGNATURE'],env=env,approved=False,transport=trace_transport)
                proof_cases=exact_module('_maintenance_actual_owned_cases',HERE/'proof_cases.py')
                ctx=make_context(env,report,session,control,received,foot_window,processes,logs)
                phase_checkpoint=len(processes)
                infrastructure_baseline=session.host.descendants()
                ctx['profile_before']=ctx['profile_tree']()
                proof_cases.run(ctx)
                report['actualCalibratedArtifactMapping']=control.mapping_observation
                finish_scenario(processes,phase_checkpoint)
                helpers=private_helpers.unexpected(session.host.descendants(),infrastructure_baseline)
                history=private_helpers.portal_activations((HERE/'owned-host/privateBus.log').read_text())
                check(report,'normal scenario shutdown has no unexpected private helpers',not helpers and not history,unexpected=helpers,activations=history)
                report['nativeMaintenanceProved']=True
                report['result']='pass'
            except Exception as error:
                startup_reporting.failure(report,error,'startup-or-campaign')
            finally:
                # All scenario device EOFs/natural releases precede retirement.
                finish_scenario(processes,phase_checkpoint)
                try:
                    if 'omarchy-a11y-monitor' in ctl(env,'plugin','list'):
                        if control is None:raise RuntimeError('normal wrapper unavailable; refusing raw unload')
                        retire_private_plugin(control,report)
                except Exception as error:
                    report['cleanupUnloadError']=repr(error);startup_reporting.failure(report,error,'normal-unload-cleanup')
                for p in reversed(processes):finish_fixture(p)
                report['fixtureExitCodes']=[dict(pid=p.pid,exitCode=p.poll()) for p in processes]
                owned={row['pid'] for _,row in session.host.processes}
                leftover=[row for row in session.host.descendants() if row['pid'] not in owned]
                report['unexpectedPrivateClientSurvivors']=leftover
                try:
                    portal_log=HERE/'owned-host/privateBus.log';portal_history=private_helpers.portal_activations(portal_log.read_text())
                    check(report,'terminal normal private client cleanup has no unexpected helper processes',not leftover and not portal_history,unexpected=leftover,portalActivations=portal_history,privateBusLogSHA256=hashlib.sha256(portal_log.read_bytes()).hexdigest())
                except Exception as error:startup_reporting.failure(report,error,'unexpected-private-client-cleanup')
                if leftover:
                    report['result']='failed'
                    for row in reversed(leftover):session.host.stop(row)
                report['ownedFixtureProcesses']=records
                startup_reporting.archive_terminal(received,HERE,report)
                for log in logs:log.close()
                PRIVATE_SESSION=None
    except Exception as error:
        startup_reporting.failure(report,error,'host-lifecycle-or-cleanup')
    finally:PRIVATE_SESSION=None
    if session is not None:
        report['hostEvidence']=session.evidence
        try:
            archived=[Path(row['archive']) for row in session.evidence.get('archivedRuntime',[]) if Path(row['archive']).name=='hyprland.log']
            assert len(archived)==1,'exact archived compositor log required'
            logs=archived+[HERE/'owned-host/weston-renderer.log']
            final_transport=host_acceptance.transport([path.read_text() for path in logs])
            check(report,'actual complete campaign archived parent transport stayed healthy',final_transport.pop('pass_'),**final_transport,logHashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in logs})
        except Exception as error:
            report['terminalTransportError']=repr(error);startup_reporting.failure(report,error,'archived-terminal-transport')
    try:
        after=observer.capture();save_json(HERE/'main-after.json',after);report['after']=after;report['restoration']=observer.compare(before,after)
        report['focusObservation']=dict(beforeIdentity=observer.focus_identity(before['focus']),afterIdentity=observer.focus_identity(after['focus']),beforeTitleSHA256=before.get('focusTitleSHA256'),afterTitleSHA256=after.get('focusTitleSHA256'))
    except Exception as error:
        report['restoration']={'mainReadOnlyObservationSucceeded':False};report['preservationError']=repr(error);startup_reporting.failure(report,error,'main-read-only-preservation')
    report['restoration'].update(frozenDependencies=manifest_unchanged(manifest),fixtureProcessesGone=all(p.poll() is not None for p in processes),ownedRuntimeGone=bool(session and session.evidence.get('runtimeGone')),ownedInfrastructureGone=bool(session and not session.evidence.get('remainingDescendants') and not session.evidence.get('cleanupErrors') and not session.evidence.get('unexpectedInnerDescendants') and session.evidence.get('runtimeGone')))
    if not all(report['restoration'].values()):report['result']='failed'
    save_json(REPORT,report);print(json.dumps(startup_reporting.summary(report,REPORT)));return 0 if report.get('result')=='pass' else 1

def freeze_attempt(destination):
    global HERE,LIB,REPORT
    manifest_path=STAGE/'proof-frozen-stage-report.json'
    manifest=json.loads(manifest_path.read_text())
    assert 'runtime-import-preflight.json' not in manifest['dependencies'],'runtime import evidence cannot be a source input'
    verify_manifest(manifest,STAGE)
    for relative,digest_value in manifest['dependencies'].items():
        assert not Path(relative).is_absolute() and '..' not in Path(relative).parts
    for name,digest_value in manifest['externalDependencies'].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest_value,name
    for name,link_value in manifest.get('externalSymlinks',{}).items():
        source=Path(name)
        assert source.is_symlink() and str(source.readlink())==link_value,name
    destination=Path(destination).expanduser().resolve()
    assert destination.parent==STAGE and destination.name.startswith('native-maintenance-attempt-'),'fresh attempt path must be scoped to this QA stage'
    destination.mkdir(mode=0o700)  # Never overwrite earlier attempts.
    for relative in manifest['dependencies']:
        source=STAGE/relative;target=destination/relative
        target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        descriptor=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(descriptor,'wb') as stream:stream.write(source.read_bytes())
        target.chmod(manifest['dependencyModes'][relative])
        assert target.stat().st_mode&0o7777==manifest['dependencyModes'][relative]
        assert hashlib.sha256(target.read_bytes()).hexdigest()==manifest['dependencies'][relative]
    target=destination/manifest_path.name;target.write_bytes(manifest_path.read_bytes());target.chmod(0o600)
    references=destination/'external-reference';references.mkdir(mode=0o700)
    for name,digest_value in manifest['externalDependencies'].items():
        source=Path(name);target=references/(hashlib.sha256(name.encode()).hexdigest()[:16]+'.'+source.name+'.'+digest_value[:12])
        descriptor=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(descriptor,'wb') as stream:stream.write(source.read_bytes())
        assert hashlib.sha256(target.read_bytes()).hexdigest()==digest_value,name
    command_path=destination/'frozen-command.json'
    command_path.write_text(json.dumps({'command':['python3',str(QA_ROOT/'qa_run.py'),'--','python3',str(STAGE/'native_probe_maintenance.py'),'--execute','--output',str(destination)],'manifestSHA256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),'externalActualSources':manifest['externalDependencies']},indent=2)+'\n');command_path.chmod(0o600)
    HERE=destination;LIB=HERE/'payload/native/libomarchy-a11y-prod-v2.so';REPORT=HERE/'native-maintenance-report.json'

def write_runtime_preflight():
    preflight=import_preflight(HERE)
    path=HERE/'runtime-import-preflight.json'
    descriptor=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(descriptor,'w') as stream:stream.write(json.dumps(preflight,indent=2)+'\n')
    return preflight

if __name__=='__main__':
    args=argparse.ArgumentParser();args.add_argument('--execute',action='store_true');args.add_argument('--output');args.add_argument('--preflight',action='store_true');options=args.parse_args()
    if options.preflight:
        assert not options.execute,'offline preflight cannot execute native'
        print(json.dumps(import_preflight(STAGE),indent=2))
    elif not options.execute:print(json.dumps({'execution':'not started; requires explicit root GUI grant','plan':'CONTRACT.md','candidate':str(LIB),'mainPluginLoad':False,'requiresFreshAttempt':True}))
    else:
        assert options.output,'--output is required; never overwrite prior evidence'
        qa.require_qa_scope()
        os.umask(0o077)
        freeze_attempt(options.output)
        write_runtime_preflight()
        raise SystemExit(execute())
