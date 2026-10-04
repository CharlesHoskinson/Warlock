"""Protected system-Python dependency and executable PNG preflight; no GUI."""
import ast,binascii,hashlib,importlib,importlib.util,json,pathlib,struct,sys,tempfile,time,zlib
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];PARENT=ROOT.parent/'elm-uncertainty-layout-review-v662'
sys.path.insert(0,str(ROOT/'qa'));from png_inspection import inspect_png,PNGError
OUT=ROOT/'qa'/('dependencies-'+str(time.time_ns()));OUT.mkdir();checks=[]
def digest(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def refused(name,data):
 p=OUT/(name+'.png');p.write_bytes(data)
 try:inspect_png(p)
 except PNGError:check(name,True);return
 raise AssertionError(name+' not refused')
check('exact_system_python',sys.executable=='/usr/bin/python3')
import gi
gi.require_foreign('cairo');gi.require_version('Gtk','3.0');gi.require_version('WebKit2','4.1')
from gi.repository import Gtk,WebKit2,GLib,Gio
import cairo
check('actual_installed_webkit_snapshot_api',all(hasattr(WebKit2.WebView,x) for x in ['evaluate_javascript','evaluate_javascript_finish','get_snapshot','get_snapshot_finish']))
check('actual_installed_cairo_png_export',hasattr(cairo.ImageSurface,'write_to_png'))
for script in ['native.py','webkit_fixture.py']:
 source=(ROOT/'qa'/script).read_text();ast.parse(source)
 for node in ast.walk(ast.parse(source)):
  if isinstance(node,ast.Import):
   for alias in node.names:importlib.import_module(alias.name)
  elif isinstance(node,ast.ImportFrom):importlib.import_module(node.module)
 check('all_direct_imports_available_'+script,True)
check('fixture_byte_exact662',digest(ROOT/'qa/webkit_fixture.py')==digest(PARENT/'qa/webkit_fixture.py'))
# Explicit AST equality of the entire six-second wait implementation and LUA.
def named(source,name):return next(n for n in ast.walk(ast.parse(source)) if isinstance(n,ast.FunctionDef) and n.name==name)
parent=(PARENT/'qa/native.py').read_text();current=(ROOT/'qa/native.py').read_text()
check('six_second_wait_byte_structure_preserved',ast.dump(named(parent,'wait'))==ast.dump(named(current,'wait')))
def assignment(source,name):return next(n.value for n in ast.walk(ast.parse(source)) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
check('original_native_geometry_preserved',ast.dump(assignment(parent,'LUA'))==ast.dump(assignment(current,'LUA')))
check('original_pixel_oracle_identity_preserved',':actual_native_pixel_dimensions_and_rendered_colors' in current and "picture['distinctColors']>8" in current)
check('no_unprovided_PIL_dependency','PIL' not in current)
def chunk(kind,body):return struct.pack('>I',len(body))+kind+body+struct.pack('>I',binascii.crc32(kind+body)&0xffffffff)
def png(width,height,raw,channels=3,**kw):
 header=struct.pack('>IIBBBBB',width,height,kw.get('bits',8),2 if channels==3 else 6,0,0,kw.get('interlace',0))
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',header)+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
def predictor(mode,left,up,corner):
 p=left+up-corner;dist=[abs(p-left),abs(p-up),abs(p-corner)]
 return [0,left,up,(left+up)//2,[left,up,corner][dist.index(min(dist))]][mode]
for channels in [3,4]:
 for mode in range(5):
  width=8;height=8;previous=bytes(width*channels);raw=b''
  for y in range(height):
   row=bytes(v for x in range(width) for v in ([x*27,y*25,(x+y)*13]+([x*31] if channels==4 else [])))
   encoded=bytes((v-predictor(mode,row[i-channels] if i>=channels else 0,previous[i],previous[i-channels] if i>=channels else 0))&255 for i,v in enumerate(row));raw+=bytes([mode])+encoded;previous=row
  p=OUT/f'filter-{channels}-{mode}.png';p.write_bytes(png(width,height,raw,channels));image=inspect_png(p)
  check(f'actual_png_all_filters_{channels}_{mode}',image['width']==8 and image['height']==8 and image['distinctColors']==64 and image['decodedPixels']==64)
# Independent installed cairo export exercises actual snapshot producer format.
surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,16,16);context=cairo.Context(surface)
for y in range(16):
 for x in range(16):context.set_source_rgba(x/15,y/15,(x+y)/30,1);context.rectangle(x,y,1,1);context.fill()
cp=OUT/'actual-cairo-export.png';surface.write_to_png(str(cp));image=inspect_png(cp)
check('genuine_cairo_decoded_pixels',image['width']==16 and image['height']==16 and image['distinctColors']>8)
valid=cp.read_bytes();refused('truncated_png',valid[:-1]);refused('trailing_png',valid+b'x');refused('crc_changed_png',valid[:30]+bytes([valid[30]^1])+valid[31:]);refused('wrong_signature',b'not a PNG')
refused('unsupported_16bit',png(1,1,b'\0\0\0\0',bits=16));refused('unsupported_interlace',png(1,1,b'\0\0\0\0',interlace=1));refused('unknown_filter',png(1,1,b'\5\0\0\0'));refused('decompressed_size_bomb',png(1,1,b'\0'*10000));refused('pixel_bound',png(2048,2048,b''));refused('zero_dimension',png(0,1,b''))
check('flat_png_true_color_count',inspect_png((OUT/'filter-3-0.png'))['distinctColors']>8)
constant=OUT/'one-color.png';constant.write_bytes(png(8,8,b''.join(b'\0'+b'\x10\x20\x30'*8 for _ in range(8))));check('one_color_negative_oracle',inspect_png(constant)['distinctColors']==1)
pins={sys.executable:digest(sys.executable)}
for line in pathlib.Path('/proc/self/maps').read_text().splitlines():
 path=line.split(maxsplit=5)[-1]
 if path.startswith('/') and pathlib.Path(path).is_file():pins[path]=digest(path)
keys=pathlib.Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard');check('native_keyboard_helper_available',keys.is_file());pins[str(keys)]=digest(keys)
report={'passed':True,'checks':checks,'assertions':len(checks),'dependencyPins':pins,'nativeExecuted':False,'sourceSHA256':{str(p.relative_to(ROOT)):digest(p) for p in (ROOT/'qa').glob('*.py')},'PNGInspection':'stdlib PNG CRC/exact inflate/all row filters/genuine decoded RGB colors','WebKitVersion':[WebKit2.get_major_version(),WebKit2.get_minor_version(),WebKit2.get_micro_version()]}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'qa/current-dependencies.json').write_text(json.dumps({'report':str(OUT/'report.json'),'sha256':digest(OUT/'report.json')},indent=2)+'\n');print(OUT/'report.json')
