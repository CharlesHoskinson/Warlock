"""Preserve the first build and refresh the shared resource wire encoder inputs."""
import hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-family-style-crop-capture-v19')
old=root/'qa/first-resource-native-build-report.json';assert not old.exists()
old.write_bytes((root/'native-build-report.json').read_bytes())
p=root/'upstream.json';d=json.loads(p.read_text())
for rel in d['sourceFiles']:d['sourceFiles'][rel]=hashlib.sha256((root/rel).read_bytes()).hexdigest()
p.write_text(json.dumps(d,indent=2)+'\n')
print('First compiled descriptor preserved; current resource encoder source hashes refreshed')
