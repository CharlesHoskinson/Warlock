import json, subprocess, threading, time
from pathlib import Path
from gi.repository import Gio,GLib
bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
loop=GLib.MainLoop()
report={'checks':[],'events':[]}
path='/com/canonical/unity/quicklist/qa'
xml='''<node><interface name="com.canonical.dbusmenu"><method name="GetLayout"><arg type="i" direction="in"/><arg type="i" direction="in"/><arg type="as" direction="in"/><arg type="u" direction="out"/><arg type="(ia{sv}av)" direction="out"/></method><method name="AboutToShow"><arg type="i" direction="in"/><arg type="b" direction="out"/></method><method name="Event"><arg type="i" direction="in"/><arg type="s" direction="in"/><arg type="v" direction="in"/><arg type="u" direction="in"/></method></interface></node>'''
label='QA app action';enabled=True

def method(connection,sender,obj,iface,name,parameters,invocation):
    global label
    if name=='GetLayout':
        child=GLib.Variant('(ia{sv}av)',(41,{'label':GLib.Variant('s',label),'enabled':GLib.Variant('b',enabled)},[]))
        hidden=GLib.Variant('(ia{sv}av)',(42,{'label':GLib.Variant('s','Hidden QA action'),'visible':GLib.Variant('b',False)},[]))
        invocation.return_value(GLib.Variant('(u(ia{sv}av))',(1,(0,{},[child,hidden]))))
    elif name=='AboutToShow':
        label='QA lazy app action'
        invocation.return_value(GLib.Variant('(b)',(True,)))
    elif name=='Event':
        report['events'].append(parameters.unpack())
        invocation.return_value(GLib.Variant('()',()))
registration=bus.register_object(path,Gio.DBusNodeInfo.new_for_xml(xml).interfaces[0],method,None,None)

def state():
    return json.loads(subprocess.check_output(['qs','-p','/usr/share/omarchy/shell','ipc','call','hoskinson.windows','state'],text=True))
def wait(check,name):
    deadline=time.monotonic()+6
    while time.monotonic()<deadline:
        data=state();entry=next(i for i in data['indicators'] if i['key']=='brave-browser')
        if check(entry):
            report['checks'].append({'name':name,'state':entry});return
        time.sleep(.2)
    raise AssertionError((name,data))
def controller():
    global label,enabled
    try:
        bus.emit_signal(None,'/com/canonical/unity/launcherentry/qa','com.canonical.Unity.LauncherEntry','Update',GLib.Variant('(sa{sv})',('application://brave-browser.desktop',{'quicklist':GLib.Variant('s',path)})))
        bus.flush_sync(None)
        wait(lambda g:g['launcher'].get('quicklistItems')==[{'id':41,'label':'QA app action','enabled':True}],'app menu imported; hidden item excluded')
        subprocess.run(['qs','-p','/usr/share/omarchy/shell','ipc','call','hoskinson.windows','menu','1'],check=True)
        wait(lambda g:g['launcher'].get('quicklistItems')==[{'id':41,'label':'QA lazy app action','enabled':True}],'opening Jump List requests AboutToShow and refreshes')
        subprocess.run(['grim','-g','0,0 650x600','/tmp/taskbar-quicklist-v35.png'],check=True)
        subprocess.run([str(Path.home()/'.local/bin/hypr-taskbar'),'quicklist','brave-browser','41'],check=True)
        assert report['events'] and report['events'][0][:2]==(41,'clicked'),report['events']
        report['checks'].append({'name':'real DBus Event delivered','event':report['events'][0]})
        label='QA disabled action';enabled=False
        bus.emit_signal(None,path,'com.canonical.dbusmenu','LayoutUpdated',GLib.Variant('(ui)',(2,0)));bus.flush_sync(None)
        wait(lambda g:g['launcher'].get('quicklistItems')==[{'id':41,'label':'QA disabled action','enabled':False}],'LayoutUpdated refreshes menu')
        failed=subprocess.run([str(Path.home()/'.local/bin/hypr-taskbar'),'quicklist','brave-browser','41'],capture_output=True,text=True)
        assert failed.returncode==2 and len(report['events'])==1
        report['checks'].append({'name':'disabled app action rejected','exit':failed.returncode})
        bus.close_sync(None)
        wait(lambda g:g['launcher']=={},'disconnect clears menu')
        report['result']='pass'
    except Exception as error:
        report['result']='fail';report['error']=repr(error)
    finally:
        subprocess.run(['qs','-p','/usr/share/omarchy/shell','ipc','call','hoskinson.windows','dismiss'],check=False)
        if not bus.is_closed():bus.close_sync(None)
        Path.home().joinpath('.cache/taskbar-quicklist-live-qa.json').write_text(json.dumps(report,indent=2))
        GLib.idle_add(loop.quit)
threading.Thread(target=controller).start()
loop.run()
print(json.dumps(report,indent=2))
assert report['result']=='pass'
