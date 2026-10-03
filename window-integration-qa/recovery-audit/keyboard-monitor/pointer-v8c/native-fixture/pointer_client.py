"""Independent public protocol caller; GTK/Orca compatibility is tested separately."""
import json,os,sys,time
from pathlib import Path
from gi.repository import Gio,GLib
from client_wire_trace import WireTrace
runtime=Path(os.environ['XDG_RUNTIME_DIR'])
assert str(runtime).startswith('/tmp/kbn-') and runtime.stat().st_mode&0o777==0o700
assert os.environ['DBUS_SESSION_BUS_ADDRESS']=='unix:path='+str(runtime/'bus')
name=sys.argv[1];bus=Gio.bus_get_sync(Gio.BusType.SESSION,None);signals=[]
trace=WireTrace(Path(__file__).resolve().parent.parent/('wire-client-'+name+'.jsonl'))
bus.add_filter(trace.filter,None)
def daemon(method,signature,args):
    return bus.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus',method,
        GLib.Variant(signature,args),None,Gio.DBusCallFlags.NONE,1000,None).unpack()[0]
def changed(connection,sender,path,iface,signal,parameters,user):
    row=dict(time=time.monotonic(),sender=sender,path=path,signal=signal,parameters=parameters.unpack())
    signals.append(row)
    trace.record('actual-pointer-callback',count=len(signals),callback=row,wireArrivals=list(trace.arrivals))
bus.signal_subscribe('org.freedesktop.a11y.Manager','org.freedesktop.a11y.PointerLocator','PointerPositionChanged',
    '/org/freedesktop/a11y/Manager',None,Gio.DBusSignalFlags.NONE,changed,None)
def owner_changed(connection,sender,path,iface,signal,parameters,user):
    trace.record('actual-own-name-callback',sender=sender,parameters=parameters.unpack())
bus.signal_subscribe('org.freedesktop.DBus','org.freedesktop.DBus','NameOwnerChanged',
    '/org/freedesktop/DBus',name,Gio.DBusSignalFlags.NONE,owner_changed,None)
loop=GLib.MainLoop()
def command(source,condition):
    line=sys.stdin.readline()
    if not line:loop.quit();return False
    request=json.loads(line);op=request['operation']
    trace.record('actual-command-begin',request=request,count=len(signals),unique=bus.get_unique_name())
    try:
        if op=='claim':value=daemon('RequestName','(su)',(name,4))
        elif op=='release':value=daemon('ReleaseName','(s)',(name,))
        elif op=='alias_claim':value=daemon('RequestName','(su)',(name+'.Alias.KeyboardMonitor',4))
        elif op=='alias_release':value=daemon('ReleaseName','(s)',(name+'.Alias.KeyboardMonitor',))
        elif op=='query':value=bus.call_sync('org.freedesktop.a11y.Manager','/org/freedesktop/a11y/Manager',
            'org.freedesktop.a11y.PointerLocator','QueryPointer',None,None,Gio.DBusCallFlags.NONE,3000,None).unpack()
        elif op in ('watch','unwatch','grab','ungrab','grabs'):
            method={'watch':'WatchKeyboard','unwatch':'UnwatchKeyboard','grab':'GrabKeyboard','ungrab':'UngrabKeyboard','grabs':'SetKeyGrabs'}[op]
            args=GLib.Variant('(aua(uu))',(request.get('modifiers',[]),request.get('strokes',[]))) if op=='grabs' else None
            value=bus.call_sync('org.freedesktop.a11y.Manager','/org/freedesktop/a11y/Manager',
                'org.freedesktop.a11y.KeyboardMonitor',method,args,None,Gio.DBusCallFlags.NONE,1000,None).unpack()
        elif op=='signals':value=list(signals)
        elif op=='exit':loop.quit();value=True
        else:raise ValueError(op)
        result=dict(pass_=True,value=value)
    except Exception as error:result=dict(pass_=False,error=str(error))
    trace.record('actual-command-end',request=request,response=result,count=len(signals),wireArrivalCount=len(trace.arrivals))
    print(json.dumps(dict(id=request.get('id'),**result)),flush=True);return op!='exit'
GLib.io_add_watch(sys.stdin.fileno(),GLib.IO_IN,command)
print(json.dumps(dict(ready=True,uniqueName=bus.get_unique_name(),name=name)),flush=True)
loop.run()
