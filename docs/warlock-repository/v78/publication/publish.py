"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='33f0afa16104467c36dc8aea9a75d028a0d55aef';BRANCH='refs/heads/feature/elm';COMMITS=[]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set();COMMITS=source(['rev-list','--reverse','25efdc897243360a0e4878036b1768418902f2b6..'+head],text=True).splitlines()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v93/', 'docs/warlock-repository/v77/publication/', 'docs/warlock-repository/v78/publication/', 'implementation/warlock-preview-provider-v110/', 'openspec/changes/warlock-preview-actor-retirement/tasks.md', 'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report110.json').read_text());assert qualification['sourceHeld'] and qualification['passed'] and qualification['uriCChecks']==66 and qualification['uriActualSealedFDs']==4 and qualification['uriCCompiledVariants']==3 and qualification['uriScenarios']==16 and qualification['uriTraces']==24 and qualification['uriStates']==320 and qualification['uriInvariantSamples']==200 and qualification['currentDetachmentCChecks']==77 and qualification['currentDetachmentStates']==715 and qualification['fullBuildCommands']==96 and len(qualification['heldFailedReports'])==2 and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']
 message="Guard native URI callbacks with exact Endpoint lifetime and receiver epoch\n\nGUI110 implements native lifetime-safe URI read capabilities and a stable\nreference-counted C router. The new WebKit dispatcher compiles and is inactive;\nthe existing shared-host legacy installation/activation remains unchanged.\n\nA capability holds weak references to the original Shared state and a distinct\nEndpoint lifetime, plus its exact Native binding, receiver identity and epoch.\nEach open validates that domain under the original Shared mutex before creating\na reader. The Endpoint destructor revokes its lifetime under that same mutex.\nExisting readers retain physical Shared/mapping storage, but their own lifetime\nand receiver guards refuse bytes after destruction or replacement. Original\nBroker token/nonce, native time/source/privacy, expiry, reader capacity and\nphysical/proof barriers remain in the common original open implementation.\nCapabilities and router references cannot pin physical storage by themselves.\n\nThe C router retains its creator GThread identity, original binding and monotonic\nrealm frontier. Same exact live capability binding is idempotent. Clear retains\nhistory; same/old or foreign realm binding refuses before changing the route.\nA trusted greater epoch can bind a new capability. The context can hold its own\natomic reference independently of the native owner's reference; clear and owner\nunref leave a valid denying callback object. Actual WebKit registration must\nretain that independent reference and release it in its context destroy notify.\nNo raw Endpoint is needed by the new dispatcher. Current legacy handler remains\ncompatible and keeps its original clear/unregister-before-destruction contract.\n\nCurrent evidence:\n- 66 sanitizer-backed actual C router/read capability/Endpoint/Broker/GIO checks.\n  Four real sealed memfd mappings close. Tests exercise stale receiver/URI,\n  same-Shared receiver replacement, foreign Native binding and creator thread,\n  Endpoint destruction with retained reader, byte revocation before physical\n  close, expiry, router clear/frontier and independent callback reference.\n  Three separately compiled unsafe variants fail exact original assertions:\n  ignoring captured receiver epoch, resetting router frontier on clear, allowing\n  existing reader bytes after Endpoint destruction. These are direct synthetic\n  native scope/signature-byte fixtures, not actual compositor capture/WebKit.\n- 16 explicitly selected Quint scenarios, 200 bounded invariant samples,\n  24 actual compiled C traces and 320 state comparisons. Actual endpoint\n  existence/receiver epoch, current callback open outcome, existing reader/epoch,\n  returned byte count/EOF position, real FD ownership, expiry, owner-reference\n  presence and operation result are compared after every event. Router route/\n  through are protocol ghosts excluded from comparison. Every successful trace\n  clears references and closes its actual mapped descriptors.\n- The full host build passes96 commands: every original95 plus the new router\n  translation unit. All original resource/capture/ticket/FD regressions pass\n  against current changed URI source. Scoped detachment C77/resource60+64+51/cohort66/model21/33/715\n  regressions also pass on this current changed URI source, retaining the two\n  resource guard variants and five model guard variants.\n\nTwo failed model fixtures remain: the initial runner required a missing separate\nnamed-test file, and its fresh replacement encountered nested main renaming and\nan unqualified Wire name. Fresh immutable model/fixture derivatives retain those\nfailures and add explicit returned-byte/EOF comparisons. No product guard,\noriginal assertion or deadline was relaxed.\n\nActual native baseline remains GUI92/native129/core16/plugin19,2517 checks/278\nnormal owned exits/full cleanup. GUI110 controlled path and its new router are\nnot activated in that baseline. Next qualify current compiled GUI110 legacy\nroutes on the same owning native tuple, then actual WebKit context callback\nownership/replacement with typed incoming/outgoing realm wrappers and retained\nnative renderer ticket outbox. Scoped Core/Wayland-window detachment/capture,\n>256 real windows/Elm neighbors and all original preview13/restore38/recovery34/\ncase34/two-second/cursor/drag52/input/popup/hardware/output/AT/IME/budget/journey/\ncoherent release/reversible deployment gates remain. No installed config, main\ndesktop or drafts changed.\n"

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
