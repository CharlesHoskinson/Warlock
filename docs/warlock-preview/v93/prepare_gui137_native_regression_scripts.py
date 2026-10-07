"""Prepare reviewed packaging derivatives, preserving original native runners."""
import hashlib,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');docs=r/'docs/warlock-preview/v93'
for old,new,name,parent in [(158,160,'cancelled_snapshot_normal',136),(159,161,'cancelled_reopened_snapshot',136),(155,162,'reopened_snapshot',135),(156,163,'reopened_snapshot_delayed',135),(157,164,'reopened_snapshot_rapid',135)]:
 p=docs/f'prepare_native{old}_{name}.py';s=p.read_text();needle=f"root=repo/'implementation/warlock-client-provider-native-v{old}';provider=repo/'implementation/warlock-preview-provider-v{parent}'";assert s.count(needle)==1
 s=s.replace(needle,f"root=repo/'implementation/warlock-client-provider-native-v{new}';provider=repo/'implementation/warlock-preview-provider-v137'").replace(f'ownNative{old}',f'ownNative{new}').replace(f'GUI{parent}', 'GUI137')
 out=docs/f'prepare_native{new}_{name}.py';assert not out.exists();out.write_text(s);print(out,hashlib.sha256(out.read_bytes()).hexdigest())
