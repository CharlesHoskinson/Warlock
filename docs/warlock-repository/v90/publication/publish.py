"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='520fdcc920b48de72672c7864ba291d5fb2442bf';BRANCH='refs/heads/feature/elm';COMMITS=[]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set();COMMITS=source(['rev-list','--reverse','88f77a78184a5676ae666052c7766a9d84b2e0d4..'+head],text=True).splitlines()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v93/', 'docs/warlock-repository/v89/publication/', 'docs/warlock-repository/v90/publication/', 'implementation/warlock-preview-provider-v120/', 'openspec/changes/warlock-preview-actor-retirement/tasks.md', 'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report120.json').read_text());assert qualification['passed'] and qualification['driverChecks']==2250 and qualification['preGrantFaultChecks']==9 and qualification['fullBuildCommands']==116 and qualification['originalBuildCommands']==115 and qualification['driverScenarios']==14 and qualification['driverSamples']==200 and qualification['compiledNativeVariantsDetected']==4 and qualification['nativeTicketCustodyCPUQualified'] and qualification['independentNativeConfirmationCPUQualified'] and not qualification['nativeOutputQueueResourceBoundQualified'] and not qualification['realHostPolicyActivated'] and not qualification['actualRendererProjectionActivated'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']
 message='Retain original native inputs and issued tickets in the policy driver\n\n# Native policy driver\n\nGUI120 connects the original persistent native JavaScriptCore Elm policy to the\nunchanged native-issued outbox in its own private transport context. The creator\nowns atomic typed input custody, original epoch stamping, exact native ticket\ncustody before issuance notification or dispatch, deferred native callbacks and\nindependent receipt confirmation. Native issuer, original Elm lifecycle, C\ndispatcher and original physical/journal/terminal/closure authorities are unchanged.\n\nOrdinary input custody holds at most 1065 items and 16 MiB of serialized wrapped\nbytes. Refused batches remain with their producer; the eventual host must stop\npolling until admission. Urgent native quarantine bypasses full ordinary custody.\nRetaining input runs no policy, issuance or effect. A step performs one action;\ncallbacks only retain bytes. Native returned events occupy separate custody so\nordinary queue pressure cannot erase them. Their aggregate resource bound and\nfull-workload progress remain unqualified and required before host activation.\n\nThe controlled original owner must have one driver. Constructor faults before\nadmission cleanly release their own contexts and registry entries. A non-null\nhandle with an admission error preserves uncertain live custody; callers must\nretain it. An uncertain driver cannot normally close or be reconstructed. The\noriginal grant cannot reset. Process-owned RAM survives renderer replacement,\nbut is not a process-loss journal or accepted crash recovery.\n\nThe actual C/JSC campaign uses the original native issuer, Bootstrap, broker,\nreceipt journal and authenticated synthetic peer. It qualifies input item/byte\nrefusal, constructor faults, foreign creators/epochs, atomic batches, ticket\nstages, independent confirmation, Unknown capture/resource retention, scoped\ndetachment and strict normal ownership teardown. Explicit Quint custody scenarios\nand compiled native guard variants supplement this bounded component evidence.\nThe custody abstraction does not replace or prove the original lifecycle model.\n\nThe current full host links the driver and keeps the legacy browser route. It\ndoes not instantiate this driver or the pure renderer. No real Core/window,\ncaptured FD/pixel, WebKit callback authentication, DOM/frame, physical concealment\nor actual URI acceptance follows. Native131 remains the current actual legacy\nbaseline on core16/plugin19/AQ155, retaining original controls and deadlines.\n\nNext qualify the retained output bound and producer schedule, then integrate the\ncontrolled driver with actual native renderer grants, original GTK admission,\nWebKit identity/leases, stale async barriers, physical concealment/frame and URI\nownership. Original delayed never-issued proposal expiry/revocation outcomes,\nlive uncertain policy/process recovery, S02 measured budgets and every S01–S16\nfull release gate remain open. Installed desktop, drafts and foreign paths stay\npreserved.\n\n\nBounded Native/C/JSC component2250 + constructor faults9; explicit custody Quint14/200 samples/six concrete ordered witnesses/four compiled guards; full116 retains115. Original parent policy/native issuance/effects/physical/assets/adapters unchanged. Output resource bound, actual host/pure renderer/WebKit/Core/URI and full release gates remain open; no installed changes.'

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
