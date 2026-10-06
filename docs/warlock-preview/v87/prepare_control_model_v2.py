"""Preserve model parse failure and create a fresh corrected Quint derivative."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v88')
s=(r/'spec/control_prefix.qnt').read_text().replace('val next=reduce(s,e);s\'= {...next','val updated=reduce(s,e);s\'= {...updated')
# Exact original has no space after assignment.
s=(r/'spec/control_prefix.qnt').read_text().replace("val next=reduce(s,e);s'={...next","val updated=reduce(s,e);s'={...updated")
assert 'val next=' not in s;(r/'spec/control_prefix_v2.qnt').write_text(s)
s=(r/'spec/control_prefix_tests.qnt').read_text().replace('"./control_prefix"','"./control_prefix_v2"')
(r/'spec/control_prefix_tests_v2.qnt').write_text(s)
s=(r/'qa/control-prefix-check.py').read_text().replace('control-prefix-check.py','control-prefix-check-v2.py').replace('control-prefix-check-','control-prefix-check-v2-').replace('control_prefix_tests.qnt','control_prefix_tests_v2.qnt').replace('control_prefix.qnt','control_prefix_v2.qnt')
(r/'qa/control-prefix-check-v2.py').write_text(s)
