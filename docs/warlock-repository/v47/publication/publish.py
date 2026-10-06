"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='21709db2c149b64ad6cf50ddb342198f7ccf174b';BRANCH='refs/heads/feature/elm';COMMITS=['b0658985040e207f5c5191b1307761dbc5704c1f',args.source_commit]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v52/', 'docs/warlock-preview/v53/', 'docs/warlock-repository/v46/publication/', 'docs/warlock-repository/v47/publication/', 'implementation/warlock-preview-provider-v37/', 'implementation/warlock-preview-provider-v38/', 'implementation/warlock-client-provider-native-v89/', 'implementation/warlock-client-provider-native-v90/', 'implementation/warlock-client-provider-native-v91/', 'implementation/warlock-client-provider-native-v92/', 'openspec/changes/warlock-preview-native-address-reuse/')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v53/report.json').read_text());assert qualification['passed'] and not qualification['fullReleaseAccepted']
 message=('Qualify preview lease isolation under actual native window address reuse\n\nFull shared GUI38 compiles optimized Elm Main/Bar/Popup and the native host:77 commands,15 private-control boundary checks, original36 compiled demand checks/10 selected Quint cases/300 samples/22 traces/564 states/3 mutants. Native92 passed '+str(qualification['nativeControls'])+' assertions including all1783 original identities and the stable native88 assertions; '+str(qualification['normalOwnedExits'])+' owned normal exits and ordered cleanup. The actual replacement reuses the old native address with a fresh incarnation before original expiry. Both held and new URI reads refuse before native polling/Elm cleanup while'+qualification['addressReuseEvidence']['beforePolicyProbe']['status']['charge']+' original bytes stay charged. Actual WebKit before/after popup has'+str(qualification['addressReuseEvidence']['webkitPixels'][0]['styledRoot'])+'/'+str(qualification['addressReuseEvidence']['webkitPixels'][1]['styledRoot'])+' old source pixels; original mapping/FD/export/producer retirement precedes exact terminal ACK and physical0/journal0. GUI37 missing toolchain, native89 stale quit stimulus and native90/91 raw-pointer/poll comparison failures retained. Four additive EARS/OpenSpec contracts preserve frozen242/417 and originalS09 identities. The complete13-case preview/product fidelity and broader GUI release gates remain open; main desktop and user drafts preserved.\n')
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
