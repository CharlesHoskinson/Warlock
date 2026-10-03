"""Whole source/selector conservation; no compositor/client/input execution."""
from pathlib import Path
import hashlib,json,unittest
B=Path(__file__).resolve().parent;OLD=B.with_name('toolkit-held-matrix-v13');Q=B.parent
class Pairing(unittest.TestCase):
 def test_complete_original_matrix_generator_inverse(self):
  for n in ('matrix.json','prepare_matrix.py'):
   raw=(B/n).read_bytes();raw=raw.replace(b'private-weston-aq-bootstrap-host-v5',b'private-weston-aq-host-v4').replace(b'private-weston-x11-bootstrap-host-v3',b'private-weston-x11-host-v2')
   self.assertEqual(raw,(OLD/n).read_bytes(),n)
 def test_entire_native_runtime_and_original_oracles_unchanged(self):
  for n in ('run_native.py','held_controller.py','held_route.py','observations.py','helper_setup.py','helper_observer.py','evaluation_setup.py','qs_lifecycle.py','delegate_diagnostics.py','frontend_route.py','scroll_route.py','input_control.py','public_toolkit.py','service_observer.py','private_shell.py','private_output_host.py','output_readiness.py','main_observer.py','main_observations.py','transport_check.py'):
   self.assertEqual(__import__('source_conservation').reconstructed_v14(n),(OLD/n).read_bytes(),n);self.assertEqual((B/n).stat().st_mode&0o7777,(OLD/n).stat().st_mode&0o7777,n)
  for root in ('payload','frontend-candidate','fixtures','native-probe'):
   for p in (OLD/root).rglob('*'):
    if '__pycache__' in p.parts or not p.is_file():continue
    fresh=B/p.relative_to(OLD);data=fresh.read_bytes()
    if fresh.name=='Windows.qml':data=__import__('terminal_qml').reconstruct(data.decode()).encode()
    self.assertEqual(data,p.read_bytes(),str(p));self.assertEqual(fresh.stat().st_mode&0o7777,p.stat().st_mode&0o7777)
 def test_exact_host_inverse_and_x11_authority(self):
  for old,fresh,left,right in [('private-weston-aq-host-v4','private-weston-aq-bootstrap-host-v5','aquamarine-nested-lifecycle-v1','aquamarine-nested-bootstrap-v2'),('private-weston-x11-host-v2','private-weston-x11-bootstrap-host-v3','private-weston-aq-host-v4','private-weston-aq-bootstrap-host-v5')]:
   source=(Q/fresh/'weston_host.py').read_bytes();self.assertEqual(source.count(right.encode()),1);self.assertEqual(source.replace(right.encode(),left.encode()),(Q/old/'weston_host.py').read_bytes())
  self.assertEqual((Q/'private-weston-x11-host-v2/x11_authority.py').read_bytes(),(Q/'private-weston-x11-bootstrap-host-v3/x11_authority.py').read_bytes())
 def test_source_ready_bootstrap_matches_candidate_hash_and_ack_guards(self):
  aq=Q/'aquamarine-nested-bootstrap-v2';r=json.loads((aq/'source-abi-formal-checkpoint.json').read_text());self.assertEqual(r['result'],'pass');self.assertEqual(r['soleSourceDelta'],['src/backend/Wayland.cpp']);self.assertTrue(r['inverseBootstrapSourceExact']);self.assertFalse(r['nativeLoaded']);self.assertFalse(r['actualFailedWireCauseProved'])
  self.assertEqual(hashlib.sha256((aq/'prefix/lib/libaquamarine.so.0.15.0').read_bytes()).hexdigest(),r['candidateSHA256']);self.assertTrue(all(r['headersByteIdentical'].values()));self.assertEqual(r['missingDirectHyprlandImports'],[])
if __name__=='__main__':unittest.main()
