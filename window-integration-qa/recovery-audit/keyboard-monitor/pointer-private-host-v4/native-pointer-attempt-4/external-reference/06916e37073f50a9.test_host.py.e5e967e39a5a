"""Offline guards: no compositor, bus, Wayland probe or input is launched."""
import hashlib,json,os,socket,stat,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
import weston_host as h

class Guards(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='kbn-');self.runtime=Path(self.tmp.name);self.runtime.chmod(0o700)
  mocked=patch.object(h.qa,'verify_runtime',side_effect=lambda path:Path(path));mocked.start();self.addCleanup(mocked.stop)
 def tearDown(self):self.tmp.cleanup()
 def test_environment_does_not_retain_main_routes(self):
  main={k:'MAIN' for k in h.DROP};main.update(HOME='/original',XDG_RUNTIME_DIR='/run/user/1000',PATH='/usr/bin')
  original=dict(main);env=h.private_env(main,self.runtime)
  self.assertEqual(main,original)
  for key in ('DISPLAY','HYPRLAND_INSTANCE_SIGNATURE','AT_SPI_BUS_ADDRESS','AQ_DRM_DEVICES','LIBGL_ALWAYS_SOFTWARE','PYTHONPATH'):self.assertNotIn(key,env)
  for key in ('HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME'):self.assertTrue(Path(env[key]).is_relative_to(self.runtime))
  self.assertEqual(env['DBUS_SESSION_BUS_ADDRESS'],'unix:path='+str(self.runtime/'bus'))
  self.assertEqual(env['WAYLAND_DISPLAY'],'weston-host');self.assertEqual(env['AQ_BACKENDS'],'wayland')
 def test_selection_is_explicit_not_default(self):
  env=h.private_env({},self.runtime);self.assertNotIn('DRI_PRIME',env);self.assertNotIn('__EGL_VENDOR_LIBRARY_FILENAMES',env)
  env=h.private_env({},self.runtime,'pci-0000_00_02_0',True)
  self.assertEqual(env['DRI_PRIME'],'pci-0000_00_02_0')
  with self.assertRaises(AssertionError):h.private_env({},self.runtime,'../../../main')
 def test_module_paths_are_owned_prefix(self):
  env=h.private_env({},self.runtime)
  modules=dict(s.split('=',1) for s in env['WESTON_MODULE_MAP'].split(';'))
  self.assertEqual(set(modules),{'headless-backend.so','gl-renderer.so','kiosk-shell.so'})
  self.assertTrue(all(Path(p).resolve().is_relative_to(h.PREFIX) for p in modules.values()))
 def test_constructor_does_not_launch(self):
  with patch.object(h.subprocess,'Popen',side_effect=AssertionError('launch')):
   session=h.PrivateHyprSession(self.runtime/'unused',{},1600,1000,b'-- reviewed Lua\n')
  self.assertFalse((self.runtime/'unused').exists());self.assertEqual(session.host.width,1600)
  with self.assertRaises(ValueError):h.PrivateHyprSession(self.runtime/'unused',{},1600,1000,'not bytes')
 def test_scope_refusal_precedes_every_mutation(self):
  host=h.PrivateWestonHost(self.runtime/'unused',{},1600,1000)
  with patch.object(h.qa,'require_qa_scope',side_effect=RuntimeError('not in scope')),patch.object(host,'verify',side_effect=AssertionError('must not verify')),patch.object(h.qa,'private_runtime',side_effect=AssertionError('must not create')):
   with self.assertRaises(RuntimeError):host.__enter__()
  self.assertFalse(host.output.exists());self.assertIsNone(host.runtime);self.assertEqual(host.processes,[])
 def test_xwayland_disabled_in_effective_private_config(self):
  source=b'hl.config({ xwayland = { enabled = true } })\n'
  effective=h.effective_lua(source)
  self.assertTrue(effective.startswith(source));self.assertTrue(effective.endswith(b'hl.config({ xwayland = { enabled = false } })\n'))
 def test_nested_parent_peer_must_be_exact_weston(self):
  host=h.PrivateWestonHost(self.runtime/'unused',{},1600,1000);host.env={};host.runtime=self.runtime;host.evidence['weston']=h.process(os.getpid())
  with patch.object(h.qa,'nested_env',return_value=({},dict(pid=os.getpid()+1))):
   with self.assertRaises(RuntimeError):h.nested_base(host)
 def test_nested_egl_uses_wayland_not_host_surfaceless_override(self):
  host=h.PrivateWestonHost(self.runtime/'unused',{},1600,1000);host.env={};host.runtime=self.runtime;host.evidence['weston']=h.process(os.getpid())
  with patch.object(h.qa,'nested_env',return_value=({'AQ_BACKENDS':'wayland','WAYLAND_DISPLAY':'explicit-private-parent','EGL_PLATFORM':'surfaceless'},dict(pid=os.getpid()))):env,parent=h.nested_base(host)
  self.assertNotIn('EGL_PLATFORM',env);self.assertEqual(env['AQ_BACKENDS'],'wayland');self.assertEqual(parent['pid'],os.getpid())
 def test_archive_preserves_inner_log_before_removal(self):
  output=self.runtime/'output';output.mkdir();inner=self.runtime/'inner';inner.mkdir()
  payload=b'actual inner log\x00bytes';(inner/'hyprland.log').write_bytes(payload)
  (inner/'hyprland.lua').write_bytes(b'-- exact config');(inner/'ignored.sock').write_bytes(b'no')
  (inner/'linked.log').symlink_to('/etc/passwd')
  rows=h.archive_runtime(inner,output)
  self.assertEqual(len(rows),2);archived=output/'runtime-archive/hyprland.log'
  self.assertEqual(archived.read_bytes(),payload);self.assertEqual(stat.S_IMODE(archived.stat().st_mode),0o600)
  self.assertEqual(rows[-1]['sha256'],h.digest(output/'runtime-archive/hyprland.lua'))
 def test_socket_inode_and_symlink_guards(self):
  s=socket.socket(socket.AF_UNIX);path=self.runtime/'private';s.bind(str(path))
  try:
   expected=h.socket_identity(path,self.runtime);self.assertEqual(expected['uid'],os.getuid())
   alias=self.runtime/'alias';alias.symlink_to(path)
   with self.assertRaises(RuntimeError):h.socket_identity(alias,self.runtime)
   with self.assertRaises(RuntimeError):h.socket_identity('/run/user/1000/wayland-0',self.runtime)
  finally:s.close()
 def session(self):
  session=h.PrivateHyprSession(self.runtime/'out',{},1600,1000,b'-- config')
  session.child_identity=h.process(os.getpid());path=self.runtime/'ipc';s=socket.socket(socket.AF_UNIX);s.bind(str(path));self.addCleanup(s.close)
  session.host.runtime=self.runtime;session.sockets=[h.socket_identity(path,self.runtime)]
  session.env={'HYPRLAND_INSTANCE_SIGNATURE':'private_sig','WAYLAND_DISPLAY':'wayland-9','XDG_RUNTIME_DIR':str(self.runtime),'DBUS_SESSION_BUS_ADDRESS':'unix:path='+str(self.runtime/'bus')}
  session.evidence.update(signature='private_sig',waylandSocket='wayland-9')
  return session
 def test_ipc_always_explicit_private_signature(self):
  session=self.session()
  with patch.object(h.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'[]','')) as run:
   self.assertEqual(session.data('clients'),[])
  self.assertEqual(run.call_args.args[0],['/usr/bin/hyprctl','-i','private_sig','-j','clients'])
  self.assertEqual(run.call_args.kwargs['env'],session.env)
 def test_no_ipc_after_routing_change(self):
  session=self.session();session.env['HYPRLAND_INSTANCE_SIGNATURE']='main'
  with patch.object(h.subprocess,'run',side_effect=AssertionError('must not request')):
   with self.assertRaises(RuntimeError):session.ctl('version')
 def test_no_ipc_after_socket_replacement(self):
  session=self.session();path=Path(session.sockets[0]['path']);path.unlink();new=socket.socket(socket.AF_UNIX);new.bind(str(path));self.addCleanup(new.close)
  with patch.object(h.subprocess,'run',side_effect=AssertionError('must not request')):
   with self.assertRaises(RuntimeError):session.ctl('version')
 def test_no_ipc_after_runtime_change(self):
  session=self.session();session.env['XDG_RUNTIME_DIR']='/run/user/1000'
  with patch.object(h.subprocess,'run',side_effect=AssertionError('must not request')):
   with self.assertRaises(RuntimeError):session.ctl('version')
 def test_known_exit_reaped_before_signal(self):
  host=h.PrivateWestonHost(self.runtime/'out',{},1600,1000);proc=Mock();proc.poll.return_value=0
  with patch.object(h.os,'kill',side_effect=AssertionError('must not signal')):host.stop(h.process(os.getpid()),proc)

if __name__=='__main__':unittest.main()
