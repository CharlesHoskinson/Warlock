"""Original regression closure for changed Elm retirement and ordered host transport."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
s=(r/'docs/warlock-preview/v87/regressions86.py').read_text().replace('warlock-preview-provider-v86','warlock-preview-provider-v88').replace('regressions86-','regressions88-')
(r/'docs/warlock-preview/v87/regressions88.py').write_text(s)
