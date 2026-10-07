"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='8496ca6e461a1e6f4d17df21c19f4bdb6347f80c';BRANCH='refs/heads/feature/elm';COMMITS=[]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set();COMMITS=source(['rev-list','--reverse','fcd4371992e09699567841eed40ab3848bcc595d..'+head],text=True).splitlines()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v93/', 'docs/warlock-repository/v97/publication/', 'docs/warlock-repository/v98/publication/', 'implementation/warlock-preview-provider-v133/', 'implementation/warlock-preview-provider-v134/', 'implementation/warlock-client-provider-native-v147/', 'implementation/warlock-client-provider-native-v148/', 'implementation/warlock-client-provider-native-v149/', 'implementation/warlock-client-provider-native-v150/', 'implementation/warlock-client-provider-native-v151/', 'implementation/warlock-client-provider-native-v152/', 'implementation/warlock-client-provider-native-v153/', 'openspec/changes/warlock-preview-actor-retirement/tasks.md', 'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report134.json').read_text());assert qualification['passed'] and qualification['actualGUIRealmReopenQualified'] and qualification['actualPendingIntentReopenQualified'] and qualification['actualRapidPointerCloseReopenQualified'] and qualification['stickyClosingRealmProducerQualified'] and qualification['rapidPendingReaderNativeChecks']==51 and qualification['rapidPendingReaderNormalOwnedExits']==17 and qualification['pendingReaderNativeChecks']==51 and qualification['pendingReaderNormalOwnedExits']==18 and qualification['readerQuintScenarios']==6 and qualification['readerInvariantSamples']==200 and qualification['readerCoupledStages']==8 and qualification['closingProducerQuintScenarios']==8 and qualification['closingProducerInvariantSamples']==200 and qualification['closingProducerCoupledChecks']==4 and qualification['normalRouteNativeChecks']==29 and qualification['normalRouteNormalOwnedExits']==13 and qualification['delayedResultNativeChecks']==18 and qualification['delayedResultNormalOwnedExits']==8 and qualification['fullBuildCommands']==119 and qualification['nativeGrantResets']==0 and not qualification['physicalRevealQualified'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']
 message='Finish retiring the old preview realm during rapid popup reopening\n\nGUI134 fixes the actual Native149 rapid pending-intent deadlock with two sticky old-realm producer guards only: poll original closing scope with no current presentation stamps and continue original detachment observations even when a later popup is ready. Native issuer/single persistent Elm policy/physical/journal/independent confirmation/router/readers/deadlines unchanged. Disabled-by-default QA-only original URI/GIO reader from held133 keeps a real owned Retiring job alive across old popup closure/later actual GTK configuration; old held/fresh reads revoke, one original reader close precedes independent strict Native close, then the retired renderer is replaced inside the same later GTK popup lease/grab and fresh DOM admission creates later same-binding epoch/pure fixed-grant renderer. Original failed rapid14933/12 normal others/host1/clean private teardown and original6s counterexample remain held. Same byte-identical rapid oracle on current Native152 passes51/17 normal exits/private cleanup, two current source URI/red19200 images, monotonic epoch/navigation/lease/request1->2, current opacity0 closed-curtain output and both strict closes. Slower Native15151/18, unchanged Native15029/13 normal and delayed Native15318/8 real-result regressions/cleanups pass separately. Current full119, reader Quint6named200samples/8 coupled stages and closing producer Quint8named200samples/4 cases coupled to actual failed/passed Native traces/source gates pass. Pending-intent/rapid coverage is these actual fixture schedules, not all timings. Broader old-context async/process/reload/Unknown, ongoing conceal/reveal/hardware, pressure/workload/RSS, original full S09/release remain open; no installed desktop/draft changes or grant reset.'

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
