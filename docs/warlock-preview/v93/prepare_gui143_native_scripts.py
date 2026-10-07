"""Prepare unchanged process fault and original regression scenario packages."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
docs=pathlib.Path(__file__).parent
for old,new,name,provider in [(186,187,'process_stop',142),(185,188,'cancelled_snapshot_normal',142),(184,189,'renderer_reload',141),(180,190,'current_failure_drain_package',141),(179,191,'cancelled_reopened_snapshot',141),(181,192,'reopened_snapshot_rapid',141),(182,193,'reopened_snapshot_delayed',141),(183,194,'reopened_snapshot',141)]:
 s=(docs/f'prepare_native{old}_{name}.py').read_text();needle=f"root=repo/'implementation/warlock-client-provider-native-v{old}';provider=repo/'implementation/warlock-preview-provider-v{provider}'";assert s.count(needle)==1
 s=s.replace(needle,f"root=repo/'implementation/warlock-client-provider-native-v{new}';provider=repo/'implementation/warlock-preview-provider-v143'").replace(f'ownNative{old}',f'ownNative{new}').replace(f'GUI{provider}','GUI143')
 p=docs/f'prepare_native{new}_{name}.py';assert not p.exists();ast.parse(s);p.write_text(s);print(p)
