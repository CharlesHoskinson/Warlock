"""Narrow the mutation to the actual polling preflight; preserve failed v2 evidence."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v105')
p=root/'qa/capture-resource-check-v3.py';assert not p.exists()
s=(root/'qa/capture-resource-check-v2.py').read_text().replace('capture-resource-check-v2-','capture-resource-check-v3-')
old="'o.value.actorCounts(o.popup,*static_cast<ReceiptDelivery*>(delivery),o.subjects);',';'"
new="'o.value.actorCounts(o.popup,*static_cast<ReceiptDelivery*>(delivery),o.subjects);\\n        if(o.controlled)o.value.pollReconciliation(o.controlGrant(popup));','if(o.controlled)o.value.pollReconciliation(o.controlGrant(popup));'"
assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)
print('Actual polling preflight selected uniquely; original v2 runner/report retained')
