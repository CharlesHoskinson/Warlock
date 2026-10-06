"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='8d116438d092770eb2f6995778a181c58a4e9002';BRANCH='refs/heads/feature/elm';COMMITS=['3805b80b67b7f2fafe5f088ee99e82069b7fcb75',args.source_commit]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v57/', 'docs/warlock-preview/v58/', 'docs/warlock-preview/v59/', 'docs/warlock-preview/v60/', 'docs/warlock-repository/v48/publication/', 'docs/warlock-repository/v49/publication/', 'implementation/warlock-preview-provider-v44/', 'implementation/warlock-preview-provider-v45/', 'implementation/warlock-preview-provider-v46/', 'implementation/warlock-preview-provider-v47/', 'implementation/warlock-preview-provider-v48/', 'implementation/warlock-preview-provider-v49/', 'implementation/warlock-preview-provider-v50/', 'implementation/warlock-client-provider-native-v94/', 'implementation/warlock-client-provider-native-v95/', 'implementation/warlock-client-provider-native-v96/', 'implementation/warlock-client-provider-native-v97/', 'openspec/changes/warlock-preview-icon-lock-boundary/', 'openspec/changes/warlock-preview-icon-lock-delivery/', 'openspec/changes/warlock-preview-locked-snapshot-carrier/')
assert all(p.startswith(allowed) or (p.startswith('docs/elm-roadmap/delivery/build-loop-events/') and '--f6779148-8f5d-4bdf-8a0f-044184e486f2--' in p) for p in paths)
actual=source(['ls-remote','github',BRANCH],text=True).split()[0];assert actual==BASE
assert mirror(['rev-parse',BRANCH],text=True).strip()==BASE
rows=[]
for line in source(['ls-tree','-rz',head,'--',*sorted(paths)]).split(b'\0'):
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
 qualification=json.loads((REPO/'docs/warlock-preview/v59/report.json').read_text());assert qualification['passed'] and not qualification['fullReleaseAccepted']
 message='Verify native icon lock guards and same Elm concealed fallback ownership\n\nFull optimized shared GUI50 passes82 build commands,82 actual Elm metadata controls,74 GIO ownership checks,22 actual controller delay boundary controls and unchanged selected demand10/22traces564states/3mutants plus metadata8/16traces210states. Actual native97 retains all1783 originals/all2372 prior93 stable checks and verified normal exits. Actual held/new own icon streams refuse under real private lock before frontend policy, retaining charged physical reader/assets and original preview job. Exact locked denial reaches the same Elm, concealing title/icon before producer retirement. After normal GTK grab/wrapper destruction, one explicit private offscreen carrier keeps the same WebKit view for independently decoded bitmap evidence; it retires before original controller FIFO delivery. Original job/deadline/Release/physical retirement/ACK preserved. Failed GUI47/native94-96 and QA fixture/parser failures retained. Seven additive EARS/OpenSpec contracts preserve frozen242/417/originalS09 thirteen. Native bitmap/component evidence does not establish hardware presentation, ordinary production enrollment or full release. Main desktop and drafts preserved.\n'
 published=mirror(['commit-tree',tree,'-p',BASE],input=message.encode()).decode().strip()
 verified={}
 for line in mirror(['ls-tree','-rz',published,'--',*sorted(paths)]).split(b'\0'):
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
