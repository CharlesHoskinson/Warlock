"""Prepare independent normal, current-fault and old-cancellation packages."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
docs=pathlib.Path(__file__).parent
for old,new,name in [(160,165,'cancelled_snapshot_normal'),(160,166,'cancelled_snapshot_normal'),(161,167,'cancelled_reopened_snapshot')]:
 source=docs/f'prepare_native{old}_{name}.py';s=source.read_text();needle=f"root=repo/'implementation/warlock-client-provider-native-v{old}';provider=repo/'implementation/warlock-preview-provider-v137'";assert s.count(needle)==1
 s=s.replace(needle,f"root=repo/'implementation/warlock-client-provider-native-v{new}';provider=repo/'implementation/warlock-preview-provider-v138'").replace(f'ownNative{old}',f'ownNative{new}').replace('GUI137','GUI138')
 suffix=name
 if new==166:
  s=s.replace("'native138_controlled_curtain_runner.py'","'native166_current_failure_runner.py'");suffix='current_snapshot_failure'
  a=s.index(";pre.update(popupCurtainOracle=");b=s.index('\nassert all',a)
  scope='Distinct QA-only actual matching-current WebKit cancellation negative control on original core16/plugin19/AQ155 and original six-second observer. Retains original GTK factory/DOM/native projection/native ticket admission and no legacy route, actual real canceled GCancellable/original WebKit finish once with same original current view/epoch/navigation/projection. Must reach original client_failure exactly once, expected host exit1/no artifact/no new realm/no false retirement; original strict Native policy/input/ticket/physical/journal/confirmation custody prevents graceful teardown and remains retained. Other owned processes exit0/private cleanup. This does NOT replace unchanged normal16529-control or old-canceled16736-control positive campaigns, does not classify host1 as normal closure or qualify graceful current failure drain/recovery, and does not grant physical/release acceptance.'
  s=s[:a]+";pre.update(popupCurtainOracle=str(oracleReport.parent/'popup-curtain-oracle'),popupCurtainOracleBuild=str(oracleReport),scope="+repr(scope)+')'+s[b:]
  a=s.index("['PROGRESS ownNative166");b=s.index("],'progress'",a)
  s=s[:a]+repr(['PROGRESS ownNative166 packaged distinct actual matching-current canceled WebKit result negative control, original GTK/native admission and six-second deadline/core16/plugin19/AQ155. Actual original finish once/current-scope branch must fail host1/no artifact; strict native custody retained. Never normal-exit or graceful-drain/recovery acceptance. Unchanged normal165 and old-canceled167 positive regressions separate. Full release/installed drafts foreign preserved.'])[:-1]+s[b:]
 out=docs/f'prepare_native{new}_{suffix}.py';assert not out.exists();ast.parse(s);out.write_text(s);print(out)
