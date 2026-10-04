import hashlib,json,os,resource,stat
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
components=[]
for name,count in [('elm-shared-held-context-fixture-v170',53),('elm-shared-held-key-host-v171',357)]:
 p=REPO/'implementation'/name/'component-manifest.json';m=json.loads(p.read_text());assert m['passed'] and len(m['files'])==count and not m['nativeAcceptance']
 for row in m['files']:
  value=p.parent/row['path']
  if 'symlink' in row:assert value.is_symlink() and os.readlink(value)==row['symlink']
  else:assert sha(value)==row['sha256']
 assert sha(m['buildReport'])==m['buildReportSHA256'] and json.loads(Path(m['buildReport']).read_text())['passed']
 components.append({'path':str(p),'sha256':sha(p),'files':count})
runtime=REPO/'implementation/elm-shared-held-runtime-v169';pair=json.loads((runtime/'qa/build-pair-manifest.json').read_text())
assert (runtime/'candidate_host.py').read_bytes()==(REPO/'implementation/elm-shared-keyboard-runtime-v435/candidate_host.py').read_bytes()
for name,digest in pair['files'].items():assert sha(runtime/name)==digest
for row in pair['nativePair'].values():assert sha(row['path'])==row['sha256']
case=REPO/'implementation/elm-shared-held-menu-focus-v180';paths=list((case/'qa').glob('native-*/report.json'));assert len(paths)==1
p=paths[0];r=json.loads(p.read_text());assert r['passed'] and r['cleanupPassed'] and not r['mainDesktopActions'] and r['pair']==pair['nativePair']
assert len(r['checks'])==83 and all(v['passed'] for v in r['checks'])
for path,digest in r['inputs'].items():assert sha(path)==digest
for rel,digest in r['artifacts'].items():assert sha(p.parent/rel)==digest
flight=case/'qa/preflight.json';pre=json.loads(flight.read_text());assert pre['passed'] and r['preflightSHA256']==sha(flight)
for path,digest in pre['inputs'].items():assert sha(path)==digest
h=r['privateHost'];aq=h['privateAquamarine'];assert aq['mappedVerified'] and aq['path']==pair['nativePair']['aquamarine']['path'] and aq['sha256']==pair['nativePair']['aquamarine']['sha256']
assert aq['mappedFiles']=={aq['path']:aq['sha256']}
assert h['runtimeGone'] and not h['cleanupErrors'] and not h['remainingDescendants'] and not h['unexpectedInnerDescendants']
loss=r['heldMenuLoss'];assert loss['kind']=='focus' and loss['cancellation']['keys']==loss['cancellation']['bindKeys']==[] and loss['cancellation']['mods']==0
assert sorted(v['hardware'] for v in loss['gtkReleases'])==[50,76] and all(v['type']==9 and v['send']==0 and v['popup']==1 for v in loss['gtkReleases'])
assert len({v['engine'] for v in loss['gtkReleases']})==1 and len(loss['freshPair'])==4
native={'path':str(p),'sha256':sha(p),'checkExecutions':83}
failures=[]
for name,error in [('elm-shared-held-menu-capability-v175',"AssertionError('protocol7F10RefusedAfterEligibleAPair')"),('elm-shared-held-menu-capability-v177',"AssertionError('heldF10ActuallyOpensCoherentElmMenu')"),('elm-shared-held-menu-capability-v179',"RuntimeError('Unchanged observation deadline')")]:
 p=next((REPO/'implementation'/name/'qa').glob('native-*/report.json'));v=json.loads(p.read_text());assert not v['passed'] and v['cleanupPassed'] and v['error']==error
 failures.append({'path':str(p),'sha256':sha(p),'error':error,'cleanupPassed':True})
for name in ['elm-shared-held-context-fixture-v167','elm-shared-held-key-host-v168']:
 p=REPO/'implementation'/name/'component-manifest.json';v=json.loads(p.read_text());assert v['passed'] and not v['files']
 failures.append({'path':str(p),'sha256':sha(p),'error':'Rejected empty source inventory by172; compiled build proof remains separate'})
review=REPO/'implementation/elm-shared-held-freeze-review-v172/review.json';assert json.loads(review.read_text())['passed'] is False
roots=['elm-shared-held-context-fixture-v167','elm-shared-held-key-host-v168','elm-shared-held-runtime-v169',
 'elm-shared-held-context-fixture-v170','elm-shared-held-key-host-v171','elm-shared-held-freeze-review-v172',
 'elm-shared-held-menu-capability-v173','elm-shared-held-menu-focus-v174',
 'elm-shared-held-menu-capability-v175','elm-shared-held-menu-focus-v176',
 'elm-shared-held-menu-capability-v177','elm-shared-held-menu-focus-v178',
 'elm-shared-held-menu-capability-v179','elm-shared-held-menu-focus-v180',
 'elm-native-escape-current-proof-v181','elm-shared-held-menu-evidence-v182']
files=[]
for name in roots:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  if p==ROOT/'acceptance-manifest.json':continue
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if p.is_symlink():row['symlink']=os.readlink(p)
  elif stat.S_ISREG(st.st_mode):row.update(sha256=sha(p),size=st.st_size)
  elif p.is_dir():continue
  else:raise RuntimeError('Runtime special file '+str(p))
  files.append(row)
assert len(files)>800
result={'schema':1,'passed':True,'nativeAcceptance':True,'keyboardFocusLossAcceptance':True,'keyboardCapabilityLossAcceptance':False,'releaseAcceptance':False,'scope':'Bounded real shared Elm held ShiftF10 keyboard focus-loss83 on compiled QA-key-receipt GUI171/fixture170/Core89/plugin409/AQ155. Capability case179 failed original early Escape before loss; stale DOM/current native publication race remains. Full roadmap/hardware/ATIME/physical/release open.','nativePair':pair['nativePair'],'components':components,'nativeReports':[native],'nativeCheckExecutions':83,'retainedFailures':failures,'files':files}
with (ROOT/'acceptance-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(ROOT/'acceptance-manifest.json'),'sha256':sha(ROOT/'acceptance-manifest.json'),'files':len(files),'focusLossCheckExecutions':83,'capabilityLossAcceptance':False}))
