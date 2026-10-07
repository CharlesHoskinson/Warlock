"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='78170391db233cbfd6b43d6361622bf742cb79dd';BRANCH='refs/heads/feature/elm';COMMITS=[]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set();COMMITS=source(['rev-list','--reverse','43498757f42a4fa785d2ff7d04a35e8de8f6ffd7..'+head],text=True).splitlines()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v93/', 'docs/warlock-repository/v90/publication/', 'docs/warlock-repository/v91/publication/', 'implementation/warlock-preview-provider-v121/', 'openspec/changes/warlock-preview-actor-retirement/tasks.md', 'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report121.json').read_text());assert qualification['passed'] and qualification['positiveChecks']==2261 and qualification['lateQuarantinedOutputChecks']==2269 and qualification['pressureChecks']==2270 and qualification['preGrantFaultChecks']==9 and qualification['fullBuildCommands']==116 and qualification['originalBuildCommands']==116 and qualification['driverScenarios']==8 and qualification['driverSamples']==200 and qualification['coupledTraces']==8 and qualification['observableStatesCompared']==48 and qualification['compiledNativeVariantsDetected']==2 and qualification['normalOutputReservationUnderHeldProducerContractQualified'] and not qualification['nativeOutputQueueResourceBoundQualified'] and not qualification['realHostPolicyActivated'] and not qualification['actualRendererProjectionActivated'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']
 message='Reserve retained native output before effects and prioritize admitted events\n\n# Normal native output custody\n\nGUI121 reserves one batch and 8192 bytes before original native effect dispatch.\nNormal returned custody is capped at 3195 batches/26173440 wire bytes under the\nheld original C producer contract. An exact ticket remains retained on WOULD_BLOCK.\nOriginal returned events are admitted before further effect output whenever the\nunchanged original deferred-input gate permits it. Issued-ticket notification and\nindependent native confirmation retain their original precedence and authorities.\n\nOriginal dispatch paths return two fixed offer/fence events on acquisition,\none next original scoped/permanent completion on retirement/detachment/final ACK,\nand no event on reconcile, physical cancel/release or terminal ACK. Maximum-field\ntests run original serializers/journals with UInt64 maximums and the fixed\n64-character token. Their journal ordinal calculation includes the maximum 20\ndecimal digits analytically. This is source/serializer evidence, not actual Core.\n\nThe positive actual Native/C/JSC roundtrip uses the existing FD-capable authenticated\nsynthetic peer: a sealed SCM_RIGHTS image is mapped by original C, two original\nevents are retained, then separately admitted to the single policy drawable state.\nThis is an actual synthetic-provider FD, not actual Core/window/pixel/DOM evidence.\nThe first failed positive run used a JSON-only peer without an image socket; that\noriginal failure and its source closure are retained. The refusal oracle remains.\n\nA labeled compiled stricter reservation gate exercises refusal before any effect,\nexact ticket retention, quarantine through that pressure and release of the same\nticket once. Its numerical boundaries use the actual compiled reservation predicate.\nIt does not fill the real output queue. Eight explicitly selected Quint first-ticket\nscenarios and 200 samples compare actual Native/C issuance/delivery/confirmation,\ncapture counts/charge/terminal status and original JSC demand/known duties. Every\nselected trace drains original obligations and closes normally. That scoped model\ndoes not prove the full lifecycle or full-workload resource/progress behavior.\n\nUnexpected original producer-contract violations retain exact outcome/ticket/\nreceipt custody as live Unknown. They are not truncated, reset or called normal\nbounded success. Live uncertain recovery and process-loss journaling remain open.\n\nThe current full legacy host links this driver but does not create it or activate\nthe pure renderer. Original issuer/effects/physical product, Elm policy and existing\nassets/adapters remain unchanged. Native131 is the actual GUI119 legacy/core16/\nplugin19/AQ155 baseline 2518/278. No installed/main-desktop/draft/foreign changes.\n\nNext actual controlled host integration: fixed native renderer initialization after\noriginal GTK admission, retained producer batches and paused polling, WebKit callback\ncontext/lease authentication, async DOM/frame and physical concealment barriers,\nand original URI reader ownership. Full-workload progress/RSS/pacing, delayed\nnever-issued proposal outcomes, uncertain live/process recovery and all original\nfull release S01–S16/right-click gates remain required.\n\nThe late-output roundtrip2269 quarantines before admitting retained offer/fence.\nBoth remain concealed and original physical/journal/confirmation duties drain to\nnormal closure. Two unsafe compiled derivatives remove reservation or output\npriority; unchanged original oracles must reject them without a normal-close claim.\nThe first guard runner expected the wrong assertion text after the correct native\nassertion fired; that failed runner and source snapshot remain retained.\n'

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
