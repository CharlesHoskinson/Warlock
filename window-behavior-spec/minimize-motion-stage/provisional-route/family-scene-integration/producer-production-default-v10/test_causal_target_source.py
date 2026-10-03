from pathlib import Path
import json,unittest
from verify_causal import bind
from verify_quantized_over import shader_digests

B=Path(__file__).resolve().parent
OLD=B.parent/'producer-quantized-over-v7'
FAIL=Path('/home/hoskinson/window-integration-qa/family-raster-quantized-v9/attempt-1')

class TargetSource(unittest.TestCase):
 def test_original_pair_guard_and_default_shader_bytes_unchanged(self):
  for name in ('verify_causal.py','CausalImage.hpp','ReadbackImage.hpp','SamplingExperiment.hpp','CommitLedger.hpp'):
   self.assertEqual((B/name).read_bytes(),(OLD/name).read_bytes())
  new,copy=shader_digests((B/'QuantizedOver.hpp').read_text());old,oldcopy=shader_digests((OLD/'QuantizedOver.hpp').read_text())
  self.assertNotEqual(new,old);self.assertEqual(copy,oldcopy)
  renderer=(B/'Renderer.cpp').read_text()
  self.assertIn('quantizedOver?OwnedOver::copyVertex:"precision highp float;attribute highp vec2 position;attribute highp vec2 uv;varying highp vec2 tex;void main(){tex=uv;gl_Position=vec4(position,0.,1.);}"',renderer)
  self.assertIn('quantizedOver?fullscreen:quad',renderer)
 def test_copy_default_before_native_query_and_both_reads(self):
  text=(B/'Renderer.cpp').read_text();body=text[text.index('    CausalObservation observeCausal'):text.index('    void initializeControls')]
  self.assertLess(body.index('copyPrefix(o,result.prefixTexture,0)'),body.index('GL_IMPLEMENTATION_COLOR_READ_FORMAT'))
  self.assertLess(body.index('result.readFramebuffer!=0'),body.index('GL_IMPLEMENTATION_COLOR_READ_FORMAT'))
  self.assertLess(body.index('GL_IMPLEMENTATION_COLOR_READ_FORMAT'),body.index('glReadPixels('))
  self.assertIn('read(GL_RGBA,GL_UNSIGNED_BYTE)',body);self.assertIn('read(format,type)',body)
 def test_causal_copy_has_no_swap_prefix_or_presentation_authority(self):
  text=(B/'Renderer.cpp').read_text();body=text[text.index('    CausalObservation observeCausal'):text.index('    void initializeControls')]
  for token in ('o.prefixRead=','o.prefixPassCount=','ledger.','eglSwapBuffers(','wp_presentation_feedback('):self.assertNotIn(token,body)
  self.assertIn('if(quantizedOver)',body)
 def test_retained_actual_native_mismatch_stays_rejected(self):
  events=[json.loads(line) for line in (FAIL/'producer-events.jsonl').read_text().splitlines()]
  full=json.loads((FAIL/'readback-0-WAYLAND-1.json').read_text())
  record=next(e for e in events if e.get('event')=='ownedCausalReadback' and e.get('sequence')==full['sequence'])
  swap=next(e for e in events if e.get('event')=='swap' and e.get('sequence')==full['sequence'])
  fixture=json.loads((FAIL/'fixture-0-WAYLAND-1.json').read_text());presented=json.loads((FAIL/'presented-0-WAYLAND-1.json').read_text())
  self.assertEqual(full['glBuffer']['framebuffer'],0);self.assertEqual(full['glBuffer']['readFormat'],32993);self.assertEqual(record['nativeFormat'],6408)
  with self.assertRaisesRegex(ValueError,'actual queried supported native pair differs'):bind(record,fixture,full,swap,presented)

if __name__=='__main__':unittest.main()
