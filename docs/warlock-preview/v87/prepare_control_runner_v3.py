"""Fresh runner with its own filename derived rather than rewritten twice."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity/implementation/warlock-preview-provider-v88')
s=(r/'qa/control-prefix-check-v2.py').read_text().replace("'qa/control-prefix-check-v2-v2.py'","str(pathlib.Path(__file__).relative_to(root))").replace('control-prefix-check-v2-','control-prefix-check-v3-')
(r/'qa/control-prefix-check-v3.py').write_text(s)
