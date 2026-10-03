import unittest
from styled_button_pixels_v2 import classify

class GlyphOracle(unittest.TestCase):
 def raster(self,color):return bytearray(bytes((*color,255))*196)
 def mark(self,raster,color,points=((5,5),(6,5),(7,5),(8,5))):
  for x,y in points:raster[(y*14+x)*4:(y*14+x)*4+4]=bytes((*color,255))
 def test_blank_native_background_has_no_glyph(self):
  for index,color in ((1,(166,227,161)),(3,(137,180,250))):self.assertFalse(classify(self.raster(color),index)['passed'])
 def test_antialiased_dark_foreground_on_green_is_a_glyph(self):
  pixels=self.raster((166,227,161));self.mark(pixels,(121,162,123));self.assertTrue(classify(pixels,1)['passed'])
 def test_color_emoji_mark_on_blue_is_a_glyph(self):
  pixels=self.raster((137,180,250));self.mark(pixels,(244,67,54));self.assertTrue(classify(pixels,3)['passed'])
 def test_circular_boundary_cannot_substitute_for_icon(self):
  pixels=self.raster((166,227,161));self.mark(pixels,(107,142,112),((0,0),(1,1),(2,2),(12,12)));self.assertFalse(classify(pixels,1)['passed'])
 def test_gold_backdrop_cannot_substitute_for_pin_mark(self):
  pixels=self.raster((137,180,250));self.mark(pixels,(255,204,51));self.assertFalse(classify(pixels,3)['passed'])

if __name__=='__main__':unittest.main()
