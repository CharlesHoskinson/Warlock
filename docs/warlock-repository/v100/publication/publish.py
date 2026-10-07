"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='2873c6289af212c6b64002cd42dad9a21e0eca68';BRANCH='refs/heads/feature/elm';COMMITS=[]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set();COMMITS=source(['rev-list','--reverse','506e513b61961a46dbca3e9a21e3957c61276d70..'+head],text=True).splitlines()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v93/', 'docs/warlock-repository/v99/publication/', 'docs/warlock-repository/v100/publication/', 'implementation/warlock-preview-provider-v136/', 'implementation/warlock-client-provider-native-v158/', 'implementation/warlock-client-provider-native-v159/', 'implementation/warlock-preview-provider-v137/', 'implementation/warlock-client-provider-native-v160/', 'implementation/warlock-client-provider-native-v161/', 'implementation/warlock-client-provider-native-v162/', 'implementation/warlock-client-provider-native-v163/', 'implementation/warlock-client-provider-native-v164/', 'openspec/changes/warlock-preview-actor-retirement/tasks.md', 'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report-gui137-stale-error.json').read_text());assert qualification['passed'] and qualification['actualCancelledOldResultQualified'] and qualification['actualNewRealmCapturedPixelsQualified'] and not qualification['actualOldSnapshotPixelsAccepted'] and qualification['cancelledReopenedSnapshotNativeChecks']==36 and qualification['cancelledReopenedSnapshotNormalOwnedExits']==13 and qualification['successfulReopenedSnapshotNativeChecks']==35 and qualification['asyncErrorScopeQuintScenarios']==10 and qualification['asyncErrorScopeInvariantSamples']==200 and qualification['asyncErrorScopeCoupledCases']==4 and qualification['normalRouteNativeChecks']==29 and qualification['normalRouteNormalOwnedExits']==13 and qualification['delayedResultNativeChecks']==18 and qualification['delayedResultNormalOwnedExits']==8 and qualification['rapidPendingReaderNativeChecks']==51 and qualification['rapidPendingReaderNormalOwnedExits']==17 and qualification['fullBuildCommands']==119 and qualification['nativeGrantResets']==0 and not qualification['currentMatchingErrorNativeQualified'] and not qualification['physicalRevealQualified'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']
 message='Reject retired WebKit errors before current GUI failure handling\n\nGUI137 repairs held GUI136/Native159 actual old cancellation shutting down reopened GUI. Original WebKit finish consumes the real result once, then existing view/epoch/navigation/projection/current-channel guard rejects stale results before current error handling. NULL-image-safe disposal clears only old image/error, without current policy/job/grant/physical settlement. Matching-current error branch remains byte-identical; actual matching-current cancellation remains a separate open native gate. Same byte-identical Native159 cancellation oracle now Native16136/13 passes: actual original G_IO_ERROR_CANCELLED/image0 after old strict close/replaced view/new epoch2, one finish, no old artifact/current failure; current request2 actual source red19200/current original image before-after opacity0 output and both strict closes/same policy/binding/no resets. Unchanged normal16029/13, successful old result16235/13, delayed16318/8, rapid real reader16451/17 all pass with normal owned exits/private cleanup. Full119, error-scope Quint10/200 and4 actual failure/fix/success projected cases pass. No native issuer/single Elm policy/physical product/sticky producer/deadline changes. Qualification covers these actual old-cancellation/success schedules, not all async scopes, current failure, process/reload/Unknown recovery, physical conceal/reveal/hardware, pressure/workload/RSS, full S09 or release. Installed/drafts/foreign untouched.'

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
