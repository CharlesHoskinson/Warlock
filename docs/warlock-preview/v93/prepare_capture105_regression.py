"""Retain the original capture oracle and select its current strengthened guard."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v105')
p=root/'qa/capture-intent-model-check-v3.py';assert not p.exists()
s=(root/'qa/capture-intent-model-check-v2.py').read_text().replace('capture-intent-model-check-v2-','capture-intent-model-check-v3-')
old='require(!f.attempted && !f.cleanup,"Single original imported capture");'
new='require(!f.attempted && !f.cleanup && !reconciling_,"Single original imported capture");'
assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)
print('Original14/three-mode capture model and mutation oracle retained')
