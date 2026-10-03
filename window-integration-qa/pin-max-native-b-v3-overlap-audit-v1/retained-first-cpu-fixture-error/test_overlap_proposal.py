"""Actual whole controller-body CPU adapter; no native query/action is executed."""
from pathlib import Path
import importlib.util,json,sys,ast,copy,unittest
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent
P=B.parent/'pin-max-native-campaign-b-v3'
A=B.parent/'pin-maximized-native-v2'
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
old=load('_actual_failed_b_controller',P/'controller/minimal_controller.py')
namespace=dict(__file__=str(P/'controller/minimal_controller.py'))
exec(compile((B/'minimal_controller.py.proposed').read_bytes(),str(B/'minimal_controller.py.proposed'),'exec'),namespace)
new=namespace['MinimalController']
D=load('_exact_current_geometry_decoder',P/'observer/decode_observation.py')
T=load('_exact_native_point_authority',A/'case_authority.py')
raw=json.loads((B/'raw-selected-overlap-observations.json').read_bytes())
probe=raw['708']['value'];qt=raw['707']['value'];max_snapshot=json.loads(raw['703']['value'])
class NextWitnessRequired(Exception):pass
class Tests(unittest.TestCase):
 def adapter(self,cls,change=None):
  c=cls.__new__(cls);c.decoder=D;c.authority=T
  state=copy.deepcopy(probe);fixture=copy.deepcopy(qt)
  if change:change(state,fixture)
  owner=probe['windows'][1];peer=probe['windows'][0];tokens={name:{k:r[k]for k in ['address','stableId','pid']}for name,r in [('owner',owner),('peer',peer)]}
  c.retained_tiled=lambda *a:{};c.native_mode=lambda *a:copy.deepcopy(max_snapshot)
  c.capture=lambda actor,title='owner':tokens[title];c.public=lambda *a:{'pinned':False}
  c.fixture_state=lambda actor:fixture;c.old_probe=lambda name:state
  c.query=lambda name:(_ for _ in ()).throw(NextWitnessRequired('actual native protected-band witness not substituted by CPU'))
  return c
 def test_original_whole_body_refuses_raw_empty_override(self):
  c=self.adapter(old.MinimalController)
  with self.assertRaisesRegex(ValueError,'actual current overlapping owner/peer point'):c.coexistence_case('B07',{})
 def test_proposed_whole_body_requires_next_actual_witness(self):
  for case in ['B07']:
   c=self.adapter(new)
   with self.assertRaises(NextWitnessRequired):c.coexistence_case(case,{})
 def test_absent_wrong_typed_or_unreachable_peer_surface_refuses(self):
  def missing(s,q):s['windows']=s['windows'][1:]
  def replaced(s,q):s['windows'][0]['stableId']='replacement'
  def malformed(s,q):s['windows'][0]['surfaceBox']=[True,45,1558,934]
  def outside(s,q):s['windows'][0]['surfaceBox']=[21,45,100,934];q['windows']['peer']['buttonClient']=[11,456,78,22]
  def nonfinite(s,q):s['windows'][0]['surfaceBox']=[float('nan'),45,1558,934]
  for change in [missing,replaced,malformed,outside,nonfinite]:
   with self.subTest(change=change.__name__):
    c=self.adapter(new,change)
    with self.assertRaises(ValueError):c.coexistence_case('B07',{})
 def test_complete_AST_inverse_only_changes_overlap_operand(self):
  before=ast.parse((P/'controller/minimal_controller.py').read_bytes());after=ast.parse((B/'minimal_controller.py.proposed').read_bytes())
  assignments=[n for n in ast.walk(after)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='peer_box'for t in n.targets)]
  self.assertEqual(len(assignments),1);n=assignments[0]
  self.assertEqual(ast.dump(n.value,include_attributes=False),ast.dump(ast.parse("self.qt_box(actor,'peer',peer)",mode='eval').body,include_attributes=False))
  n.value=ast.parse("peer_max['body']['visualBox']",mode='eval').body
  self.assertEqual(ast.dump(before,include_attributes=False),ast.dump(after,include_attributes=False))
if __name__=='__main__':unittest.main(verbosity=2)
