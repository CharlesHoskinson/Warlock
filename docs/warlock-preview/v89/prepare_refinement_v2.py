"""Preserve first refinement report; exercise the actual FinalFirst guard mutant."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v89')
source=r/'spec/retirement_async_tests.qnt';target=r/'spec/retirement_async_tests_v2.qnt'
assert not target.exists()
s=source.read_text();old='run pendingJobCannotForget=init.then(fire(ObserveFirst)).then(fire(PrematureFinal))'
assert s.count(old)==1
target.write_text(s.replace(old,'run pendingJobCannotForget=init.then(fire(ObserveFirst)).then(fire(FinalFirst))'))
source=r/'qa/retirement-refinement-check.py';target=r/'qa/retirement-refinement-check-v2.py'
assert not target.exists()
s=source.read_text().replace('retirement-refinement-check-','retirement-refinement-check-v2-').replace('retirement_async_tests.qnt','retirement_async_tests_v2.qnt')
s=s.replace("'qa/retirement-refinement-check.py'","'qa/retirement-refinement-check-v2.py'")
target.write_text(s)
