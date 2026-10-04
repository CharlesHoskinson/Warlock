"""Freeze bounded native rebase evidence; execute in the protected QA scope."""
import hashlib,json,os,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=Path(__file__).resolve().parents[3]
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
AQ=REPO/'implementation/elm-nested-pointer-rebase-v17/component-manifest.json'
a=json.loads(AQ.read_text());assert a['passed']
for item in a['files']:
 p=AQ.parent/item['path']
 if 'symlink' in item:assert p.is_symlink() and os.readlink(p)==item['symlink']
 else:assert digest(p)==item['sha256']
for name,reports,accepted in [('elm-parent-cursor-scale-v20',['qa/native-1791096191973440672/report.json'],False)]:
 root=REPO/'implementation'/name
 source=[p for p in root.iterdir() if p.is_file()]+[p for p in (root/'qa').iterdir() if p.is_file()]
 if (root/'native').exists():source += [p for p in (root/'native').rglob('*') if p.is_file()]
 source={str(p.relative_to(root)):digest(p) for p in source if p.name!='slice-manifest.json'}
 evidence=[]
 for rel in reports:
  path=root/rel;r=json.loads(path.read_text())
  assert r['passed'] is accepted and r['cleanupPassed']
  for key in ['inputs','sourceInputs']:
   for p,sha in r.get(key,{}).items():assert digest(p)==sha,p
  for relpath,sha in r['artifacts'].items():assert digest(path.parent/relpath)==sha,relpath
  evidence.append({'path':str(path),'sha256':digest(path),'checks':len(r['checks']),
                   'passed':r['passed'],'cleanupPassed':r['cleanupPassed'],'error':r.get('error')})
 packet={'schema':1,'passed':accepted,'normalCleanup':True,'source':source,'reports':evidence,
         'aqComponentManifest':str(AQ),'aqComponentManifestSHA256':digest(AQ),
         'mainDesktopActions':False,'releaseAcceptance':False,
         'scope':'Retained stationary cursor failure' if not accepted else 'Bounded native pointer rebase and retained original regression identities only',
         'remaining':['Scale-only same-pixel-mode geometry','Staged parent configure fences and stale callback/device retirement native stimuli',
                      'Multiple outputs/rotation, physical hardware, AT/IME and coherent full release'],
         'artifacts':{str(p.relative_to(root)):digest(p) for p in root.rglob('*') if p.is_file() and not p.is_symlink()}}
 output=root/'qa/slice-manifest.json';assert not output.exists();output.write_text(json.dumps(packet,indent=2)+'\n')
 print(output,flush=True)
