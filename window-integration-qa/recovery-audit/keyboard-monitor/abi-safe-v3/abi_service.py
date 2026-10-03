#!/usr/bin/env python3
"""PRIVATE-BUS ABI probe only. Fabricated packets are not native input evidence."""
import json,os,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,verify_runtime
import gi
from gi.repository import Gio,GLib

NAME='org.freedesktop.a11y.Manager';PATH='/org/freedesktop/a11y/Manager'
IFACE='org.freedesktop.a11y.KeyboardMonitor'
XML='''<node><interface name="org.freedesktop.a11y.KeyboardMonitor">
<method name="WatchKeyboard"/><method name="UnwatchKeyboard"/>
<method name="GrabKeyboard"/><method name="UngrabKeyboard"/>
<method name="SetKeyGrabs"><arg type="au" direction="in"/><arg type="a(uu)" direction="in"/></method>
<signal name="KeyEvent"><arg type="b"/><arg type="u"/><arg type="u"/><arg type="u"/><arg type="q"/></signal>
</interface><interface name="org.omarchy.KeyboardMonitorABIProbe">
<method name="State"><arg type="s" direction="out"/></method>
<method name="EmitPacket"><arg type="b" direction="in"/><arg type="u" direction="in"/><arg type="u" direction="in"/><arg type="u" direction="in"/><arg type="q" direction="in"/></method>
</interface></node>'''

def main():
    root=Path(os.environ.get('KEYBOARD_ABI_RUNTIME',''))
    require_qa_scope();verify_runtime(root)
    assert root==Path(os.environ['XDG_RUNTIME_DIR'])
    assert os.environ.get('DBUS_SESSION_BUS_ADDRESS') and not os.environ.get('DISPLAY')
    log=root/'service-events.jsonl';clients={};bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
    def record(**item):
        with log.open('a') as out:out.write(json.dumps(dict(item,time=time.monotonic()))+'\n')
    def dbus(method,args,signature):
        return bus.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus',method,GLib.Variant(signature,args),None,Gio.DBusCallFlags.NONE,2000,None).unpack()
    def names(sender):
        result=[]
        for name in dbus('ListNames',(), '()')[0]:
            if name.endswith('.KeyboardMonitor') and not name.startswith(':'):
                try:
                    if dbus('GetNameOwner',(name,),'(s)')[0]==sender:result.append(name)
                except GLib.Error:pass
        return result
    def state():return {'clients':clients,'readerEnabled':False,'nativeInputImplemented':False}
    def method(connection,sender,path,interface,name,parameters,invocation):
        if interface=='org.omarchy.KeyboardMonitorABIProbe':
            if name=='State':invocation.return_value(GLib.Variant('(s)',(json.dumps(state()),)))
            elif name=='EmitPacket':
                event=parameters.unpack();recipients=[]
                for client,config in clients.items():
                    if config['watched'] or config['grabbed'] or event[2] in config['modifiers'] or (event[2],event[1]) in [tuple(v) for v in config['keystrokes']]:
                        connection.emit_signal(client,PATH,IFACE,'KeyEvent',GLib.Variant('(buuuq)',event));recipients.append(client)
                record(event='fabricatedABIPacket',packet=event,directedRecipients=recipients)
                invocation.return_value(GLib.Variant('()',()))
            return
        registrations=names(sender)
        if not registrations:
            record(event='denied',sender=sender,method=name)
            invocation.return_dbus_error('org.freedesktop.DBus.Error.AccessDenied','Caller has no owned KeyboardMonitor registration');return
        client=clients.setdefault(sender,{'registrations':registrations,'watched':False,'grabbed':False,'modifiers':[],'keystrokes':[]})
        if name=='WatchKeyboard':client['watched']=True
        elif name=='UnwatchKeyboard':client['watched']=False
        elif name=='GrabKeyboard':client['grabbed']=True
        elif name=='UngrabKeyboard':client['grabbed']=False
        elif name=='SetKeyGrabs':client['modifiers'],client['keystrokes']=parameters.unpack()
        record(event='method',sender=sender,registrations=registrations,method=name,arguments=parameters.unpack(),state=client.copy())
        invocation.return_value(GLib.Variant('()',()))
    def name_change(connection,sender,path,interface,signal,parameters):
        name,old,new=parameters.unpack()
        if old in clients and (name==old or name in clients[old]['registrations']) and not names(old):
            clients.pop(old,None);record(event='clientRemoved',sender=old,name=name)
    node=Gio.DBusNodeInfo.new_for_xml(XML)
    for interface in node.interfaces:bus.register_object(PATH,interface,method,None,None)
    bus.signal_subscribe('org.freedesktop.DBus','org.freedesktop.DBus','NameOwnerChanged','/org/freedesktop/DBus',None,Gio.DBusSignalFlags.NONE,name_change)
    result=dbus('RequestName',(NAME,4),'(su)')[0];assert result==1,result
    record(event='ready',name=NAME);(root/'service-ready').touch()
    GLib.MainLoop().run()

if __name__=='__main__':main()
