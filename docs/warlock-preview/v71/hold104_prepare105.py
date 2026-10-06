"""Keep actual native104 failure; supply genuine intended third-window stimulus."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v104';target=repo/'implementation/warlock-client-provider-native-v105';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=next(parent.glob('qa/native-*/report.json'));d=json.loads(report.read_text());assert not d['passed'] and d['cleanupPassed'] and len(d['checks'])==929 and len(d['ownedExitCodes'])==109 and all(row['exitCode']==0 for row in d['ownedExitCodes'])
assert [row['name'] for row in d['checks'] if not row['passed']]==['receiverGrowthActualThirdPixelsAfterRealCapacity'];probe=next(row for row in d['checks'] if row['name']=='receiverGrowthActualOwnCJournalAndPhysicalDrain')['evidence'];assert probe['passed'] and probe['checks']==69 and probe['empty']
for rel,h in d['artifacts'].items():assert sha(report.parent/rel)==h,rel
files={}
for p in sorted(parent.rglob('*')):
 rel=p.relative_to(parent);assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
manifest=parent/'component-manifest.json';assert not manifest.exists();manifest.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'evidenceIntegrityPassed':True,'passed':False,'files':files,'failure':'Actual native growth probe69/allphysical+journal checks passed/empty/normal exit. Third pixel oracle failed because original companion default fixture has no blue child surface. Native104929 checks/109normal exits/clean retained. Fresh105 adds dedicated actual third source with genuine child-create/barrier; same pixel oracle and original deadlines, original companion untouched.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
def exclusions(path,names):return [name for name in names if name in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path).name=='qa' and (name.startswith('native-') or name.startswith('prepare-')))]
assert not target.exists();shutil.copytree(parent,target,ignore=exclusions)
(target/'ANCESTRY.json').write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'purpose':'Keep native104 physical/journal69 passing and missing third blue-child stimulus failure. Supply dedicated actual third fixture child-create and original server barrier, then normal quit after probe; keep original companion and all pixel/scenario/deadline oracles unchanged. Same exactGUI60/core/plugin tuple.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
event=loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS native104 actualown3actors2pool+receiver/Cjournalgrowth probe69 PASS/empty; campaign thirdbluepixelsfail due originalcompanion defaultred/nochild. Held104929checks109normalclean. Fresh105 adds dedicatedthirdactualbluechildfixture/barrier/normalquit, leaves originalcompanion andalloracles/deadlines untouched. Recompilepreflight/serialnative allpriororiginals; fullreleaseopen. All104handles terminal.'],'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))])
print(json.dumps({'heldFiles':len(files),'source':str(target),'checkpoint':str(event)}))
