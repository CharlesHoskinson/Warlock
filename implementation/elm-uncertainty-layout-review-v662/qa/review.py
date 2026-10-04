import ast,hashlib,json,pathlib,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
ROOT=pathlib.Path(__file__).resolve().parents[1];GUI=ROOT.parent/'elm-recovery-delivery-integrated-gui-v640'
OUT=ROOT/'qa'/('review-'+str(time.time_ns()));OUT.mkdir();checks=[]
def digest(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
pointer=json.loads((ROOT/'qa/current-preparation.json').read_bytes());check('preparation_hash_matches',digest(pointer['report'])==pointer['sha256']);prep=json.loads(pathlib.Path(pointer['report']).read_bytes());check('compiled_root_fixtures_passed',prep['passed'])
for p,h in prep['sourcePins'].items():check('held_actual_input_'+p,digest(p)==h)
cases={x['name']:x for x in json.loads(pathlib.Path(prep['cases']).read_bytes())}
check('bounded_authoritative_title',max(len(c['label']) for case in cases.values() for c in case['frame']['bar'])<=256)
check('actual_unknown_disabled_group',any(not c['enabled'] and c['detail']=='Awaiting native confirmation' for c in cases['unknown']['frame']['bar']))
check('actual_pending_disabled_read_only_refresh',next(c for c in cases['pending']['frame']['bar'] if c['id']=='bar:recovery-refresh')['enabled'] is False)
check('actual_unknown_enabled_read_only_refresh',next(c for c in cases['unknown']['frame']['bar'] if c['id']=='bar:recovery-refresh')['enabled'] is True)
check('actual_popup_control_uncertainty_missing_accessible_name',any(c['detail']=='Awaiting native confirmation' and 'awaiting native confirmation' not in c['ariaLabel'].lower() for c in cases['unknown-menu']['frame']['popup']))
renderer=(GUI/'src/SurfaceRenderer.elm').read_text();css=(GUI/'assets/shell.css').read_text()
check('controlled_markup_label_precedes_detail','[text item.label,span [class "control-detail"] [text item.detail]]' in renderer)
check('controlled_css_truncates_whole_bar_button','max-width:240px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis' in css)
check('controlled_css_truncates_popup_explanation','.popup .surface-popup>p[role=status]{line-height:20px;margin:0 0 4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}' in css)
for name in ['prepare.py','webkit_fixture.py','native.py']:
 source=(ROOT/'qa'/name).read_text();ast.parse(source);check('python_syntax_'+name,True)
 if name=='native.py':
  check('original_private_output_geometry','mode="800x600@60"' in source and '800,600,LUA' in source)
  check('six_second_observation_deadline','deadline=time.monotonic()+6' in source)
  check('root_owned_separate_future_evidence','ELM_LAYOUT_NATIVE_OUTPUT' in source and 'not OUT.is_relative_to(ROOT)' in source)
  check('fresh_renderer_each_independent_trace',"command('reload')" in source)
 if name=='webkit_fixture.py':
  check('actual_assets_no_detached_fake_html','view.load_uri(' in source and 'load_html' not in source)
  check('network_navigation_refused',"decision.ignore()" in source and "name not in ALLOWED" in source)
  check('actual_elm_adapter_ports','window.receivePresentation(' in source and 'window.receiveFocus(' in source)
import gi
gi.require_foreign('cairo')
gi.require_version('WebKit2','4.1')
from gi.repository import WebKit2
check('installed_webkit_snapshot_api',hasattr(WebKit2.WebView,'get_snapshot') and hasattr(WebKit2.WebView,'evaluate_javascript'))
report={'passed':True,'checks':checks,'assertions':len(checks),'nativeExecuted':False,'requirementRegistrySHA256':digest(GUI.parents[1]/'docs/elm-roadmap/requirements.json'),'sourceFindings':[{'id':'UX-UNC-001','severity':'high','requirementIds':['ELM-UI-013','ELM-UI-015','ELM-UX-027'],'contract':'Blocked target uncertainty must remain visually visible independently of title length','evidence':'actual root packet +actual markup/CSS: entire button ellipsis clips trailing detail; actual pixels pending','proposedChange':'Separate .control-label sibling; ellipsis label only; preserve detail on own line in48px bar or explicit persistent visible status affordance; do not rely on global visually hidden status.'},{'id':'UX-UNC-002','severity':'medium','requirementIds':['ELM-UI-009','ELM-UI-010','ELM-UI-015'],'contract':'Window menu/picker accessible names explain blocked uncertainty','evidence':'actual compiled Surface packets ariaLabel omits blocked detail; aria-label overrides content; actual AT pending','proposedChange':'Include awaiting native confirmation in blocked menu/picker ariaLabel while preserving full operation/title and DOM identity.'},{'id':'UX-UNC-003','severity':'medium','requirementIds':['ELM-UI-013','ELM-UI-015','ELM-UX-027'],'contract':'Read-only refresh explanation remains visible at narrow popup viewport','evidence':'actual popup status text and CSS forces one-line ellipsis; actual rendered text/pixels pending','proposedChange':'Wrap popup status and retain read-only/no-retry wording; check all rows/focus remain scroll reachable inside420px viewport.'}],'preparationReport':pointer['report'],'sourceSHA256':{str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/'qa').glob('*.py'))},'WebKitVersion':[WebKit2.get_major_version(),WebKit2.get_minor_version(),WebKit2.get_micro_version()]}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
