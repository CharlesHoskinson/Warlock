"""Run current aggregate-native code through unchanged original GUI checks."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
text=(r/'docs/warlock-preview/v85/regressions85.py').read_text().replace('warlock-preview-provider-v85','warlock-preview-provider-v86').replace('regressions85-','regressions86-')
target=r/'docs/warlock-preview/v87/regressions86.py';assert not target.exists();target.write_text(text)
