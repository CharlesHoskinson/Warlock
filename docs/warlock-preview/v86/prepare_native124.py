"""Hold native123; fix only the parent's private lock control inode publication."""
import ast,hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent=repo/'implementation/warlock-client-provider-native-v123';target=repo/'implementation/warlock-client-provider-native-v124'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
failure=parent/'qa/native-1791319359771305032/report.json';failed=json.loads(failure.read_text())
assert not failed['passed'] and failed['cleanupPassed'] and [r['name'] for r in failed['checks'] if not r['passed']]==['guiSessionLockFixtureNormalExitAfterUnlock']
assert [(r['name'],r['exitCode']) for r in failed['ownedExitCodes'] if r['exitCode']!=0]==[('gui-lock',1)]
log=failure.parent/'private-evidence/gui-lock.log';assert 'Private lock fixture refused: private control identity' in log.read_text() and 'unlock-synced' in log.read_text()
for rel,value in failed['artifacts'].items():assert sha(failure.parent/rel)==value,rel
pre=json.loads((parent/'qa/preflight.json').read_text());assert pre['passed']
for name,value in pre['inputs'].items():assert sha(pathlib.Path(name))==value,name
race=pathlib.Path(__file__).parent/'lock-control-check-1791319612925994989/report.json';proof=json.loads(race.read_text())
assert proof['passed'] and proof['evidence'][0]['reproducedOriginalUnlinkedReaderRefusal'] and proof['evidence'][1]['stableIdentityPublisherAccepted']
for name,value in proof['inputs'].items():assert sha(pathlib.Path(name))==value,name
for rel,value in proof['artifacts'].items():assert sha(race.parent/rel)==value,rel
manifest=parent/'component-manifest.json';assert not manifest.exists() and not target.exists()
files={}
for p in sorted(parent.rglob('*')):
 rel=p.relative_to(parent)
 if '__pycache__' in rel.parts:continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest.write_text(json.dumps({'schema':1,'sourceHeld':True,'passed':False,'evidenceIntegrityPassed':True,'files':files,
 'nativeReport':str(failure),'nativeAcceptance':False,'fullReleaseAccepted':False,
 'failure':'834 checks reached; original guiSessionLockFixtureNormalExitAfterUnlock failed, gui-lock exit1, ordered cleanup passed. Actual helper reports private control identity; it opens a single-link0600 file then fstats it. Parent atomic rename can unlink that already-open inode. Deterministic actual unchanged C wants_unlock guard replay reproduces this refusal, and accepts in-place same-inode publisher. Native124 changes only parent hold/unlock publication; exact helper/source guard and every original oracle/deadline remain.'},indent=2)+'\n')
def ignore(path,names):return [name for name in names if name in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path)==parent/'qa' and name.startswith(('native-','prepare-')))]
shutil.copytree(parent,target,ignore=ignore)
shutil.copy2(pathlib.Path(__file__).parent/'lock_control.py',target/'qa/lock_control.py')
path=target/'qa/native.py';text=path.read_text();old="writeControl(lockControl,";assert text.count(old)==6;text=text.replace(old,"writeLockControl(lockControl,")
marker="   def writeControl(path,command):";assert text.count(marker)==1
text=text.replace(marker,"   from lock_control import publish as writeLockControl\n"+marker);ast.parse(text);path.write_text(text)
path=target/'qa/prepare.py';text=path.read_text();marker=' assert all(sha(p)==h for p,h in inputs.items());';assert text.count(marker)==1
extra=" failed123=REPO/'"+str(failure.relative_to(repo))+"';failed123Proof=json.loads(failed123.read_text());assert not failed123Proof['passed'] and failed123Proof['cleanupPassed'] and [row['name'] for row in failed123Proof['checks'] if not row['passed']]==['guiSessionLockFixtureNormalExitAfterUnlock'];inputs[str(failed123)]=sha(failed123);pre['retainedFailedLockControlRace']=str(failed123)\n"
extra+=" lockRace=REPO/'"+str(race.relative_to(repo))+"';lockRaceProof=json.loads(lockRace.read_text());assert lockRaceProof['passed'] and lockRaceProof['evidence'][0]['reproducedOriginalUnlinkedReaderRefusal'] and lockRaceProof['evidence'][1]['stableIdentityPublisherAccepted'];inputs[str(lockRace)]=sha(lockRace);pre['lockControlRaceReport']=str(lockRace)\n"
extra+=" for path,digest in lockRaceProof['inputs'].items():assert sha(path)==digest,path;inputs[path]=digest\n for rel,digest in lockRaceProof['artifacts'].items():assert sha(lockRace.parent/rel)==digest,rel;inputs[str(lockRace.parent/rel)]=digest\n"
text=text.replace(marker,extra+marker);ast.parse(text);path.write_text(text)
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),
 'purpose':'Unchanged fullGUI85/core16/plugin18. Correct only native parent lock-control publication to retain same private single-link0600 inode during helper open/fstat/read; unchanged actual session lock helper and all original runtime/deadline/physical/ACK/oracle gates. Preserve failed123 cleanup/abnormal helper evidence and deterministic actual C guard race proof.',
 'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),
 ['PROGRESS native123 terminalFAIL834: original gui-lock identity guard exit1; orderedcleanup passed, no registry/nativeacceptance. Source123 heldfailed. Actual unchanged C lock guard deterministically reproduces atomic rename/open/fstat unlinked inode refusal and accepts stable-inode Python publisher. Fresh124 changes parent hold/unlock writer only, keeps helper strict guard/original deadlines/fullGUI85/core16/plugin18. Next preflight/serialized124 native, then atomic actor/history/Elm retirement beyond256 and all original release gates. PUBLIC60 03582f63 exact8175 ownerblobs/receipt70c6f9 preserved; main desktop/drafts intact.'],
 'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo)),str(race.relative_to(repo))]))
