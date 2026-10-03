#!/usr/bin/env python3
"""Actual Brave download on private D-Bus; no synthetic LauncherEntry emitter.

Run: python3 real_brave_publisher.py
Uses a disposable profile and privately extracted optional libunity libraries.
"""
import hashlib
import http.server
import json
import os
from pathlib import Path
import subprocess
import socket
import sys
import tempfile
import threading
import time
from gi.repository import Gio, GLib

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from qa_launch import require_qa_scope,owned_runtime,verify_parent
require_qa_scope()
PREFIX = ROOT/'libunity-prefix/usr/lib/x86_64-linux-gnu'
REPORT = ROOT/'real-brave-publisher-report.json'
PAYLOAD = b'actual-brave-download-qa\n' * 180000
signals = []
requests = []
snapshots = []


def main_a11y_state():
    path = Path('/run/user')/str(os.getuid())/'at-spi/bus_0'
    try: identity = [path.stat().st_dev, path.stat().st_ino]
    except FileNotFoundError: identity = None
    connected = False
    if identity:
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as connection:
            connection.settimeout(.2)
            try: connection.connect(str(path));connected=True
            except OSError: pass
    return {'identity':identity,'connects':connected}


MAIN_BUS = os.environ.get('BRAVE_QA_MAIN_BUS') == '1'
if os.environ.get('BRAVE_QA_PRIVATE_BUS') != '1' and not MAIN_BUS:
    before = main_a11y_state()
    with owned_runtime() as directory:
        bus_env = dict(os.environ, XDG_RUNTIME_DIR=directory, BRAVE_QA_PRIVATE_BUS='1')
        # The D-Bus daemon must inherit isolation before any service activation.
        # Keeping only the receiver/browser runtime private is insufficient.
        for name in ['AT_SPI_BUS_ADDRESS','DBUS_SESSION_BUS_ADDRESS','SESSION_MANAGER']:
            bus_env.pop(name,None)
        if bus_env.get('BRAVE_QA_GUI') != '1':
            for name in ['DISPLAY','WAYLAND_DISPLAY']:
                bus_env.pop(name,None)
            bus_env.update(NO_AT_BRIDGE='1',GTK_A11Y='none')
        else:
            bus_env['WAYLAND_DISPLAY']=verify_parent(dict(os.environ))['path']
        result = subprocess.run(['dbus-run-session','--',sys.executable,str(Path(__file__).resolve())],env=bus_env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    after = main_a11y_state()
    report_name = 'real-brave-wrapper-report.json' if os.environ.get('BRAVE_QA_WRAPPER') == '1' else 'real-brave-baseline-report.json' if os.environ.get('BRAVE_QA_BASELINE') == '1' else REPORT.name
    report_path = ROOT/report_name
    report = json.loads(report_path.read_text())
    report['isolation'] = {'runtimeBeforeBusDaemon':True,'mainA11yBefore':before,'mainA11yAfter':after,'mainA11yUnchanged':before==after}
    report['checks']['mainA11yUnchanged'] = before==after
    if not before==after:report['result']='incomplete'
    report_path.write_text(json.dumps(report,indent=2))
    report_path.with_suffix('.private-bus.log').write_text(result.stdout)
    print(json.dumps({'result':report['result'],'checks':report['checks'],'signals':len(report['signals']),'report':str(report_path)}))
    sys.exit(result.returncode)

if MAIN_BUS:
    REPORT = ROOT/'real-brave-main-qml-report.json'
elif os.environ.get('BRAVE_QA_WRAPPER') == '1':
    REPORT = ROOT/'real-brave-wrapper-report.json'
elif os.environ.get('BRAVE_QA_BASELINE') == '1':
    REPORT = ROOT/'real-brave-baseline-report.json'


class Server(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def do_GET(self):
        requests.append(self.path)
        if self.path == '/':
            html = b'<html><body>Disposable Brave download QA<script>setTimeout(()=>{let a=document.createElement("a");a.href="/download";a.download="publisher-check.bin";a.click()},1200)</script></body></html>'
            self.send_response(200);self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(html)
        elif self.path == '/download':
            self.send_response(200);self.send_header('Content-Type','application/octet-stream');self.send_header('Content-Disposition','attachment; filename="publisher-check.bin"');self.send_header('Content-Length',str(len(PAYLOAD)));self.end_headers()
            try:
                for i in range(0,len(PAYLOAD),32768):
                    self.wfile.write(PAYLOAD[i:i+32768]);self.wfile.flush();time.sleep(.045)
            except (BrokenPipeError, ConnectionResetError): pass
        else:
            self.send_response(404);self.end_headers()


connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)
def update(bus, sender, path, interface, signal, parameters, data):
    uri, props = parameters.unpack()
    pid_reply = connection.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','GetConnectionUnixProcessID',GLib.Variant('(s)',(sender,)),GLib.VariantType('(u)'),Gio.DBusCallFlags.NONE,1000,None)
    signals.append({'sender':sender,'pid':pid_reply.unpack()[0],'path':path,'uri':uri,'properties':props})
connection.signal_subscribe(None,'com.canonical.Unity.LauncherEntry','Update',None,None,Gio.DBusSignalFlags.NONE,update,None)
context = GLib.MainContext.default()
def pump(seconds):
    end = time.monotonic()+seconds
    while time.monotonic()<end:
        while context.pending(): context.iteration(False)
        time.sleep(.02)

with tempfile.TemporaryDirectory(prefix='real-brave-publisher-') as temporary:
    temp = Path(temporary)
    # Keep one runtime for the entire private bus/client tree.
    runtime=Path(os.environ['XDG_RUNTIME_DIR'])
    downloads = temp/'downloads';downloads.mkdir()
    profile = temp/'profile';(profile/'Default').mkdir(parents=True)
    (profile/'Default/Preferences').write_text(json.dumps({'download':{'default_directory':str(downloads),'prompt_for_download':False},'browser':{'has_seen_welcome_page':True}}))
    env = dict(os.environ, XDG_RUNTIME_DIR=str(runtime))
    log = REPORT.with_suffix('.log').open('w')
    receiver = None if MAIN_BUS else subprocess.Popen([str(Path.home()/'.local/bin/hypr-taskbar-launcher')],env=env,stdout=log,stderr=log)
    state_runtime = Path(os.environ['XDG_RUNTIME_DIR']) if MAIN_BUS else runtime
    state_path = state_runtime/'hypr-taskbar-launcher.json'
    initial_launcher = json.loads(state_path.read_text()) if MAIN_BUS else {}
    a11y_before = main_a11y_state()
    qml_indicators = []
    pump(.5)
    server = http.server.ThreadingHTTPServer(('127.0.0.1',0),Server)
    thread = threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    browser_env = dict(env)
    if MAIN_BUS:
        for name in ['DISPLAY','WAYLAND_DISPLAY','AT_SPI_BUS_ADDRESS']:
            browser_env.pop(name,None)
        browser_env.update(NO_AT_BRIDGE='1',GTK_A11Y='none')
    executable = '/opt/brave-bin/brave'
    compatibility = {'XDG_CURRENT_DESKTOP':'KDE','CHROME_DESKTOP':'brave-browser.desktop','optionalLibunity':'private Ubuntu noble packages; no system installation'}
    if os.environ.get('BRAVE_QA_WRAPPER') == '1' or MAIN_BUS:
        executable = str(Path.home()/'.local/bin/brave-browser') if MAIN_BUS else str(ROOT/'staged/brave-taskbar')
        if not MAIN_BUS:browser_env.update(BRAVE_LAUNCHER_LIB_DIR=str(ROOT/'staged/lib/brave-launcher'))
        compatibility = {'XDG_CURRENT_DESKTOP':'Hyprland:Unity','CHROME_DESKTOP':'brave-browser.desktop','optionalLibunity':'staged private user libraries; packaged launcher retains flags'}
    elif os.environ.get('BRAVE_QA_BASELINE') == '1':
        compatibility = {'XDG_CURRENT_DESKTOP':browser_env.get('XDG_CURRENT_DESKTOP'),'optionalLibunity':'system default; unavailable'}
    else:
        browser_env.update(XDG_CURRENT_DESKTOP='KDE', CHROME_DESKTOP='brave-browser.desktop', LD_LIBRARY_PATH=str(PREFIX)+':'+str(PREFIX/'libunity'))
    mode = [] if os.environ.get('BRAVE_QA_GUI') == '1' else ['--headless=new']
    browser = subprocess.Popen([executable,*mode,'--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-component-update','--disable-sync','--disable-extensions','--disable-features=MediaRouter','--user-data-dir='+str(profile),'http://127.0.0.1:'+str(server.server_port)+'/'],env=browser_env,stdout=log,stderr=log,start_new_session=True)
    receiver_restart = None
    browser_identity = None
    try:
        deadline=time.monotonic()+22
        while time.monotonic()<deadline:
            pump(.1)
            try:
                snapshot=json.loads(state_path.read_text())
                if not snapshots or snapshots[-1]!=snapshot:snapshots.append(snapshot)
                if MAIN_BUS:
                    qml = json.loads(subprocess.check_output(['qs','-p','/usr/share/omarchy/shell','ipc','call','hoskinson.windows','state'],text=True,timeout=3))
                    indicator = next((g for g in qml.get('indicators',[]) if g.get('key')=='brave-browser'),None)
                    if indicator and (not qml_indicators or qml_indicators[-1]!=indicator):qml_indicators.append(indicator)
                if browser_identity is None and Path(f'/proc/{browser.pid}/cmdline').exists():
                    actual_env = dict(row.split('=',1) for row in Path(f'/proc/{browser.pid}/environ').read_text().split('\0') if '=' in row)
                    browser_identity = {'environment':{key:actual_env.get(key) for key in ['XDG_CURRENT_DESKTOP','XDG_SESSION_TYPE','WAYLAND_DISPLAY','CHROME_DESKTOP','LD_LIBRARY_PATH','XDG_RUNTIME_DIR']},'argv':Path(f'/proc/{browser.pid}/cmdline').read_text().split('\0')[:-1]}
                if (os.environ.get('BRAVE_QA_RECEIVER_RESTART') == '1' and receiver_restart is None
                        and snapshot.get('brave-browser',{}).get('progress',0) > .15):
                    receiver_restart = {'before':snapshot,'signalOffset':len(signals),'pidBefore':receiver.pid}
                    receiver.terminate();receiver.wait(timeout=5)
                    pump(.1)
                    receiver = subprocess.Popen([str(Path.home()/'.local/bin/hypr-taskbar-launcher')],env=env,stdout=log,stderr=log)
                    receiver_restart['pidAfter'] = receiver.pid
            except (OSError,ValueError):pass
            if (downloads/'publisher-check.bin').exists() and signals and any(not s['properties'].get('count-visible',True) for s in signals):break
        downloaded=downloads/'publisher-check.bin'
        report={'publisher':'installed Brave','browserPid':browser.pid,'version':subprocess.check_output(['/opt/brave-bin/brave','--version'],text=True).strip(),'mode':'gui' if not mode else 'headless','environment':compatibility,'requests':requests,'signals':signals,'snapshots':snapshots,'downloadComplete':downloaded.is_file(),'downloadSha256':hashlib.sha256(downloaded.read_bytes()).hexdigest() if downloaded.is_file() else None,'expectedSha256':hashlib.sha256(PAYLOAD).hexdigest()}
        report['actualBrowserProcess'] = browser_identity
        report['qmlIndicators'] = qml_indicators
        report['checks']={'realBrowserSender':bool(signals) and all(s['pid']==browser.pid for s in signals),'correctAppURI':bool(signals) and all(s['uri']=='application://brave-browser.desktop' for s in signals),'countReceived':any(s['properties'].get('count',0)>0 and s['properties'].get('count-visible') for s in signals),'progressReceived':any(0<s['properties'].get('progress',0)<1 and s['properties'].get('progress-visible') for s in signals),'receiverImported':any(s.get('brave-browser',{}).get('count-visible') and s.get('brave-browser',{}).get('progress-visible') for s in snapshots),'downloadIntegrity':report['downloadSha256']==report['expectedSha256']}
        if os.environ.get('BRAVE_QA_RECEIVER_RESTART') == '1':
            report['receiverRestart'] = receiver_restart
            report['checks']['receiverRestartRepublished'] = bool(receiver_restart) and any(s['properties'].get('count')==1 and s['properties'].get('count-visible') for s in signals[receiver_restart['signalOffset']:])
        if MAIN_BUS:
            report['checks']['qmlRealAppCountProgress'] = any(s.get('launcher',{}).get('count')==1 and s.get('launcher',{}).get('count-visible') and s.get('launcher',{}).get('progress-visible') and 0<s.get('launcher',{}).get('progress',0)<1 for s in qml_indicators)
        browser.terminate();browser.wait(timeout=10);pump(.4)
        report['afterBrowserExit']=json.loads(state_path.read_text())
        report['checks']['disconnectClears']=report['afterBrowserExit']==initial_launcher
        if MAIN_BUS:
            deadline=time.monotonic()+3
            qml_after=None
            while time.monotonic()<deadline:
                pump(.1)
                qml=json.loads(subprocess.check_output(['qs','-p','/usr/share/omarchy/shell','ipc','call','hoskinson.windows','state'],text=True,timeout=3))
                qml_after=next((g for g in qml.get('indicators',[]) if g.get('key')=='brave-browser'),{})
                if qml_after.get('launcher',{})==initial_launcher.get('brave-browser',{}):break
            report['qmlAfterBrowserExit']=qml_after
            report['checks']['qmlDisconnectClears']=qml_after.get('launcher',{})==initial_launcher.get('brave-browser',{})
            report['isolation']={'mainA11yBefore':a11y_before,'mainA11yAfter':main_a11y_state()}
            report['checks']['mainA11yUnchanged']=report['isolation']['mainA11yBefore']==report['isolation']['mainA11yAfter']
        report['result']='pass' if all(report['checks'].values()) else 'incomplete'
        REPORT.write_text(json.dumps(report,indent=2));print(json.dumps({'result':report['result'],'checks':report['checks'],'signals':len(signals),'report':str(REPORT)}))
    finally:
        if browser.poll() is None:browser.terminate();browser.wait(timeout=10)
        if receiver is not None:receiver.terminate();receiver.wait(timeout=5)
        server.shutdown();server.server_close();log.close()
