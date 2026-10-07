"""Rebind the retained real lost-receipt/restart scenario to GUI143/core16.

Only storage/wire-schema observers and private-host packaging are adapted.
The pointer, keyboard, pixels, original six-second clocks and actual native
Restart sequence remain required. This is the main window-command route;
it does not qualify the separate controlled-preview route.
"""
import ast
import hashlib
import json
import pathlib
import resource
import shutil
import sys

sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
repo = pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent = repo / 'implementation/warlock-client-provider-native-v194'
root = repo / 'implementation/warlock-client-provider-native-v195'
original = repo / 'implementation/elm-restore-lost-native-v230'
old_supervisor = repo / 'implementation/elm-disappearance-supervisor-v229'
supervisor = repo / 'implementation/warlock-window-restart-supervisor-v1'
sha = lambda path: hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
assert not root.exists() and not supervisor.exists()
pre = json.loads((parent / 'qa/preflight.json').read_text())
assert pre['passed'] and not pre['nativeLaunched']
for path, digest in pre['inputs'].items():
    assert sha(path) == digest, path
build_path = pathlib.Path(pre['controlledHostBuild'])
build = json.loads(build_path.read_text())
assert build['passed'] and len(build['commands']) == 119
assert sha(build_path.parent / 'elm-host') == build['binarySHA256']
root.mkdir(mode=0o700)
(root / 'qa').mkdir(mode=0o700)
supervisor.mkdir(mode=0o700)
origins = {}
def copy(source, target):
    shutil.copy2(source, target)
    origins[str(source)] = sha(source)
for path in parent.iterdir():
    if path.is_file() and path.name not in {'component-manifest.json', 'ANCESTRY.json'}:
        copy(path, root / path.name)
for name in ['session_bus.py', 'system_isolation.py', 'isolation.py']:
    copy(parent / 'qa' / name, root / 'qa' / name)
copy(original / 'fixture.py', root / 'fixture.py')
for name in ['inspection.py', 'sampling.py']:
    copy(original / 'qa' / name, root / 'qa' / name)
for name in ['supervisor.py', 'cohort.py']:
    copy(old_supervisor / name, supervisor / name)
runtime_files = {pre['controlledHostBinary']: sha(pre['controlledHostBinary'])}
for directory in [pathlib.Path(pre['controlledHostAssets']), pathlib.Path(pre['controlledHostBackend']).parent]:
    for path in directory.iterdir():
        assert path.is_file() and not path.is_symlink()
        runtime_files[str(path)] = sha(path)
for name in ['supervisor.py', 'cohort.py']:
    runtime_files[str(supervisor / name)] = sha(supervisor / name)
manifest = {'schema': 1, 'scope': 'GUI143 main window-command lost receipt and explicit whole-host restart; controlled preview/full release open',
            'host': pre['controlledHostBinary'], 'assets': pre['controlledHostAssets'],
            'backend': pre['controlledHostBackend'], 'coreSHA256': pre['pair']['core']['sha256'], 'files': runtime_files}
(supervisor / 'runtime-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
source = (original / 'qa/native.py').read_text()
origins[str(original / 'qa/native.py')] = sha(original / 'qa/native.py')
def replace(old, new):
    global source
    assert source.count(old) == 1, old
    source = source.replace(old, new)
replace("CORE=REPO/'implementation/elm-grab-safe-background-v89';GUI=REPO/'implementation/elm-before-write-fault-v211'", "CORE=ROOT;GUI=REPO/'implementation/warlock-preview-provider-v143'")
replace("host.original.qa.require_qa_scope()", "host.original.qa.require_qa_scope()\nsys.path.insert(0,str(ROOT/'qa'))\nfrom session_bus import isolate_session_host\nfrom system_isolation import supply,validate\nisolate_session_host(host)\npre=json.loads((ROOT/'qa/preflight.json').read_text())\nassert pre['passed'] and not pre['nativeLaunched']\nfor path,digest in pre['inputs'].items():assert host.digest(path)==digest,path")
replace("SUP=REPO/'implementation/elm-disappearance-supervisor-v229'", "SUP=REPO/'implementation/warlock-window-restart-supervisor-v1'")
replace("build_path=sorted((GUI/'qa').glob('build-*/report.json'))[-1]", "build_path=Path(pre['controlledHostBuild'])")
replace("manifest=json.loads((CORE/'qa/build-pair-manifest.json').read_text());assert manifest['passed']\n for relative,digest in manifest['files'].items():assert host.digest(CORE/relative)==digest,relative\n pair=manifest['nativePair']", "pair=pre['pair']")
replace("env=dict(s.env,GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0',WAYLAND_DEBUG='client')", "env=supply(s.env,s.host.runtime);validate(env,s.host.runtime)\n   env.update(GTK_A11Y='none',NO_AT_BRIDGE='1',GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0',WAYLAND_DEBUG='client')")
replace("recovery_dir=Path(config['runtime'])/'elm-window-recovery'", "attached=next(f for f in reversed(frames('backend-frame: ')) if f['kind']=='attached')\n   recovery_dir=Path(config['runtime'])/'elm-window-recovery'/config['instance']/attached['binding']['lifetime']\n   def admission_path(request):\n    b=request['binding'];i=request['intent'];c=i['context']\n    values=[b[k] for k in ['lifetime','session','frontend']]+[request['effectProtocol']]+[i[k] for k in ['request','generation','incarnation','operation']]+[c[k] for k in ['lifetime','epoch','output','revision']]\n    import hashlib\n    key=hashlib.sha256(json.dumps(values,separators=(',',':')).encode()).hexdigest()\n    return recovery_dir/'admissions-v1'/(key+'.json')")
replace("admitted=json.loads((recovery_dir/'host-intent.json').read_text())", "admitted=json.loads(admission_path(old_request).read_text())")
replace("record_path=Path(config['runtime'])/'elm-window-recovery/host-intent.json'", "record_path=admission_path(old_request)")
replace("f.get('kind')=='host-uncertain'", "f.get('kind')=='host-reservation-unknown' and f.get('record',{}).get('intent')==old_request['intent']")
replace("uncertain['binding']==fresh_binding and uncertain['intent']==old_request['intent']", "uncertain['binding']==fresh_binding and uncertain['record']['binding']==old_binding and uncertain['record']['intent']==old_request['intent'] and uncertain['record']['status']=='Pending'")
# Preserve historical check identities. Every short-lived helper now has a
# registered PID/start and a separately recorded, actually waited exit status.
replace("def check(name,value,**evidence):", "helper_sequence=0\ndef owned_helper(command,**kwargs):\n global helper_sequence\n helper_sequence+=1\n input_text=kwargs.pop('input',None);timeout=kwargs.pop('timeout',5);env=kwargs.pop('env',s.env)\n check_required=kwargs.pop('check',False);kwargs.pop('capture_output',None);kwargs.pop('text',None);assert not kwargs,kwargs\n name='restart-helper-'+str(helper_sequence)\n proc=s.host.launch(name,command,env=env)\n try:\n  if input_text is not None:\n   raise RuntimeError('Helper stdin must use registered pipe launch')\n  proc.wait(timeout=timeout)\n except BaseException:\n  if proc.poll() is None:\n   owned=next(row for p,row in s.host.processes if p is proc);s.host.stop(owned,proc);proc.wait(timeout=5)\n  raise\n result=subprocess.CompletedProcess(command,proc.returncode,'','')\n report.setdefault('ownedHelperExits',[]).append({'name':name,'pid':proc.pid,'exitCode':proc.returncode,'expected':0})\n if check_required:assert proc.returncode==0,name\n return result\ndef check(name,value,**evidence):")
# The legacy host launch opens stdout/stderr logs itself; input helpers require
# their original stdin pipe. Register them through the host then use communicate.
replace("proc=s.host.launch(name,command,env=env)\n try:\n  if input_text is not None:\n   raise RuntimeError('Helper stdin must use registered pipe launch')\n  proc.wait(timeout=timeout)", "if input_text is None:\n  proc=s.host.launch(name,command,env=env)\n else:\n  proc=s.host.launch(name,['/usr/bin/python3','-B',str(ROOT/'qa/input_helper.py'),str(ROOT/'qa/helper-input-'+str(helper_sequence)),*command],env=env)\n try:\n  proc.wait(timeout=timeout)")
# A sealed input file feeds the exact original command without shell parsing.
replace("name='restart-helper-'+str(helper_sequence)\n if input_text", "name='restart-helper-'+str(helper_sequence)\n if input_text is not None:\n  p=ROOT/'qa'/('helper-input-'+str(helper_sequence));fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)\n  with os.fdopen(fd,'w') as stream:stream.write(input_text)\n if input_text")
source = source.replace('subprocess.run(', 'owned_helper(')
source = source.replace("'checks':[],'mainDesktopActions':False", "'checks':[],'mainDesktopActions':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'controlledPreviewRecoveryQualified':False")
replace("report['passed']=True", "check('allRegisteredShortLivedHelpersWaitedNormalExit',all(row['exitCode']==0 for row in report['ownedHelperExits']),exits=report['ownedHelperExits'])\n   report['passed']=True")
ast.parse(source)
(root / 'qa/native-window-restart.py').write_text(source)
helper = '''"""Feed sealed QA input to the exact pointer/keyboard command; retain exit."""
import os,sys,stat
from pathlib import Path
path=Path(sys.argv[1]);info=path.lstat()
assert stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid() and stat.S_IMODE(info.st_mode)==0o600 and info.st_nlink==1
fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW);os.dup2(fd,0);os.close(fd)
os.execv(sys.argv[2],sys.argv[2:])
'''
ast.parse(helper)
(root / 'qa/input_helper.py').write_text(helper)
inputs = dict(pre['inputs'])
inputs.update(origins)
inputs.update(runtime_files)
inputs[str(supervisor / 'runtime-manifest.json')] = sha(supervisor / 'runtime-manifest.json')
for base in [root, root / 'qa']:
    for path in base.iterdir():
        if path.is_file():
            inputs[str(path)] = sha(path)
inputs[str(pathlib.Path(__file__))] = sha(__file__)
pre.update(inputs=inputs, scope=manifest['scope'], retainedScenario=str(original / 'qa/native.py'), supervisorManifest=str(supervisor / 'runtime-manifest.json'))
(root / 'qa/preflight.json').write_text(json.dumps(pre, indent=2) + '\n')
(root / 'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','origins':origins,'build':str(build_path),'buildSHA256':sha(build_path),'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'))
import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),[
 'Native195 prepared the retained real restore lost-native-receipt whole-host Restart campaign on current GUI143/core16/plugin19/AQ155. Adapted namespaced keyed admission and host-reservation-unknown observers to current wire/storage contracts. Preserved original pending intent/Unknown/no automatic replay, real native committed restore, actual pixels/keyboard, real native Restart, coherent fresh binding and advanced explicit intent, original six-second/three-second/five-second deadlines. Current protected private bus/system isolation and registered short-lived helper normal exits required. Separate controlled-preview+whole-host journal scenario/full release remain open; no installed changes.'
], 'progress', [str((root/'qa/preflight.json').relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
