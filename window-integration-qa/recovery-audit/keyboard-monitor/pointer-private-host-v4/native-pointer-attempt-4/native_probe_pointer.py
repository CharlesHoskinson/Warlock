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
LIB=HERE/'native/libkeyboard-monitor-private-v8-host.so'
EXPECTED='241432e788b77775a8d73438d3dcc03fe3c11ca30d96fa7c38f31c2690a066fa'
REPORT=HERE/'native-pointer-report.json'
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
def rpc(env,dest,path,method,*args):return GLib.Variant.parse(None,command('gdbus','call','--session','--dest',dest,'--object-path',path,'--method',method,*args,env=env),None,None).unpack()[0]
def manager(env,method):return rpc(env,'org.freedesktop.a11y.Manager','/org/freedesktop/a11y/Manager','org.omarchy.KeyboardMonitorProbe.'+method)
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
def retire_private_plugin(env,library,report):
    ready=manager(env,'PrepareUnload');report['cleanupUnloadQuiescent']=ready
    if ready is not True:raise RuntimeError('private plugin not quiescent; normal unload refused')
    result=ctl(env,'plugin','unload',library);report['cleanupNormalUnloadResult']=result
    if result!='ok':raise RuntimeError('normal private plugin unload failed: '+result)
    return ready

def load_cases(root):
    import importlib.util
    source=Path(root)/'native-fixture/pointer_cases.py'
    assert source.is_file() and not source.is_symlink() and source.stat().st_uid==os.getuid()
    spec=importlib.util.spec_from_file_location('private_native_pointer_cases',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def import_preflight(root):
    module=load_cases(root);helper=Path(module._geometry.__file__).resolve()
    assert helper==Path(root).resolve()/'native-fixture/popup_geometry.py'
    assert Path(module._ax_wire.__file__).resolve()==Path(root).resolve()/'ax_wire_trace.py'
    extra={}
    for name in ('policy_cases.py','lifecycle_cases.py'):
        source=Path(root)/'native-fixture'/name;loaded=load_additional(name,root)
        assert Path(loaded.__file__).resolve()==source.resolve() and callable(loaded.run)
        extra[name]=dict(path=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    return dict(pass_=True,cases=str(Path(module.__file__).resolve()),helper=str(helper),fullKeyboardPhases=extra,
        casesSHA256=hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(),
        helperSHA256=hashlib.sha256(helper.read_bytes()).hexdigest(),GUI=False,nativeCalled=False)

def save_json(path,row):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as stream:stream.write(json.dumps(row,indent=2)+'\n')
def verify_manifest(manifest):
    for name,value in manifest['dependencies'].items():assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==value,name
    for name,value in manifest['externalDependencies'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==value,name
    for name,value in manifest.get('externalSymlinks',{}).items():assert Path(name).is_symlink() and str(Path(name).readlink())==value,name
def manifest_unchanged(manifest):
    try:
        verify_manifest(manifest)
        return all(hashlib.sha256((STAGE/name).read_bytes()).hexdigest()==value for name,value in manifest['dependencies'].items())
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

def load_additional(name,root=None):
    assert name in ('policy_cases.py','lifecycle_cases.py')
    source=Path(root if root is not None else HERE)/'native-fixture'/name
    assert source.is_file() and not source.is_symlink() and source.stat().st_uid==os.getuid()
    spec=importlib.util.spec_from_file_location('private_'+source.stem,source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def config_bytes():
    return ('hl.monitor({output="WAYLAND-1",mode="1280x800@60",position="0x0",scale=1.25})\n'
        'hl.config({animations={enabled=false},input={follow_mouse=0,repeat_delay=1000,virtualkeyboard={release_pressed_on_close=false}},ecosystem={enforce_permissions=true},misc={name_vk_after_proc=true},debug={disable_logs=false,enable_stdout_logs=true}})\n'
        'hl.on("window.open",function(w) if not w.floating then hl.dispatch(hl.dsp.window.float({action="set",window="address:"..w.address})) end end)\n'
        'hl.permission({binary='+json.dumps(str(LIB))+',type="plugin",mode="allow"})\n'
        'hl.permission({binary='+json.dumps(str(READER/'physical-commands/evdev-keyboard'))+',type="keyboard",mode="allow"})\n'
        'hl.permission({binary='+json.dumps(DENY_DEVICE)+',type="keyboard",mode="deny"})\n'
        'hl.permission({binary='+json.dumps(str(HERE/'native-fixture/native-input'))+',type="keyboard",mode="allow"})\n'
        'hl.bind("F12",function() local f=io.open(os.getenv("XDG_RUNTIME_DIR").."/shortcut-count","a");f:write("shortcut\\n");f:close() end)\n').encode()

def policy_baseline(ctx):
    env,report=ctx['env'],ctx['report'];state=json.loads(manager(env,'State'))
    check(report,'fresh policy manager has no inferred subscriptions',state['clients']==0 and state['quiescent'],state=state)
    producer=subprocess.Popen([str(READER/'physical-commands/evdev-keyboard')],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True);ctx['processes'].append(producer)
    producer_control.ready(producer,report,label='no-reader evdev baseline')
    def keys(codes):
        for code in codes:producer.stdin.write(f'key {code} 1\nsleep 90\nkey {code} 0\nsleep 90\n')
        producer.stdin.write('sync\n');producer.stdin.flush();ready,_,_=select.select([producer.stdout],[],[],10)
        assert ready and producer.stdout.readline().strip()=='ready';time.sleep(.2)
    before=ctx['received'].read_bytes();keys([30,48,46])
    check(report,'no-reader actual private ordinary bytes preserved',ctx['received'].read_bytes()==before+b'abc')
    ctx['marker'].unlink(missing_ok=True);keys([88])
    check(report,'no-reader actual private compositor shortcut works',ctx['marker'].read_text()=='shortcut\n')
    finish_fixture(producer)
    ctx['packet_path']=HERE/'policy-observer-packets.jsonl';(ctx['runtime']/'observer-ready').unlink(missing_ok=True)
    ctx['launch'](['python3',HERE/'host_event_observer.py'],{**env,'KEYBOARD_QA_PACKETS':str(ctx['packet_path'])},'policy-independent-observer')
    wait(lambda:(ctx['runtime']/'observer-ready').exists(),'independent actual watch-only observer ready')
    check(report,'independent policy observer requests watch only',json.loads(manager(env,'State'))['clients']==1)

def execute():
    global PRIVATE_SESSION
    qa.require_qa_scope()
    main=dict(os.environ);observer=MainObserver(main)
    report=dict(kind='private headless GL host/full PointerLocator/GTK/Orca/keyboard campaign',checks=[],restoration={},nativeInputProved=False,nativePointerProved=False,widerPolicyInputProved=False,physicalHardwareProved=False,mainInputWrites=False,mainRestorationWrites=False)
    before=observer.capture()
    assert 'false' in before['reader'],'original reader must remain disabled'
    save_json(HERE/'main-before.json',before);report['before']=before
    manifest=json.loads((HERE/'pointer-frozen-stage-report.json').read_text());verify_manifest(manifest)
    assert manifest['hostAdapter']==str(HOST_ROOT),'actual host differs from reviewed dependency packet'
    assert hashlib.sha256(LIB.read_bytes()).hexdigest()==EXPECTED
    report['fixtureParentEnvDelta']={'HYPR_A11Y_BRIDGE_PRIVATE':'1'}
    fixture_parent=fixture_parent_env(main)
    records=[];processes=ProcessList(records);logs=[];session=None;received=None;phase_checkpoint=0
    try:
        session=HOST.PrivateHyprSession(output=HERE/'owned-host',main_env=fixture_parent,width=1280,height=800,nested_lua=config_bytes(),dri_prime='pci-0000_00_02_0',mesa_vendor=True)
        with session:
            PRIVATE_SESSION=session;runtime=Path(session.env['XDG_RUNTIME_DIR']);config=Path(session.evidence['compositorConfig']);effective=config.read_bytes()
            env={**session.env,'HYPR_WINDOWCTL_MOTION':'0','GSETTINGS_BACKEND':'memory','PYTHONDONTWRITEBYTECODE':'1','GDK_DEBUG':'no-portals','PYTHONPATH':str(HERE),'ORCA_QA_READER_ROOT':str(READER),'POINTER_QA_COMPOSITOR_PID':str(session.evidence['compositorPID']),'POINTER_QA_COMPOSITOR_START':session.evidence['compositorStart']}
            report['private']=session.evidence
            report['privateClientEnvironmentDelta']={'GDK_DEBUG':'no-portals'}
            for name in ('config','data','cache'):
                source=READER/name
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
                ctx=dict(here=HERE,reader_root=READER,env=env,report=report,check=check,manager=manager,ctl=ctl,data=data,received=received,marker=marker,launch=launch,processes=processes,pid_stop=pid_stop,wait=wait,lib=LIB,runtime=runtime,config=config,ax_address=ax_address,foot=foot,foot_window=foot_window,deny_name=DENY_DEVICE)
                def producer_ready(process,stderr_path,label):
                    session.guard();return producer_control.ready(process,report,stderr_path,label)
                ctx['producer_ready']=producer_ready
                infrastructure_baseline=session.host.descendants()
                report['privateInfrastructureBaseline']=infrastructure_baseline
                report['phases']=[]
                for name,module in [('pointer',load_cases(HERE)),('policy',load_additional('policy_cases.py')),('lifecycle',load_additional('lifecycle_cases.py'))]:
                    phase_checkpoint=len(processes);start=len(report['checks']);phase={'name':name,'started':time.monotonic(),'startCheck':start};report['phases'].append(phase)
                    config.write_bytes(effective);ctl(env,'reload');check(report,name+' baseline private config valid',not ctl(env,'configerrors'))
                    ctl(env,'dispatch','hl.dsp.focus({window='+json.dumps('address:'+foot_window['address'])+'})')
                    if name=='policy':
                        ctl(env,'plugin','load',LIB)
                        policy_baseline(ctx)
                    try:module.run(ctx)
                    finally:finish_scenario(processes,phase_checkpoint)
                    helper_rows=private_helpers.unexpected(session.host.descendants(),infrastructure_baseline)
                    portal_log=HERE/'owned-host/privateBus.log';portal_history=private_helpers.portal_activations(portal_log.read_text())
                    check(report,name+' normal client shutdown has no activated or leaked private helpers',not helper_rows and not portal_history,unexpected=helper_rows,portalActivations=portal_history,privateBusLogSHA256=hashlib.sha256(portal_log.read_bytes()).hexdigest())
                    if 'keyboard-monitor-private' in ctl(env,'plugin','list'):retire_private_plugin(env,LIB,report)
                    phase.update(completed=time.monotonic(),checks=len(report['checks'])-start,pass_=True)
                    if name=='pointer':report['nativePointerProved']=True
                    if name=='lifecycle':report['nativeInputProved']=True
                report['result']='pass'
            except Exception as error:
                startup_reporting.failure(report,error,'startup-or-campaign')
            finally:
                # All scenario device EOFs/natural releases precede retirement.
                finish_scenario(processes,phase_checkpoint)
                try:
                    if 'keyboard-monitor-private' in ctl(env,'plugin','list'):retire_private_plugin(env,LIB,report)
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
    manifest_path=STAGE/'pointer-frozen-stage-report.json'
    manifest=json.loads(manifest_path.read_text())
    for relative,digest_value in manifest['dependencies'].items():
        assert not Path(relative).is_absolute() and '..' not in Path(relative).parts
        assert hashlib.sha256((STAGE/relative).read_bytes()).hexdigest()==digest_value,relative
    for name,digest_value in manifest['externalDependencies'].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest_value,name
    for name,link_value in manifest.get('externalSymlinks',{}).items():
        source=Path(name)
        assert source.is_symlink() and str(source.readlink())==link_value,name
    destination=Path(destination).expanduser().resolve()
    assert destination.parent==STAGE and destination.name.startswith('native-pointer-attempt-'),'fresh attempt path must be scoped to this QA stage'
    destination.mkdir(mode=0o700)  # Never overwrite earlier attempts.
    for relative in manifest['dependencies']:
        source=STAGE/relative;target=destination/relative
        target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        descriptor=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(descriptor,'wb') as stream:stream.write(source.read_bytes())
        if source.stat().st_mode&0o111:target.chmod(0o700)
        assert hashlib.sha256(target.read_bytes()).hexdigest()==manifest['dependencies'][relative]
    target=destination/manifest_path.name;target.write_bytes(manifest_path.read_bytes());target.chmod(0o600)
    references=destination/'external-reference';references.mkdir(mode=0o700)
    for name,digest_value in manifest['externalDependencies'].items():
        source=Path(name);target=references/(hashlib.sha256(name.encode()).hexdigest()[:16]+'.'+source.name+'.'+digest_value[:12])
        descriptor=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(descriptor,'wb') as stream:stream.write(source.read_bytes())
        assert hashlib.sha256(target.read_bytes()).hexdigest()==digest_value,name
    command_path=destination/'frozen-command.json'
    command_path.write_text(json.dumps({'command':['python3',str(QA_ROOT/'qa_run.py'),'--','python3',str(STAGE/'native_probe_pointer.py'),'--execute','--output',str(destination)],'manifestSHA256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),'externalActualSources':manifest['externalDependencies']},indent=2)+'\n');command_path.chmod(0o600)
    HERE=destination;LIB=HERE/'native/libkeyboard-monitor-private-v8-host.so';REPORT=HERE/'native-pointer-report.json'

if __name__=='__main__':
    args=argparse.ArgumentParser();args.add_argument('--execute',action='store_true');args.add_argument('--output');args.add_argument('--preflight',action='store_true');options=args.parse_args()
    if options.preflight:
        assert not options.execute,'offline preflight cannot execute native'
        print(json.dumps(import_preflight(STAGE),indent=2))
    elif not options.execute:print(json.dumps({'execution':'not started; requires explicit root GUI grant','plan':'POINTER_NATIVE_REVIEW.md','candidate':str(LIB),'mainPluginLoad':False,'requiresFreshAttempt':True}))
    else:
        assert options.output,'--output is required; never overwrite prior evidence'
        qa.require_qa_scope()
        os.umask(0o077)
        freeze_attempt(options.output)
        preflight=import_preflight(HERE)
        descriptor=os.open(HERE/'import-preflight.json',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(descriptor,'w') as stream:stream.write(json.dumps(preflight,indent=2)+'\n')
        raise SystemExit(execute())
