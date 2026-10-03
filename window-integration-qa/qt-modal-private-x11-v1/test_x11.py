from pathlib import Path
import ast,hashlib,json,tempfile,unittest
from unittest.mock import patch
from private_target import assert_private_environment
from xcb_loader import native_loader_gate,QXCB,QPA,sha
B=Path(__file__).resolve().parent
class X11Packet(unittest.TestCase):
 def test_same_nineteen_action_oracles(self):
  def gates(p):return [ast.get_source_segment(p.read_text(),n) for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='check']
  original=gates(B.parent/'qt-modal-private-v9/private_session.py');fresh=gates(B/'private_session.py');self.assertEqual(len(fresh),19);self.assertEqual(fresh[1:],original[1:])
 def test_same_compiled_public_fixture(self):
  for name in ('fixture.cpp','build-v7/qt-window-modal-fixture','native-probe/probe.cpp','native-probe/libqt-modal-probe.so'):
   self.assertEqual((B/name).read_bytes(),(B.parent/'qt-modal-private-v9'/name).read_bytes())
 def test_required_xcb_modules_are_real_resolved_loader_inputs(self):
  closure=json.loads((B/'xcb-loader-closure.json').read_text());self.assertEqual(closure['files'][str(QXCB.resolve())],sha(QXCB));self.assertEqual(closure['files'][str(QPA)],sha(QPA));self.assertTrue(closure['actualMapsRequired']);self.assertFalse(closure['nativeLoaderProved'])
 def test_missing_native_module_refused(self):
  with patch('xcb_loader.mapped',return_value={}):
   with self.assertRaisesRegex(RuntimeError,'mapping'):native_loader_gate(1)
 def test_wrong_loaded_binary_refused(self):
  with patch('xcb_loader.mapped',return_value={str(QXCB.resolve()):'wrong',str(QPA):sha(QPA)}):
   with self.assertRaisesRegex(RuntimeError,'mapping'):native_loader_gate(1)
 def test_exact_two_required_maps_accepted(self):
  with patch('xcb_loader.mapped',return_value={str(QXCB.resolve()):sha(QXCB),str(QPA):sha(QPA)}):self.assertTrue(native_loader_gate(1)['passed'])
 def test_owned_authority_and_display_required(self):
  with tempfile.TemporaryDirectory() as d:
   runtime=Path(d);authority=runtime/'auth';authority.write_bytes(b'fixture');authority.chmod(0o600)
   main={'XDG_RUNTIME_DIR':'/main','HYPRLAND_INSTANCE_SIGNATURE':'main','WAYLAND_DISPLAY':'main','DISPLAY':':0'}
   private={'XDG_RUNTIME_DIR':d,'HYPRLAND_INSTANCE_SIGNATURE':'private','WAYLAND_DISPLAY':'wayland-2','DISPLAY':':2','XAUTHORITY':str(authority)}
   for k in ('HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME'):private[k]=d
   self.assertEqual(assert_private_environment(main,private,allow_x11=True),runtime/'wayland-2')
   for values in ({'DISPLAY':':0'},{'DISPLAY':'localhost:2'},{'XAUTHORITY':'/main/auth'}):
    with self.subTest(values=values),self.assertRaises(AssertionError):assert_private_environment(main,{**private,**values},allow_x11=True)
   authority.chmod(0o644)
   with self.assertRaises(AssertionError):assert_private_environment(main,private,allow_x11=True)
 def test_default_target_rejects_x11(self):
  main={'XDG_RUNTIME_DIR':'/main','HYPRLAND_INSTANCE_SIGNATURE':'main','WAYLAND_DISPLAY':'main'}
  private={'XDG_RUNTIME_DIR':'/private','HYPRLAND_INSTANCE_SIGNATURE':'private','WAYLAND_DISPLAY':'wayland-2','DISPLAY':':2'}
  for k in ('HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME'):private[k]='/private'
  with self.assertRaises(AssertionError):assert_private_environment(main,private)
 def test_source_truthful_peer_creator(self):
  source=(B.parent/'private-weston-x11-host-v1/weston_host.py').read_text();self.assertIn("'peerCreator'",source);self.assertIn("pid!=self.child.pid",source);self.assertIn("auth.has_fd(server['pid'],inode)",source)

if __name__=='__main__':unittest.main()
