import hashlib,json,os,resource,stat
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
aq=REPO/'implementation/elm-parent-held-key-cancellation-v138';component=aq/'component-manifest.json'
c=json.loads(component.read_text());assert c['passed'] and not c['nativeAcceptance']
for row in c['files']:
 p=aq/row['path']
 if 'symlink' in row:assert p.is_symlink() and os.readlink(p)==row['symlink']
 else:assert sha(p)==row['sha256']
b=json.loads(Path(c['buildReport']).read_text());assert b['passed'] and b['publicHeadersUnchanged'] and not b['missingParentSymbols']
assert sha(c['buildReport'])==c['buildReportSHA256'] and sha(b['library'])==b['librarySHA256']
lib=Path(b['library']).resolve();libsha=b['librarySHA256'];native=[]
cases=[('elm-held-key-cancellation-native-v147',37)]+[(f'elm-held-key-cancellation-masks-v148/mask-{i}',38) for i in range(1,4)]+[
 ('elm-held-key-cancellation-input-v141',159),('elm-held-key-cancellation-geometry-v142',96),
 ('elm-held-key-cancellation-unheld-v143',26),('elm-held-key-cancellation-pointer-v144',35)]
tuple_expected=json.loads((REPO/'implementation'/cases[0][0]/'aq-tuple.json').read_text())
assert tuple_expected=={'manifest':str(component),'manifestSHA256':sha(component),'library':str(lib),'librarySHA256':libsha}
for name,count in cases:
 root=REPO/'implementation'/name;reports=list((root/'qa').glob('native-*/report.json'));assert len(reports)==1
 p=reports[0];r=json.loads(p.read_text());assert r['passed'] and r['cleanupPassed'] and r['mainDesktopActions'] is False
 assert len(r['checks'])==count and all(v['passed'] for v in r['checks'])
 for path,digest in r['inputs'].items():assert sha(path)==digest,path
 for rel,digest in r['artifacts'].items():assert sha(p.parent/rel)==digest,rel
 assert json.loads((root/'aq-tuple.json').read_text())==tuple_expected
 h=r['privateHost'];actual=h['privateAquamarine']
 assert actual['mappedVerified'] is True and actual['path']==str(lib) and actual['sha256']==libsha
 assert actual['mappedFiles'].get(str(lib))==libsha and actual['contractManifestSHA256']==sha(component)
 assert h['runtimeGone'] and not h['cleanupErrors'] and not h['remainingDescendants'] and not h['unexpectedInnerDescendants']
 if 'heldKeyMask' in r:
  assert r['heldStateAfterLoss']['keys']==r['heldStateAfterLoss']['bindKeys']==[] and r['heldStateAfterLoss']['mods']==0
 native.append({'root':name,'report':str(p),'reportSHA256':sha(p),'checkExecutions':count})
assert sum(v['checkExecutions'] for v in native)==467
prior=REPO/'implementation/elm-parent-held-key-native-v135';p=next((prior/'qa').glob('native-*/report.json'));failure=json.loads(p.read_text())
assert failure['passed'] is False and failure['cleanupPassed'] and failure['error']=="AssertionError('actualChildHeldKeysCancelled')"
assert failure['heldStateAfterLoss']['keys']==[30] and failure['heldStateAfterLoss']['bindKeys']==[38]
assert (prior/'qa/native.py').read_bytes()==(REPO/'implementation/elm-held-key-cancellation-native-v147/qa/native.py').read_bytes()
bad=next((REPO/'implementation/elm-held-key-cancellation-native-v139/qa').glob('native-*/report.json'));r=json.loads(bad.read_text())
assert r['passed'] is False and r['cleanupPassed'] is False and r['heldStateAfterLoss']['keys']==r['heldStateAfterLoss']['bindKeys']==[]
assert r['privateHost']['runtimeGone'] and not r['privateHost']['remainingDescendants']
roots=['elm-parent-held-key-fixture-v131','elm-held-key-observer-v132']+[f'elm-parent-held-key-native-v{i}' for i in range(133,136)]+[
 f'elm-parent-held-key-cancellation-v{i}' for i in range(136,139)]+[
 'elm-held-key-cancellation-native-v139','elm-held-key-cancellation-masks-v140','elm-held-key-cancellation-input-v141',
 'elm-held-key-cancellation-geometry-v142','elm-held-key-cancellation-unheld-v143','elm-held-key-cancellation-pointer-v144',
 'elm-parent-held-key-fixture-v145','elm-parent-held-key-fixture-v146','elm-held-key-cancellation-native-v147',
 'elm-held-key-cancellation-masks-v148','elm-held-key-cancellation-regressions-v149','elm-held-key-cancellation-acceptance-v150']
files=[]
for name in roots:
 root=REPO/'implementation'/name;assert root.is_dir() and not root.is_symlink()
 for p in sorted(root.rglob('*')):
  if p==ROOT/'acceptance-manifest.json':continue
  info=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(info.st_mode)}
  if p.is_symlink():row['symlink']=os.readlink(p)
  elif stat.S_ISREG(info.st_mode):row.update(sha256=sha(p),size=info.st_size)
  elif p.is_dir():continue
  else:raise RuntimeError('Runtime special file in archival roots: '+str(p))
  files.append(row)
result={'schema':1,'passed':True,'nativeAcceptance':True,'releaseAcceptance':False,
 'scope':'Bounded parent held-key cancellation on Core89/plugin90/AQ138; full roadmap/device/IME/deployment remains open',
 'componentManifest':str(component),'componentManifestSHA256':sha(component),
 'nativeCheckExecutions':467,'nativeReports':native,'files':files,
 'retainedActualFailure':{'path':str(p),'note':'Original135 failed held-key cancellation and139 failed later parent admission are retained unchanged'}}
result['retainedActualFailure']['path']=str(next((prior/'qa').glob('native-*/report.json')))
with (ROOT/'acceptance-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(ROOT/'acceptance-manifest.json'),'sha256':sha(ROOT/'acceptance-manifest.json'),'files':len(files),'nativeCheckExecutions':467}))
