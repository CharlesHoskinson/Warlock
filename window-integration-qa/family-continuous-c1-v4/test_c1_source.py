"""Inherited gate/source preservation and explicit reviewed pairing checks."""
from pathlib import Path
import unittest
B=Path(__file__).resolve().parent
QA=B.parent
class Preserve(unittest.TestCase):
    def test_all_original_runtime_gates_preserved(self):
        old=(QA/'family-continuous-reversal-v3/native_integration.py').read_text().split('def main():',1)[1]
        new=(B/'native_integration.py').read_text().split('def main():',1)[1]
        start=new.index('                c1_audit=verify_c1.verify(')
        end=new.index("                fourth=service_request_live('restore')",start)
        new=new[:start]+new[end:]
        new=new.replace("len(report['checks'])!=39","len(report['checks'])!=38").replace('Original38 plus1 C1 immutable position/velocity gate required','Original29 plus8 continuous episode and1default selection gates required')
        self.assertEqual(old,new)
    def test_original_origin_and_capture_lifecycle_helpers_exact(self):
        for name in ['verify_reversal.py','capture_evidence.py','private_shell.py','service_observer.py','helper_setup.py','helper_observer.py','service_helper.py','helper_backend.py']:
            if (B/name).exists():self.assertEqual((B/name).read_bytes(),(QA/'family-continuous-reversal-v3'/name).read_bytes(),name)
    def test_original44_oracle_and_entire_runtime_body_exact(self):
        old=QA/'family-raster-production-default-v12';new=QA/'family-raster-c1-v13'
        for name in ['raster_oracle.py','compare_scene.py','producer_observer.py','readback_evidence.py','verify_causal_target.py','private-nested.lua','observations.py','catalog_preservation.py']:
            self.assertEqual((old/name).read_bytes(),(new/name).read_bytes(),name)
        previous=(old/'run_private_raster.py').read_text().split('def main():',1)[1]
        current=(new/'run_private_raster.py').read_text().split('def main():',1)[1].replace('packet = c1_pairing.verified_packet()','packet = json.loads(PACKET.read_text())')
        self.assertEqual(previous,current)
    def test_authority_is_reviewed_v13_and_responsive_not_recovery(self):
        import c1_pairing
        self.assertEqual(c1_pairing.PACKET.name,'source-ready.json')
        self.assertEqual(c1_pairing.verified_packet()['binarySHA256'],c1_pairing.BINARY_SHA)
        source=(B/'native_integration.py').read_text()
        self.assertIn("service-responsive-v13",source);self.assertNotIn('service-recovery-v14',source)
        self.assertIn('c1_pairing.verified_packet()',source)
    def test_formal_precedes_audit(self):
        import json
        evidence=json.loads((B/'c1-formal-before-implementation.json').read_text())
        self.assertTrue(evidence['beforeAuditImplementation']);self.assertFalse(evidence['nativeExecuted'])
        self.assertEqual(evidence['namedCases'],10)
    def test_software_cancel_is_explicit_limited_delegate(self):
        software=QA/'producer-c1-software-cases-v1'
        source=(software/'run_software.py').read_text()
        self.assertIn("observer.send(command='start',token=tokens[0],identities=ids)",source)
        self.assertIn("reduced.send(command='cancel',token=tokens[0],identities=ids)",source)
        self.assertIn('endUserReducedMotionSettingAccepted=False',source)
        self.assertNotIn('.kill(',source);self.assertNotIn('.terminate(',source)
        self.assertIn('resources.callback(close_all)',source)
        self.assertEqual((software/'verify_c1.py').read_bytes(),(B/'verify_c1.py').read_bytes())
if __name__=='__main__':unittest.main()
