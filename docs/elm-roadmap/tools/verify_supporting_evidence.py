"""Verify full retained corpus and bind final supporting evidence, independently of prose audit."""
import datetime,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];REF=ROOT/'reference'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checked=0
def verify(p,sha,size=None):
 global checked
 assert p.is_file(),p
 assert digest(p)==sha,p
 if size is not None:assert p.stat().st_size==size,p
 checked+=1
mutter=json.loads((REF/'mutter/portable-corpus-manifest.json').read_text())
for item in mutter['archives']+mutter['docs']:
 verify(REF/'mutter'/item['path'],item['sha256'],item['bytes'])
assert not mutter['remainingDocQueue']
assert len(mutter['docs'])==mutter['docPagesVisited']
assert sum(r['status']==200 for r in mutter['docs'])==mutter['docPagesSuccessful']
assert sum(r['status']!=200 for r in mutter['docs'])==len(mutter['failures'])
for filename in ['49.0-source-inventory.json','main-pinned-source-inventory.json']:
 inv=json.loads((REF/'mutter'/filename).read_text())
 prefix=Path(inv['extractedRoot']).name
 for item in inv['files']:verify(REF/'mutter/complete'/prefix/item['path'],item['sha256'],item.get('bytes'))
kwin=json.loads((REF/'kwin/manifest.json').read_text())
for item in kwin['records']:verify(REF/'kwin'/item['path'],item['sha256'],item['bytes'])
counts={}
for line in (REF/'kwin/source-inventory.jsonl').read_text().splitlines():
 item=json.loads(line);verify(REF/'kwin'/item['path'],item['sha256'],item['bytes']);counts[item['variant']]=counts.get(item['variant'],0)+1
assert counts==kwin['sourceFileCounts']
for item in json.loads((REF/'planning/sources.json').read_text()):verify(REF/'planning'/item['file'],item['sha256'])
# Original author input hashes remain in the frozen generation record. Reconstruct coordinator input only if exact bytes hash-match its recorded root.
original=json.loads((ROOT/'audits/draft-packet/docs/elm-roadmap/generation.json').read_text())
lineage=ROOT/'audits/author-inputs';lineage.mkdir(exist_ok=True)
for item in original['inputs']:
 path=REPO/item['path'];body=path.read_bytes()
 if hashlib.sha256(body).hexdigest()!=item['sha256'] and path.name=='coordinator-requirements.json':
  rows=json.loads(body);body=(json.dumps(rows[:13],indent=2)+'\n').encode()
 assert hashlib.sha256(body).hexdigest()==item['sha256'],item['path']
 (lineage/path.name).write_bytes(body)
# Inventory preserves all raw sources and extracted files in branch, including non-success bodies.
files=sorted(p for p in REF.rglob('*') if p.is_file())+sorted(p for p in lineage.iterdir() if p.is_file())
files+=[ROOT/'generation.json',ROOT/'coordinator-requirements.json',ROOT/'revisions.json',ROOT/'requirements.json']
files+=sorted((ROOT/'contributions').glob('*.json'))
files+=[REPO/'AGENTS.md',REPO/'docs/HANDOFF.md',REPO/'docs/crash-noise/HANDOFF-codex-window-qa.md']
entries=[{'path':str(p.relative_to(REPO)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in files]
summary={'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Scoped primary source and documentation acquisition integrity; not complete source review or native implementation acceptance','verifiedAcquisitionRecordsAndFiles':checked,'mutterSourceFiles':4462,'mutterDocURLs':mutter['docPagesVisited'],'mutterDocSuccess':mutter['docPagesSuccessful'],'mutterDocFailures':len(mutter['failures']),'mutterRemainingQueue':0,'kwinSourceFiles':sum(counts.values()),'kwinDownloadedResponses':len(kwin['records']),'kwinDeveloperUniqueFinalURLs':len({r['finalUrl'] for r in kwin['records'] if r['path'].startswith('developer/')}),'kwinAcquisitionFailures':kwin['failures'],'files':entries}
(ROOT/'audits/supporting-evidence-manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='files'}))
