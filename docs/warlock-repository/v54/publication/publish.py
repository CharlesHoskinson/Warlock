"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='6d98bb1a385ae674b68820f163a50232c9c96861';BRANCH='refs/heads/feature/elm';COMMITS=['cd372c98502e57125b35dd62b3d57941fcccd648',args.source_commit]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v72/','docs/warlock-preview/v73/','docs/warlock-repository/v53/publication/','docs/warlock-repository/v54/publication/','implementation/warlock-preview-provider-v61/','implementation/warlock-preview-provider-v62/','implementation/warlock-preview-provider-v63/','implementation/warlock-preview-provider-v64/','implementation/warlock-preview-provider-v65/','implementation/warlock-client-provider-native-v106/','implementation/warlock-client-provider-native-v107/','implementation/warlock-client-provider-native-v108/','openspec/changes/warlock-preview-dynamic-enrollment/')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v73/report.json').read_text());assert qualification['passed'] and qualification['enrollmentCoupledStates']==577 and qualification['nativeChecks']==2416 and qualification['normalOwnedExits']==269 and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']
 message='Enroll native preview subjects without renewing original deadlines\n\nThe trusted dynamic C bridge admits bounded native subjects under the original receiver epoch, native grant and shared allocator. Retain original binding, incarnation, clock, publication, lease and deadline across unissued capacity; return typed local feedback without fabricated terminal proof or capture replay. Receiver validation, scope admission, membership and reservation share one native critical section. Exact known native rejected jobs remain owned for settlement; dedicated frontend rejection coverage is still open. Full optimized GUI65 build94/C34/intent27 and original physical/catalog/metadata controls pass. Eight selected Quint scenarios and24 implementation traces compare577 states and detect three unsafe mutants. Original intent6/demand10/delivery6/catalog8/metadata8 pass. Native108 on the exact owning core/plugin tuple passes2416 checks with269 normal owned exits and clean teardown, retaining all original1783 and2401 stable prior105 controls with the unchanged comparator. Its actual dynamic C probe passes95 controls for three real windows sharing two physical items, retained original waiting deadline, old GIO reader, explicit original journal membership, actual backend/mapping/FD/consumer cleanup and exact terminal ACK. Independent PNGs establish source identity. Four additive EARS requirements/eight scenarios preserve242/417/right-click24/48 and originalS09 identities. Failed model/compiler/preflight attempts retained. Ordinary eligible capture, fullS09/hardware and the coherent full release remain open. Main desktop and concurrent workers preserved.\n'
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
