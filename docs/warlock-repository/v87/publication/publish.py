"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='99c357235f940af304314501ce76efe76cbd91c5';BRANCH='refs/heads/feature/elm';COMMITS=[]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set();COMMITS=source(['rev-list','--reverse','356ebb9de9a5c203f67c4fd40b614ecd22d39c76..'+head],text=True).splitlines()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v93/', 'docs/warlock-repository/v86/publication/', 'docs/warlock-repository/v87/publication/', 'implementation/warlock-preview-provider-v118/', 'openspec/changes/warlock-preview-actor-retirement/tasks.md', 'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report118.json').read_text());assert qualification['sourceHeld'] and qualification['passed'] and qualification['singlePreviewPolicy'] and qualification['parentElmPolicyUnchanged'] and qualification['parentNativeIssuerAndPhysicalProductUnchanged'] and qualification['parentAssetsAndAdaptersUnchanged'] and qualification['nativeOwnedJavaScriptCore'] and qualification['persistentPolicyContexts']==1 and qualification['nativeElmOutboxChecks']==207 and qualification['additiveVisualProjectionChecks']==90 and qualification['readonlyProjectionChecks']==74 and qualification['lifetimeBoundaryChecks']==37 and qualification['readonlyBoundaryChecks']==15 and qualification['constructorFaults']==13 and qualification['backpressureChecks']==48 and qualification['backpressureReadonlyChecks']==28 and qualification['backpressureFactsSynthetic'] and qualification['lifetimeScenarios']==14 and qualification['lifetimeTraces']==26 and qualification['lifetimeStates']==430 and qualification['lifetimeCompiledNativeVariantsDetected']==5 and qualification['fullBuildCommands']==112 and qualification['originalBuildCommands']==112 and qualification['heldFailedReports']==[] and qualification['readonlyVisualCPUQualified'] and not qualification['realHostPolicyActivated'] and not qualification['actualRendererProjectionActivated'] and not qualification['actualDOMQualified'] and not qualification['projectionDeliveryOrderingQualified'] and not qualification['realHostInputBackpressureQualified'] and not qualification['nativeDelayedProposalLivenessQualified'] and not qualification['uncertainLiveWorkerRecoveryQualified'] and not qualification['fullElmRecoveryQualified'] and not qualification['typedHostRoutingActivated'] and not qualification['webKitActivated'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']
 message='Copy committed visual data from the native-owned Elm policy\n\n# Native read-only visual custody\n\nGUI118 adds a creator-owned getter returning a detached `g_malloc` string from\nthe last successfully processed private output. It copies only the six typed\nvisual fields. It calls no JavaScript and advances no policy, effect or ordinal.\nThe original policy implementation, native issuer and physical authority remain\nunchanged. A caller must free its copy and conceal on refusal.\n\nMissing owners/destinations refuse INVALID_INPUT; foreign threads refuse\nWRONG_THREAD; inflight or uncertain processing refuses PROCESSING_UNKNOWN;\nabsent or closed control authority refuses NO_VISUAL_AUTHORITY. Ordinary input\nbackpressure preserves the last committed projection. The getter neither accepts\nrefused inputs nor releases known jobs, proposals or physical resources.\n\nQualification retains the original207 native C/JSC controls plus90 visual\ncomparisons and adds74 read-only comparisons, with two native epochs, one\npersistent policy, two transport contexts and normal owned exits. Lifetime\nqualification retains37 original boundaries and13 pre-grant constructor faults,\nadds15 readonly boundaries, executes14 selected Quint scenarios and26 actual\nC/JSC traces/430 states with200 invariant samples, and detects five compiled\nnative guard variants. Caller-mutated copies do not alter subsequent reads.\nBackpressure retains48 original controls and adds28 exact visual comparisons;\nticket/terminal/close inputs in that fixture remain explicitly synthetic.\n\nThis is committed data custody, not a freshness or authenticated delivery channel.\nActual renderer leases, monotonic delivery, context/reload concealment, durable\nhost input/ticket custody, delayed proposal outcome/order and uncertain worker\nrecovery remain open. Actual WebKit/Core/DOM/URI/captured-resource acceptance and\nall original full release gates remain separate. The host route is inactive;\nNative130 GUI110 legacy2518/278 remains the actual bounded native baseline.\n'

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
