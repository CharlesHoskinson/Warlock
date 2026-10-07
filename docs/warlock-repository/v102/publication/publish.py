"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='608fa06d684f1c2d94a6dec92f937c93ff6c63d0';BRANCH='refs/heads/feature/elm';COMMITS=[]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set();COMMITS=source(['rev-list','--reverse','295769b0c62a30ba124e229a7f54e7040dfae348..'+head],text=True).splitlines()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v93/', 'docs/warlock-repository/v101/publication/', 'docs/warlock-repository/v102/publication/', 'implementation/warlock-preview-provider-v139/', 'implementation/warlock-client-provider-native-v169/', 'implementation/warlock-client-provider-native-v170/', 'implementation/warlock-client-provider-native-v171/', 'implementation/warlock-client-provider-native-v172/', 'implementation/warlock-client-provider-native-v173/', 'implementation/warlock-client-provider-native-v174/', 'openspec/changes/warlock-preview-actor-retirement/tasks.md', 'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report-gui139-current-drain.json').read_text());assert qualification['passed'] and qualification['actualCurrentMatchingErrorNativeQualified'] and qualification['actualCurrentFailureNativeCustodyDrained'] and qualification['gracefulCurrentFailureDrainQualified'] and qualification['currentFailureNativeControls']==22 and qualification['currentFailureExpectedExitCode']==1 and qualification['currentFailureOtherNormalOwnedExits']==7 and not qualification['currentFailureGLibCriticalsObserved'] and qualification['actualCancelledOldResultQualified'] and qualification['cancelledOldResultNativeChecks']==36 and qualification['cancelledOldResultNormalOwnedExits']==13 and qualification['successfulOldResultNativeChecks']==35 and qualification['normalRouteNativeChecks']==29 and qualification['normalRouteNormalOwnedExits']==13 and qualification['rapidPendingReaderNativeChecks']==51 and qualification['rapidPendingReaderNormalOwnedExits']==17 and qualification['delayedResultNativeChecks']==18 and qualification['delayedResultNormalOwnedExits']==8 and qualification['currentFailureDrainQuintScenarios']==8 and qualification['currentFailureDrainInvariantSamples']==200 and qualification['currentFailureDrainCoupledStages']==5 and qualification['fullBuildCommands']==119 and qualification['nativeGrantResets']==0 and not qualification['uncertainCurrentFailureDrainQualified'] and not qualification['physicalRevealQualified'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']
 message='Drain original native duties before exiting a failed renderer\n\nGUI139 repairs actual held138/Native168 current matching WebKit cancellation exiting before Native drain. Original finish/current scope disposition remains; matching controlled failure retains original error/failure outcome, native opacity0 curtain, original visual invalidation and urgent same-policy quarantine. Original sticky retiring producer/input/step/poll/receipts continue; only original policy/physical/ticket/journal/confirmation strict Native retirement, closed policy and empty custody allow failure exit1. No renderer replacement/reopen/reset/inferred settlement; Native uncertainty retains original refusal path. Exact byte-identical Native168 drain oracle now16922 controls/seven other normal/private cleanup passes: real current G_IO_ERROR_CANCELLED once/no artifact, actual owned->closing->strict closed empty model/input/ticket/confirmation/transport, original failure1 after retirement, no incomplete teardown or GLib/GObject criticals. Failure1 remains negative outcome, not normal-exit success. Unchanged normal17029/13, canceled-old17136/13, successful old17235/13, rapid real-reader17351/17 and closure-delayed17418/8 positive regressions/full119 pass with all normal owned exits/private cleanup. New failure-drain Quint8/200 and5 actual failed/fixed projected stages pass. Native issuer/single Elm reducer/physical product/original retirement gates/deadlines unchanged; only host current-error drain changes. Qualification covers this actual known current-cancellation duty schedule; uncertain/process/reload/Unknown recovery, all async errors, ongoing physical conceal/reveal/hardware, pressure/full workload/RSS, full S09 and release remain open. Installed desktop/drafts/foreign preserved.'

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
