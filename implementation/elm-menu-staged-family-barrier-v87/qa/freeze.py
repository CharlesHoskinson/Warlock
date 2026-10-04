"""Protected source/evidence hold for the staged native family guard."""
import difflib,hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
lineage=json.loads((ROOT/'LINEAGE.json').read_text());parent=Path(lineage['parent'])
assert sha(parent/'qa/held-source-manifest.json')==lineage['heldManifestSHA256']
assert sha(lineage['semanticHarness'])==lineage['semanticHarnessSHA256']
parent_manifest=json.loads((parent/'qa/held-source-manifest.json').read_text())
for relative,row in parent_manifest['files'].items():assert sha(parent/relative)==row['sha256']
for p in sorted((ROOT/'src').glob('*.elm')):
 if p.name!='MenuBridge.elm':assert p.read_bytes()==(parent/'src'/p.name).read_bytes(),p.name
assert (ROOT/'elm.json').read_bytes()==(parent/'elm.json').read_bytes()
assert set(p.name for p in (ROOT/'src').glob('*.elm'))==set(p.name for p in (parent/'src').glob('*.elm'))
old=(parent/'src/MenuBridge.elm').read_text();new=(ROOT/'src/MenuBridge.elm').read_text()
assert new.replace(new[new.index('        nativeBlocked ='):new.index('\n\n\nguardedAct')],'    in blocked')==old
reports={
 'semantic':ROOT/'semantic/qa/replay-1791108165649621275/report.json',
 'postClose':ROOT/'post-close/qa/replay-1791108165648889457/report.json',
 'mutations':ROOT/'post-close/qa/mutations-1791108165634785258/report.json',
 'family':ROOT/'family/qa/family-1791108381750401231/report.json'}
accepted={}
for name,path in reports.items():
 data=json.loads(path.read_text());assert data['passed']
 for relative,wanted in data['artifacts'].items():assert sha(path.parent/relative)==wanted,relative
 for relative,wanted in data['sourceInputs'].items():assert sha(ROOT/relative)==wanted,relative
 qa_root=path.parent.parent.parent
 for relative,wanted in data['qaInputs'].items():assert sha(qa_root/relative)==wanted,relative
 accepted[name]={'path':str(path),'sha256':sha(path)}
semantic=json.loads(reports['semantic'].read_text());assert all(x['passed'] for x in semantic['stagedSuites'].values())
assert [semantic['stagedSuites'][k]['checks'] for k in ['menu','geometry','refresh']]==[78,53,21]
post=json.loads(reports['postClose'].read_text());assert post['postCloseChecks']['checks']==59
mutants=json.loads(reports['mutations'].read_text());assert len(mutants['mutants'])==5 and all(x['compiled'] and x['failedCases'] for x in mutants['mutants'])
family=json.loads(reports['family'].read_text());assert family['profiles']['actual']['checks']==6
assert all(family['profiles'][k]['compiled'] and family['profiles'][k]['exitCode']==1 for k in ['root-only','missing-native-guard'])
mapping={}
for name in ['menu','geometry','refresh']:
 passed=json.loads((reports['semantic'].parent/(name+'-staged-checks.json')).read_text())
 assert len({x['name'] for x in passed['cases']})==len(passed['cases'])
 assert all(x['passed'] for x in passed['cases'])
 mapping[name]=[x['name'] for x in passed['cases']]
(ROOT/'qa/semantic-case-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
(ROOT/'qa/production.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='held-v69/MenuBridge.elm',tofile='v87/MenuBridge.elm')))
destination=ROOT/'qa/held-source-manifest.json'
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size}
       for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p!=destination}
manifest={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'releaseAcceptance':False,
 'scope':'Compiled typed full-family guard and all staged semantic equivalents; synthetic native observations/outcomes only',
 'files':files,'reports':accepted,'semantics':{'menu':78,'geometry':53,'refresh':21,'postClose':59,'family':6,'compiledMutantsRejected':7},
 'originalFailuresPreserved':semantic['originalSuites'],'failureManifest':lineage['semanticHarness'],'failureManifestSHA256':lineage['semanticHarnessSHA256']}
destination.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(destination),'sha256':sha(destination),'files':len(files)}))
