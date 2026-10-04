import hashlib,json,resource,stat,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out=ROOT/'qa'/('freeze-'+str(time.time_ns()));out.mkdir();r={'passed':False,'nativeAcceptance':False,'fullCampaignPassed':False}
try:
 origin=json.loads((ROOT/'origin.json').read_text());external={origin['parentManifest']:origin['parentSHA256'],origin['fixtureManifest']:origin['fixtureSHA256']}
 for p,d in external.items():assert sha(Path(p))==d,p
 parent=Path(origin['parentManifest']).parent
 old=(parent/'qa/actor.py').read_text();new=(ROOT/'qa/actor.py').read_text()
 assert old[old.index('class Actor:'):]==new[new.index('class Actor:'):]
 old=(parent/'qa/journal.py').read_text();new=(ROOT/'qa/journal.py').read_text().split('def gtk_parent_relation(',1)[0]
 assert old.rstrip()==new.replace("('A','B','C','D','P','E')","('A','B','C','D','P')").rstrip()
 reports=['journal-1791142840233178095/report.json','actor-1791142840226716495/report.json','sibling-1791142840217138531/report.json','actor-sibling-1791142891341503704/report.json']
 verified={}
 for name in reports:
  p=ROOT/'qa'/name;d=json.loads(p.read_text());assert d['passed'] is True and d['nativeAcceptance'] is False
  for path,digest in d['inputs'].items():assert sha(Path(path))==digest,path
  assert all(c['passed'] is True for c in d['checks']);verified[name]={'sha256':sha(p),'checks':len(d['checks'])}
 r.update(passed=True,reports=verified,unchangedActorLifecycle=True,unchangedJournalCoreExceptERole=True)
except BaseException as error:r['error']=repr(error)
finally:(out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:
 files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
 (ROOT/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'nativeAcceptance':False,'fullCampaignPassed':False,'scope':'sibling toolkit journal/request boundary and real CPU subprocess ownership only','files':files,'externalFiles':external,'verificationReport':str(out/'report.json')},indent=2)+'\n')
print(out/'report.json');raise SystemExit(0 if r['passed'] else 1)
