"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='999882f42faba9ba1e008d273dc9f14ea984473a';BRANCH='refs/heads/feature/elm';COMMITS=[]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set();COMMITS=source(['rev-list','--reverse','5317904baf6303f73fc7c48574453a0e27a460a9..'+head],text=True).splitlines()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v93/', 'docs/warlock-repository/v98/publication/', 'docs/warlock-repository/v99/publication/', 'implementation/warlock-preview-provider-v135/', 'implementation/warlock-client-provider-native-v154/', 'implementation/warlock-client-provider-native-v155/', 'implementation/warlock-client-provider-native-v156/', 'implementation/warlock-client-provider-native-v157/', 'openspec/changes/warlock-preview-actor-retirement/tasks.md', 'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report135.json').read_text());assert qualification['passed'] and qualification['actualOldResultAcrossReopenedRealmQualified'] and qualification['actualNewRealmCapturedPixelsQualified'] and not qualification['actualOldSnapshotPixelsAccepted'] and qualification['reopenedSnapshotNativeChecks']==35 and qualification['reopenedSnapshotNormalOwnedExits']==13 and qualification['hostLifecycleQuintScenarios']==9 and qualification['hostLifecycleInvariantSamples']==200 and qualification['hostLifecycleCoupledStages']==7 and qualification['normalRouteNativeChecks']==29 and qualification['normalRouteNormalOwnedExits']==13 and qualification['delayedResultNativeChecks']==18 and qualification['delayedResultNormalOwnedExits']==8 and qualification['rapidPendingReaderNativeChecks']==51 and qualification['rapidPendingReaderNormalOwnedExits']==17 and qualification['fullBuildCommands']==119 and qualification['nativeGrantResets']==0 and not qualification['canceledOrFailedOldResultQualified'] and not qualification['physicalRevealQualified'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']
 message='Reject an old WebKit result after native realm reopening\n\nGUI135 adds disabled-by-default QA retention of one real original WebKit result/strong old view across strict old C/Bootstrap close, renderer replacement and later same-policy/native epoch. It calls original finish once only after current new-view native projection acknowledgement; unchanged original view/epoch/navigation/projection guard rejects old request1 pixels/artifact. Actual Native15535 checks/13 normal exits/private cleanup prove epoch/navigation1->2/old view replaced, old result consumed once with zero old artifact, then new current source URI/red19200 request2 pixels, current image before/after actual opacity0 output region, both original strict native closes/same policy/binding/no reset. Original snapshot pixels remain rejected; new realm captured pixels qualify separately. Unchanged Native15429/13 normal, Native15618/8 closure-delayed result and Native15751/17 rapid real-reader regressions pass separately. Current full119, lifecycle Quint9named200samples and7 stages coupled to actual observations pass. Native issuer/single Elm policy/physical product/readers/original completion guard/sticky producer/deadlines unchanged. This actual retained-success-result schedule does not qualify canceled/failed result, all async timing/process/reload/Unknown recovery, ongoing conceal/reveal/hardware, pressure/workload/RSS, full S09 or release. Installed/drafts/foreign untouched.'

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
