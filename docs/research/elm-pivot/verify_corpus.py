"""Verify portable evidence hashes and links in the hand-written research index."""
import hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parent
manifest=json.loads((root/'CORPUS_MANIFEST.json').read_text())
for item in manifest['files']:
 path=root/item['path']
 assert path.stat().st_size==item['bytes'],path
 assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'],path
links=0
for name in ['README.md','CORPUS_INDEX.md']:
 for target in re.findall(r'\]\(([^)]+)\)',(root/name).read_text()):
  if '://' in target or target.startswith('#'):continue
  assert (root/target.split('#')[0]).exists(),(name,target)
  links+=1
print(json.dumps({'verifiedFiles':len(manifest['files']),'verifiedBytes':sum(i['bytes'] for i in manifest['files']),'localIndexLinks':links,'sourceRecordsVerified':manifest['sourceRecordsHashVerified']}))
