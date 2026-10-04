import hashlib,json,os,resource,stat,time,traceback
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'qa'/('freeze-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'passed':False,'fullReleaseAccepted':False}
try:
 refs={}
 parent=REPO/'implementation/elm-focus-recovery-integrated-held-v340/acceptance-manifest.json';assert sha(parent)=='86d318a1e44007f3d8ac581cd2f0f364c981f1740fe0a93bdd6fc3d27b367912';m=json.loads(parent.read_text());assert m['passed'] and m['currentNativeScopedChecks']==224
 for row in m['files']:
  p=REPO/row['path']
  if 'symlink' in row:assert p.is_symlink() and os.readlink(p)==row['symlink']
  else:assert sha(p)==row['sha256'] and p.stat().st_size==row['size']
 refs[str(parent.relative_to(REPO))]=sha(parent)
 fixture=REPO/'implementation/elm-focus-recovery-current-fixture-v342';fp=fixture/'component-manifest.json';assert sha(fp)=='18a3c9966f40360721ac2e1e68da71c396c54f597ef01740726a4a05164e8a0c';fm=json.loads(fp.read_text());assert fm['passed'] and fm['finalChecks']==159 and fm['backendRoot']==str(REPO/'implementation/elm-focus-recovery-integrated-gui-v333/qa/build-1791154674626733228/inputs/adapter')
 for name,v in fm['files'].items():assert sha(fixture/name)==v['sha256'] and (fixture/name).stat().st_size==v['size']
 for name,v in fm['special'].items():assert v['kind']=='symlink' and (fixture/name).is_symlink() and os.readlink(fixture/name)==v['target']
 refs[str(fp.relative_to(REPO))]=sha(fp);native=[]
 for name,packet in [('elm-focus-recovery-integrated-capability-v343','native-1791155736788534260'),('elm-focus-recovery-integrated-focus-v344','native-1791155783734329032')]:
  p=REPO/'implementation'/name/'qa'/packet/'report.json';d=json.loads(p.read_text());assert d['passed'] and len(d['checks'])==83 and all(c['passed'] for c in d['checks']) and d['cleanupPassed'] and d['pair']==m['pair']
  assert d['buildReport']==str(REPO/'implementation/elm-focus-recovery-integrated-gui-v333/qa/build-1791154674626733228/report.json')
  h=d['privateHost'];assert not h['mainDisplayUsed'] and h['runtimeGone'] and not any(h[k] for k in ['cleanupErrors','remainingDescendants','unexpectedInnerDescendants'])
  for path,digest in d['inputs'].items():assert sha(path)==digest,path
  for path,digest in d['artifacts'].items():assert sha(p.parent/path)==digest,path
  refs[str(p.relative_to(REPO))]=sha(p);native.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'checks':83,'passed':True,'normalCleanupPassed':True})
 roots=['implementation/elm-focus-recovery-current-fixture-v341','implementation/elm-focus-recovery-current-fixture-v342','implementation/elm-focus-recovery-integrated-capability-v343','implementation/elm-focus-recovery-integrated-focus-v344',str(ROOT.relative_to(REPO))];files=[]
 for name in roots:
  for p in sorted((REPO/name).rglob('*')):
   if p in [ROOT/'acceptance-manifest.json',OUT/'report.json']:continue
   st=p.lstat();v={'path':str(p.relative_to(REPO)),'mode':stat.S_IMODE(st.st_mode)}
   if p.is_symlink():v['symlink']=os.readlink(p)
   elif p.is_file():v.update(sha256=sha(p),size=st.st_size)
   elif p.is_dir():continue
   else:raise RuntimeError('Owned special file: '+str(p))
   files.append(v)
 manifest={'passed':True,'component':ROOT.name,'selectedProduction':m['selectedProduction'],'fixtureChecks':159,'nativeCurrentAdditionalChecks':166,'nativeCurrentTotalScopedChecksWith340':390,'nativeCurrentGeneralGUISubset':255,'nativeCampaigns':native,'sameCompiledGUIAndPair':True,'pair':m['pair'],'references':refs,'ownedRoots':roots,'files':files,'fullGUI473Accepted':False,'lostReleaseRepeatNativeAccepted':False,'fullReleaseAccepted':False,'next':['original geometry161 with current333/342 source closure','original reconnect57 with current333/342 source closure','actual lost-release/repeated restart','current narrow/wide render','fullGTKQt','capture/restore/motion','outputs/GPU/ATIME/budgets/user/reversible-release']}
 (ROOT/'acceptance-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');r.update(passed=True,files=len(files),additionalNativeChecks=166,scopedNativeChecks=390,manifestSHA256=sha(ROOT/'acceptance-manifest.json'))
except Exception as e:r.update(error=repr(e),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'report':str(OUT/'report.json'),**r}));raise SystemExit(not r['passed'])
