"""Prepare current drain fix qualification with original immutable runner bytes."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
docs=pathlib.Path(__file__).parent
for old,new,name,provider in [(168,169,'current_failure_drain_package',138),(165,170,'cancelled_snapshot_normal',138),(167,171,'cancelled_reopened_snapshot',138),(162,172,'reopened_snapshot',137),(164,173,'reopened_snapshot_rapid',137),(163,174,'reopened_snapshot_delayed',137)]:
 p=docs/f'prepare_native{old}_{name}.py';s=p.read_text();needle=f"root=repo/'implementation/warlock-client-provider-native-v{old}';provider=repo/'implementation/warlock-preview-provider-v{provider}'";assert s.count(needle)==1
 s=s.replace(needle,f"root=repo/'implementation/warlock-client-provider-native-v{new}';provider=repo/'implementation/warlock-preview-provider-v139'").replace(f'ownNative{old}',f'ownNative{new}').replace(f'GUI{provider}','GUI139')
 if new==169:
  a=s.index("['PROGRESS ownNative169");b=s.index("],'progress'",a)
  s=s[:a]+repr(['PROGRESS ownNative169 packaged exact unchanged original168 real current cancellation/error/finish1/failure1/no-artifact and mandatory native strict drain-before-failure-exit oracle against fresh139 candidate. Original core16/plugin19/AQ155/deadline6/native issuer single policy original physical/input/ticket/journal/confirmation gates unchanged; normal and old-error controls remain separate, expected failure1 never normal exit or full recovery acceptance. Full release/installed drafts foreign preserved.'])[:-1]+s[b:]
 out=docs/f'prepare_native{new}_{name}.py';assert not out.exists();ast.parse(s);out.write_text(s);print(out)
