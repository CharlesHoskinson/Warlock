"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='822dee9f18a3240679dabcb9b9788f30916545bc';BRANCH='refs/heads/feature/elm';COMMITS=['3ac23aab2dcc2efe5fdfc3fc6274a6dca83f6be8',args.source_commit]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v62/', 'docs/warlock-preview/v63/', 'docs/warlock-preview/v64/', 'docs/warlock-preview/v65/', 'docs/warlock-preview/v66/', 'docs/warlock-preview/v67/', 'docs/warlock-preview/v68/', 'docs/warlock-repository/v50/publication/', 'docs/warlock-repository/v51/publication/', 'implementation/warlock-preview-provider-v52/', 'implementation/warlock-preview-provider-v53/', 'implementation/warlock-preview-provider-v54/', 'implementation/warlock-client-provider-native-v98/', 'implementation/warlock-client-provider-native-v99/', 'implementation/warlock-client-provider-native-v100/', 'implementation/warlock-client-provider-native-v101/', 'openspec/changes/warlock-preview-product-enrollment/')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v68/report.json').read_text());assert qualification['passed'] and qualification['nativeControls']==2392 and not qualification['fullReleaseAccepted']
 message='Enroll ordinary picker windows through the own native catalog in Elm\n\nThe normal host correlates its own authenticated native catalog with current ordinary picker controls under one immutable Elm policy. Metadata-only rows retain exact minimized facts without fabricated Scope/clock/job/privacy/capture authority. Only actual source seeds promote native lifecycles; inventory closure retains original jobs, deadlines, accepted historical resources and late cleanup/ACK. Full optimized shared GUI54 build86, catalog60/decoder26, selected catalog8/16 traces214 states, metadata8/16 traces210 states and demand10/22 traces564 states/3 mutants pass. Actual native101 passes2392 controls including all1783 originals/all2380 stable prior97 controls,260 normal exits and clean teardown. Real pointer opens the normal two-window picker without fixed preview subjects, and the actual Elm renders unavailable entries with no capture start. Existing native shader/blur/source-loss/address-reuse/title/icon/lock/physical-retirement oracles retained. Failed52/53/native98/100 and unused99 preparation retain evidence. Original242/417/S09 thirteen unchanged; eligible multi-entry physical capture, hardware and full release remain open. Main desktop and concurrent workers preserved.\n'
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
