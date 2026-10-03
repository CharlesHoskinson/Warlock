"""Offline system loader closure. LD_TRACE only; no browser init/GUI execution."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
scope=require_qa_scope();files={};links={};traces=[];optional=[]
def add(path):
 path=Path(path)
 if path.is_symlink():links[str(path)]=os.readlink(path);add(path.resolve())
 if path.is_file():
  files[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
  if path.resolve()!=path:add(path.resolve())
seeds=[]
for path in Path('/opt/brave-bin').rglob('*'):
 if path.is_file():
  add(path)
  with path.open('rb') as stream:
   if stream.read(4)==b'\x7fELF':seeds.append(path)
for folder in ['/usr/lib/qt6/qml','/usr/lib/qt6/plugins','/home/hoskinson/.local/share/omarchy-files-native/WindowAccessibilityV6_routing_20261001']:
 for path in Path(folder).rglob('*'):
  if path.is_file():
   add(path)
   with path.open('rb') as stream:
    used_qml=not str(path).startswith('/usr/lib/qt6/qml/') or path.relative_to('/usr/lib/qt6/qml').parts[0] in ('QtQuick','QtQml','Quickshell')
    used_plugin=not str(path).startswith('/usr/lib/qt6/plugins/') or any(part in path.parts for part in ['platforms','platformthemes','imageformats','wayland-decoration-client','wayland-graphics-integration-client','wayland-shell-integration','tls'])
    if stream.read(4)==b'\x7fELF' and used_qml and used_plugin:seeds.append(path)
for name in ['qs','wtype','unshare','bash','find','sort','head','tail','nice','ionice','du','df','mkdir','gio','stat','basename','dirname','date','readlink','realpath','hyprctl','python3']:
 path=shutil.which(name);assert path,name;add(path);seeds.append(Path(path))
for path in ['/usr/lib/libgtk-3.so.0','/usr/lib/libgtk-4.so.1']:
 add(path);seeds.append(Path(path))
for folder in ['/usr/share/fonts','/etc/fonts','/var/cache/fontconfig']:
 for path in Path(folder).rglob('*'):
  if path.is_file():add(path)
add('/usr/bin/ldd')
for path in sorted(set(seeds)):
 result=subprocess.run(['/usr/bin/ldd',str(path)],capture_output=True,text=True,env={k:v for k,v in os.environ.items() if not k.startswith('LD_')},timeout=8)
 text=result.stdout+result.stderr
 if 'not found' in text:
  if path!=Path('/opt/brave-bin/libqt5_shim.so'):raise RuntimeError('Missing loader closure:'+str(path)+'\n'+text)
  optional.append({'path':str(path),'trace':text,'classification':'Distributed optional Qt5 shim; no Qt5 fixture. Actual runtime module load must fail acceptance.'})
 paths=re.findall(r'(?:=>\s*)?(/[^\s()]+)',text)
 for dep in paths:
  if Path(dep).is_file():add(dep)
 traces.append({'path':str(path),'returncode':result.returncode,'trace':text,'traceOnly':True})
record={'result':'pass','scope':scope,'files':files,'symlinks':links,'loaderTraces':traces,'executedBrowser':False,'executedGui':False,'method':'glibc ldd LD_TRACE_LOADED_OBJECTS (before program initialization) plus complete browser resources/Qt QML/plugins and exact helper binaries','dynamicLoadedModuleVerificationPending':True,'optionalUnselectedMissingModules':optional}
with (B/'loader-closure.json').open('x') as handle:json.dump(record,handle,indent=2)
print(json.dumps({'result':'pass','files':len(files),'symlinks':len(links),'traces':len(traces),'executedBrowser':False}))
