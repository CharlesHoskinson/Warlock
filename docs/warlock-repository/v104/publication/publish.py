"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='0ddc454b739f0a8dce50530d661a8b2e86551ca7';BRANCH='refs/heads/feature/elm';COMMITS=[]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set();COMMITS=source(['rev-list','--reverse','3a25f38c155bcf60fd27110a9a0190a3be418d65..'+head],text=True).splitlines()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v93/', 'docs/warlock-repository/v103/publication/', 'docs/warlock-repository/v104/publication/', 'implementation/warlock-preview-provider-v142/', 'implementation/warlock-client-provider-native-v185/', 'implementation/warlock-client-provider-native-v186/', 'implementation/warlock-preview-provider-v143/', 'implementation/warlock-client-provider-native-v187/', 'implementation/warlock-client-provider-native-v188/', 'implementation/warlock-client-provider-native-v189/', 'implementation/warlock-client-provider-native-v190/', 'implementation/warlock-client-provider-native-v191/', 'implementation/warlock-client-provider-native-v192/', 'implementation/warlock-client-provider-native-v193/', 'implementation/warlock-client-provider-native-v194/', 'openspec/changes/warlock-preview-actor-retirement/tasks.md', 'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
assert all(p.startswith(allowed) or (p.startswith('docs/elm-roadmap/delivery/build-loop-events/') and '--f6779148-8f5d-4bdf-8a0f-044184e486f2--' in p) for p in paths)
actual=source(['ls-remote','github',BRANCH],text=True).split()[0];assert actual==BASE
assert mirror(['rev-parse',BRANCH],text=True).strip()==BASE
def tree_rows(call,commit,paths):
 ordered=sorted(paths)
 for offset in range(0,len(ordered),400):
  yield from call(['ls-tree','-rz',commit,'--',*ordered[offset:offset+400]]).split(b'\0')
rows=[]
for line in tree_rows(source,head,paths):
 if not line:continue
 metadata,name=line.split(b'\t',1);mode,kind,oid=metadata.decode().split();assert kind=='blob';rows.append({'path':name.decode(),'mode':mode,'gitBlob':oid})
assert {r['path'] for r in rows}==paths
index_fd,index=tempfile.mkstemp(prefix='warlock-publish-index-');os.close(index_fd);os.unlink(index);env=dict(os.environ,GIT_INDEX_FILE=index)
try:
 mirror(['read-tree',BASE],env=env)
 batch=subprocess.Popen(['git','cat-file','--batch'],cwd=REPO,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
 try:
  for n,row in enumerate(rows,1):
   batch.stdin.write((row['gitBlob']+'\n').encode());batch.stdin.flush();header=batch.stdout.readline().decode().split();assert header[:2]==[row['gitBlob'],'blob'];size=int(header[2]);assert size<100*1024*1024
   content=batch.stdout.read(size);assert len(content)==size and batch.stdout.read(1)==b'\n';oid=mirror(['hash-object','-w','--stdin'],input=content).decode().strip();assert oid==row['gitBlob'];row['bytes']=size;row['sha256']=hashlib.sha256(content).hexdigest()
   if n%500==0:print('Imported exact owner blobs',n,flush=True)
 finally:
  batch.stdin.close();assert batch.wait()==0
 update=''.join(r['mode']+' '+r['gitBlob']+'\t'+r['path']+'\n' for r in rows).encode();mirror(['update-index','--index-info'],input=update,env=env)
 tree=mirror(['write-tree'],env=env).decode().strip()
 qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report-gui143-shared-process-drain.json').read_text());assert qualification['passed'] and qualification['actualKnownSharedProcessNativeDrainQualified'] and qualification['actualGTKRecoveryAfterStrictDrainQualified'] and qualification['processFailureNativeControls']==21 and qualification['processFailureExpectedHostExitCode']==1 and qualification['processFailureOtherNormalOwnedExits']==7 and not qualification['processFailureGLibCriticalsObserved'] and qualification['processDrainQuintScenarios']==9 and qualification['processDrainQuintInvariantSamples']==200 and qualification['processDrainCoupledStages']==6 and qualification['reloadNativeChecks']==34 and qualification['reloadNormalOwnedExits']==12 and qualification['currentFailureNativeControls']==22 and qualification['normalRouteNativeChecks']==29 and qualification['cancelledOldResultNativeChecks']==36 and qualification['rapidPendingReaderNativeChecks']==51 and qualification['delayedResultNativeChecks']==18 and qualification['successfulOldResultNativeChecks']==35 and qualification['fullBuildCommands']==119 and qualification['nativeGrantResets']==0 and qualification['navigationResets']==0 and qualification['snapshotOrdinalResets']==0 and not qualification['wholeHostRestartQualified'] and not qualification['durableUnknownRecoveryQualified'] and not qualification['uncertainProcessDrainQualified'] and not qualification['physicalRevealQualified'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']
 message='Drain native custody before shared renderer recovery\n\nGUI143 repairs actual held142/Native186 shared related WebKit process death presenting GTK recovery with original known native duties retained. Owning shared termination wrapper retains actual reason/failure and urgent original same-policy quarantine; original native input/step/poll/receipts continue until original strict policy/physical/ticket/journal/confirmation close and empty custody. Multiple actual related-view signals never cancel drain. Optional original evaluation finish/error hook retains its original failure but defers early GTK exit in this controlled known realm; standalone/noncontrolled default remains original. Only strict retired custody permits original GTK recovery controls; unretired/uncertain custody explicitly refuses them. Native187 unchanged186 oracle passes21 controls: actual API termination/reason2/shared signals/original first source red19200, known owning/closing/strict closed before GTK recovery/backend normal, explicit recovery dismissal keeps failure1/seven other normal exits/private cleanup/no criticals or incomplete teardown. No new renderer/realm/reset/replay/inferred settlement. Normal18829/13, known-reload18934/12, current-failure19022/host1+seven other normal, old-canceled19136/13, rapid19251/17, delayed19318/8 and old-success19435/13 pass separately with original source/pixel/output/strict close controls. Full119/new process-drain Quint9/200/6 actual projected stages pass. This qualifies known preview-duty drain before GTK recovery for this actual shared process stop; all evaluation-error/termination schedules, whole-host restart/window-command journal/durable Unknown/actual native uncertainty, physical/hardware/pressure/full workload/RSS, original full S09/release remain open. Original policy/issuer/physical product/grants/epochs/nav/snapshot/clocks/deadlines unchanged; installed desktop/drafts/foreign preserved.'

 published=mirror(['commit-tree',tree,'-p',BASE],input=message.encode()).decode().strip()
 verified={}
 for line in tree_rows(mirror,published,paths):
  if not line:continue
  metadata,name=line.split(b'\t',1);mode,kind,oid=metadata.decode().split();verified[name.decode()]=(mode,oid)
 assert len(verified)==len(rows) and all(verified[r['path']]==(r['mode'],r['gitBlob']) for r in rows)
 receipt={'schema':1,'repository':'https://github.com/CharlesHoskinson/Warlock','branch':'feature/elm','sourceCommits':COMMITS,'sourceCommit':head,'priorPublication':BASE,'publishedCommit':published,'ownedFiles':len(rows),'inventory':rows,'nativeAcceptance':False,'fullReleaseAccepted':False,'providerComponentImplemented':True,'pushCompleted':False}
 (OUT/'prepared.json').write_text(json.dumps(receipt,indent=2)+'\n')
 mirror(['update-ref',BRANCH,published,BASE]);result=subprocess.run(['git','--git-dir='+str(MIRROR),'-c','http.postBuffer=268435456','-c','http.version=HTTP/1.1','push','origin',BRANCH+':'+BRANCH],capture_output=True,text=True,timeout=180)
 (OUT/'push.stdout').write_text(result.stdout);(OUT/'push.stderr').write_text(result.stderr);receipt['gitPushExitCode']=result.returncode
 if result.returncode:raise RuntimeError('Push failed; retain prepared evidence and inspect remote without force')
 observed=source(['ls-remote','github',BRANCH],text=True).split()[0];assert observed==published;receipt.update(pushCompleted=True,remoteObserved=observed)
 (OUT/'delivery.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'publishedCommit':published,'ownerFiles':len(rows),'remoteVerified':True}),flush=True)
finally:
 if os.path.exists(index):os.unlink(index)
