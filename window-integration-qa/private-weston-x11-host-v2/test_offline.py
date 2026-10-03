import importlib.util,json,os,resource,socket,stat,struct,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import x11_authority as a
spec=importlib.util.spec_from_file_location('_test_x11_host',Path(__file__).parent/'weston_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
class X11Tests(unittest.TestCase):
 def test_reviewed_launcher_mode_survives_umask077(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'Xwayland';previous=os.umask(0o077)
   try:host.write_exclusive(p,b'fixture',0o755)
   finally:os.umask(previous)
   self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o755);self.assertEqual(p.read_bytes(),b'fixture')
 def test_actual_primary_availability_mode700_refused(self):
  with tempfile.TemporaryDirectory() as folder:
   private=Path(folder);private.chmod(0o700);wrapper=private/'Xwayland';wrapper.write_text('#!/bin/sh\nexit 99\n');wrapper.chmod(0o700)
   r=subprocess.run([str(Path(__file__).parent/'executable-probe')],env={**os.environ,'PATH':str(private)+':/usr/bin'},capture_output=True,text=True,timeout=4)
   self.assertEqual((r.returncode,r.stdout.strip()),(0,'false'))
 def test_actual_primary_availability_mode755_accepted(self):
  with tempfile.TemporaryDirectory() as folder:
   private=Path(folder);private.chmod(0o700);wrapper=private/'Xwayland';wrapper.write_text('#!/bin/sh\nexit 99\n');wrapper.chmod(0o755)
   r=subprocess.run([str(Path(__file__).parent/'executable-probe')],env={**os.environ,'PATH':str(private)+':/usr/bin'},capture_output=True,text=True,timeout=4)
   self.assertEqual((r.returncode,r.stdout.strip()),(0,'true'));self.assertEqual(stat.S_IMODE(private.stat().st_mode),0o700)
 def test_upstream_args(self):self.assertEqual(a.parse_args([':2','-rootless','-core','-listenfd','4','-listenfd','5','-displayfd','6','-wm','7']),(':2',[4,5,6,7]))
 def test_main_or_remote_display_refused(self):
  for name in (':33','localhost:1','1',':1.0'):
   with self.assertRaises(RuntimeError):a.parse_args([name,'-rootless','-core','-listenfd','4','-listenfd','5','-displayfd','6','-wm','7'])
 def test_unapproved_flags_refused(self):
  for args in ([':1','-ac'],[':1','-rootless','-core','-listenfd','4','-listenfd','4','-displayfd','6','-wm','7'],[':1','-rootless','-core','-listenfd','2','-listenfd','5','-displayfd','6','-wm','7'],[':1','-rootless','-core','-listenfd','4','-listenfd','5','-displayfd','6','-wm','7','-auth','foreign']):
   with self.assertRaises(RuntimeError):a.parse_args(args)
 def test_cookie_binary_roundtrip(self):
  cookie=bytes(range(16));raw=a.authority_bytes(':12',cookie);self.assertEqual(a.decode_authority(raw),(':12',cookie));self.assertEqual(raw[:2],b'\xff\xff')
 def test_authority_reject_truncated_changed_role(self):
  raw=a.authority_bytes(':2',b'x'*16)
  for bad in (raw[:-1],raw+b'x',b'\0\0'+raw[2:]):
   with self.assertRaises((ValueError,struct.error)):a.decode_authority(bad)
 def test_setup_without_cookie(self):
  raw=a.setup_request();self.assertEqual(len(raw),12);self.assertEqual(struct.unpack('<HHHHH',raw[2:]),(11,0,0,0,0))
 def test_setup_cookie_padding(self):
  raw=a.setup_request(b'x'*16);self.assertEqual(len(raw)%4,0);self.assertEqual(struct.unpack('<HHHHH',raw[2:12]),(11,0,18,16,0));self.assertEqual(raw[12:30],a.NAME)
 def test_setup_success_real_fragment_reads(self):
  left,right=socket.socketpair()
  with left,right:
   right.sendall(b'\x01\0'+struct.pack('<HHH',11,0,2)+b'x'*8);reply=a.setup_reply(left);self.assertEqual((reply['status'],reply['major'],reply['bytes']),(1,11,16))
 def test_setup_refusal_not_success(self):
  left,right=socket.socketpair()
  with left,right:
   right.sendall(b'\0\x04'+struct.pack('<HHH',11,0,1)+b'fail');self.assertEqual(a.setup_reply(left)['status'],0)
 def test_setup_truncation_refused(self):
  left,right=socket.socketpair()
  with left,right:
   right.sendall(b'\1\0'+struct.pack('<HHH',11,0,1));right.shutdown(socket.SHUT_WR)
   with self.assertRaises(RuntimeError):a.setup_reply(left)
 def test_setup_oversize_refused(self):
  left,right=socket.socketpair()
  with left,right:
   right.sendall(b'\1\0'+struct.pack('<HHH',11,0,16385))
   with self.assertRaises(RuntimeError):a.setup_reply(left)
 def test_private_file_symlink_and_mode_refusal(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'secret';p.write_bytes(b'x');p.chmod(0o600);self.assertEqual(a.private_file(p)['mode'],0o600)
   link=Path(folder)/'link';link.symlink_to(p)
   with self.assertRaises(RuntimeError):a.private_file(link)
   p.chmod(0o644)
   with self.assertRaises(RuntimeError):a.private_file(p)
 def test_effective_config_x11_only(self):
  original=b'hl.config({xwayland={enabled=false}})';effective=host.effective_lua(original)
  self.assertTrue(effective.startswith(original));self.assertTrue(effective.endswith(b'hl.config({ xwayland={enabled=true,create_abstract_socket=false} })\n'))
 def test_bad_config_refused(self):
  for value in ('text',b'',None):
   with self.assertRaises(ValueError):host.effective_lua(value)
 def test_import_no_launch(self):
  with patch('subprocess.Popen',side_effect=AssertionError('launch forbidden')),patch('os.execve',side_effect=AssertionError('exec forbidden')):
   loader=importlib.util.spec_from_file_location('_import_x11_no_actions',Path(__file__).parent/'weston_host.py');module=importlib.util.module_from_spec(loader);loader.loader.exec_module(module)
 def test_launcher_missing_scope_refuses_before_exec(self):
  with patch.object(a,'require_qa_scope',side_effect=RuntimeError('scope absent')),patch('os.execve',side_effect=AssertionError('exec forbidden')):
   with self.assertRaisesRegex(RuntimeError,'scope absent'):a.launcher()
 def test_launcher_bad_core_refuses_before_exec(self):
  with patch.object(a,'require_qa_scope',return_value={}),patch.object(resource,'getrlimit',return_value=(0,0)),patch('os.execve',side_effect=AssertionError('exec forbidden')):
   with self.assertRaisesRegex(RuntimeError,'core1'):a.launcher()
 def test_base_config_stays_disabled(self):self.assertTrue(host.original.effective_lua(b'baseline').endswith(b'hl.config({ xwayland = { enabled = false } })\n'))

if __name__=='__main__':unittest.main()
