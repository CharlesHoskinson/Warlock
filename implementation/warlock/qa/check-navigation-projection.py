"""Original bracketing and ordinary-workspace listing on real projection code."""
import copy,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'adapter'))
from taskbar_projection import coherent_scene

class NavigationProjection(unittest.TestCase):
 def setUp(self):
  self.row={'incarnation':'7','application':'Editor','label':'Editor','minimized':True}
  self.facts={'revision':'11','outputGeneration':'3','facts':{'focused':None,'windows':[
   {'incarnation':'7','application':'Editor','owner':None,'minimized':True,'workspace':'2','workspaceVisible':False,'hidden':False}]}}
 def project(self):return coherent_scene(self.facts,{'windows':[self.row]},copy.deepcopy(self.facts))
 def test_hidden_ordinary_workspace_can_be_listed_for_native_restore(self):
  self.assertTrue(self.project()['windows'][0]['available'])
 def test_special_missing_or_hidden_still_unavailable(self):
  for workspace,hidden in [('-99',False),('0',False),(None,False),('2',True)]:
   self.facts['facts']['windows'][0].update(workspace=workspace,hidden=hidden)
   self.assertFalse(self.project()['windows'][0]['available'])
 def test_changing_native_revision_or_output_withholds_projection(self):
  for name in ('revision','outputGeneration'):
   after=copy.deepcopy(self.facts);after[name]='12'
   self.assertIsNone(coherent_scene(self.facts,{'windows':[self.row]},after))
 def test_retired_or_state_mismatched_target_never_substitutes(self):
  for change in ({'incarnation':'8'},{'minimized':False},{'application':'Replacement'}):
   changed={**self.row,**change}
   self.assertIsNone(coherent_scene(self.facts,{'windows':[changed]},copy.deepcopy(self.facts)))

if __name__=='__main__':unittest.main()
