#!/usr/bin/env python3
"""Prepare a new reviewed package/plan only; never writes live source or signals a process."""
from pathlib import Path
import hashlib,json,shutil,subprocess
B=Path(__file__).resolve().parent;H=Path.home();LIVE=H/'.local/share/omarchy-files'
OUT=B/'deployment-prepared';NATIVE=H/'.local/share/omarchy-files-native/WindowAccessibilityV4_keyboard_20261001'
assert not OUT.exists(),'Require a fresh prepared directory'
assert not NATIVE.exists(),'Native destination must be a fresh unused URL'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(*a):return subprocess.check_output(list(map(str,a)),text=True,timeout=8).strip()
def ipc(method,*args):return run('qs','-p',LIVE,'ipc','call','files',method,*args)
m=json.loads((B/'source-hashes.json').read_text())
for i in m['changedQml']:
 assert sha(LIVE/i['path'])==i['baselineSha256'],i['path']
 assert sha(B/'app'/i['path'])==i['candidateSha256'],i['path']
for i in m['unchangedOperationsAndSpec']:
 assert (LIVE/i['path']).read_bytes()==(B/'app'/i['path']).read_bytes(),i['path']
instances=json.loads(run('qs','-p',LIVE,'list','-j'));assert len(instances)==1
instance=instances[0];assert instance['pid']==667402
public=json.loads(ipc('state'));ui=json.loads(ipc('uiState'));status=json.loads(ipc('migrationStatus'))
assert status['ready'] and status['pid']==667402 and status['instance']==instance['id']
assert not ui['visible'] and public['view']=='home' and not public['sel'] and not public['clip'] and not public['lb']
assert not ui['prompt']['visible'] and not ui['menu']['visible'] and not ui['clip']['paths']
assert ipc('act','promptinfo','')=='none'
OUT.mkdir(mode=0o700);shutil.copytree(B/'app',OUT/'app');shutil.copytree(B/'app/WindowAccessibilityV4',OUT/'native')
host=OUT/'app/shell.qml';s=host.read_text();old=(B/'app/WindowAccessibilityV4').as_uri();assert old in s;s=s.replace(old,NATIVE.as_uri());host.write_text(s)
# The deployment package keeps the native library separate from the app watcher.
shutil.rmtree(OUT/'app/WindowAccessibilityV4')
locked=[]
for i in m['changedQml']:
 locked.append({'path':i['path'],'baselineSha256':sha(LIVE/i['path']),'candidateSha256':sha(OUT/'app'/i['path'])})
plan={'execution':'Root review required; this script only prepares isolated QA files',
 'original':{'pid':667402,'instance':instance['id'],'processStart':Path('/proc/667402/stat').read_text().rsplit(')',1)[1].split()[19]},
 'nativeDestination':str(NATIVE),'nativeSha256':sha(OUT/'native/libwindowaccessibility.so'),
 'changedQml':locked,'legacyMigrationRequired':False,
 'publicStateSha256':hashlib.sha256(json.dumps(public,sort_keys=True).encode()).hexdigest(),
 'uiStateSha256':hashlib.sha256(json.dumps(ui,sort_keys=True).encode()).hexdigest(),
 'steps':['Install native assets into the fresh unused user-only destination; do not overwrite any loaded library.',
 'Revalidate exact source hashes, process start/instance and hidden idle state immediately before mutation.',
 'Prepare all QML temporary bytes and private backup before stopping the exact pidfd; no user app termination.',
 'Stop exact original briefly, atomically replace all15 QML files; on partial write failure restore original bytes before continuing.',
 'Continue once; current PersistentProperties strings transfer full state. Do not create ui-migration.json or call files open/toggle.',
 'Verify exact same PID/instance, ready/hidden-before-map, public and full UI state, original native identities/geometries/focus/cursor/layers, clipboard/MIME hashes/catalog/dashboard/a11y/socket and script/spec hashes.',
 'Retain the private source/state backup after reviewed success for later recovery; never revert to a legacy stateless host.'],
 'nativeReaderUrlBoundary':'Only shell import URL changes from tested app; the V4 binary and all other candidate QML bytes are identical. Prove URL/module resolution on copied offscreen reload before live deployment.'}
(OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
(OUT/'private-ui-state.json').write_text(json.dumps({'public':public,'ui':ui},indent=2)+'\n');(OUT/'private-ui-state.json').chmod(0o600)
print(json.dumps({'result':'prepared-only','changedQml':len(locked),'nativeInstalled':False,'originalTouched':False,'planSha256':sha(OUT/'plan.json')},indent=2))
