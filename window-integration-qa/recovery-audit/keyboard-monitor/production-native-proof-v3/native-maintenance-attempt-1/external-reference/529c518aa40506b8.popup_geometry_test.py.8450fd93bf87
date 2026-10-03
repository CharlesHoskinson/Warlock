import sys,unittest,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'native-fixture'))
from popup_geometry import *
class GeometryTests(unittest.TestCase):
 def row(self):return dict(nativeMapped=True,position=[75,-42],surfaceTransform=[0,0],button=dict(x=12,y=11,width=186,height=34),popoverAllocation=[210,68],buttonAllocation=[186,34],centerPickedButton='Actual popup target A')
 def test_actual_retained_target(self):self.assertEqual(popup_target(dict(at=[96,120]),self.row()),(276,106))
 def test_zero_allocated_before_layout_refused(self):
  row=self.row();row['button']['width']=0;self.assertFalse(ready_popup(row))
 def test_native_unmapped_refused(self):
  row=self.row();row['nativeMapped']=False;self.assertFalse(ready_popup(row))
 def test_independent_pick_wrong_child_refused(self):
  row=self.row();row['centerPickedButton']='Pointer target A';self.assertFalse(ready_popup(row))
 def test_bad_transform_refused(self):
  row=self.row();row['surfaceTransform']=[float('nan'),0];self.assertFalse(ready_popup(row))
 def test_surface_to_widget_transform_direction(self):
  row=self.row();row['surfaceTransform']=[5,7];self.assertEqual(popup_target(dict(at=[96,120]),row),(271,99))
if __name__=='__main__':unittest.main()
