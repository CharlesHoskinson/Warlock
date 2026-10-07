"""Refresh only the fresh plugin19 source lineage before owning-ABI compilation."""
import hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
root=repo/'implementation/warlock-family-style-crop-capture-v19'
parent=repo/'implementation/warlock-family-style-crop-capture-v18'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (root/'native-build-report.json').exists()
p=root/'upstream.json';d=json.loads(p.read_text())
d['parent']=str(parent);d['parentDescriptorSHA256']=sha(parent/'native-build-report.json')
original=json.loads((parent/'upstream.json').read_text())
d['parentSourceFiles']=original['sourceFiles']
for rel,wanted in d['parentSourceFiles'].items():assert sha(parent/rel)==wanted,rel
d['sourceFiles']={rel:sha(root/rel) for rel in original['sourceFiles']}
for name in ['capture-resources.hpp','capture-resources.inc','capture-resources-test.cpp']:
 rel='native/'+name;d['sourceFiles'][rel]=sha(root/rel)
d['change']='Add authenticated exact original capture resource observation, scoped idempotent export release and locked producer retirement. Original capture request/subject/binding remain authoritative; complete response allocation precedes mutation. Does not establish local FD/readers/Broker proofs, native window retirement or ordinary capture eligibility.'
p.write_text(json.dumps(d,indent=2)+'\n')
print('plugin19 original parent and current source hashes verified')
