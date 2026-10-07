"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='0670a4500e3b668285b43e163adda958d1996f82';BRANCH='refs/heads/feature/elm';COMMITS=[]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set();COMMITS=source(['rev-list','--reverse','d7ff0259f7a6bf3783ee44d45d48966ce604e0ba..'+head],text=True).splitlines()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v93/', 'docs/warlock-repository/v82/publication/', 'docs/warlock-repository/v83/publication/', 'implementation/warlock-preview-provider-v114/', 'openspec/changes/warlock-preview-actor-retirement/tasks.md', 'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report114.json').read_text());assert qualification['sourceHeld'] and qualification['passed'] and qualification['singlePreviewPolicy'] and qualification['nativeElmOutboxChecks']==192 and qualification['packetizerChecks']==43 and qualification['ingressScenarios']==12 and qualification['ingressTraces']==22 and qualification['ingressStates']==300 and qualification['unsafeCompiledNativeVariantsDetected']==5 and qualification['fullBuildCommands']==104 and qualification['originalBuildCommands']==103 and qualification['resourceRegressionSuites']==4 and qualification['scopedRegressionSuites']==4 and len(qualification['heldFailedReports'])==1 and not qualification['proposalRetentionQualified'] and not qualification['popupTypedPortsWebKitExecuted'] and not qualification['fullElmRecoveryQualified'] and not qualification['typedHostRoutingActivated'] and not qualification['webKitActivated'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']
 message='Validate native proposal ingress and compile typed Popup realm ports\n\nGUI114 adds an exact native realm proposal entry point and a pure ordered\nsingleton packetizer. Native validates the original creator thread, popup,\nborrowed delivery capability, binding and receiver epoch before passing a\nsingleton command to the existing purpose issuer. Refused malformed, foreign,\naggregate or oversized envelopes consume no ticket ordinal and cannot mutate\nthe original broker job. Exact duplicates retain original native ticket bytes.\n\nActual Popup now delegates decoded realm grant, event, quarantine and close\nports to the existing single immutable PreviewPresenter. The full host build\ncompiles this Popup; its typed ports have not yet executed in actual WebKit.\nThe actual coupled policy witness is the optimized ScopedPreviewPresenterReplay\nworker, the current C Bootstrap/Native with an authenticated synthetic peer,\nthe pure packetizer and the existing native-issued recovered JS transport.\n\nCurrent qualification:192 native/Elm/transport checks across two receiver\nepochs with no Native grant reset, the same synthetic Active subject and normal\nowned exits;43 pure packetization boundary checks;12 explicitly selected Quint\nscenarios,22 actual compiled C traces,300 state comparisons,200 bounded samples\nand five detected compiled native admission variants. The104-command build\nretains all103 original commands. All four original resource and four scoped\ndetachment regression suites pass on this changed native source. One failed\nmodel runner attempt remains:its aggregate mutation anchor matched two guards,\nso it refused before mutating or compiling that variant. The fresh runner uses\nthe exact new ingress guard, preserving product code and original oracle.\n\nLegacy popup HTML, adapter and shared-host route remain unchanged. The new\npacketizer is not loaded by that HTML and controlled routes remain inactive.\nNative-issued ticket recovery cannot recover an Elm proposal lost before native\nissuance. GUI115 must retain original proposal intents in the same immutable\nElm policy before emission, qualify exact native issuance correlation and retry,\nand preserve separate delivery, processing, confirmation and physical barriers.\nActual host routing, WebKit ownership/context loss, full Elm policy recovery,\nCore captured FD/render/fence/readers and real window detachment remain open.\nNative130 with GUI110 legacy/core16/plugin19/AQ155 remains the bounded actual\nnative baseline:2518 checks,278 normal owned exits and full cleanup. No actual\nGUI114 Wayland-window acceptance or full release acceptance follows. No installed\ndesktop or draft changes;five foreign tracked changes remain preserved.\n'

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
