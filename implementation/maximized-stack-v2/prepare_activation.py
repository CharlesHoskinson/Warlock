"""Prepare a verified user-owned native pair and reviewable next-session wiring."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();B=Path(__file__).resolve().parent;home=Path.home()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pair=json.loads((B/'PAIR_READY.json').read_text());assert pair['result']=='pass'
smokes=sorted(B.glob('native-stack-smoke-*.json'));proof=json.loads(smokes[-1].read_text());assert proof['result']=='pass' and not proof.get('error') and all(proof['checks'].values())
full=json.loads(Path(pair['plugin']['full_report']).read_text())
for p,h in full['compiler_dependency_headers'].items():assert sha(p)==h,p
package=home/'.local/share/omarchy-native-pairs/floating-max-stack-v2'
if package.exists():raise RuntimeError('Prepared package already exists')
package.mkdir(mode=0o700,parents=True)
for key,name in [(pair,'Hyprland'),(pair['plugin'],'hyprbars.so')]:
 assert sha(key['binary'])==key['sha256']
 shutil.copy2(key['binary'],package/name);(package/name).chmod(0o755);assert sha(package/name)==key['sha256']
record={'core':str(package/'Hyprland'),'coreSHA256':pair['sha256'],'plugin':str(package/'hyprbars.so'),'pluginSHA256':pair['plugin']['sha256']}
(package/'pair.json').write_text(json.dumps(record,indent=2)+'\n');(package/'pair.json').chmod(0o600)
launcher='''#!/usr/bin/python3
import hashlib,json,os,sys
from pathlib import Path
p=Path(__file__).resolve().parent;r=json.loads((p/'pair.json').read_text())
for path,key in [(r['core'],'coreSHA256'),(r['plugin'],'pluginSHA256')]:
 if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=r[key]:raise SystemExit('Native pair changed; restore original session wiring before login')
os.environ['HYPR_WINDOW_STACK_PLUGIN']=r['plugin']
os.execv('/usr/bin/start-hyprland',['start-hyprland','--path',r['core'],'--',*sys.argv[1:]])
'''
(package/'launch').write_text(launcher);(package/'launch').chmod(0o755)
stage=B/'activation';stage.mkdir(mode=0o700)
source=home/'.config/hypr/autostart.lua'
old=source.read_text();needle='p="$HOME/.local/lib/libhyprbars-controls-v18.so"'
assert old.count(needle)==1
(stage/'autostart.lua').write_text(old.replace(needle,'p="${HYPR_WINDOW_STACK_PLUGIN:-$HOME/.local/lib/libhyprbars-controls-v18.so}"'))
(stage/'60-floating-max-stack.conf').write_text('[Service]\nExecStart=\nExecStart=/usr/bin/uwsm aux exec -- '+str(package/'launch')+'\n')
report={'scope':scope,'prepared':True,'enabled':False,'restartPerformed':False,'package':str(package),
 'proof':str(smokes[-1]),'autostartOriginalSHA256':sha(source),'autostartCandidateSHA256':sha(stage/'autostart.lua'),
 'files':{str(p):sha(p) for p in package.iterdir() if p.is_file()},'unit':'wayland-wm@hyprland.desktop.service',
 'stagedUnitSHA256':sha(stage/'60-floating-max-stack.conf'),'remainingGate':'Apply wiring then logout/restart closes current applications; requires explicit user agreement'}
(B/'activation-ready.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
