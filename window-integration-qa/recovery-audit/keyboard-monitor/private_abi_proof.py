#!/usr/bin/env python3
"""Private runtime before D-Bus; ABI proof uses fabricated packets, never native keys."""
import json,os,socket,subprocess,sys,tempfile,time
from pathlib import Path
import gi
from gi.repository import Gio,GLib

HERE=Path(__file__).resolve().parent
def wait(fn,label):
    end=time.monotonic()+6
    while time.monotonic()<end:
        result=fn()
        if result:return result
        time.sleep(.03)
    raise AssertionError(label)
def a11y():
    path=Path('/run/user/1000/at-spi/bus_0')
    if not path.exists():return {'exists':False}
    st=path.stat();stream=socket.socket(socket.AF_UNIX);stream.settimeout(1)
    try:stream.connect(str(path));connects=True
    except OSError:connects=False
    finally:stream.close()
    return {'exists':True,'dev':st.st_dev,'inode':st.st_ino,'connects':connects}
def main_status():
    return subprocess.check_output(['gdbus','call','--session','--dest','org.a11y.Bus','--object-path','/org/a11y/bus','--method','org.freedesktop.DBus.Properties.Get','org.a11y.Status','ScreenReaderEnabled'],text=True,timeout=4).strip()

def inner():
    root=Path(os.environ['KEYBOARD_ABI_RUNTIME']);processes=[]
    report={'kind':'private session bus ABI with actual official Orca factory and public AT-SPI clients','nativeInputProved':False,'checks':[]}
    def check(name,value,**evidence):
        report['checks'].append(dict(name=name,pass_=bool(value),**evidence));assert value,name
    log=(root/'process-errors.log').open('a')
    try:
        service=subprocess.Popen(['python3',str(HERE/'abi_service.py')],stdout=log,stderr=log);processes.append(service)
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
            process=subprocess.Popen(['python3',str(HERE/'abi_client.py'),app,tag],stdout=log,stderr=log);processes.append(process)
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
        for process in processes:
            if process.poll() is None:process.terminate()
            try:process.wait(timeout=3)
            except subprocess.TimeoutExpired:process.kill();process.wait()
        log.close();report['processErrors']=(root/'process-errors.log').read_text()
        if (root/'service-events.jsonl').exists():report['serviceEvents']=[json.loads(line) for line in (root/'service-events.jsonl').read_text().splitlines()]
        (root/'proof-report.json').write_text(json.dumps(report,indent=2))
    return 0 if report['result']=='pass' else 1

def outer():
    before=a11y();status_before=main_status()
    with tempfile.TemporaryDirectory(prefix='kbd-') as temporary:
        root=Path(temporary);(root/'config').mkdir()
        env=os.environ.copy();env.update(XDG_RUNTIME_DIR=str(root),XDG_CONFIG_HOME=str(root/'config'),KEYBOARD_ABI_RUNTIME=str(root),GTK_A11Y='none',NO_AT_BRIDGE='1',ATSPI_USE_A11Y_MANAGER_DEVICE='1')
        env.pop('ATSPI_USE_LEGACY_DEVICE',None)
        for name in ('DISPLAY','WAYLAND_DISPLAY','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','SESSION_MANAGER','HYPRLAND_INSTANCE_SIGNATURE','XDG_SESSION_TYPE'):env.pop(name,None)
        result=subprocess.run(['dbus-run-session','--','python3',str(Path(__file__).resolve()),'--inner'],env=env,text=True,capture_output=True,timeout=35)
        report=json.loads((root/'proof-report.json').read_text()) if (root/'proof-report.json').exists() else {'result':'fail','error':'private inner did not produce a report'}
        report['privateProcessExit']=result.returncode;report['privateLogs']=result.stderr
        report['mainPreservation']={'a11ySocket':before==a11y(),'readerStatus':status_before==main_status()}
        report['mainBefore']={'a11y':before,'readerStatus':status_before}
        if result.returncode or not all(report['mainPreservation'].values()):report['result']='fail'
        (HERE/'private-abi-report.json').write_text(json.dumps(report,indent=2))
        print(json.dumps({name:report[name] for name in ('result','nativeInputProved','mainPreservation')},indent=2))
        if report['result']!='pass':print(report.get('error'),report.get('processErrors'),report.get('privateLogs'));raise SystemExit(1)

if __name__=='__main__':
    if '--inner' in sys.argv:raise SystemExit(inner())
    outer()
