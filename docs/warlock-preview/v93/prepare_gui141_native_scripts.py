"""Generate fresh packages; retain byte-identical native scenario runners."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
docs=pathlib.Path(__file__).parent
items=[(176,177,'renderer_reload',140),(175,178,'cancelled_snapshot_normal',140),(171,179,'cancelled_reopened_snapshot',139),(169,180,'current_failure_drain_package',139),(173,181,'reopened_snapshot_rapid',139),(174,182,'reopened_snapshot_delayed',139),(172,183,'reopened_snapshot',139)]
for old,new,name,provider in items:
 s=(docs/f'prepare_native{old}_{name}.py').read_text()
 needle=f"root=repo/'implementation/warlock-client-provider-native-v{old}';provider=repo/'implementation/warlock-preview-provider-v{provider}'"
 assert s.count(needle)==1
 s=s.replace(needle,f"root=repo/'implementation/warlock-client-provider-native-v{new}';provider=repo/'implementation/warlock-preview-provider-v141'").replace(f'ownNative{old}',f'ownNative{new}').replace(f'GUI{provider}','GUI141')
 p=docs/f'prepare_native{new}_{name}.py';assert not p.exists();ast.parse(s);p.write_text(s);print(p)
