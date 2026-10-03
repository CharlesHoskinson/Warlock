from fractions import Fraction as F
import unittest
from audit_pixels import exact_pixel,nearest,vertex_quantized_members

class PixelArithmeticTests(unittest.TestCase):
    def member(self,pixels,extent=(1,1),rect=None):
        return dict(stableId='abc',pid=1,pixels=list(extent),premultiplied=bytes(pixels),rectangle=rect or dict(x=0,y=0,width=1,height=1))
    def output(self,width=1,height=1,bw=1,bh=1):return dict(x=0,y=0,width=width,height=height,bufferWidth=bw,bufferHeight=bh)
    def test_exact_texel_center_identity(self):
        m=self.member([100,50,25,255]);p,_=exact_pixel(self.output(),[m],0,0);self.assertEqual(p,[100,50,25,255])
    def test_equal_bilinear_corner_weights(self):
        m=self.member([0,0,0,0,255,0,0,255,0,0,0,0,255,0,0,255],(2,2));p,steps=exact_pixel(self.output(),[m],0,0)
        self.assertEqual(p,[128,0,0,128]);self.assertEqual([t['weight'] for t in steps[0]['taps']],['1/4']*4)
    def test_clamped_corner_preserves_alpha_and_rgb(self):
        m=self.member([24,12,6,32,255,255,255,255,100,100,100,128,0,0,0,0],(2,2),dict(x=0,y=0,width=2,height=2))
        p,steps=exact_pixel(self.output(2,2,4,4),[m],0,0);self.assertEqual(p,[24,12,6,32]);self.assertEqual(steps[0]['sampleCoordinates'],['-1/4','-1/4'])
    def test_premultiplied_source_over_ordered_quantization(self):
        a=self.member([100,50,25,255]);b=self.member([10,0,0,128]);p,steps=exact_pixel(self.output(),[a,b],0,0)
        self.assertEqual(p,[60,25,12,255]);self.assertEqual(steps[1]['previousRGBA'],[100,50,25,255])
    def test_transparent_source_preserves_destination(self):
        p,_=exact_pixel(self.output(),[self.member([100,50,25,255]),self.member([0,0,0,0])],0,0);self.assertEqual(p,[100,50,25,255])
    def test_normative_half_quantization_not_fitted_to_gpu(self):
        self.assertEqual(nearest(F(1,2)),1);self.assertEqual(nearest(F(1,2)-F(1,1000000)),0);self.assertEqual(nearest(F(255)),255)
    def test_float32_cpu_vertices_preserve_exact_aligned_edges(self):
        m=self.member([100,50,25,255],rect=dict(x=25,y=50,width=50,height=25))
        transformed=vertex_quantized_members(self.output(100,100,150,150),[m])[0]
        self.assertEqual(transformed['rectangle'],m['rectangle'])
    def test_float32_cpu_vertices_are_explicit_not_gpu_precision_assumption(self):
        m=self.member([100,50,25,255],rect=dict(x=.1,y=.3,width=.2,height=.4))
        transformed=vertex_quantized_members(self.output(),[m])[0]
        self.assertNotEqual(transformed['rectangle']['x'],F('0.1'))
        self.assertLess(abs(transformed['rectangle']['x']-F('0.1')),F(1,10000000))

if __name__=='__main__':unittest.main()
