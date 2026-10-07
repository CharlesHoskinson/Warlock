"""Package original normal oracle and a distinct actual same-popup reload oracle."""
import ast,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
docs=pathlib.Path(__file__).parent
for old,new,name in [(170,175,'cancelled_snapshot_normal'),(172,176,'reopened_snapshot')]:
 s=(docs/f'prepare_native{old}_{name}.py').read_text();needle=f"root=repo/'implementation/warlock-client-provider-native-v{old}';provider=repo/'implementation/warlock-preview-provider-v139'";assert s.count(needle)==1
 s=s.replace(needle,f"root=repo/'implementation/warlock-client-provider-native-v{new}';provider=repo/'implementation/warlock-preview-provider-v140'").replace(f'ownNative{old}',f'ownNative{new}').replace('GUI139','GUI140');suffix=name
 if new==176:
  s=s.replace("'native155_reopened_snapshot_runner.py'","'native176_renderer_reload_runner.py'");suffix='renderer_reload'
  a=s.index(";pre.update(popupCurtainOracle=");b=s.index('\nassert all',a)
  scope='Distinct actual current original WebKit reload after first current Native-owned source snapshot. Original GTK factory/DOM/native ticket/current projection/no legacy route controls retained; real API request and actual original LOAD_STARTED/navigation1->2, original first source PNG/red19200, host continuity, old strict C/Bootstrap close/empty original custody BEFORE replacement, fresh fixed-grant renderer/later native epoch2 on exact original policy/binding and same GTK popup lease1, new navigation>=3/request2/source pixels/current image before-after original grim opacity0 region and final strict close/all owned normal exits/private cleanup. Original observer6/core16/plugin19/AQ155/clock/physical/journal/confirmation gates unchanged. Separate normal17529-control oracle remains byte-identical; this reload fixture does not qualify arbitrary/process/uncertain reload, full S09/hardware/reveal/resource/release.'
  s=s[:a]+";pre.update(popupCurtainOracle=str(oracleReport.parent/'popup-curtain-oracle'),popupCurtainOracleBuild=str(oracleReport),scope="+repr(scope)+')'+s[b:]
  a=s.index("['PROGRESS ownNative176");b=s.index("],'progress'",a);s=s[:a]+repr(['PROGRESS ownNative176 actual known same-URI WebKit reload recovery oracle after first current PNG, original admission/source/native ownership/current bindings; require actual LOAD_STARTED/old strict close BEFORE fixed-grant replacement, later same-policy epoch2/original popup lease1/current source pixels/opacity0 output/final strict close/all normal exits. Original core16/plugin19/AQ155/deadline6/Native ownership gates unchanged, no manufactured callback/grant/reset. Normal175 original29-control separate; full release/installed drafts foreign preserved.'])[:-1]+s[b:]
 out=docs/f'prepare_native{new}_{suffix}.py';assert not out.exists();ast.parse(s);out.write_text(s);print(out)
