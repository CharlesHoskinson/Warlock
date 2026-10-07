"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='377cfb985322ab82eab1f3192803cbec540ec093';BRANCH='refs/heads/feature/elm';COMMITS=[]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set();COMMITS=source(['rev-list','--reverse','1c052f9948a9602155fd50ca0540a352ebbbbfbe..'+head],text=True).splitlines()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v93/', 'docs/warlock-repository/v102/publication/', 'docs/warlock-repository/v103/publication/', 'implementation/warlock-preview-provider-v140/', 'implementation/warlock-client-provider-native-v175/', 'implementation/warlock-client-provider-native-v176/', 'implementation/warlock-preview-provider-v141/', 'implementation/warlock-client-provider-native-v177/', 'implementation/warlock-client-provider-native-v178/', 'implementation/warlock-client-provider-native-v179/', 'implementation/warlock-client-provider-native-v180/', 'implementation/warlock-client-provider-native-v181/', 'implementation/warlock-client-provider-native-v182/', 'implementation/warlock-client-provider-native-v183/', 'implementation/warlock-client-provider-native-v184/', 'openspec/changes/warlock-preview-actor-retirement/tasks.md', 'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report-gui141-known-reload.json').read_text());assert qualification['passed'] and qualification['actualKnownRendererReloadQualified'] and qualification['actualSamePopupLeaseAcrossReloadQualified'] and qualification['actualSamePolicyRetained'] and qualification['actualOriginalNativeBindingRetained'] and qualification['reloadNativeChecks']==34 and qualification['reloadNormalOwnedExits']==12 and qualification['reloadQuintScenarios']==9 and qualification['reloadQuintInvariantSamples']==200 and qualification['reloadCoupledStages']==7 and qualification['currentFailureNativeControls']==22 and qualification['currentFailureExpectedExitCode']==1 and qualification['normalRouteNativeChecks']==29 and qualification['cancelledOldResultNativeChecks']==36 and qualification['rapidPendingReaderNativeChecks']==51 and qualification['delayedResultNativeChecks']==18 and qualification['successfulOldResultNativeChecks']==35 and qualification['fullBuildCommands']==119 and qualification['nativeGrantResets']==0 and qualification['navigationResets']==0 and qualification['snapshotOrdinalResets']==0 and not qualification['reloadRecoveryQualified'] and not qualification['uncertainRecoveryQualified'] and not qualification['physicalRevealQualified'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']
 message='Recover known renderer reload after strict native retirement\n\nGUI141 repairs actual held140/Native176 reload-as-uncertain failure. Known trusted same-URI original initialized view LOAD_STARTED navigation2 invalidates visual authority and urgently quarantines same original realm without claiming native settlement. Original sticky Native input/step/poll/receipts and strict policy/physical/ticket/journal/confirmation close/empty custody precede fresh renderer context replacement inside SAME GTK popup lease1. Fresh DOM/fixed native grant admits later epoch2 on identical original policy/binding, navigation3 and original request2. Actual18434/12 proves real first and current source red19200, current image before-after original grim opacity0 region, final strict closure/all normal owned exits/private cleanup/no criticals. Native177 premature snapshot-wait assertion failure retained; fresh184 waits for request2 while accepting known request1 as pending, keeping original six-second deadline and every actual pixel/output/final strict close oracle. Original normal17829/13, canceled-old17936/13, current-failure18022/host1+seven other normal, rapid18151/17, delayed18218/8 and old-success18335/13 pass separately. Full119, new reload Quint9/200 and7 actual projected stages pass. Historical wrong-build-entry failure and coupling closed-command schema check failure retained. Only host known navigation handling changed; no issuer/Elm reducer/physical product/grant/nav/snapshot/clock/reset/replay changes. Unexpected/uncertain/failing ownership remains failclosed; actual arbitrary/unknown/process/repeated reload schedules, physical reveal/hardware/pressure/full workload/RSS, original full S09 and release remain open. Installed desktop/drafts/foreign preserved.'

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
