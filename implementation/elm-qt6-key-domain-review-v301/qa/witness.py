"""Actual old compiled Qt converter on exact callback file semantics; no display."""
import ctypes,hashlib,importlib.util,json,os,resource,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('witness-'+str(time.time_ns()));OUT.mkdir();checks=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'checks':checks,'inputs':{str(p):sha(p) for p in (ROOT/'inputs').rglob('*') if p.is_file()}}
try:
 desc=json.loads((ROOT/'inputs/qt-domains-build-report.json').read_text());assert sha(desc['binary'])==desc['binarySHA256'];report['binary']=desc
 lib=ctypes.CDLL('/usr/lib/libxkbcommon.so.0');report['xkbLibrarySHA256']=sha('/usr/lib/libxkbcommon.so.0')
 lib.xkb_context_new.argtypes=[ctypes.c_int];lib.xkb_context_new.restype=ctypes.c_void_p
 lib.xkb_keymap_new_from_names.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int];lib.xkb_keymap_new_from_names.restype=ctypes.c_void_p
 lib.xkb_keymap_get_as_string.argtypes=[ctypes.c_void_p,ctypes.c_int];lib.xkb_keymap_get_as_string.restype=ctypes.c_void_p
 lib.xkb_keymap_unref.argtypes=[ctypes.c_void_p];lib.xkb_context_unref.argtypes=[ctypes.c_void_p]
 ctx=lib.xkb_context_new(0);assert ctx;keymap=lib.xkb_keymap_new_from_names(ctx,None,0);assert keymap
 ptr=lib.xkb_keymap_get_as_string(keymap,1);assert ptr;raw=ctypes.string_at(ptr);assert raw and not raw.endswith(b'\0')
 libc=ctypes.CDLL(None);libc.free.argtypes=[ctypes.c_void_p];libc.free(ptr);lib.xkb_keymap_unref(keymap);lib.xkb_context_unref(ctx)
 path=OUT/'actual-size-minus-one.xkb';path.write_bytes(raw)
 r=subprocess.run([desc['binary'],str(path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=3);(OUT/'stdout').write_bytes(r.stdout);(OUT/'stderr').write_bytes(r.stderr);assert r.returncode==3
 checks.append({'name':'actual compiled old converter rejects exact valid callback file bytes','passed':True,'exitCode':r.returncode,'fileSHA256':sha(path),'size':len(raw)})
 # Same actual map plus transport terminator shows the failure is the file contract.
 nul=OUT/'same-map-plus-nul.xkb';nul.write_bytes(raw+b'\0');r=subprocess.run([desc['binary'],str(nul)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=3);(OUT/'nul.stdout').write_bytes(r.stdout);(OUT/'nul.stderr').write_bytes(r.stderr);assert r.returncode==0
 mapping=json.loads(r.stdout);assert mapping['qtVersion']=='6.11.2' and mapping['mapping'];checks.append({'name':'same actual map plus NUL converts using actual Qt installed code','passed':True,'exitCode':r.returncode,'mapping':mapping})
 spec=importlib.util.spec_from_file_location('oldkeyboard',ROOT/'inputs/qa/keyboard.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 from types import SimpleNamespace
 mask=mapping['xkbShiftMask'];table=mapping['mapping']
 # Old consumer entirely ignores actual registry/seat acquisition provenance.
 calls=[{'iface':'wl_registry','id':1,'direction':'request','method':'bind','args':'99, "wl_seat", 7, new id wl_seat@8'}, {'iface':'wl_seat','id':8,'direction':'request','method':'get_keyboard','args':'new id wl_keyboard@9'}, {'iface':'wl_keyboard','id':9,'direction':'event','method':'enter','args':'1, wl_surface@42, array[0]'}, {'iface':'wl_keyboard','id':9,'direction':'event','method':'modifiers','args':'2, 0, 0, 0, 0'}, {'iface':'wl_keyboard','id':9,'direction':'event','method':'key','args':'3, 10, 42, 1'}, {'iface':'wl_keyboard','id':9,'direction':'event','method':'key','args':'4, 11, 42, 0'}]
 value=m.shift_pair(SimpleNamespace(calls=calls),4,surface_id=42,xkb_shift_mask=mask,qt_shift_mask=mapping['constants']['shiftModifier'],mapping=table);assert len(value)==2
 checks.append({'name':'predecessor accepts selected keyboard on uncorrelated registry seat99','passed':True,'accepted':value,'scope':'synthetic valid-domain helper witness; no native seat acquisition claim'})
 report['passed']=True
finally:
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'checks':len(checks)}))
