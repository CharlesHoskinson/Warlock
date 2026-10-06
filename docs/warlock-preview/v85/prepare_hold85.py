"""Keep the current full freeze contract for the entry-serial derivative."""
import pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
text=(repo/'docs/warlock-preview/v84/hold84.py').read_text().replace('GUI84','GUI85').replace('warlock-preview-provider-v84','warlock-preview-provider-v85').replace('docs/warlock-preview/v84/','docs/warlock-preview/v85/')
text=text.replace('current GUI85/native122','current GUI85/native123').replace('actual native122 next','actual native123 next').replace('Real typed C/native retirement path and atomic actor turnover remain open;', 'Native122 qualifies the parent GUI84 typed C path. Current explicit bounded C membership and monotonic entry serials compile; native123 qualification and atomic actor turnover remain open;')
text=text.replace('Typed retirement decoder and C/socket suites passed; actual native123 next.', 'Explicit bounded C membership and monotonic entry serials, typed decoder and C/socket suites passed; actual native123 next.')
target=pathlib.Path(__file__).parent/'hold85.py';assert not target.exists();target.write_text(text);print(target)
