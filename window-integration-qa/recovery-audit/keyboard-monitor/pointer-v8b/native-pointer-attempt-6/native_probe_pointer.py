#!/usr/bin/env python3
"""Prepared private compositor/official Orca/Foot probe. Requires root GUI slot."""
import argparse,base64,hashlib,json,os,select,shutil,signal,socket,subprocess,tempfile,time,traceback
from pathlib import Path
import sys
import lifecycle_preservation as preservation
from gi.repository import GLib
STAGE=Path(__file__).resolve().parent
HERE=STAGE
HOME=Path.home()
READER=HOME/'window-integration-qa/orca-reader'
LIB=HERE/'native/libkeyboard-monitor-private-v8.so'
EXPECTED='af79dfc55411edd8dbbf5d56e3047fb4f1bf1479412b42f488045d4925d30992'
REPORT=HERE/'native-pointer-report.json'
DENY_DEVICE='hl-virtual-keyboard-native-input'
CATALOG=[HOME/'.config/omarchy'/p for p in ('virtual-desktops.json','taskbar-settings.json','taskbar-order.json','taskbar-session-order.json')]

def command(*args,env=None):return subprocess.check_output(list(map(str,args)),env=env,text=True,stderr=subprocess.PIPE,timeout=10).strip()
def ctl(env,*args):return command('hyprctl',*args,env=env)
def data(env,*args):return json.loads(ctl(env,*args,'-j'))
def identity(w):return [w.get('address'),w.get('pid'),w.get('stableId')]
def client_state(w):return {k:w.get(k) for k in preservation.CLIENT_FIELDS}
def a11y():
    path=Path('/run/user')/str(os.getuid())/'at-spi/bus_0';s=path.stat();connection=socket.socket(socket.AF_UNIX);connection.settimeout(.3)
    try:connection.connect(str(path));connects=True
    except OSError:connects=False
    finally:connection.close()
    return dict(dev=s.st_dev,inode=s.st_ino,connects=connects)
def reader_status(env):return command('gdbus','call','--session','--dest','org.a11y.Bus','--object-path','/org/a11y/bus','--method','org.freedesktop.DBus.Properties.Get','org.a11y.Status','ScreenReaderEnabled',env=env)
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
            process.wait(timeout=1)
        except (OSError,subprocess.TimeoutExpired):pass
    pid_stop(process)
def finish_scenario(processes,checkpoint):
    assert 0<=checkpoint<=len(processes),'invalid scenario process checkpoint'
    for process in reversed(processes[checkpoint:]):finish_fixture(process)
def retire_private_plugin(env,library,report):
    ready=manager(env,'PrepareUnload');report['cleanupUnloadQuiescent']=ready
    if ready:
        report['cleanupNormalUnloadResult']=ctl(env,'plugin','unload',library)
    return ready

def private_processes(runtime):
    rows=[];token=('XDG_RUNTIME_DIR='+str(runtime)).encode()
    for path in Path('/proc').glob('[0-9]*'):
        try:
            if path.stat().st_uid!=os.getuid() or token not in (path/'environ').read_bytes().split(b'\0'):continue
            stat=(path/'stat').read_text();start=stat[stat.rfind(')')+2:].split()[19]
            rows.append(dict(pid=int(path.name),start=start))
        except (OSError,IndexError):pass
    return rows
def cleanup_private_descendants(runtime):
    before=private_processes(runtime)
    for action in (signal.SIGTERM,signal.SIGKILL):
        for row in private_processes(runtime):
            if row not in before:continue
            try:os.kill(row['pid'],action)
            except ProcessLookupError:pass
        end=time.monotonic()+1
        while private_processes(runtime) and time.monotonic()<end:time.sleep(.05)
    return dict(before=before,remaining=private_processes(runtime))

def execute(host_path=False):
    main=dict(os.environ);report={'kind':'private PointerLocator/real GTK/Omarchy Orca compat navigation','checks':[],'restoration':{},'nativeInputProved':False,'nativePointerProved':False,'widerPolicyInputProved':False,'physicalHardwareProved':False}
    original=data(main,'clients');focus=data(main,'activewindow');cursor=data(main,'cursorpos');monitors=data(main,'monitors');accessible=a11y();enabled=reader_status(main);original_plugins=ctl(main,'plugin','list');original_keyboards=data(main,'devices')['keyboards']
    original_files=preservation.files_state(HOME)
    assert not original_files['visible'] and not any(w['pid']==original_files['pid'] for w in original),'original Files must be hidden'
    original_clients=preservation.project_clients(original)
    files_backup=HERE/'original-files-before.json'
    files_backup.write_text(json.dumps(original_files,indent=2)+'\n');files_backup.chmod(0o600)
    catalogs={str(p):p.read_bytes() if p.exists() else None for p in CATALOG}
    def digest(blob):return hashlib.sha256(blob).hexdigest() if blob is not None else None
    backup=HERE/'catalog-before.json'
    backup.write_text(json.dumps({p:{'base64':base64.b64encode(b).decode() if b is not None else None,'sha256':digest(b)} for p,b in catalogs.items()},indent=2)+'\n');backup.chmod(0o600)
    processes=[];logs=[];nested=None;env=None;loaded=False;keyboard=None;host_keyboard=None;observer=None
    report['before']=dict(files=original_files,clientStates=original_clients,clients=[identity(w) for w in original],focus=identity(focus),cursor=cursor,a11y=accessible,readerStatus=enabled,catalogHashes={p:digest(b) for p,b in catalogs.items()},catalogBackup=str(backup))
    assert 'false' in enabled,'main reader must be disabled at entry'
    manifest=json.loads((HERE/'pointer-frozen-stage-report.json').read_text())
    for name,digest_value in manifest['dependencies'].items():assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest_value,'frozen dependency changed: '+name
    for name,digest_value in manifest['externalDependencies'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest_value,'actual reader dependency changed: '+name
    assert hashlib.sha256(LIB.read_bytes()).hexdigest()==EXPECTED,'reviewed library changed'
    assert not any('sudo-askpass' in layer.get('namespace','') or 'hyprlock' in layer.get('namespace','') for mon in data(main,'layers').values() for rows in mon.get('levels',{}).values() for layer in rows if layer.get('alpha',1)>0),'foreign input grab; leave it untouched'
    host=main['WAYLAND_DISPLAY'];host=host if host.startswith('/') else str(Path(main['XDG_RUNTIME_DIR'])/host)
    with tempfile.TemporaryDirectory(prefix='kbn-') as directory:
        runtime=Path(directory);os.chmod(runtime,0o700)
        base={**main,'XDG_RUNTIME_DIR':directory,'XDG_CONFIG_HOME':directory+'/config','XDG_DATA_HOME':directory+'/data','XDG_CACHE_HOME':directory+'/cache','AQ_BACKENDS':'wayland','WAYLAND_DISPLAY':host,'HYPR_A11Y_BRIDGE_PRIVATE':'1','HYPR_WINDOWCTL_MOTION':'0','GSETTINGS_BACKEND':'memory','PYTHONDONTWRITEBYTECODE':'1'}
        for name in ('DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','HYPRLAND_INSTANCE_SIGNATURE','DISPLAY','SESSION_MANAGER','XDG_SESSION_TYPE','ATSPI_USE_LEGACY_DEVICE','ATSPI_USE_A11Y_MANAGER_DEVICE'):base.pop(name,None)
        base['DBUS_SESSION_BUS_ADDRESS']='unix:path='+directory+'/bus'
        for name in ('config','data','cache'):
            destination=runtime/name
            if (READER/name).exists():shutil.copytree(READER/name,destination,ignore=shutil.ignore_patterns('__pycache__'))
            else:destination.mkdir()
        def launch(args,launch_env=base,label='fixture'):
            log=(HERE/(label+'.log')).open('w');logs.append(log)
            p=subprocess.Popen(list(map(str,args)),env=launch_env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);processes.append(p);return p
        config=runtime/'hyprland.lua'
        marker=runtime/'shortcut-count'
        config.write_text('hl.monitor({output="WAYLAND-1",mode="1280x800@60",position="0x0",scale=1.25})\n'
            'hl.config({animations={enabled=false},input={follow_mouse=0,repeat_delay=1000,virtualkeyboard={release_pressed_on_close=false}},ecosystem={enforce_permissions=true},misc={name_vk_after_proc=true},debug={disable_logs=false}})\n'
            'hl.on("window.open",function(w) if not w.floating then hl.dispatch(hl.dsp.window.float({action="set",window="address:"..w.address})) end end)\n'
            'hl.permission({binary='+json.dumps(str(LIB))+',type="plugin",mode="allow"})\n'
            'hl.permission({binary='+json.dumps(str(READER/'physical-commands/evdev-keyboard'))+',type="keyboard",mode="allow"})\n'
            'hl.permission({binary='+json.dumps(DENY_DEVICE)+',type="keyboard",mode="deny"})\n'
            'hl.permission({binary='+json.dumps(str(HERE/'native-fixture/native-input'))+',type="keyboard",mode="allow"})\n'
            'hl.bind("F12",function() local f=io.open('+json.dumps(str(marker))+',"a");f:write("shortcut\\n");f:close() end)\n')
        try:
            launch(['dbus-daemon','--session','--nofork','--nopidfile','--address='+base['DBUS_SESSION_BUS_ADDRESS']],label='private-bus')
            wait(lambda:(runtime/'bus').exists(),'private session bus socket')
            nested=launch(['Hyprland','--config',config],label='native-compositor')
            info=wait(lambda:next((r for r in data(base,'instances') if r['pid']==nested.pid),None),'exact dedicated compositor')
            env={**base,'HYPRLAND_INSTANCE_SIGNATURE':info['instance'],'WAYLAND_DISPLAY':info['wl_socket']}
            report['private']=dict(pid=nested.pid,signature=info['instance'],runtime=directory,config=str(config))
            wait(lambda:data(env,'monitors'),'private output');check(report,'private config errors absent',not ctl(env,'configerrors'))
            host_window=wait(lambda:next((w for w in data(main,'clients') if w['pid']==nested.pid),None),'visible nested host window')
            if not host_window.get('floating'):ctl(main,'dispatch','hl.dsp.window.float({action="set",window='+json.dumps('address:'+host_window['address'])+'})')
            receiver=runtime/'terminal_receiver.py';received=runtime/'terminal.bin'
            receiver.write_text('import os,sys,termios,tty\nold=termios.tcgetattr(0)\ntty.setraw(0)\nprint("Private native Foot byte receiver",flush=True)\ntry:\n with open(sys.argv[1],"ab",buffering=0) as f:\n  while True:\n   b=os.read(0,256)\n   if not b:break\n   f.write(b)\nfinally:termios.tcsetattr(0,termios.TCSANOW,old)\n')
            foot=launch(['foot','--app-id=org.omarchy.keyboardnativeqa','--title=Keyboard native private QA','python3',receiver,received],env,'native-foot')
            foot_window=wait(lambda:next((w for w in data(env,'clients') if w['pid']==foot.pid),None),'private Foot receiver')
            ctl(env,'dispatch','hl.dsp.focus({window='+json.dumps('address:'+foot_window['address'])+'})');time.sleep(.3)
            def fixture_input(device,lines):
                device.stdin.write(lines+'sync\n');device.stdin.flush()
                ready,_,_=select.select([device.stdout],[],[],10)
                assert ready and device.stdout.readline().strip()=='ready','keyboard fixture sync failed'
                time.sleep(.25)
            if host_path:
                ctl(main,'dispatch','hl.dsp.focus({window='+json.dumps('address:'+host_window['address'])+'})');time.sleep(.3)
                assert identity(data(main,'activewindow'))==identity(host_window),'host baseline focus identity'
                wait(lambda:received.exists(),'byte receiver starts')
                baseline=received.read_bytes()
                command('wtype','x',env=main);time.sleep(.3)
                wtype_bytes=received.read_bytes()[len(baseline):]
                report['nestedBackendBaseline']={'pluginLoaded':False,'wtypeExpectedHex':'78','wtypeActualHex':wtype_bytes.hex(),'keymapTranslationCorrect':wtype_bytes==b'x','classification':'nested backend keymap translation; retained separately from bridge gates'}
                host_keyboard=subprocess.Popen([str(READER/'physical-commands/evdev-keyboard')],env=main,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True);processes.append(host_keyboard)
                baseline=received.read_bytes();fixture_input(host_keyboard,'key 30 1\nsleep 90\nkey 30 0\nsleep 90\n')
                check(report,'pre-plugin stable host evdev typing preserved',received.read_bytes()==baseline+b'a',before=baseline.hex(),after=received.read_bytes().hex(),host=identity(host_window))
            accessibility_launcher=launch(['/usr/lib/at-spi-bus-launcher','--launch-immediately'],env,'private-a11y-launcher')
            ax_address=wait(lambda:rpc(env,'org.a11y.Bus','/org/a11y/bus','org.a11y.Bus.GetAddress'),'own accessibility bus address')
            assert ax_address.startswith('unix:path='+str(runtime)+'/'),ax_address
            ax_socket=Path(ax_address[10:].split(',')[0]).resolve()
            assert str(ax_socket).startswith(str(runtime.resolve())+'/') and ax_socket.stat().st_uid==os.getuid()
            env['AT_SPI_BUS_ADDRESS']=ax_address
            registry=launch(['/usr/lib/at-spi2-registryd'],env,'private-a11y-registry')
            wait(lambda:command('gdbus','call','--address',ax_address,'--dest','org.freedesktop.DBus',
                 '--object-path','/org/freedesktop/DBus','--method','org.freedesktop.DBus.GetNameOwner','org.a11y.atspi.Registry',env=env),
                 'own actual accessibility Registry')
            report['privateAccessibility']=dict(address=ax_address,socket=str(ax_socket),registryPID=registry.pid,launcherPID=accessibility_launcher.pid)
            import importlib.util
            spec=importlib.util.spec_from_file_location('private_native_pointer_cases',HERE/'native-fixture/pointer_cases.py')
            cases=importlib.util.module_from_spec(spec);spec.loader.exec_module(cases)
            scenario_checkpoint=len(processes)
            try:
                loaded=True  # cleanup handles partial case execution safely
                cases.run(dict(here=HERE,reader_root=READER,env=env,report=report,check=check,manager=manager,
                    ctl=ctl,data=data,received=received,marker=marker,launch=launch,processes=processes,
                    pid_stop=pid_stop,wait=wait,lib=LIB,runtime=runtime,config=config,ax_address=ax_address,foot=foot,foot_window=foot_window))
                loaded=False
            finally:
                if loaded:
                    finish_scenario(processes,scenario_checkpoint)
            report['nativePointerProved']=True;report['result']='pass'
        except Exception as error:report.update(result='failed',error=repr(error),traceback=traceback.format_exc())
        finally:
            if host_keyboard and host_keyboard.poll() is None:
                try:host_keyboard.stdin.close();host_keyboard.wait(timeout=5)
                except Exception:pass
            if keyboard and keyboard.poll() is None:
                try:keyboard.stdin.close();keyboard.wait(timeout=5)
                except Exception:pass
            if loaded and nested and nested.poll() is None and env:
                try:
                    retire_private_plugin(env,LIB,report)
                except Exception as error:report['cleanupUnloadError']=repr(error)
            for process in reversed(processes):finish_fixture(process)
            report['privateDescendantCleanup']=cleanup_private_descendants(runtime)
            for log in logs:log.close()
            if received.exists():report['terminalBytes']=received.read_bytes().hex();(HERE/'native-terminal.bin').write_bytes(received.read_bytes())
    after=data(main,'clients');keys=[identity(w) for w in after]
    if identity(focus) in keys:ctl(main,'dispatch','hl.dsp.focus({window='+json.dumps('address:'+focus['address'])+'})')
    ctl(main,'dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})');time.sleep(.15)
    # The shell's catalog poll outlives the native client's destruction. Allow
    # its normal pruning to settle and record exact per-file comparisons.
    settle=time.monotonic()+4
    while time.monotonic()<settle:
        if all((Path(p).read_bytes() if Path(p).exists() else None)==b for p,b in catalogs.items()):break
        time.sleep(.15)
    report['catalogComparison']={p:{'expectedSHA256':digest(b),'actualSHA256':digest(Path(p).read_bytes() if Path(p).exists() else None),'exactBytes':(Path(p).read_bytes() if Path(p).exists() else None)==b} for p,b in catalogs.items()}
    after_keyboards=data(main,'devices')['keyboards']
    keyboard_fields=('address','name','layout','variant','options','capsLock','numLock','main')
    report['mainKeyboardComparison']={'before':original_keyboards,'after':after_keyboards}
    try:
        after_files=preservation.files_state(HOME)
        report['originalFilesComparison']={'before':original_files,'after':after_files}
        files_preserved=after_files==original_files and not after_files['visible'] and not any(w['pid']==original_files['pid'] for w in after)
    except Exception as error:
        files_preserved=False;report['originalFilesComparison']={'before':original_files,'error':repr(error)}
    dependencies_unchanged=all(hashlib.sha256((HERE/name).read_bytes()).hexdigest()==value and hashlib.sha256((STAGE/name).read_bytes()).hexdigest()==value for name,value in manifest['dependencies'].items()) and all(hashlib.sha256(Path(name).read_bytes()).hexdigest()==value for name,value in manifest['externalDependencies'].items())
    report['restoration']=dict(originalHiddenFilesExactProcessAndState=files_preserved,frozenDependencies=dependencies_unchanged,keyboards=[{k:r.get(k) for k in keyboard_fields} for r in after_keyboards]==[{k:r.get(k) for k in keyboard_fields} for r in original_keyboards],originalClients=sorted(map(tuple,keys))==sorted(tuple(identity(w)) for w in original),originalClientStates=preservation.project_clients(after)==original_clients,mainPlugins=ctl(main,'plugin','list')==original_plugins,focus=identity(data(main,'activewindow'))==identity(focus),cursor=data(main,'cursorpos')==cursor,a11y=a11y()==accessible,readerDisabled=reader_status(main)==enabled,catalogBytes=all((Path(p).read_bytes() if Path(p).exists() else None)==b for p,b in catalogs.items()),outputs=preservation.project_outputs(data(main,'monitors'))==preservation.project_outputs(monitors),fixturesExited=all(p.poll() is not None for p in processes) and not report.get('privateDescendantCleanup',{}).get('remaining',[]),configErrors=not ctl(main,'configerrors'))
    if not all(report['restoration'].values()):report['result']='failed'
    REPORT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return 0 if report.get('result')=='pass' else 1

def freeze_attempt(destination):
    global HERE,LIB,REPORT
    manifest_path=STAGE/'pointer-frozen-stage-report.json'
    manifest=json.loads(manifest_path.read_text())
    for relative,digest_value in manifest['dependencies'].items():
        assert not Path(relative).is_absolute() and '..' not in Path(relative).parts
        assert hashlib.sha256((STAGE/relative).read_bytes()).hexdigest()==digest_value,relative
    for name,digest_value in manifest['externalDependencies'].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest_value,name
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
        source=Path(name);target=references/(source.name+'.'+digest_value[:12])
        descriptor=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(descriptor,'wb') as stream:stream.write(source.read_bytes())
        assert hashlib.sha256(target.read_bytes()).hexdigest()==digest_value,name
    command_path=destination/'frozen-command.json'
    command_path.write_text(json.dumps({'command':['python3',str(STAGE/'native_probe_pointer.py'),'--execute','--output',str(destination)],'manifestSHA256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),'externalActualSources':manifest['externalDependencies']},indent=2)+'\n');command_path.chmod(0o600)
    HERE=destination;LIB=HERE/'native/libkeyboard-monitor-private-v8.so';REPORT=HERE/'native-pointer-report.json'

if __name__=='__main__':
    args=argparse.ArgumentParser();args.add_argument('--execute',action='store_true');args.add_argument('--output');options=args.parse_args()
    if not options.execute:print(json.dumps({'execution':'not started; requires explicit root GUI grant','plan':'POINTER_NATIVE_REVIEW.md','candidate':str(LIB),'mainPluginLoad':False,'requiresFreshAttempt':True}))
    else:
        assert options.output,'--output is required; never overwrite prior evidence'
        freeze_attempt(options.output)
        raise SystemExit(execute(False))
