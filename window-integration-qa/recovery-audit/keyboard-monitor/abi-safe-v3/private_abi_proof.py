#!/usr/bin/env python3
"""Private runtime before D-Bus; ABI proof uses fabricated packets, never native keys."""
import argparse,hashlib,json,os,shutil,signal,socket,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,private_runtime,verify_runtime

from owned_cleanup import capture,stop_owned
HERE=Path(__file__).resolve().parent
def verify_inputs():
    packet=json.loads((HERE/'frozen-inputs.json').read_text())
    for row in packet['files']:
        if hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()!=row['sha256']:raise RuntimeError('Frozen ABI input changed:'+row['path'])
    return hashlib.sha256((HERE/'frozen-inputs.json').read_bytes()).hexdigest()
def process_start(pid):return Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]
def wait(fn,label):
    end=time.monotonic()+6
    while time.monotonic()<end:
        result=fn()
        if result:return result
        time.sleep(.03)
    raise AssertionError(label)
def a11y():
    path=Path(os.environ['XDG_RUNTIME_DIR'])/'at-spi/bus_0'
    if not path.exists():return {'exists':False}
    st=path.stat();stream=socket.socket(socket.AF_UNIX);stream.settimeout(1)
    try:stream.connect(str(path));connects=True
    except OSError:connects=False
    finally:stream.close()
    return {'exists':True,'dev':st.st_dev,'inode':st.st_ino,'connects':connects}
def main_status():
    return subprocess.check_output(['gdbus','call','--session','--dest','org.a11y.Bus','--object-path','/org/a11y/bus','--method','org.freedesktop.DBus.Properties.Get','org.a11y.Status','ScreenReaderEnabled'],text=True,timeout=4).strip()

def inner():
    require_qa_scope();verify_inputs()
    import gi
    from gi.repository import Gio,GLib
    root=verify_runtime(Path(os.environ['KEYBOARD_ABI_RUNTIME']));processes=[];starts={};clients=[];owned=[]
    report={'kind':'private session bus ABI with actual official Orca factory and public AT-SPI clients','nativeInputProved':False,'checks':[]}
    def check(name,value,**evidence):
        report['checks'].append(dict(name=name,pass_=bool(value),**evidence));assert value,name
    log=(root/'process-errors.log').open('a')
    def register(process,role):
        owned.append(capture(process,role));temporary=root/'owned-processes.new';temporary.write_text(json.dumps(owned));os.replace(temporary,root/'owned-processes.json')
    try:
        service=subprocess.Popen(['python3',str(HERE/'abi_service.py')],stdout=log,stderr=log,start_new_session=True);processes.append(service);starts[service.pid]=process_start(service.pid);register(service,'service')
        wait(lambda:(root/'service-ready').exists(),'private ABI service owns manager')
        bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
        def call(interface,method,values=(),signature='()'):
            return bus.call_sync('org.freedesktop.a11y.Manager','/org/freedesktop/a11y/Manager',interface,method,GLib.Variant(signature,values),None,Gio.DBusCallFlags.NONE,3000,None).unpack()
        def state():return json.loads(call('org.omarchy.KeyboardMonitorABIProbe','State')[0])
        check('default no subscriptions and reader state false',state()['clients']=={} and not state()['readerEnabled'])
        try:call('org.freedesktop.a11y.KeyboardMonitor','WatchKeyboard');denied=False
        except GLib.Error as error:denied='AccessDenied' in str(error)
        check('unregistered sender denied',denied)
        for app,tag in [('org.gnome.Orca','orca'),('org.example.ABIReader','generic')]:
            process=subprocess.Popen(['python3',str(HERE/'abi_client.py'),app,tag],stdout=log,stderr=log,start_new_session=True);processes.append(process);clients.append(process);starts[process.pid]=process_start(process.pid);register(process,'client')
            wait(lambda:(root/(tag+'-ready')).exists(),'actual public Device client starts '+tag)
        def registrations_ready():
            found=state()
            return found if len(found['clients'])==2 and all(c['watched'] and c['modifiers']==[65509] and len(c['keystrokes'])==4 and not c['grabbed'] for c in found['clients'].values()) else None
        ready=wait(registrations_ready,'both real devices configured generic keyed subscriptions')
        check('independent unique callers registered',len(ready['clients'])==2,registrations=ready)
        initial={tag:wait(lambda:json.loads((root/(tag+'-report.json')).read_text()) if (root/(tag+'-report.json')).exists() else None,'device report '+tag) for tag in ('orca','generic')}
        check('official Orca factory selects DeviceA11yManager',initial['orca']['officialOrcaFactory'] and initial['orca']['deviceType']=='AtspiDeviceA11yManager',device=initial['orca'])
        check('other application ID selects same protocol backend',initial['generic']['deviceType']=='AtspiDeviceA11yManager',device=initial['generic'])
        check('actual Atspi SetKeyGrabs keysym and lock variants',all(c['keystrokes']==[[104,0],[104,16],[104,2],[104,18]] for c in ready['clients'].values()))
        for packet in [(False,0,65509,0,66),(False,0,104,104,43),(True,0,104,104,43),(True,0,65509,0,66)]:
            call('org.omarchy.KeyboardMonitorABIProbe','EmitPacket',packet,'(buuuq)')
        final={tag:wait(lambda:json.loads((root/(tag+'-report.json')).read_text()) if len(json.loads((root/(tag+'-report.json')).read_text())['events'])>=4 else None,'directed actual Device events '+tag) for tag in ('orca','generic')}
        check('buuuq ABI decodes key down/up and custom modifier',all([e['pressed'] for e in client['events']]==[True,True,False,False] and client['events'][1]['args'][0]==43 and client['events'][1]['args'][1]==104 and client['events'][1]['args'][2]&client['mappedCapsModifier'] for client in final.values()),reports=final)
        (root/'clients-exit').touch()
        for process in processes[1:]:process.wait(timeout=4)
        wait(lambda:state()['clients']=={},'disconnect removes all subscriptions/grabs')
        check('all client state cleared on D-Bus exit',state()['clients']=={})
        events=[json.loads(line) for line in (root/'service-events.jsonl').read_text().splitlines()]
        report['serviceEvents']=events
        check('signals explicitly targeted to registered unique clients',all(len(event['directedRecipients'])==2 and all(client.startswith(':') for client in event['directedRecipients']) for event in events if event['event']=='fabricatedABIPacket'))
        check('GrabKeyboard and UngrabKeyboard actual public calls',sum(event.get('method')=='GrabKeyboard' for event in events)==2 and sum(event.get('method')=='UngrabKeyboard' for event in events)==2)
        report['result']='pass'
    except Exception as error:
        import traceback
        report.update(result='fail',error=repr(error),traceback=traceback.format_exc())
    finally:
        # Both clients are requested to exit while the service remains live.
        (root/'clients-exit').touch();cleanup=[]
        for process in [*clients,*(p for p in processes if p not in clients)]:
            row={'pid':process.pid,'start':starts[process.pid],'client':process in clients}
            try:
                if process.poll() is None:
                    assert process_start(process.pid)==starts[process.pid] and os.getpgid(process.pid)==process.pid
                    if process not in clients:process.terminate()
                    process.wait(timeout=4)
            except Exception as error:
                row['error']=repr(error)
                if process.poll() is None:
                    try:
                        assert process_start(process.pid)==starts[process.pid] and os.getpgid(process.pid)==process.pid
                        row['forcedTERM']=True;os.killpg(process.pid,signal.SIGTERM)
                        try:process.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            assert process_start(process.pid)==starts[process.pid]
                            row['forcedKILL']=True;os.killpg(process.pid,signal.SIGKILL);process.wait(timeout=3)
                    except Exception as fallback:row['fallbackError']=repr(fallback)
            row.update(exitCode=process.poll(),gone=not Path('/proc',str(process.pid)).exists());cleanup.append(row)
        report['cleanupClientsFirst']=cleanup
        report['normalClientsExit']=len(clients)==2 and all(row['exitCode']==0 and row['gone'] and not row.get('error') for row in cleanup if row['client'])
        report['allOwnedProcessesGone']=all(row['gone'] for row in cleanup)
        if not report['normalClientsExit'] or not report['allOwnedProcessesGone'] or any(row.get('error') for row in cleanup):report['result']='fail'
        log.close();report['processErrors']=(root/'process-errors.log').read_text()
        if (root/'service-events.jsonl').exists():report['serviceEvents']=[json.loads(line) for line in (root/'service-events.jsonl').read_text().splitlines()]
        (root/'proof-report.json').write_text(json.dumps(report,indent=2))
    return 0 if report['result']=='pass' else 1

def outer():
    require_qa_scope();manifest_before=verify_inputs()
    parser=argparse.ArgumentParser();parser.add_argument('--attempt',type=Path,required=True);args=parser.parse_args()
    output=args.attempt.resolve();assert output.parent==HERE and output.name.startswith('attempt-');os.umask(0o077);output.mkdir(mode=0o700)
    before=a11y();status_before=main_status();root=private_runtime();launcher=None;launcher_identity=None;result=None;report={}
    try:
        for name in ('home','config','cache','data','state'):(root/name).mkdir(mode=0o700)
        env=dict(os.environ,HOME=str(root/'home'),XDG_RUNTIME_DIR=str(root),XDG_CONFIG_HOME=str(root/'config'),XDG_CACHE_HOME=str(root/'cache'),XDG_DATA_HOME=str(root/'data'),XDG_STATE_HOME=str(root/'state'),KEYBOARD_ABI_RUNTIME=str(root),GTK_A11Y='none',NO_AT_BRIDGE='1',ATSPI_USE_A11Y_MANAGER_DEVICE='1')
        for name in ('ATSPI_USE_LEGACY_DEVICE','DISPLAY','WAYLAND_DISPLAY','WAYLAND_SOCKET','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','SESSION_MANAGER','HYPRLAND_INSTANCE_SIGNATURE','XDG_SESSION_TYPE'):env.pop(name,None)
        launcher=subprocess.Popen(['dbus-run-session','--','python3',str(Path(__file__).resolve()),'--inner'],env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True);launcher_identity=capture(launcher,'private-session')
        stdout,stderr=launcher.communicate(timeout=35)
        report=json.loads((root/'proof-report.json').read_text()) if (root/'proof-report.json').exists() else {'result':'fail','error':'private inner did not produce a report','nativeInputProved':False}
        report['privateProcessExit']=launcher.returncode;report['privateLogs']=stderr
        if launcher.returncode:report['result']='fail'
    except Exception as error:report.update(result='fail',error=repr(error),nativeInputProved=False)
    finally:
        fallback=[]
        if launcher and launcher.poll() is None:
            (root/'clients-exit').touch()
            try:records=json.loads((root/'owned-processes.json').read_text())
            except FileNotFoundError:records=[]
            # On outer timeout, preserve client-first order even across detached groups.
            for record in sorted(records,key=lambda r:0 if r['role']=='client' else 1):fallback.append(stop_owned(record))
            fallback.append(stop_owned(launcher_identity));launcher.wait(timeout=5)
            report.update(result='fail',timeoutCleanup=fallback)
        if launcher:report['privateSessionCleanup']={'pid':launcher.pid,'exitCode':launcher.poll(),'gone':not Path('/proc',str(launcher.pid)).exists()}
        try:records=json.loads((root/'owned-processes.json').read_text())
        except FileNotFoundError:records=[]
        survivors=[r for r in records if Path('/proc',str(r['pid'])).exists()]
        if survivors:
            (root/'clients-exit').touch()
            report['lateOwnedCleanup']=[stop_owned(r) for r in sorted(survivors,key=lambda r:0 if r['role']=='client' else 1)];report['result']='fail'
        all_gone=not any(Path('/proc',str(r['pid'])).exists() for r in records)
        report['recordedOwnedProcessesGone']=all_gone
        evidence=output/'private-runtime-evidence';evidence.mkdir(mode=0o700)
        for path in root.rglob('*'):
            if path.is_file() and not path.is_symlink():
                target=evidence/path.relative_to(root);target.parent.mkdir(mode=0o700,parents=True,exist_ok=True);shutil.copy2(path,target);target.chmod(0o600)
        # D-Bus/session teardown has completed before private runtime removal.
        if all_gone:shutil.rmtree(root)
        else:report['retainedPrivateRuntimeForRecovery']=str(root);report['result']='fail'
        report['privateRuntimeGone']=not root.exists()
        report['mainPreservation']={'a11ySocket':before==a11y(),'readerStatus':status_before==main_status()}
        report['mainBefore']={'a11y':before,'readerStatus':status_before}
        if not all(report['mainPreservation'].values()):report['result']='fail'
        try:report['frozenInputsExact']=verify_inputs()==manifest_before
        except Exception as error:report.update(frozenInputsExact=False,sourceError=repr(error),result='fail')
        if not report['frozenInputsExact']:report['result']='fail'
        path=output/'private-abi-report.json';path.write_text(json.dumps(report,indent=2)+'\n');path.chmod(0o600)
    print(json.dumps({'result':report['result'],'nativeInputProved':False,'mainPreservation':report['mainPreservation'],'reportSHA256':hashlib.sha256(path.read_bytes()).hexdigest()}))
    return int(report['result']!='pass')

if __name__=='__main__':
    if '--inner' in sys.argv:raise SystemExit(inner())
    raise SystemExit(outer())
