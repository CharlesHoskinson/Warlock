"""Freeze cursor-oracle, corrected native tuple and retained stationary-click failure."""
import hashlib,json,os,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=Path(__file__).resolve().parents[3]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
AQ=REPO/'implementation/elm-nested-pointer-rebase-v17/component-manifest.json'
PAIR=REPO/'implementation/elm-cursor-authority-pair-v23/qa/build-pair-manifest.json'
for item in json.loads(AQ.read_text())['files']:
 p=AQ.parent/item['path']
 if 'symlink' in item:assert p.is_symlink() and os.readlink(p)==item['symlink']
 else:assert digest(p)==item['sha256']
pair=json.loads(PAIR.read_text());assert pair['passed']
for rel,sha in pair['files'].items():assert digest(PAIR.parents[1]/rel)==sha,rel
CORE=pair['nativePair']['core'];assert digest(CORE['path'])==CORE['sha256']
for name,overall,reports in [
 ('elm-cursor-oracle-v21',False,[('qa/oracle-1791096543806302078/report.json',True,False),('qa/native-1791096552440949941/report.json',False,True)]),
 ('elm-parent-cursor-v24',True,[('qa/native-1791096952765523270/report.json',True,True),('qa/menu-1791096996333334810/report.json',True,True)]),
 ('elm-parent-button-cursor-v25',True,[('qa/native-1791097035909939187/report.json',True,True)]),
 ('elm-parent-stationary-click-v26',False,[('qa/native-1791097090711114043/report.json',False,True)])]:
 root=REPO/'implementation'/name
 source=[p for p in root.iterdir() if p.is_file()]+[p for p in (root/'qa').iterdir() if p.is_file()]
 if (root/'native').exists():source += [p for p in (root/'native').rglob('*') if p.is_file()]
 sources={str(p.relative_to(root)):digest(p) for p in source if p.name!='slice-manifest.json'}
 evidence=[]
 for rel,accepted,native in reports:
  path=root/rel;r=json.loads(path.read_text());assert r['passed'] is accepted
  if native:
   assert r['cleanupPassed']
   if name!='elm-cursor-oracle-v21':
    assert r['privateHost']['hyprlandMaps']['files'][str(Path(CORE['path']).resolve())]==CORE['sha256']
  for key in ['inputs','sourceInputs']:
   for p,sha in r.get(key,{}).items():assert digest(p)==sha,p
  for relpath,sha in r.get('artifacts',{}).items():assert digest(path.parent/relpath)==sha,relpath
  evidence.append({'path':str(path),'sha256':digest(path),'passed':accepted,'checks':len(r['checks']),
                   'native':native,'cleanupPassed':r.get('cleanupPassed'),'error':r.get('error')})
 packet={'schema':1,'passed':overall,'normalCleanup':True,'source':sources,'reports':evidence,
         'aqManifest':str(AQ),'aqManifestSHA256':digest(AQ),'pairManifest':str(PAIR),'pairManifestSHA256':digest(PAIR),
         'mainDesktopActions':False,'releaseAcceptance':False,
         'scope':'Retained diagnostic/failure evidence' if not overall else 'Bounded native cursor extent and retained original regression identities',
         'remaining':['Stationary click after scale-only logical layout change','Native parent configure/generation and capability-loss fencing',
                      'Multiple outputs/rotation, shared-shell integration, physical devices, AT/IME, budgets and full release'],
         'artifacts':{str(p.relative_to(root)):digest(p) for p in root.rglob('*') if p.is_file() and not p.is_symlink()}}
 output=root/'qa/slice-manifest.json';assert not output.exists();output.write_text(json.dumps(packet,indent=2)+'\n');print(output)
