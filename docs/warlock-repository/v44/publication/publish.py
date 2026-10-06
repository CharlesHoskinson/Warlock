"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='c16b84dad453aa0cf4337109afc5d23204271a4e';BRANCH='refs/heads/feature/elm';COMMITS=['4c5286186a62436bd873e5975299d471b6f15eec',args.source_commit]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v49/', 'docs/warlock-repository/v43/publication/', 'docs/warlock-repository/v44/publication/', 'implementation/warlock-client-provider-native-v84/', 'implementation/warlock-client-provider-native-v85/', 'implementation/warlock-core-family-crop-v13/', 'implementation/warlock-core-family-crop-v14/', 'implementation/warlock-core-family-crop-v15/', 'implementation/warlock-core-family-crop-v16/', 'implementation/warlock-family-style-revisions-v12/', 'implementation/warlock-family-style-crop-capture-v17/', 'implementation/warlock-generated-backdrop-fd-qualification-v1/', 'openspec/changes/warlock-preview-owned-backdrop-blur/')
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
 tree=mirror(['write-tree'],env=env).decode().strip();published=mirror(['commit-tree',tree,'-p',BASE],input=b'Render native family blur over declared owned generated backdrop\n\nPreserve native84 actual omission:2297 controls/all1783 original assertions/237 normal0 exits/clean; all76800 native body pixels change with brightness while family0 changes,76800 RGB delta mismatches. New owning core16 compiles Renderer/OpenGL and exact relink with431 ordered archive members/public layouts retained; actual generated-color/family full-output source, two private initialized blur scratch buffers and disabled monitor caches, GPU completion/scratch retirement before linked screen destination and crop. Nominal3-plane planner retains9+9 selected Quint runs/26+26 real Budget states under unchanged capacity; driver measurement remains open. Immutable model12 adds copied optional color:436 compiled controls/46 selected cases/181 states retain original425/41/160. Actual collector17 exact strong ABI closure exposes distinct authenticated generated scope/capture/state/retire plus FD4 plane256/color/crop/scale; compiled mapping retains legacy150/style295 and ownership/refusal checks. Native85 passes2307/all1783 exact/239 normal0/clean: unchanged delta oracle now76800 family/native changes,zero mismatch; stronger all76800 RGBA comparison in each brightness state haszero mismatch/alpha errors and independently unchanged tinted white. Legacy FD3 import/plane retirement refuse, original context/native two-second deadline/map-FD-export-producer retirement unchanged. Original transparent half-alpha/whole-crop/coordinate/full shared GUI controls retained. Strict7 WRLK-BACKDROP EARS/OpenSpec validate. Preserve failed core13 preparation/core14 runner/core15 namespace compile. This bounded generated-background projection does not qualify arbitrary wallpaper/layer/foreign authorization/provenance/privacy, general shader/CM/HDR/transforms/GPU-driver/hardware/resources or original coherent release gates; new mode shared GUI integration remains next. Main desktop/drafts preserved.\n').decode().strip()
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
