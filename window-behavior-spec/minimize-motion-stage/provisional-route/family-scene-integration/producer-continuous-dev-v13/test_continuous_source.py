from pathlib import Path
import hashlib,json,unittest
B=Path(__file__).resolve().parent
OLD=B.parent/'producer-production-default-v10'
V12=B.parent/'producer-trajectory-dev-v12'

def block(text,start,end):return text[text.index(start):text.index(end,text.index(start))]
class ContinuousSourceTests(unittest.TestCase):
 def test_predecessors_exact(self):
  x=json.loads((B/'predecessor-inputs.json').read_text())
  for name,digest in x['v10Inputs'].items():self.assertEqual(hashlib.sha256((OLD/name).read_bytes()).hexdigest(),digest)
  for name,digest in x['v12Inputs'].items():self.assertEqual(hashlib.sha256((V12/name).read_bytes()).hexdigest(),digest)
 def test_accepted_primitive_exact(self):self.assertEqual((B/'ContinuousTrajectory.hpp').read_bytes(),(V12/'ContinuousTrajectory.hpp').read_bytes())
 def test_shaders_pixels_resource_policy_exact(self):
  for n in ['QuantizedOver.hpp','PixelCoverage.hpp','SamplingExperiment.hpp','CausalImage.hpp','ReadbackImage.hpp','BackendPolicy.hpp','LibraryMaterial.hpp','ProductionPipeline.hpp','verify_quantized_over.py','verify_causal.py','verify_sampling.py']:
   self.assertEqual((B/n).read_bytes(),(OLD/n).read_bytes(),n)
 def test_original_member_json_exact(self):
  self.assertEqual(block((B/'Renderer.cpp').read_text(),'static QJsonArray membersJson','class Renderer'),block((OLD/'Renderer.cpp').read_text(),'static QJsonArray membersJson','class Renderer'))
 def test_diagnostic_mix_and_geometry_exact(self):
  a=(B/'CommitLedger.hpp').read_text();b=(OLD/'CommitLedger.hpp').read_text()
  for start,end in [('inline Rect mix','inline Rect bounds'),('    std::vector<MemberFrame> sceneRectangles','    std::optional<Frame> prepareFamily')]:self.assertEqual(block(a,start,end),block(b,start,end))
  self.assertEqual(block(a,'    std::optional<Frame> prepareFamily','    const auto& familySources').replace('        if(motionPlan)return {};\n',''),block(b,'    std::optional<Frame> prepareFamily','    const auto& familySources'))
 def test_diagnostic_sample_and_validate_exact(self):
  a=(B/'Renderer.cpp').read_text();b=(OLD/'Renderer.cpp').read_text();self.assertEqual(block(a,'        if(kind=="sample")','        if(kind=="start")'),block(b,'        if(kind=="sample")','        if(kind=="start")'))
 def test_original_drawing_upload_and_retirement_exact(self):
  a=(B/'Renderer.cpp').read_text();b=(OLD/'Renderer.cpp').read_text()
  for start,end in [('    void releasePrefix','    void cancel'),('    void cancel','    void changed'),('    GLuint upload','    void notifyAuthority'),('    void drawQuad','    void beginPrefix'),('    void beginPrefix','    void diagnosticReadback'),('    void diagnosticReadback','    void draw')]:self.assertEqual(block(a,start,end),block(b,start,end))
 def test_only_one_ordinary_sample_reused_in_draw_and_submission(self):
  a=block((B/'Renderer.cpp').read_text(),'    void draw(','    void applyRetarget(')
  self.assertEqual(a.count('ledger.continuousSample('),1);self.assertIn('sceneSample->members',a);self.assertIn('ledger.prepareContinuousFamily(*sceneSample,',a);self.assertIn('frame->members!=members',a);self.assertIn('frame->kinematics!=std::optional<Kinematics>(sceneSample->timing)',a)
  p=block((B/'CommitLedger.hpp').read_text(),'    std::optional<Frame> prepareContinuousFamily','    bool continuous()');self.assertNotIn('.sample(',p);self.assertIn('issuedSamples.at(sample.output)!=sample',p);self.assertIn('frame->members=sample.members;frame->kinematics=sample.timing;',p)
 def test_complete_planning_precedes_token_mutation(self):
  a=block((B/'CommitLedger.hpp').read_text(),'    bool retargetContinuousFamily','    bool startContinuousFamily')
  self.assertLess(a.index('CommonTrajectoryPlan plan'),a.index('advanceToken('));self.assertLess(a.index('nextFrom[name].push_back'),a.index('advanceToken('));self.assertLess(a.index('nextOperation=operation'),a.index('advanceToken('));self.assertLess(a.index('advanceToken('),a.index('installMotion('))
 def test_ordinary_duplicate_start_uses_idempotent_ledger(self):
  a=block((B/'Renderer.cpp').read_text(),'        if(kind=="start")','    void publishOutputs');self.assertIn('ledger.startContinuousFamily(',a);self.assertIn('startedNs=ledger.continuousStartNs()',a);self.assertNotIn('startedNs=monotonicNs()',a)
  a=block((B/'CommitLedger.hpp').read_text(),'    bool startContinuousFamily','    std::optional<SceneSample> continuousSample');self.assertLess(a.index('if(motionRunning)return'),a.index('motionStartNs=now'))
 def test_formal_contract_first(self):
  a=json.loads((B/'continuous-formal-before-implementation.json').read_text());self.assertTrue(a['beforeRuntimeImplementation']);self.assertEqual(a['result'],'pass');self.assertTrue(all(c['returncode']==0 for c in a['commands']))
 def test_no_duration_nanosecond_truncation(self):
  a=(B/'CommonTrajectoryPlan.hpp').read_text();self.assertIn('upper*1e9<1',a);self.assertIn('double(now-start)/1e9',a);self.assertNotIn('uint64_t(duration',a)
if __name__=='__main__':unittest.main()
