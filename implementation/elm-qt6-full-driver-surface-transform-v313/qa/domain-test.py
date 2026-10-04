"""Actual compiled Qt/XKB objects and production keyboard guard; no display."""
import ctypes,copy,hashlib,importlib.util,json,resource,subprocess,sys,time
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('domains-test-'+str(time.time_ns()));OUT.mkdir()
sys.path.insert(0,str(ROOT/'qa'));import keyboard
report={'passed':False,'nativeAcceptance':False,'syntheticMapNotNativeSeat':True,'checks':[]}
def check(n,b):assert b,n;report['checks'].append({'name':n,'passed':True})
def rejected(n,fn):
 try:fn()
 except keyboard.Refused:check(n,True)
 else:check(n,False)
try:
 lib=ctypes.CDLL('libxkbcommon.so.0');lib.xkb_context_new.argtypes=[ctypes.c_int];lib.xkb_context_new.restype=ctypes.c_void_p;lib.xkb_keymap_new_from_names.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int];lib.xkb_keymap_new_from_names.restype=ctypes.c_void_p;lib.xkb_keymap_get_as_string.argtypes=[ctypes.c_void_p,ctypes.c_int];lib.xkb_keymap_get_as_string.restype=ctypes.c_void_p
 ctx=lib.xkb_context_new(0);assert ctx;keymap=lib.xkb_keymap_new_from_names(ctx,None,0);assert keymap;ptr=lib.xkb_keymap_get_as_string(keymap,1);assert ptr;data=ctypes.string_at(ptr)
 # The owning keymap callback deliberately persists size-1 bytes, no trailing NUL.
 path=OUT/'keymap.xkb';path.write_bytes(data);assert data and b'\0' not in data
 descriptor=json.loads((ROOT/'qt-domains-build-report.json').read_text());binary=descriptor['binary'];check('exact-built-binary',hashlib.sha256(Path(binary).read_bytes()).hexdigest()==descriptor['binarySHA256'])
 p=subprocess.run([binary,str(path)],capture_output=True,timeout=3);(OUT/'actual.stdout').write_bytes(p.stdout);(OUT/'actual.stderr').write_bytes(p.stderr);check('actual-size-minus-one-file-accepted',p.returncode==0)
 actual=json.loads(p.stdout);mask=actual['xkbShiftMask'];mapping=actual['mapping'];constants=actual['constants']
 check('compiled-QKeyEvent-Shift-XOR-zero-state',mapping['0']['qtModifiers']==constants['shiftModifier'])
 check('compiled-QKeyEvent-Shift-XOR-active-state',mapping[str(mask)]['qtModifiers']==0)
 check('actual-XKB-Shift-native-domain',mapping['0']['nativeScanCode']==50 and mapping['0']['nativeVirtualKey']==65505 and mapping['0']['qtKey']==constants['shiftKey'])
 calls=[]
 def row(iface,oid,method,args,direction='event'):calls.append(dict(iface=iface,id=oid,method=method,args=args,direction=direction))
 row('wl_registry',2,'bind','4, "wl_seat", 9, new id wl_seat#7','request');row('wl_seat',7,'get_keyboard','new id wl_keyboard#8','request');row('wl_keyboard',8,'enter','1, wl_surface#21, array[0]');row('wl_keyboard',8,'modifiers','1, 0, 0, 0, 0');baseline=len(calls);row('wl_keyboard',8,'key','2, 10, 42, 1');row('wl_keyboard',8,'modifiers',f'3, {mask}, 0, 0, 0');row('wl_keyboard',8,'key','4, 11, 42, 0')
 args=dict(surface_id=21,xkb_shift_mask=mask,qt_shift_mask=constants['shiftModifier'],mapping=mapping,seat_registry_id=4)
 result=keyboard.shift_pair(SimpleNamespace(calls=calls),baseline,**args);check('production-wire-order-maps-actual-Qt-events',[r['qtModifiers'] for r in result]==[constants['shiftModifier'],0])
 rejected('unrelated-seat-rejected',lambda:keyboard.shift_pair(SimpleNamespace(calls=calls),baseline,**dict(args,seat_registry_id=99)))
 for name,event in [('keyboard-retirement',dict(iface='wl_keyboard',id=8,method='release',args='',direction='request')),('seat-global-retirement',dict(iface='wl_registry',id=2,method='global_remove',args='4',direction='event'))]:
  changed=calls[:baseline]+[event]+calls[baseline:];rejected(name,lambda c=changed:keyboard.shift_pair(SimpleNamespace(calls=c),baseline,**args))
 changed=copy.deepcopy(mapping);changed['0']['nativeScanCode']=True;rejected('bool-native-domain',lambda:keyboard.shift_pair(SimpleNamespace(calls=calls),baseline,**dict(args,mapping=changed)))
 changed=copy.deepcopy(mapping);changed['0']['extra']=1;rejected('unknown-mapping-field',lambda:keyboard.shift_pair(SimpleNamespace(calls=calls),baseline,**dict(args,mapping=changed)))
 for name,raw in [('embedded-NUL',data[:10]+b'\0'+data[10:]),('empty',b''),('over-bound',b'x'*(1024*1024+1))]:
  bad=OUT/(name+'.xkb');bad.write_bytes(raw);p=subprocess.run([binary,str(bad)],capture_output=True,timeout=3);check('actual-map-file-reject-'+name,p.returncode!=0)
 report['passed']=True
finally:
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'qa/keyboard.py',ROOT/'native/qt-domains.cpp',ROOT/'qt-domains-build-report.json']};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
