import hashlib,json,os,resource,stat
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
ancestral=REPO/'implementation/elm-keyboard-focus-acceptance-v158/acceptance-manifest.json'
a=json.loads(ancestral.read_text());assert a['passed'] and a['nativeAcceptance'] and not a['releaseAcceptance']
for row in a['files']:
 p=REPO/row['path']
 if 'symlink' in row:assert p.is_symlink() and os.readlink(p)==row['symlink']
 else:assert sha(p)==row['sha256']
runtime=REPO/'implementation/elm-keyboard-focus-runtime-v163'
assert (runtime/'candidate_host.py').read_bytes()==(REPO/'implementation/elm-geometry-bounds-runtime-v420/candidate_host.py').read_bytes()
pair=json.loads((runtime/'qa/build-pair-manifest.json').read_text());assert pair['passed']
assert pair['owningAcceptance']==str(ancestral) and pair['owningAcceptanceSHA256']==sha(ancestral)
for name,digest in pair['files'].items():assert sha(runtime/name)==digest
for row in pair['nativePair'].values():assert sha(row['path'])==row['sha256']
t=json.loads((runtime/'aq-tuple.json').read_text());assert pair['nativePair']['aquamarine']=={'path':t['library'],'sha256':t['librarySHA256']}
assert sha(t['manifest'])==t['manifestSHA256'] and sha(t['library'])==t['librarySHA256']
reports=[]
for current,original,count in [('elm-keyboard-focus-gui-relay-v164','elm-geometry-current-relay-native-v428',50),('elm-keyboard-focus-gui-reconnect-v165','elm-geometry-current-reconnect-native-v429',57)]:
 root=REPO/'implementation'/current;src=REPO/'implementation'/original
 assert (root/'qa/native.py').read_text()==(src/'qa/native.py').read_text().replace('elm-geometry-bounds-runtime-v420','elm-keyboard-focus-runtime-v163')
 for q in ['inspection.py','grab_guard.py','sampling.py']:assert (root/'qa'/q).read_bytes()==(src/'qa'/q).read_bytes()
 assert (root/'fixture.py').read_bytes()==(src/'fixture.py').read_bytes()
 pre=root/'qa/preflight.json';flight=json.loads(pre.read_text());assert flight['passed']
 for path,digest in flight['inputs'].items():assert sha(path)==digest
 paths=list((root/'qa').glob('native-*/report.json'));assert len(paths)==1
 p=paths[0];r=json.loads(p.read_text());assert r['passed'] and r['cleanupPassed'] and not r['mainDesktopActions']
 assert r['pair']==pair['nativePair'] and r['preflightSHA256']==sha(pre)
 assert len(r['checks'])==count and all(v['passed'] for v in r['checks'])
 for path,digest in r['inputs'].items():assert sha(path)==digest
 for rel,digest in r['artifacts'].items():assert sha(p.parent/rel)==digest
 h=r['privateHost'];aq=h['privateAquamarine'];assert aq['mappedVerified']
 assert aq['path']==t['library'] and aq['sha256']==t['librarySHA256'] and aq['contractManifestSHA256']==t['manifestSHA256']
 assert aq['mappedFiles']=={t['library']:t['librarySHA256']}
 assert h['runtimeGone'] and not h['cleanupErrors'] and not h['remainingDescendants'] and not h['unexpectedInnerDescendants']
 reports.append({'report':str(p),'sha256':sha(p),'checkExecutions':count})
files=[]
for name in ['elm-keyboard-focus-runtime-v163','elm-keyboard-focus-gui-relay-v164','elm-keyboard-focus-gui-reconnect-v165','elm-keyboard-focus-gui-acceptance-v166']:
 for p in sorted((REPO/'implementation'/name).rglob('*')):
  if p==ROOT/'acceptance-manifest.json':continue
  st=p.lstat();row={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
  if p.is_symlink():row['symlink']=os.readlink(p)
  elif stat.S_ISREG(st.st_mode):row.update(sha256=sha(p),size=st.st_size)
  elif p.is_dir():continue
  else:raise RuntimeError('Runtime special file '+str(p))
  files.append(row)
result={'schema':1,'passed':True,'nativeAcceptance':True,'releaseAcceptance':False,'scope':'Shared Elm422/receipt427 GUI recovery on Core89/plugin409/AQ155: native107; ancestral158 input543 uses plugin90 where applicable. Full geometry08/09/10, hardware/ATIME/roadmap/release gates remain open.','ancestralInputAcceptance':str(ancestral),'ancestralInputAcceptanceSHA256':sha(ancestral),'nativePair':pair['nativePair'],'nativeCheckExecutions':107,'nativeReports':reports,'files':files}
with (ROOT/'acceptance-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(ROOT/'acceptance-manifest.json'),'sha256':sha(ROOT/'acceptance-manifest.json'),'files':len(files),'nativeCheckExecutions':107}))
