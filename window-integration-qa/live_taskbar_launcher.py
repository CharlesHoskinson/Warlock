import json, os, subprocess, time
from pathlib import Path
from gi.repository import Gio, GLib

artifact=Path.home()/'.cache/taskbar-launcher-live-qa.json'
connection=Gio.bus_get_sync(Gio.BusType.SESSION,None)
report={'checks':[]}
uri='application://brave-browser.desktop'

def ui():
    return json.loads(subprocess.check_output(['qs','-p','/usr/share/omarchy/shell','ipc','call','hoskinson.windows','state'],text=True))
def wait(check,label):
    deadline=time.monotonic()+6
    while time.monotonic()<deadline:
        data=ui(); group=next(g for g in data['indicators'] if g['key']=='brave-browser')
        if check(group):
            report['checks'].append({'name':label,'state':group}); return
        time.sleep(.2)
    raise AssertionError((label,data))
def emit(props):
    connection.emit_signal(None,'/com/canonical/unity/launcherentry/qa','com.canonical.Unity.LauncherEntry','Update',GLib.Variant('(sa{sv})',(uri,props)))
    connection.flush_sync(None)

attention=Path(os.environ['XDG_RUNTIME_DIR'])/'hypr-taskbar-attention.json'
original=attention.read_bytes()
try:
    emit({'count':GLib.Variant('x',12),'count-visible':GLib.Variant('b',True)})
    wait(lambda g:g['launcher'].get('count')==12 and g['launcher'].get('count-visible'),'live count signal reaches QML')
    emit({'progress':GLib.Variant('d',.4),'progress-visible':GLib.Variant('b',True),'urgent':GLib.Variant('b',True)})
    wait(lambda g:g['launcher'].get('progress')==.4 and g['launcher'].get('count')==12 and g['launcher'].get('urgent'),'partial progress keeps count')
    subprocess.run(['grim','-g','0,0 600x26','/tmp/taskbar-count-progress-v33.png'],check=True)
    emit({'count-visible':GLib.Variant('b',False),'progress-visible':GLib.Variant('b',False),'urgent':GLib.Variant('b',False)})
    wait(lambda g:not g['launcher'].get('count-visible',True) and not g['launcher'].get('progress-visible',True),'visibility updates reach QML')
    connection.close_sync(None)
    wait(lambda g:g['launcher']=={},'disconnect clears indicators')
    clients=json.loads(subprocess.check_output(['hyprctl','clients','-j'],text=True))
    brave=next(w for w in clients if w['class']=='brave-browser' and w['workspace']['name']=='special:win-minimized')
    previous=json.loads(original)
    previous[brave['address']]={'pid':brave['pid'],'stableId':brave['stableId']}
    temp=attention.with_suffix('.qa');temp.write_text(json.dumps(previous));temp.replace(attention)
    wait(lambda g:g['urgent'],'compositor urgency changes QML independently')
    temp=attention.with_suffix('.qa');temp.write_bytes(original);temp.replace(attention)
    wait(lambda g:not g['urgent'],'compositor urgency clears QML independently')
    report['result']='pass'
finally:
    attention.write_bytes(original)
    if not connection.is_closed(): connection.close_sync(None)
    artifact.write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
