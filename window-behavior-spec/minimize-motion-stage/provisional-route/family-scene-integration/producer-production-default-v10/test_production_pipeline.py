from pathlib import Path
import unittest
from verify_production_pipeline import verify_selection,ROLES

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'producer-half-open-v9'


def observed(role):
    raster,experiment,manual,over=ROLES[role]
    return {'event':'renderPipelineSelected','role':role,'explicitExperiment':experiment,'rasterDiagnostic':raster,
        'manualSampling':manual,'quantizedOver':over,'nativeAuthority':False,'pixelProof':False}


class ProductionPipelineTests(unittest.TestCase):
    def test_exact_production_mode_remains_configuration_only(self):
        result=verify_selection([observed('production-default')],'production-default')
        self.assertTrue(result['repairedDefault']);self.assertFalse(result['pixelProof'] or result['nativeAuthority'])
    def test_default_diagnostic_selects_same_pipeline_without_experiment(self):
        event=observed('diagnostic-default');self.assertTrue(event['manualSampling'] and event['quantizedOver']);self.assertFalse(event['explicitExperiment'])
        self.assertTrue(verify_selection([event],'diagnostic-default')['repairedDefault'])
    def test_production_cannot_masquerade_as_raster_scope(self):
        event=observed('production-default');event['rasterDiagnostic']=True
        with self.assertRaises(ValueError):verify_selection([event],'production-default')
    def test_experiment_cannot_masquerade_as_default(self):
        with self.assertRaises(ValueError):verify_selection([observed('diagnostic-over-experiment')],'diagnostic-default')
    def test_diagnostic_default_cannot_claim_production(self):
        with self.assertRaises(ValueError):verify_selection([observed('diagnostic-default')],'production-default')
    def test_every_mode_getter_typed_and_exact(self):
        for key in observed('production-default'):
            if key in ('event','role'):continue
            event=observed('production-default');event[key]=int(event[key])
            with self.subTest(key=key),self.assertRaises(ValueError):verify_selection([event],'production-default')
    def test_missing_duplicate_and_unknown_role_reject(self):
        for events,role in (([],'production-default'),([observed('production-default')]*2,'production-default'),([observed('production-default')],'unknown')):
            with self.subTest(events=events,role=role),self.assertRaises(ValueError):verify_selection(events,role)
    def test_extra_mode_authority_cannot_be_inferred(self):
        event=observed('production-default');event['validated']=True
        with self.assertRaises(ValueError):verify_selection([event],'production-default')
    def test_all_preexisting_pixel_shader_coverage_readback_ledger_bytes_preserved(self):
        for name in ('QuantizedOver.hpp','PixelCoverage.hpp','SamplingExperiment.hpp','CommitLedger.hpp','CausalImage.hpp','ReadbackImage.hpp','verify_quantized_over.py','verify_causal.py','verify_sampling.py'):
            with self.subTest(name=name):self.assertEqual((HERE/name).read_bytes(),(OLD/name).read_bytes())
    def test_accepted_actual_drawing_and_resource_methods_unchanged(self):
        new=(HERE/'Renderer.cpp').read_text();old=(OLD/'Renderer.cpp').read_text()
        for start,end in (('    void releasePrefix','    void cancel'),('    void upload','    void notifyAuthority'),('    void drawQuad','    void beginPrefix'),('    void beginPrefix','    void diagnosticReadback'),('    void diagnosticReadback','    void applyRetarget'),('    void command','    void publishOutputs')):
            if start=='    void upload':start='    GLuint upload'
            with self.subTest(start=start):
                a=new[new.index(start):new.index(end)];b=old[old.index(start):old.index(end)]
                self.assertTrue(a);self.assertEqual(a,b)
    def test_raster_mode_is_const_and_has_no_postconstruction_assignment(self):
        text=(HERE/'Renderer.cpp').read_text()
        self.assertIn('const bool rasterFixture;',text);self.assertNotIn('rasterFixture=',text)


if __name__=='__main__':unittest.main()
