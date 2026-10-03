#!/usr/bin/env python3
"""Offline target/snapshot checks; no native or main-desktop connections."""
from pathlib import Path
import ast,hashlib,json,unittest
from unittest.mock import patch
import main_observations as obs
from main_observer import encode,decode
from private_target import assert_private_environment
from run_native import transport_log_gate,EXPECTED_HOST_GATES
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
  for name in ('fixture.cpp','CMakeLists.txt','build/qt-window-modal-fixture','build/CMakeCache.txt'):self.assertEqual((B/name).read_bytes(),(old/name).read_bytes())
 def clean_log(self):return 'Private AQ_BACKENDS=wayland: mandatory parent, no DRM or libseat backend\nOutput WAYLAND-1: configure surface with 3'
 def test_clean_mandatory_configure_log(self):self.assertTrue(transport_log_gate([self.clean_log()])['passed']);self.assertEqual(EXPECTED_HOST_GATES,9)
 def test_all_broken_pipes_refused_without_waiver(self):
  for error in ["ERR ]: Couldn't write to socket. Error: Broken pipe",'Broken pipe','parent transport failed','error 3: xdg_surface has never been configured','Starting the DRM backend','[libseat] forbidden']:
   with self.subTest(error=error):self.assertFalse(transport_log_gate([self.clean_log(),error])['passed'])
 def test_mandatory_marker_and_configure_both_required(self):
  for text in ['',self.clean_log().splitlines()[0],self.clean_log().splitlines()[1]]:self.assertFalse(transport_log_gate([text])['passed'])
 def test_retained_raster_failed_guard_remains_refused(self):
  old=B.parent/'family-raster-oracle-v3/attempt-private-1/private-session/runtime-archive/hypr'
  logs=list(old.glob('*/hyprland.log'));self.assertEqual(len(logs),1);self.assertFalse(transport_log_gate([logs[0].read_text()])['passed'])

if __name__=='__main__':unittest.main()
