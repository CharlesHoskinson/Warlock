"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='5ad30ad20254454a534adfa7ae0fee3eb7a3733c';BRANCH='refs/heads/feature/elm';COMMITS=[]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set();COMMITS=source(['rev-list','--reverse','dd836cb2b40daf793b41a5a6cd9f76253c69c911..'+head],text=True).splitlines()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v93/', 'docs/warlock-repository/v100/publication/', 'docs/warlock-repository/v101/publication/', 'implementation/warlock-preview-provider-v138/', 'implementation/warlock-client-provider-native-v165/', 'implementation/warlock-client-provider-native-v166/', 'implementation/warlock-client-provider-native-v167/', 'implementation/warlock-client-provider-native-v168/', 'openspec/changes/warlock-preview-actor-retirement/tasks.md', 'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report-gui138-current-failure.json').read_text());assert not qualification['passed'] and qualification['actualCurrentMatchingErrorNativeQualified'] and qualification['actualCurrentCancellationConsumedOnce'] and qualification['actualCurrentFailureStrictTeardownRefusalObserved'] and qualification['currentFailureNegativeControls']==22 and qualification['currentFailureExpectedExitCode']==1 and qualification['currentFailureOtherNormalOwnedExits']==7 and qualification['actualCurrentFailureDrainCounterexample'] and not qualification['gracefulCurrentFailureDrainQualified'] and qualification['actualCancelledOldResultQualified'] and qualification['cancelledOldResultNativeChecks']==36 and qualification['cancelledOldResultNormalOwnedExits']==13 and qualification['normalRouteNativeChecks']==29 and qualification['normalRouteNormalOwnedExits']==13 and qualification['retainedAsyncErrorScopeQuintScenarios']==10 and qualification['retainedAsyncErrorScopeInvariantSamples']==200 and qualification['currentErrorScopeCoupledCases']==4 and qualification['fullBuildCommands']==119 and qualification['nativeGrantResets']==0 and not qualification['physicalRevealQualified'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']
 message='Qualify current snapshot failure and retain native drain counterexample\n\nGUI138 adds disabled-by-default explicit current-snapshot real GCancellable/WebKit cancellation, with old-result retention disabled and readonly observation after existing matching-scope guard. Actual Native16622-control negative qualifies real image0/G_IO_ERROR_CANCELLED in original current view/epoch1/navigation/projection, original finish once/current failure branch exactly once, host1/no snapshot artifact; strict teardown refuses current accepted/known original duties, seven other owned processes normal/private cleanup. This is fail-closed/strict-refusal evidence, NOT normal exit, graceful failure drain or custody persistence after process death. Separately Native168 original same real current-error admission/result/failure/artifact controls fails mandatory drain oracle: current realm not closed/models still retained, no strict realm retirement and incomplete native teardown, original host1/seven normal/private cleanup. Fault teardown GLib/GObject criticals are retained evidence, not healthy release behavior. Unchanged normal16529/13 and canceled-old16736/13 positive regressions/full119 pass. Original single Elm policy/native issuer/physical products/sticky producer/scope guard/error reporting/deadlines unchanged; four current native outcomes coupled to explicit Quint cases pass, unchanged abstract Quint10/200 retained by exact source hash without rerun. Source held unqualified for mandatory failure drain. Next fresh139 actual failure quarantine/conceal/continued original native observations/receipts to strict close before failure exit1, with unchanged168 drain oracle and separate normal/old-result regressions; no false success/reset/Unknown settlement. All physical reveal/hardware/pressure/recovery/full S09/full release gates remain; installed drafts foreign preserved.'

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
