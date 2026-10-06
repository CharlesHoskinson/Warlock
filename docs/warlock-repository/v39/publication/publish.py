"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='c90b0e0d0ec861bd8a50e97b834b672a954e2dc9';BRANCH='refs/heads/feature/elm';COMMITS=['1ac8c2cd2553da0b4ff019c0b2fc9029f6e42b1a',args.source_commit]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v44/', 'docs/warlock-repository/v38/publication/', 'docs/warlock-repository/v39/publication/', 'implementation/warlock-core-family-crop-v3/', 'implementation/warlock-core-family-crop-v4/', 'implementation/warlock-family-style-revisions-v10/', 'implementation/warlock-family-style-revisions-v11/', 'implementation/warlock-family-style-crop-capture-v11/', 'implementation/warlock-family-style-crop-capture-v12/', 'implementation/warlock-client-provider-native-v69/', 'implementation/warlock-client-provider-native-v70/', 'implementation/warlock-client-provider-native-v71/', 'implementation/warlock-client-provider-native-v72/', 'openspec/changes/warlock-preview-applied-shaders/')
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
 tree=mirror(['write-tree'],env=env).decode().strip();published=mirror(['commit-tree',tree,'-p',BASE],input=b'Track actual applied screen shader input facts\n\nOwning corecrop3/4 compile two translation units with431 unchanged ordered archive members and preserved public object layouts. Fresh4 resets copied successful linked vertex/fragment facts with OpenGL-owner lifetime. Model10/11 pass425 compiled controls and41 explicitly selected Quint scenarios with160 coupled C++ states, retaining original coverage and exact bounded copied source/canonical unsupported recovery. Preserve failed collector11 namespace integration; collector12 compiles strong closure on exact corecrop4. Native69 new shader checks pass, but a later original GUI snapshot hits its unchanged six-second deadline after the intentional shader compile fault leaves a native reserved error bar;2130 checks/205 normal exits/clean teardown retained. Fresh70 restores only private fault-induced overlay/reserved geometry; it preserves a further original1636 identity failure from one extra dim poll, with2158 checks/206 normal exits/clean teardown. Fresh71 separates intermediate dim polls but preserves a missing original initial .3 read failure,2161 checks/206 normal exits/clean teardown. Fresh72 explicitly retains both original .3 initial/final observations and one original .6 applied observation within the same deadlines, then qualifies actual file-edit-without-reload stability, same-path successful reload changes, static identical reload stability, stale-context refusal before allocation, contextual-uniform refusal/recovery and failed/off program facts without buffer commits. Retain all1783 original assertions in order and all2136 prior native68 assertions as an ordered subsequence, normalizing only two runtime ASLR address suffixes while preserving raw labels and all original1783 names exactly. Additive WRLK-SHADER001-004 EARS/OpenSpec validate strictly. Actual full static/contextual shader pixels and output dependencies, backdrop blur/privacy, transforms/color/hardware, original preview13/restore38/recovery34/drag52, resources, AT/IME, journeys and coherent release remain open. No installed desktop changes.\n').decode().strip()
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
