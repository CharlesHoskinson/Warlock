"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='3cd4db6f232d185d8655de3b76106b2229da7272';BRANCH='refs/heads/feature/elm';COMMITS=[]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set();COMMITS=source(['rev-list','--reverse','b0fbf91cc20661423c9f3b29784686f1b5e3c518..'+head],text=True).splitlines()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v91/', 'docs/warlock-preview/v93/', 'docs/warlock-repository/v64/publication/', 'docs/warlock-repository/v65/publication/', 'implementation/warlock-preview-provider-v93/', 'openspec/changes/warlock-preview-actor-retirement/tasks.md', 'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report.json').read_text());assert qualification['passed'] and qualification['buildCommands']==95 and qualification['readinessNativeElmControls']==54 and qualification['readinessScenarios']==8 and qualification['readinessTraces']==20 and qualification['readinessStates']==384 and qualification['unsafeCompiledNativeMutantsDetected']==3 and qualification['unchangedElmAssetIdentityVerified'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']
 message='Retain exact Elm readiness until native receiver barriers clear\n\nHeld GUI93 retains validated readiness in its existing bounded native journal row, preserving original receiver epoch/binding and all physical/proof/receiver barriers. Native polling retries the retained input without another Elm effect or replay of capture/release/terminal ACK. Current full95 build and byte-identical Elm assets pass45 processing-prefix controls. Actual C/socket/native/compiled Elm54 controls validate a real second receiver barrier, completion after it clears without another readiness effect, lost final delivery and processing ACK, original neighbor/counter and normal confirmed close. Eight explicitly selected Quint scenarios/200 sampled30-step runs match20 actual C++ journal traces/384 states, and three separately compiled native mutations fail exact witnesses. Preserve reserved-name Quint and fake-clock fixture failures. This journal is transport metadata; trusted commit is not a physical proof or a second Elm policy. The fully qualified runtime remains GUI92/native128/core16/plugin18 with2466 checks/277 normal exits and all original gates. GUI93 readiness API is not yet wired through WebKit. Bounded outgoing control delivery/retry/ACK, cleanup reservation, reload/namespace/fairness/budgets, actual host retirement routing, captured resources, >256 real windows and all original GUI release gates remain open.\n'

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
