"""Publish only committed owner paths over the existing GitHub history."""
import hashlib,json,os,pathlib,subprocess,tempfile,argparse
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');MIRROR=pathlib.Path('/home/hoskinson/omarchy-windows-parity-github.git');OUT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--source-commit',required=True);args=parser.parse_args()
BASE='48451e88124dd0ae9aa8e69f25e25c7ba8e82e05';BRANCH='refs/heads/feature/elm';COMMITS=[]
def source(args,**kw):return subprocess.check_output(['git',*args],cwd=REPO,**kw)
def mirror(args,**kw):return subprocess.check_output(['git','--git-dir='+str(MIRROR),*args],**kw)
head=source(['rev-parse',args.source_commit],text=True).strip();paths=set();COMMITS=source(['rev-list','--reverse','0ac8ba2f19859b7b1429dc106b6c36e74ee2bce2..'+head],text=True).splitlines()
for commit in COMMITS:paths.update(source(['diff-tree','--no-commit-id','--name-only','-r',commit],text=True).splitlines())
allowed=('docs/warlock-preview/v93/', 'docs/warlock-repository/v79/publication/', 'docs/warlock-repository/v80/publication/', 'implementation/warlock-preview-provider-v111/', 'openspec/changes/warlock-preview-actor-retirement/tasks.md', 'openspec/changes/warlock-preview-actor-retirement/specs/preview-actors/spec.md')
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
 qualification=json.loads((REPO/'docs/warlock-preview/v93/component-report111.json').read_text());assert qualification['sourceHeld'] and qualification['passed'] and qualification['nativeTicketRoundtripChecks']==93 and qualification['protocolChecks']==47 and qualification['nativeOutboxScenarios']==14 and qualification['nativeOutboxTraces']==26 and qualification['nativeOutboxStates']==463 and qualification['unsafeActualJSVariantsDetected']==6 and qualification['fullBuildCommands']==97 and len(qualification['heldFailedReports'])==3 and not qualification['rendererReloadRecoveryQualified'] and not qualification['webKitActivated'] and not qualification['nativeAcceptance'] and not qualification['fullReleaseAccepted']
 message='Retain native-issued renderer tickets and independent confirmation\n\nGUI111 adds `assets/native-preview-control-outbox.js`, a transport for exact\nnative-issued tickets. It never constructs a control command or assigns an\nordinal. Native purpose reservation/admission, immutable ticket issuance and\nthe existing controlled dispatcher remain the only effect admission route.\n\nThe outbox checks the exact original Native binding, receiver epoch, canonical\nuint64 strings, native ticket/enclosed packet correspondence, original4096-byte\nUTF8 bound and reserved queue capacity. It retains contiguous issued tickets\nas immutable raw strings. Retry posts only the oldest packet. Changed bytes,\ngaps, foreign domains and invalid receipts cannot advance its frontier.\nRepeated proposal advisories never remove a pending row. A trusted matching\nhead receipt advances only transport delivery and prepares an exact independent\nconfirmation string. Confirmation retries remain possible after the data queue\nempties. Callback guards avoid recursive data posts; the next host poll supplies\nprogress. No transport method certifies effect, physical or Elm settlement.\n\nThe constructor describes an empty fresh realm. The host must retain native\nownership across renderer reload and recover its exact retained tickets and\nprefix before resuming. A JavaScript object cannot survive destruction of its\nWebKit context; the source comment about retaining an object across reload is\nan integration obligation, not implemented reload recovery. Recovery remains\nan explicit unchecked OpenSpec task. This file is not loaded by popup.html.\n\nCurrent qualification:\n\n- `qa/native-outbox-check-v4-1791354355501494232/report.json`:93 sanitizer-backed\n  actual controlled C/Bootstrap/Native authenticated socket/Broker/ReceiptDelivery\n  checks through the actual JS transport. Two same-subject realm epochs use one\n  unchanged Native grant. Application-boundary lost posts, receipts and\n  confirmations retain original bytes. Actual native modified-ticket refusal,\n  exact duplicate receipt, physical job retained after delivery/confirmation,\n  native polling/proofs, terminal ACK, distinct scoped readiness/completion/final\n  processing/independent confirmation and strict close all pass. Old epoch\n  ticket refuses against the actual replacement C owner. Synthetic Native\n  subject21 remains Active; native peer and fixture exit normally.\n- `qa/native-outbox-protocol-check-1791354413823194560/report.json`:47 adversarial\n  protocol controls cover full uint64 binding/epoch beyond JS safe integers,\n  malformed/foreign/gap/changed tickets, UTF8 byte bound, capacity, immutable\n  retention, stale receipts, independent compact prefix and synchronous\n  callback reentry. Maximum data-post depth is1. Issuer is a synthetic fixture.\n- `qa/native-outbox-model-check-1791354287844124126/report.json`:14 explicitly\n  selected Quint scenarios,200 bounded samples,26 actual JS traces and463 state\n  comparisons. Retained frontier/observed receipt/queue occupancy, exact ordered\n  data attempts, independent confirmation attempts and operation results are\n  compared. Native issue/history/failure controls are trace-driver inputs and\n  are not reported as a second application policy or actual native issuer.\n  Six executable JS variants fail exact observations: changed bytes accepted,\n  advisory drains row, future receipt, dropped-post forget, dropped-confirmation\n  forget and capacity ignored. Actual C issuance is qualified separately above.\n\nThree failed fixture reports remain immutable: an unused shared fixture helper\nfailed `-Werror`; a diagnostic status used positive-wire counters for zero\nvalues and exited with retained ownership; a test mistook an unconfirmed native\nproposal for independently confirmed delivery. Fresh fixture derivatives use\nthe helper, encode zero-valued diagnostic counts as decimal strings, and test\nthe native distinction before/after actual independent confirmation. No product\nguard, native purpose, physical/proof barrier or original deadline was relaxed.\n\nExisting product native/src/adapter/assets files are byte-identical to held110\nexcept the added inactive outbox. Held110 resource/capture/control/FD/scoped\ndetachment evidence retains that parent source identity. Native130 current110\nlegacy host qualification passes2518/278/full cleanup and is public79\n48451e88124dd0ae9aa8e69f25e25c7ba8e82e05. This GUI111 component does not activate\ncontrolled host/Core/WebKit routes or establish actual Wayland-window, renderer\nreload, ordinary capture eligibility or full release acceptance.\n'

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
