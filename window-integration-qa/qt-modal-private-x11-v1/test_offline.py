#!/usr/bin/env python3
"""Offline target/snapshot checks; no native or main-desktop connections."""
from pathlib import Path
import ast,hashlib,json,unittest,importlib.util,math
from unittest.mock import patch
import main_observations as obs
from main_observer import encode,decode
from private_target import assert_private_environment
from run_native import transport_log_gate,EXPECTED_HOST_GATES
from button_geometry import button_point,contains,layout_ready
from cursor_readiness import native_arrived,native_delta,TOLERANCE_LOGICAL_PX
B=Path(__file__).resolve().parent
class OfflineTests(unittest.TestCase):
 def test_files_current_different_pid_and_visible(self):
  def answer(*args):
   if args[-2:]==('list','-j'):return json.dumps([{'pid':12345,'id':'current-instance'}])
   return json.dumps({'state':{'cwd':'public-home'},'uiState':{'visible':True,'history':['home'],'focusIdentity':'path'},'migrationStatus':{'ready':True,'instance':'current-instance','pid':12345}}[args[-1]])
  with patch.object(obs,'run',side_effect=answer),patch.object(obs,'start',return_value='current-start'):
   actual=obs.files();self.assertEqual(actual['pid'],12345);self.assertEqual(actual['start'],'current-start');self.assertTrue(actual['ui']['visible']);self.assertEqual(actual['instance'],'current-instance')
 def test_files_absent_snapshot_without_starting_app(self):
  with patch.object(obs,'run',return_value='[]') as command:
   actual=obs.files();self.assertFalse(actual['running']);self.assertIsNone(actual['pid']);self.assertIsNone(actual['ui']);self.assertEqual(command.call_count,1)
 def test_multiple_instances_fail_without_selecting_first(self):
  with patch.object(obs,'run',return_value=json.dumps([{'pid':1},{'pid':2}])):
   with self.assertRaises(AssertionError):obs.files()
 def test_private_snapshot_roundtrip_retains_types(self):
  sample={'catalog':{'path':b'\x00private\xff'},'clipboard':[[(0,'hash'),('mime',0,5,'payload')],[]],'dashboard':None}
  self.assertEqual(decode(json.loads(json.dumps(encode(sample)))),sample)
 def environments(self):
  main={'XDG_RUNTIME_DIR':'/run/user/1000','HYPRLAND_INSTANCE_SIGNATURE':'main','WAYLAND_DISPLAY':'wayland-1','DBUS_SESSION_BUS_ADDRESS':'unix:path=/run/user/1000/bus'}
  private={'XDG_RUNTIME_DIR':'/run/user/1000/wqa/abcd','HYPRLAND_INSTANCE_SIGNATURE':'private','WAYLAND_DISPLAY':'wayland-1','DBUS_SESSION_BUS_ADDRESS':'unix:path=/run/user/1000/wqa/abcd/bus'}
  for key,tail in [('HOME','home'),('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data'),('XDG_STATE_HOME','state')]:private[key]=private['XDG_RUNTIME_DIR']+'/'+tail
  return main,private
 def test_same_basename_distinct_private_runtime(self):
  main,private=self.environments();self.assertEqual(str(assert_private_environment(main,private)),'/run/user/1000/wqa/abcd/wayland-1')
 def test_main_target_and_state_escapes_refused(self):
  main,private=self.environments()
  for key,value in [('XDG_RUNTIME_DIR',main['XDG_RUNTIME_DIR']),('HYPRLAND_INSTANCE_SIGNATURE','main'),('WAYLAND_DISPLAY','/run/user/1000/wayland-1'),('HOME','/home/hoskinson'),('DBUS_SESSION_BUS_ADDRESS',main['DBUS_SESSION_BUS_ADDRESS']),('AT_SPI_BUS_ADDRESS','main-a11y')]:
   with self.subTest(key=key),self.assertRaises(AssertionError):assert_private_environment(main,dict(private,**{key:value}))
 def test_exact19_planned_toolkit_gates(self):
  tree=ast.parse((B/'private_session.py').read_text());gates=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='check'];self.assertEqual(len(gates),19)
 def test_fixture_byte_identical_and203_unchanged(self):
  old=B.parent/'qt-modal-compat-v2';packet=json.loads((old/'frozen-inputs.json').read_text())
  for row in packet['files']:self.assertEqual(hashlib.sha256(Path(row['path']).read_bytes()).hexdigest(),row['sha256'])
  for name in ('CMakeLists.txt','build/qt-window-modal-fixture','build/CMakeCache.txt'):self.assertEqual((B/name).read_bytes(),(old/name).read_bytes())
  self.assertNotEqual((B/'fixture.cpp').read_bytes(),(old/'fixture.cpp').read_bytes())
  # Window creation/actions stay exact; only state/event observation changed.
  original=(old/'fixture.cpp').read_text();current=(B/'fixture.cpp').read_text()
  self.assertEqual(current[current.index('  QWidget* create'):current.index('protected:')],original[original.index('  QWidget* create'):original.index('protected:')])
 def clean_log(self):return 'Private AQ_BACKENDS=wayland: mandatory parent, no DRM or libseat backend\nOutput WAYLAND-1: configure surface with 3'
 def test_clean_mandatory_configure_log(self):self.assertTrue(transport_log_gate([self.clean_log()])['passed']);self.assertEqual(EXPECTED_HOST_GATES,10)
 def test_all_broken_pipes_refused_without_waiver(self):
  for error in ["ERR ]: Couldn't write to socket. Error: Broken pipe",'Broken pipe','parent transport failed','error 3: xdg_surface has never been configured','Starting the DRM backend','[libseat] forbidden']:
   with self.subTest(error=error):self.assertFalse(transport_log_gate([self.clean_log(),error])['passed'])
 def test_mandatory_marker_and_configure_both_required(self):
  for text in ['',self.clean_log().splitlines()[0],self.clean_log().splitlines()[1]]:self.assertFalse(transport_log_gate([text])['passed'])
 def test_retained_raster_failed_guard_remains_refused(self):
  old=B.parent/'family-raster-oracle-v3/attempt-private-1/private-session/runtime-archive/hypr'
  logs=list(old.glob('*/hyprland.log'));self.assertEqual(len(logs),1);self.assertFalse(transport_log_gate([logs[0].read_text()])['passed'])
 def test_diagnostic_plugin_has_no_actor_or_hooks(self):
  source=(B/'native-probe/probe.cpp').read_text()
  for token in ('fullWindowFocus(', 'info.cancelled =', 'raise(', 'moveWindowToWorkspace(', 'createFunctionHook(', 'invokeHyprctlCommand('):self.assertNotIn(token,source)
  for token in ('hasHeldButtons()', 'm_seatGrab', 'getClickMode()'):
   self.assertIn(token,source)
 def test_quit_oracle_uses_events_and_exit(self):
  tree=ast.parse((B/'private_session.py').read_text());command=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='command');source=ast.get_source_segment((B/'private_session.py').read_text(),command)
  self.assertIn("if name=='quit'",source);self.assertIn("process.returncode==0",source);self.assertIn("row.get('epoch')==epoch",source)
 def test_supported_portal_disable_only_fixture_env(self):
  source=(B/'private_session.py').read_text();self.assertIn("QT_NO_XDG_DESKTOP_PORTAL='1'",source);self.assertNotIn('QT_NO_XDG_DESKTOP_PORTAL', (B/'run_native.py').read_text())
 def test_button_point_uses_client_bounds_and_native_origin(self):
  widget={'geometryGlobal':[9999,9999,460,300],'buttonClient':[11,139,438,22],'layoutGeometry':[0,0,460,300]};native={'surfaceBox':[100,250,460,300]}
  point=button_point(widget,native);self.assertEqual(point,(116,400));self.assertFalse(contains([260,310,320,180],point))
 def test_different_client_surface_extent_refused(self):
  widget={'geometryGlobal':[0,0,460,300],'buttonClient':[11,139,438,22],'layoutGeometry':[0,0,460,300]}
  with self.assertRaises(AssertionError):button_point(widget,{'surfaceBox':[100,250,920,600]})
 def test_invalid_button_bounds_refused(self):
  for button in ([11,139,500,22],[-1,10,20,20],[10,300,20,20],[10,10,0,20]):
   with self.subTest(button=button),self.assertRaises(AssertionError):button_point({'geometryGlobal':[0,0,460,300],'buttonClient':button,'layoutGeometry':[0,0,460,300]},{'surfaceBox':[100,250,460,300]})
 def test_retained_v6_stale_capture_generates_outside_point_then_new_refuses(self):
  old=B.parent/'qt-modal-private-v6';report=json.loads((old/'attempt-1/qt/report.json').read_text());baseline=report['checks'][0]['ownerBaselineCallback']
  spec=importlib.util.spec_from_file_location('retained_v6_geometry',old/'button_geometry.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  stale={'geometryGlobal':[0,0,773,942],'buttonClient':baseline['buttonClient'],'layoutGeometry':[0,0,773,942]};native=baseline['nativeSurface']
  point=module.button_point(stale,native);self.assertEqual(list(point),baseline['point']);self.assertFalse(contains([111,389,438,22],point))
  with self.assertRaises(AssertionError):button_point(stale,native)
  self.assertFalse(layout_ready(stale,native));self.assertFalse(baseline['passed'])
 def test_layout_must_finish_and_configured_extent_match(self):
  native={'surfaceBox':[100,250,460,300]};current={'geometryGlobal':[0,0,460,300],'buttonClient':[11,139,438,22],'layoutGeometry':[0,0,460,300]}
  self.assertTrue(layout_ready(current,native));self.assertEqual(button_point(current,native),(116,400))
  for layout in ([0,0,773,942],[0,0,0,0],[1,0,460,300]):
   with self.subTest(layout=layout):self.assertFalse(layout_ready(dict(current,layoutGeometry=layout),native))
 def test_geometry_refresh_is_observation_only(self):
  source=(B/'fixture.cpp').read_text();observed=source[source.index('protected:'):source.index('public:')]
  for token in ('QEvent::Resize','QEvent::Move','QEvent::LayoutRequest','QTimer::singleShot(0,this,[this]{saveState();})'):self.assertIn(token,observed)
  for token in ('activate()', 'setGeometry(', 'resize(', 'setFocus('):self.assertNotIn(token,observed)
  source=(B/'private_session.py').read_text();self.assertIn("return capture_button(name)",source);self.assertIn('previous==key',source);self.assertIn('previous=None;return None',source)
 def test_actual_v7_floor_and_virtual_pointer_normalization(self):
  old=B.parent/'qt-modal-private-v7/attempt-1';qt=json.loads((old/'qt/report.json').read_text());report=json.loads((old/'report.json').read_text())
  requested=qt['pointerCoordinateTrace'][0]['requestedLogical'];integer=qt['pointerCoordinateTrace'][0]['observationsBeforeButtons'][0];native=report['cleanup']['nativeButtonObservations'][0]['native']
  self.assertEqual(requested,[116,400]);self.assertEqual(native['cursor'][0],(116/1600)*1600);self.assertEqual(integer,{'x':math.floor(native['cursor'][0]),'y':math.floor(native['cursor'][1])})
  self.assertGreater(abs(integer['x']-requested[0]),TOLERANCE_LOGICAL_PX);self.assertTrue(native_arrived(native,requested));self.assertLess(abs(native_delta(native,requested)[0]),1e-10)
  self.assertFalse(any(e.get('event')=='dialogOpened' or e.get('eventType')==2 for e in qt['qtEvents']))
 def test_native_error_threshold_unchanged_and_bad_actual_refused(self):
  self.assertEqual(TOLERANCE_LOGICAL_PX,0.5)
  for actual in ([116.500001,400],[115.499999,400],[116,400.500001],[116,399.499999]):
   with self.subTest(actual=actual):self.assertFalse(native_arrived({'cursor':actual},[116,400]))
  self.assertTrue(native_arrived({'cursor':[116.5,399.5]},[116,400]))
 def test_nonfinite_missing_or_boolean_native_coordinate_refused(self):
  for position in ([math.nan,400],[116,math.inf],[False,400],[116],['116',400]):
   with self.subTest(position=position),self.assertRaises(AssertionError):native_arrived({'cursor':position},[116,400])
 def test_native_probe_and_qt_fixture_exact_v7_sources_binaries(self):
  old=B.parent/'qt-modal-private-v7'
  for name in ('fixture.cpp','build-v7/qt-window-modal-fixture','native-probe/probe.cpp','native-probe/libqt-modal-probe.so'):
   self.assertEqual((B/name).read_bytes(),(old/name).read_bytes())
  cli=(B/'primary-cursor/HyprCtl.cpp').read_text();self.assertIn('getMouseCoordsInternal().floor()',cli)
  self.assertIn('sc<double>(x) / xExtent',(B/'primary-cursor/VirtualPointer.cpp').read_text());self.assertIn('mappedArea.pos() + mappedArea.size() * abs',(B/'primary-cursor/PointerManager.cpp').read_text())
 def test_strict_callback_and_focus_oracle_stays_joint(self):
  source=(B/'private_session.py').read_text();self.assertIn("count('owner')==start and active('child')",source);self.assertIn("baselineVerified=True",source)

if __name__=='__main__':unittest.main()
