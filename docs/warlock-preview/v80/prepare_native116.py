"""Preserve115 failure; fix only the new ownership log stream selector."""
import ast,hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');p=r/'implementation/warlock-client-provider-native-v115';t=r/'implementation/warlock-client-provider-native-v116';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
reports=list(p.glob('qa/native-*/report.json'));assert len(reports)==1;failure=reports[0];d=json.loads(failure.read_text())
assert not d['passed'] and d['cleanupPassed'] and all(row['exitCode']==0 for row in d['ownedExitCodes']) and 'wait(nextPoolDrained)' in d['traceback']
for name,h in d['artifacts'].items():assert sha(failure.parent/name)==h,name
log=failure.parent/'private-evidence/full-imported-feedback.log';text=log.read_text()
prefix='native-imported-ownership: ';rows=[json.loads(line[len(prefix):]) for line in text.splitlines() if line.startswith(prefix)]
assert rows and all(row['records']==0 and int(row['charge'])==0 and row['mappedFDClosed'] and row['exportReleased'] and row['producerRetired'] and not row['retirementPending'] for row in rows[-1])
assert 'shared-host-exit: failure=0 rendered=1' in text and not any(line.startswith('native-imported-status: ') for line in text.splitlines())
assert all(row['passed'] for row in d['checks']) and any(row['name']=='nextIntentGUIActualThirdOwnedURIComplete' for row in d['checks'])
m=p/'component-manifest.json';assert not m.exists() and not t.exists()
files={str(f.relative_to(p)):{'kind':'file','sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode))} for f in sorted(p.rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
m.write_text(json.dumps({'sourceHeld':True,'passed':False,'evidenceIntegrityPassed':True,'files':files,'nativeReport':str(failure),'nativeAcceptance':False,'fullReleaseAccepted':False,'failure':'Actual same-host third successor job/cutoff/image and terminal ACK occurred. New wait parsed nonexistent native-imported-status label instead of actual native-imported-ownership, so full campaign stopped before remaining original guards. Final archived ownership rows prove zero records/charge and physical/backend closure. All115 owned exits normal. Fresh116 corrects only the new stream selector, retaining original six-second deadline and all actual drain predicates.'},indent=2)+'\n')
def ignore(path,names):return [n for n in names if n in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path)==p/'qa' and n.startswith(('native-','prepare-')))]
shutil.copytree(p,t,ignore=ignore)
f=t/'qa/native.py';s=f.read_text();assert s.count('native-imported-status: ')==2;s=s.replace('native-imported-status: ','native-imported-ownership: ');ast.parse(s);f.write_text(s)
f=t/'qa/prepare.py';s=f.read_text();marker=" assert all(sha(p)==h for p,h in inputs.items());";assert s.count(marker)==1
added=" failed115=REPO/'"+str(failure.relative_to(r))+"';failedProof=json.loads(failed115.read_text());assert not failedProof['passed'] and failedProof['cleanupPassed'] and all(row['exitCode']==0 for row in failedProof['ownedExitCodes']) and 'wait(nextPoolDrained)' in failedProof['traceback'];inputs[str(failed115)]=sha(failed115);pre['retainedFailedOwnershipLabelFixture']=str(failed115)\n"
s=s.replace(marker,added+marker);ast.parse(s);f.write_text(s)
(t/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(p),'parentManifestSHA256':sha(m),'purpose':'Unchanged GUI80 successor/unissued-priority production. Preserve failed115 actual third image/ACK/normal cleanup; correct new native fixture ownership label only. Original deadlines, predicates, pool and full114 guards remain exact.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(t.relative_to(r)),['PROGRESS80 full95/new10/22/447states/C45Elm21/currentallregressionsheld. Native115 reached actualthirdsuccessorjob/request1/laterlease/native2s/ownedURI andexactACK; newdrainfixturewrongloglabel failed, all119ownednormalclean finalrecordscharge0 archived. Fresh116 changesnewselector only; nextpreflight thenserialized fullnative toretainall114guards. No fullnative/releaseclaim, originalcompletegoalsremain.'],'progress',[str(m.relative_to(r)),str((t/'ANCESTRY.json').relative_to(r))]))
