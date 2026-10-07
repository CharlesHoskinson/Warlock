"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='8bc0b5dd33e97f06e37284d0ca518db4d8e829fb';BRANCH='refs/heads/feature/elm';COMMITS=[]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set();COMMITS=source(['rev-list','--reverse','e17f3e5dcb66a3a3cc083e83dcfc6951580e5234..'+head],text=True).splitlines()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v93/', 'docs/warlock-repository/v87/publication/', 'docs/warlock-repository/v88/publication/', 'implementation/warlock-preview-provider-v119/', 'openspec/changes/warlock-preview-actor-retirement/tasks.md', 'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report119.json').read_text());expected={'sourceHeld': True, 'passed': True, 'singlePreviewPolicy': True, 'parentElmPolicyUnchanged': True, 'parentNativeIssuerAndPhysicalProductUnchanged': True, 'parentAssetsAndAdaptersUnchanged': True, 'nativeOwnedJavaScriptCore': True, 'persistentPolicyContexts': 1, 'nativeElmOutboxChecks': 207, 'additiveVisualProjectionChecks': 90, 'readonlyProjectionChecks': 74, 'visualChannelChecks': 67, 'visualChannelBoundaryChecks': 33, 'pureRendererInstances': 2, 'rendererWindowPolicies': 0, 'visualChannelScenarios': 14, 'visualChannelTraces': 26, 'visualChannelObservableStates': 451, 'visualChannelSamples': 200, 'visualChannelCompiledNativeVariantsDetected': 4, 'compiledSeededCounterBoundaries': 2, 'orderedVisualCustodyCPUQualified': True, 'nativeControlOrdinalsUnchanged': True, 'fullBuildCommands': 115, 'originalBuildCommands': 112, 'realHostPolicyActivated': False, 'actualRendererProjectionActivated': False, 'actualDOMQualified': False, 'actualWebKitContextAuthenticationQualified': False, 'physicalConcealmentQualified': False, 'ongoingProjectionFreshnessQualified': False, 'realHostInputBackpressureQualified': False, 'nativeDelayedProposalLivenessQualified': False, 'uncertainLiveWorkerRecoveryQualified': False, 'fullElmRecoveryQualified': False, 'typedHostRoutingActivated': False, 'webKitActivated': False, 'nativeAcceptance': False, 'fullReleaseAccepted': False};assert all(qualification.get(k)==v for k,v in expected.items());assert len(qualification['heldFailedReports'])==1
 message="Retain ordered visual snapshots in native context custody\n\n# Ordered visual custody — bounded component qualification\n\nNative creator-owned `WarlockVisualChannel` keeps a strong reference to its\nattached native context, one pending visual snapshot and exact expected receipt.\nIts renderer lease and visual sequence are separate monotonically increasing\nUInt64 counters. They never issue or consume original native control ordinals.\nDetach retains both floors; replacement requires detach then a new native lease.\nExhaustion refuses without resetting either counter.\n\nThe channel derives its domain and visual fields through the GUI118 read-only\ngetter. Offer invalidates earlier acceptance and issues a new visual sequence.\nRetry copies the exact pending packet without invoking Elm or allocating another\nsequence. Ack requires byte-exact latest receipt from the attached native context.\nRetry, ack and current checks compare the snapshot with the same policy's latest\ncommitted visual bytes; a changed/closed/uncertain cache removes visual custody.\nForeign threads/contexts and stale receipts refuse. Normal destruction requires\ndetachment and does not close a policy, settle an effect or retire resources.\n\n`NativePreviewReceiver` holds only a validated projection, native grant, ordering\nfloor and concealment latch. It imports no window/lifecycle policy. A native\ngrant is fixed at initialization; incoming packets cannot establish or replace\nauthority. Older sequences and other domains/leases are ignored. Exact duplicates\nrepeat only the acceptance receipt. Conflicting same-sequence visual data or a\nmalformed current channel/projection conceals and latches uncertainty; a packet\ncannot reset that instance. A recreated renderer needs a new native-issued grant.\nThe browser component compiles but no HTML/adapter/native host route activates it.\n\nThis component's receipt establishes pure receiver acceptance, not actual DOM or\nframe application. GObject fixture identities do not qualify actual WebKit callback\nauthentication. Cache comparison establishes currency at that check, not ongoing\nfreshness or concealment between policy transitions and async WebKit evaluation.\nThe real host must physically conceal before policy changes/invalidation, bind\nthe actual WebKit instance and callback to its native lease, reject old async\ncompletions, qualify DOM/frame application and original URI reader lifetime, then\nreveal only with that full native barrier. No such host route is active yet.\n\nQualification passes67 actual C/JSC/pure receiver checks and33 native missing\ndestination/context/policy/receipt, absent/closed/destroyed custody boundaries.\nQuint executes14 selected native custody scenarios and200 invariant samples;\n26 traces compare451 observable states against actual sanitizer C/JSC with\nnormal fixture/policy teardown. Four compiled unsafe guard derivatives are\ndetected; the early-destroy variant also fails sanitizer ownership. Two separately\nlabeled seeded native counter builds preserve original exhaustion guards and\nnormal teardown. The pure receiver's maximum-sequence stress packet is explicitly\nsynthetic and is refused by native acceptance because native did not issue it.\nThe original native207 controls plus90 visual/74 getter comparisons still pass;\nparent policy/getter/lifetime/backpressure/native issuer/physical/assets/adapters\nstay byte-identical. Full115 commands retain112 and add two pure renderer builds\nand native channel compilation/link. One new-header compile failure remains\nwith its exact original input snapshot. No original deadline or oracle is weakened.\n\nNext: freeze/publication, current legacy native source requalification and actual\nhost integration with durable original input/ticket custody and bounded retry.\nUncertain worker/process recovery, delayed proposal outcome/order, actual native\ncaptured FD/render/fence/readers, >256 native windows and all full release gates\nremain open. Native130 remains the actual bounded legacy2518/278 baseline.\n"

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
