"""Actual source/CPU/formal stage verification, never GUI/native module loading."""
from pathlib import Path
import hashlib,json,os,subprocess,time,re
B=Path(__file__).resolve().parent;N=B/'native-candidate';QA=Path('/home/hoskinson/window-integration-qa/pin-native-qa-v1')
sources=[p for root in (B,QA)for p in root.rglob('*') if p.is_file()and not p.is_symlink()and p.suffix in ('.py','.cpp','.hpp','.h','.c','.qml','.js','.qnt','.lua','.md')and '__pycache__'not in p.parts]
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in sources};commands=[]
for source,exe in [(B/'test_pin_stacking.cpp',B/'test-pin-stacking'),(B/'test_pin_boundary.cpp',B/'test-pin-boundary'),(B/'test_pin_lifetime.cpp',B/'test-pin-lifetime'),(N/'test_pin_action.cpp',N/'test-pin-action')]:
 extra=['-ljson-c']if source.name=='test_pin_lifetime.cpp'else[]
 commands.extend([['/usr/bin/g++','-std=c++23','-Wall','-Wextra','-Werror','-pedantic',str(source),'-o',str(exe),*extra],[str(exe)]])
flags=subprocess.check_output(['pkg-config','--cflags','--libs','Qt6Core','Qt6Qml'],text=True).split()
commands.extend([['/usr/bin/g++','-std=c++23',str(B/'frontend/test_pin_menu.cpp'),'-o',str(B/'frontend/test-pin-menu'),*flags],[str(B/'frontend/test-pin-menu'),str(B/'frontend/widget_v66/PinMenu.js'),str(B/'frontend/test_pin_menu.js')]])
for source in [B/'frontend/test_capture.py',B/'frontend/test_pin_config.py',B/'pin-helper-v1/test_helper.py',B/'keyboard-chords/test_chord_keyboard.py',QA/'test_case_authority.py',QA/'test_native_trace.py']:
 commands.append(['/usr/bin/python3',str(source)])
models=[(B,'pin_action'),(B,'pin_transport'),(B,'pin_stacking'),(B,'pin_frontend'),(B,'pin_exception'),(B,'pin_capture'),(B,'stable_representation'),(B,'pin_focus'),(B,'pin_titlebar'),(B/'pin-helper-v1','helper_boundary'),(B/'pin-helper-v1','receipt_projection'),(B/'keyboard-chords','chord'),(B/'keyboard-chords','physical_owner'),(QA,'pin_case'),(Path('/home/hoskinson/window-integration-qa/browser-files-flow-v20'),'pointer_syntax')]
for folder,name in models:
 model=folder/(name+'.qnt');test=folder/(name+'_test.qnt');commands.extend([['quint','test',str(test if test.exists()else model)],['quint','run',str(model),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']])
rows=[]
for command in commands:
 r=subprocess.run(command,cwd=B,capture_output=True,text=True,timeout=120)
 rows.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));print(json.dumps(dict(command=command[:3],returncode=r.returncode)),flush=True)
 if r.returncode:break
ok=len(rows)==len(commands)and all(r['returncode']==0 for r in rows)
report=dict(result='pass'if ok else'fail',commands=rows,plannedCommands=len(commands),sourceSHA256=before,sourceUnchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in before.items()),nativeGUIExecuted=False,nativeModuleLoaded=False,mainWrites=False,models=len(models),namedTests=sum(sum(map(int,re.findall(r'(\d+) passing',r['stdout'])))for r in rows),CPUAssertions=sum(sum(map(int,re.findall(r'(\d+) .*assertions PASS',r['stdout'])))for r in rows))
destination=B/('offline-final-report.json'if ok else f'offline-final-failure-{time.time_ns()}.json');destination.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(result=report['result'],artifact=str(destination),sourceUnchanged=report['sourceUnchanged'],namedTests=report['namedTests'],models=report['models'],commands=len(rows))));raise SystemExit(not ok or not report['sourceUnchanged'])
