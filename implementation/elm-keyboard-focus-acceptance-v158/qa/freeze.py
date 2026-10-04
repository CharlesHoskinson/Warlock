import hashlib,json,os,resource,stat
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
aq=REPO/'implementation/elm-keyboard-focus-cancellation-v155';component=aq/'component-manifest.json'
c=json.loads(component.read_text());assert c['passed'] and not c['nativeAcceptance']
for row in c['files']:
 p=aq/row['path']
 if 'symlink' in row:assert p.is_symlink() and os.readlink(p)==row['symlink']
 else:assert sha(p)==row['sha256']
b=json.loads(Path(c['buildReport']).read_text());assert b['passed'] and b['publicHeadersUnchanged'] and not b['missingParentSymbols']
assert sha(c['buildReport'])==c['buildReportSHA256'] and sha(b['library'])==b['librarySHA256']
lib=Path(b['library']).resolve();libsha=b['librarySHA256'];native=[]
cases=[('elm-keyboard-focus-native-v156/'+kind,38) for kind in ['capability','focus']]+[
 ('elm-keyboard-focus-regressions-v157/parent-loss',37),
 *[(f'elm-keyboard-focus-regressions-v157/mask-{i}',38) for i in range(1,4)],
 ('elm-keyboard-focus-regressions-v157/input',159),('elm-keyboard-focus-geometry-v159',96),
 ('elm-keyboard-focus-unheld-v160',26),('elm-keyboard-focus-pointer-v161',35)]
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
assert sum(v['checkExecutions'] for v in native)==543
failures=[]
for kind in ['capability','focus']:
 prior=REPO/'implementation/elm-keyboard-loss-native-v152'/kind
 p=next((prior/'qa').glob('native-*/report.json'));failure=json.loads(p.read_text())
 assert failure['passed'] is False and failure['cleanupPassed']
 assert failure['error']=="RuntimeError('Unchanged six-second observation deadline')"
 assert failure['lastStateDuringCancellation']['keys']==[30,42]
 assert failure['lastStateDuringCancellation']['bindKeys']==[38,50] and failure['lastStateDuringCancellation']['mods']==1
 corrected=REPO/'implementation/elm-keyboard-focus-native-v156'/kind
 assert (prior/'qa/native.py').read_bytes()==(corrected/'qa/native.py').read_bytes()
 failures.append({'report':str(p),'sha256':sha(p),'scope':kind,'cleanupPassed':True})
for rel in ['elm-keyboard-focus-cancellation-v153/qa/model-1791127253247952435/report.json',
 'elm-keyboard-focus-cancellation-v154/build-1791128074606032672/report.json',
 'elm-keyboard-focus-regressions-v157/dispatch-1791129324669684962/report.json']:
 p=REPO/'implementation'/rel;r=json.loads(p.read_text());assert r['passed'] is False
 failures.append({'report':str(p),'sha256':sha(p)})
roots=['elm-keyboard-loss-fixture-v151','elm-keyboard-loss-native-v152',
 'elm-keyboard-focus-cancellation-v153','elm-keyboard-focus-cancellation-v154',
 'elm-keyboard-focus-cancellation-v155','elm-keyboard-focus-native-v156',
 'elm-keyboard-focus-regressions-v157','elm-keyboard-focus-acceptance-v158',
 'elm-keyboard-focus-geometry-v159','elm-keyboard-focus-unheld-v160',
 'elm-keyboard-focus-pointer-v161','elm-keyboard-focus-dispatch-v162']
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
 'scope':'Bounded parent held-key cancellation on Core89/plugin90/AQ155; full roadmap/device/IME/deployment remains open',
 'componentManifest':str(component),'componentManifestSHA256':sha(component),
 'nativeCheckExecutions':543,'nativeReports':native,'files':files,
 'retainedFailures':failures}
with (ROOT/'acceptance-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(ROOT/'acceptance-manifest.json'),'sha256':sha(ROOT/'acceptance-manifest.json'),'files':len(files),'nativeCheckExecutions':543}))
