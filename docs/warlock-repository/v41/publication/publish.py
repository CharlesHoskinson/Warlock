"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='53e1f9f6212fafea42b35950dd2b3776c42b28c5';BRANCH='refs/heads/feature/elm';COMMITS=['e3965577e36fabee72562a58a12a774fa03fb344',args.source_commit]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v46/', 'docs/warlock-repository/v40/publication/', 'docs/warlock-repository/v41/publication/', 'implementation/warlock-core-family-crop-v8/', 'implementation/warlock-core-family-crop-v9/', 'implementation/warlock-core-family-crop-v10/', 'implementation/warlock-core-family-crop-v11/', 'implementation/warlock-core-family-crop-v12/', 'implementation/warlock-family-style-crop-capture-v14/', 'implementation/warlock-family-style-crop-capture-v15/', 'implementation/warlock-family-style-crop-capture-v16/', 'implementation/warlock-client-provider-native-v76/', 'implementation/warlock-client-provider-native-v77/', 'implementation/warlock-client-provider-native-v78/', 'openspec/changes/warlock-preview-screen-coordinates/')
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
 tree=mirror(['write-tree'],env=env).decode().strip();published=mirror(['commit-tree',tree,'-p',BASE],input=b'Preserve native shader coordinates and resource phase admission\n\nNative76 preserves all1783 original assertions,2216 total checks and216 normal exits/clean teardown before its terminal crop-local coordinate mismatch:family21/28 versus independent native32/43. Preserve core8 missing-GIO fixture compile,9 reserved Quint action name,10 unparenthesized effect/typecheck,11 accepted nine selected Quint cases then failed Renderer GLFB namespace integration. Fresh12 fixes checked owning GL framebuffer casts, compiles Renderer/OpenGL with431 unchanged ordered archive members/exact relink/retained public layouts and exports. Nine explicitly selected Quint cases replay26 states through sanitized actual shaderPlanePlan and real producer Budget admission/exact bytes/RAII retirement; noninteger/NaN/dimension controls remain. Actual renderer uses isolated output-sized source/destination for native UV/texture/framebuffer coordinates, completes work and retires source before crop allocation, then performs exact cropped blit and completes work before destination retirement. Matching collector16 queries/rechecks native nominal phase peak and reserves under unchanged capacity before allocation, compiling exact owning closure; preserve collector14 optional README preparation stop and15 uncompiled precursor. Native77 matches coordinate32/43,passes2218/all1783/216 normal0 clean and prior whole identity/tint oracle. Native78 matches all76800 opaque root coordinate pixels in all four channels with zero mismatches/alpha errors,passes2217/all1783 exact/217 normal0 clean. Same compiled oracle detects76796 mismatches in held76 and zero in77 before native admission. Intermediate added nonoriginal readonly poll counts vary by scheduling; preserve raw labels/counts and every stable prior control, proving all1783 originals exact. Strict WRLK-SHADER-COORD001-004 EARS/OpenSpec validate. Full transparent family/decorations, off-output/context/neighborhood/backdrop/privacy, color/HDR/transform, measured GPU/driver budgets, hardware and every original preview13/restore38/recovery34/case34/drag52/input/AT/IME/journey/coherent release gate remain open. Main desktop/drafts preserved.\n').decode().strip()
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
