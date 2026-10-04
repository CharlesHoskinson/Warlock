"""Original293 reconnect assertions/deadlines against current626 source/634 fixture."""
import ast,hashlib,json,resource,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sys.path.insert(0,str(ROOT/'qa'));from closure import verify_current,verify_profiles
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=REPO/'implementation/elm-responsive-reconnect-v293';a=ast.parse((old/'qa/native.py').read_text());b=ast.parse((ROOT/'qa/native.py').read_text())
def dump(n):return ast.dump(n,include_attributes=False)
def calls(t,name):return [dump(n) for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==name]
for name in ('check','wait'):assert calls(a,name)==calls(b,name),name
for name in ('check','wait','click','keys','right'):
 x=next(n for n in ast.walk(a) if isinstance(n,ast.FunctionDef) and n.name==name);y=next(n for n in ast.walk(b) if isinstance(n,ast.FunctionDef) and n.name==name);assert dump(x)==dump(y),name
for name in ('fixture.py','qa/inspection.py','qa/grab_guard.py','qa/sampling.py'):assert sha(ROOT/name)==sha(old/name)
code=(ROOT/'qa/native.py').read_text();assert 'xwayland={enabled=false}' in code and 'Unchanged observation deadline' in code and "'--backend',str(RELAY)" in code and "if loaded:s.guard();assert s.ctl('plugin','unload',plugin).strip()=='ok'" in code
pins=verify_current(ROOT);profiles=verify_profiles(ROOT);pins.update(profiles['profileConfigSHA256'])
for p in [*sorted((ROOT/'qa').glob('*.py')),ROOT/'fixture.py',Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer'),Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard'),Path('/usr/bin/grim'),Path('/usr/bin/magick')]:pins[str(p.resolve())]=sha(p)
out=ROOT/'qa/preflight.json';assert not out.exists();out.write_text(json.dumps({'passed':True,'source':str(REPO/'implementation/elm-focus-recovery-integrated-gui-v333'),'runtime':str(REPO/'implementation/elm-grant-retirement-runtime-v595'),'inputs':pins,'originalCheckCallCount':len(calls(a,'check')),'profiles':profiles,'claim':'Source/oracle/ABI/profile closure only; original57 native reconnect acceptance remains pending','mainDesktopActions':False},indent=2)+'\n');print(out)
