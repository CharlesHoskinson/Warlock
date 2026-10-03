"""CPU-only canonical map/driver/shim build, per-TU headers and ELF closure."""
from pathlib import Path
import subprocess,json,hashlib,os,re,stat,time
B=Path(__file__).resolve().parent
sysroot=Path('/usr/share/X11/xkb')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
commands=[]
def run(cmd):
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=60,cwd=B);commands.append(dict(command=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr;return p.stdout
before={str(p):sha(p)for p in B.glob('physical*')if p.suffix in {'.c','.h','.inc'}}
run(['/usr/bin/cc','-std=c11','-Wall','-Wextra','-Werror','-O2','physical_map_generator.c','-o','physical-map-generator','-lxkbcommon'])
temporary=B/'physical-keymap-regenerated.tmp';assert not temporary.exists();run([str(B/'physical-map-generator'),str(temporary)]);assert temporary.read_bytes()==(B/'physical_keymap.inc').read_bytes(),'Materialized full map changed';temporary.unlink()
run(['/usr/bin/cc','-std=c11','-Wall','-Wextra','-Werror','-O2','physical_keyboard.c','physical_plan.c','virtual-keyboard-protocol.c','-o','physical-keyboard','-lwayland-client','-lxkbcommon','-lcrypto'])
run(['/usr/bin/cc','-std=c11','-Wall','-Wextra','-Werror','-O2','physical_keyboard.c','physical_plan.c','virtual-keyboard-protocol.c','physical_protocol_cpu.c','-o','physical-protocol-cpu','-lwayland-client','-lxkbcommon','-lcrypto'])
files={};links={}
def add(p):
 p=Path(p)
 if p.is_symlink():links[str(p)]=os.readlink(p);add(p.resolve())
 if p.is_file():files[str(p)]={'path':str(p),'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)}
 if p.resolve()!=p:add(p.resolve())
for source in ['physical_keyboard.c','physical_plan.c','physical_map_generator.c','physical_protocol_cpu.c','virtual-keyboard-protocol.c']:
 text=run(['/usr/bin/cc','-std=c11','-M',source]);tokens=text.replace('\\\n',' ').split(':',1)[1].split();deps=[]
 for token in tokens:
  p=Path(token);p=p if p.is_absolute()else B/p;add(p);deps.append(str(p))
 (B/(source+'.dependencies.json')).write_text(json.dumps(deps,indent=2)+'\n')
for p in sysroot.rglob('*'):
 if p.is_file():add(p)
for p in ['/usr/bin/cc','/usr/bin/ldd']:add(p)
for name in ['physical-map-generator','physical-keyboard','physical-protocol-cpu']:
 p=B/name;add(p);text=run(['/usr/bin/ldd',str(p)]);assert 'not found'not in text
 for path in re.findall(r'(?:=>\s*)?(/[^\s()]+)',text):
  if Path(path).is_file():add(path)
after={str(p):sha(p)for p in B.glob('physical*')if p.suffix in {'.c','.h','.inc'}}
assert before==after
r=dict(result='pass',commands=commands,dependencies=list(files.values()),symlinks=[{'path':p,'target':v}for p,v in sorted(links.items())],perTranslationUnitHeaders=True,completeExpandedMapGeneratorSourceTreePinned=True,sourceUnchanged=True,nativeExecuted=False,mainWrites=False,binaries={n:sha(B/n)for n in ['physical-map-generator','physical-keyboard','physical-protocol-cpu']});(B/'physical-build-report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k not in {'commands','dependencies','symlinks'}}))
