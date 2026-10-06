"""Run the same original suite against the changed current serial registry."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
text=(repo/'docs/warlock-preview/v84/regressions84.py').read_text().replace('warlock-preview-provider-v84','warlock-preview-provider-v85').replace('regressions84-','regressions85-')
target=pathlib.Path(__file__).parent/'regressions85.py';assert not target.exists();target.write_text(text);print(target)
