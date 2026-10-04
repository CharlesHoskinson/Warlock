"""Parse staged wiring and verify the prospective systemd unit without activating."""
import ast,json,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();B=Path(__file__).resolve().parent;r=json.loads((B/'activation-ready.json').read_text())
ast.parse((Path(r['package'])/'launch').read_text());ast.parse((B/'apply_activation.py').read_text())
lua=subprocess.run(['/usr/bin/lua','-e','assert(loadfile('+json.dumps(str(B/'activation/autostart.lua'))+'))'],capture_output=True,text=True,timeout=5)
if lua.returncode:raise RuntimeError(lua.stderr)
with tempfile.TemporaryDirectory(prefix='stack-unit-') as d:
 p=Path(d)/'wayland-wm@hyprland.desktop.service';p.write_text(Path('/usr/lib/systemd/user/wayland-wm@.service').read_text()+'\n'+(B/'activation/60-floating-max-stack.conf').read_text())
 check=subprocess.run(['systemd-analyze','--user','verify',str(p)],capture_output=True,text=True,timeout=15)
 if check.returncode:raise RuntimeError(check.stderr)
report={'result':'pass','scope':scope,'pythonSyntax':True,'luaSyntax':True,'unitVerified':True,'enabled':False,'restartPerformed':False};(B/'activation-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
