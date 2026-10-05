"""Read-only installed Omarchy vocabulary and effective binding inventory."""
import datetime,hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parent
assert not (ROOT/'inventory.json').exists(), 'Use a fresh version for a new observation'
rows=[]
def observe(name,argv):
 p=subprocess.run(argv,capture_output=True,timeout=30,check=True)
 assert not p.stderr,p.stderr.decode()
 path=ROOT/name;path.write_bytes(p.stdout)
 rows.append({'argv':argv,'exitCode':p.returncode,'file':name,'sha256':hashlib.sha256(p.stdout).hexdigest()})
 return p.stdout
commands=json.loads(observe('commands.json',['omarchy','commands','--json','--all']))
bindings=json.loads(observe('effective-bindings.json',['hyprctl','-j','binds']))
observe('keybindings.txt',['omarchy','menu','keybindings','--print'])
assert commands['ok'] and commands['commands'] and bindings
sources=[]
paths=[pathlib.Path('/usr/share/omarchy/default/hypr')/name for name in ['bootstrap.lua','omarchy.lua','helpers.lua','bindings.lua','require_optional.lua','require_all.lua','paths.lua']]
paths+=sorted(pathlib.Path('/usr/share/omarchy/default/hypr/bindings').rglob('*.lua'))
paths+=[pathlib.Path('/home/hoskinson/.config/hypr')/name for name in ['hyprland.lua','bindings.lua','snap.lua','pin.lua']]
for p in paths:
 data=p.read_bytes();relative=('user/' if str(p).startswith('/home/') else 'packaged/')+p.name
 if '/bindings/' in str(p):relative='packaged/bindings/'+p.name
 target=ROOT/'sources'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 sources.append({'path':str(p),'snapshot':str(target.relative_to(ROOT)),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
 routes=commands['commands']
 summary={'schema':1,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Read-only live Omarchy vocabulary, effective Hyprland bindings and binding source; not Warlock native acceptance','commandCount':len(routes),'effectiveBindingCount':len(bindings),'hiddenCommandsIncluded':True,'observations':rows,'sources':sources,'warnings':['Hyprland __lua arg values are runtime callback IDs, never portable command targets. Preserve Lua source semantics and prove action routing on the owning release tuple.','User overrides take precedence over packaged defaults; effective order and binding flags must remain intact.'],'productCompatibilityQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False}
(ROOT/'inventory.json').write_text(json.dumps(summary,indent=2)+'\n')
keywords=sorted({word for row in routes for route in row.get('routes',[row['route']]) for word in route.split()})
(ROOT/'keywords.json').write_text(json.dumps({'keywords':keywords,'commands':[{k:row.get(k) for k in ['route','binary','summary','args','aliases','routes','hidden','requires_sudo']} for row in routes]},indent=2)+'\n')
print(json.dumps({'commands':len(routes),'effectiveBindings':len(bindings),'sourceFiles':len(sources),'keywords':len(keywords)}))
