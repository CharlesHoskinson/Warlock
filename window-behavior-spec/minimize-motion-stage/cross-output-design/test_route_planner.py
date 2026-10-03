#!/usr/bin/env python3
import random,unittest
from route_planner import Output,Rect,fragments,required_outputs
class Planner(unittest.TestCase):
 def setUp(self):self.outputs=[Output('left',0,0,100,100),Output('right',100,0,100,100)]
 def test_cross_output_icon_route_uses_both_participants(self):
  a=Rect(10,20,70,60);b=Rect(170,10,19,19)
  self.assertEqual(required_outputs(a,b,self.outputs),['left','right'])
  middle=fragments(a.lerp(b,.5),self.outputs);self.assertEqual(len(middle),2)
  self.assertAlmostEqual(sum(f.global_clip.width for f in middle),44.5)
 def test_spanning_native_rect_all_pixels_have_one_owner(self):
  a=Rect(80,20,80,60)
  parts=fragments(a,self.outputs);self.assertEqual([p.global_clip.width for p in parts],[20,60]);self.assertEqual(parts[0].uv.right,parts[1].uv.x)
 def test_global_coordinates_support_negative_origin(self):
  out=Output('left',-1920,-100,1920,1080);part=fragments(Rect(-50,0,100,20),[out])[0]
  self.assertEqual(part.local_clip.x,1870);self.assertEqual(part.global_clip.x,-50);self.assertEqual(part.uv.width,.5)
 def test_rotated_and_flipped_outputs_have_correct_logical_extents(self):
  for t in range(8):
   with self.subTest(transform=t):
    b=Output('rot',200,-20,1920,1080,1.5,t).bounds
    self.assertEqual((b.width,b.height),(720,1280) if t%2 else (1280,720))
 def test_mixed_scale_fragment_uv_is_scale_independent(self):
  outputs=[Output('a',0,0,200,200,2),Output('b',100,0,150,150,1.5)]
  parts=fragments(Rect(80,10,40,20),outputs)
  self.assertEqual([p.uv.width for p in parts],[.5,.5]);self.assertEqual([p.local_clip.x for p in parts],[80,0])
 def test_fullscreen_source_covers_exact_output_before_shrink(self):
  out=Output('rot',0,0,1080,1920,1.5,1);src=out.bounds;dst=Rect(20,src.bottom-19,19,19)
  self.assertEqual(fragments(src,[out])[0].uv,Rect(0,0,1,1));self.assertEqual(required_outputs(src,dst,[out]),['rot'])
 def test_disconnected_outputs_do_not_fake_capture_in_gaps(self):
  outputs=[Output('a',0,0,100,100),Output('b',150,0,100,100)]
  source=Rect(80,10,90,20);parts=fragments(source,outputs)
  self.assertEqual(sum(p.global_clip.width for p in parts),40)
  self.assertLess(sum(p.uv.width for p in parts),1) # monitor crops cannot be a full canonical atlas
 def test_reversal_starts_at_exact_global_rect(self):
  a=Rect(5,10,70,60);b=Rect(170,10,19,19);frozen=a.lerp(b,.37)
  self.assertEqual(frozen.lerp(a,0),frozen);self.assertEqual(frozen.lerp(a,1),a)
 def test_invalid_geometry_scale_transform_are_rejected(self):
  for out in [Output('bad',0,0,100,100,0),Output('bad',0,0,100,100,1,8)]:
   with self.assertRaises(ValueError):fragments(Rect(0,0,10,10),[out])
  with self.assertRaises(ValueError):Rect(float('nan'),0,10,10)
 def test_duplicate_output_names_are_rejected_before_planning(self):
  outputs=[Output('same',0,0,100,100),Output('same',100,0,100,100)]
  for fn in (lambda:fragments(Rect(0,0,10,10),outputs),lambda:required_outputs(Rect(0,0,10,10),Rect(10,0,10,10),outputs)):
   with self.assertRaisesRegex(ValueError,'duplicate'):fn()
 def test_nonfinite_and_nonpositive_output_geometry_is_rejected(self):
  for field in ('x','y','width','height','scale'):
   for value in (float('nan'),float('inf'),-float('inf')):
    args=dict(name='bad',x=1000,y=0,width=100,height=100,scale=1)
    args[field]=value
    with self.subTest(field=field,value=value),self.assertRaises(ValueError):fragments(Rect(0,0,10,10),[Output(**args)])
  for field in ('width','height'):
   args=dict(name='bad',x=1000,y=0,width=100,height=100)
   args[field]=0
   with self.subTest(field=field),self.assertRaises(ValueError):required_outputs(Rect(0,0,10,10),Rect(10,0,10,10),[Output(**args)])
 def test_invalid_names_and_fractional_transform_are_rejected(self):
  for out in [Output('',0,0,100,100),Output('bad',0,0,100,100,1,1.5),Output('bad',0,0,100,100,1,True)]:
   with self.assertRaises(ValueError):fragments(Rect(0,0,10,10),[out])
 def test_2000_sampled_routes_preserve_clip_uv_and_coverage(self):
  rng=random.Random(3435019)
  for _ in range(2000):
   x=rng.uniform(0,150);w=rng.uniform(1,200-x);r=Rect(x,rng.uniform(0,50),w,rng.uniform(1,50));parts=fragments(r,self.outputs)
   self.assertAlmostEqual(sum(p.global_clip.width for p in parts),r.width)
   self.assertAlmostEqual(sum(p.uv.width for p in parts),1)
   for p in parts:
    self.assertGreaterEqual(p.local_clip.x,0);self.assertLessEqual(p.local_clip.right,100+1e-9)
if __name__=='__main__':unittest.main()
