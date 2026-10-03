"""Actual extracted callback source tests; no native/synthetic reader events."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
SOURCE=Path(__file__).parent/'orca-compat/orca/mouse_review.py'
OLD=Path('/home/hoskinson/window-integration-qa/recovery-audit/keyboard-monitor/pointer-private-host-v3/mouse-review-v2/orca-compat/orca/mouse_review.py')
def actual(source=SOURCE):
    cls=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.ClassDef) and n.name=='MouseReviewer')
    cls.decorator_list=[];cls.bases=[];cls.keywords=[]
    cls.body=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in {'_decode_pointer_coordinate','_on_mouse_moved'}]
    ns={'Atspi':NS(Role=NS(APPLICATION='app')),'AXObject':NS(get_role=lambda obj:obj)}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[cls],type_ignores=[])),str(source),'exec'),ns)
    obj=ns['MouseReviewer']();obj.calls=[]
    def query(window,x,y):
        if not (-2147483648<=x<=2147483647 and -2147483648<=y<=2147483647):raise OverflowError('signed gint AX boundary')
        obj.calls.append((window,x,y))
    obj._mouse_moved_common=query
    obj._accessible_window_at_point=lambda app,x,y:('app-window',x,y)
    return obj
class SignedSource(unittest.TestCase):
    def test_old_actual_callback_counterexample(self):
        obj=actual(OLD)
        with self.assertRaises(OverflowError):obj._on_mouse_moved('frame',180,4294967282)
        self.assertEqual(obj.calls,[])
    def test_actual_popup_trace(self):
        obj=actual();obj._on_mouse_moved('frame',180,4294967282);self.assertEqual(obj.calls,[('frame',180,-14)])
    def test_signed_negative_preserved(self):
        obj=actual();obj._on_mouse_moved('frame',-14,-1);self.assertEqual(obj.calls,[('frame',-14,-1)])
    def test_positive_preserved(self):
        obj=actual();obj._on_mouse_moved('frame',180,81);self.assertEqual(obj.calls,[('frame',180,81)])
    def test_application_path_uses_signed_values(self):
        obj=actual();obj._on_mouse_moved('app',4294967295,4294967282);self.assertEqual(obj.calls,[('app-window',-1,-14)])
    def test_minimum_boundaries(self):
        obj=actual();obj._on_mouse_moved('frame',2147483648,-2147483648);self.assertEqual(obj.calls,[('frame',-2147483648,-2147483648)])
    def test_maximum_boundaries(self):
        obj=actual();obj._on_mouse_moved('frame',2147483647,4294967295);self.assertEqual(obj.calls,[('frame',2147483647,-1)])
    def test_invalid_never_queries(self):
        for value in [True,False,1.0,-14.0,'4294967282',None,-2147483649,4294967296]:
            for coords in [(value,0),(0,value)]:
                with self.subTest(coords=coords):
                    obj=actual();obj._on_mouse_moved('frame',*coords);self.assertEqual(obj.calls,[])
if __name__=='__main__':unittest.main()
