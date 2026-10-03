from pathlib import Path
import importlib.util,json,tempfile,unittest
spec=importlib.util.spec_from_file_location('retirement_auditor',Path(__file__).with_name('audit.py'));a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
P=dict(address='0xa',stableId='1',pid=123);T=dict(address='0xb',stableId='2',pid=123)
class Replay(unittest.TestCase):
 def data(self,folder,theft=False):
  before=dict(coreDragTarget=T,nativeFocus=P,signalDownButtonIds=[272],groups=[]);after=dict(before,coreDragTarget=None,nativeFocus=T if theft else P);public=dict(activeWindow='peer');path=Path(folder)/'retirement-observation.json';row=dict(before=before,after=after,publicBefore=public,publicAfter=public,nativeClientsAfter=[T,P],target=T,peer=P,interruptionACK=dict(actualNativeEscape=True),timeNs=20,pointerKnownDown=[272],keyboardKnownDown=[],errors=[])
  path.write_text(json.dumps(row));path.chmod(0o600)
  case=dict(result='fail' if theft else 'pass',trace=[dict(label='actual press',target=T),dict(label='separate WM focus intervention',native=dict(nativeFocus=P)),dict(label='before actual nonrelease interruption',native=before,public=public,timeNs=10),dict(label='after actual nonrelease interruption',native=after,public=public,nativeClients=[T,P],interruptionACK=row['interruptionACK'],timeNs=20,observationErrors=[],observationPath=str(path))]);return case,path
 def test_strict_focus_failure_preserves_evidence_integrity_and_attribution(self):
  with tempfile.TemporaryDirectory() as folder:
   case,path=self.data(folder,True);r=a.replay(Path(folder),case,dict(button=272,end='escape'));self.assertTrue(r['evidenceIntegrity']);self.assertTrue(r['independentFocusBefore']);self.assertFalse(r['independentFocusAfter']);self.assertTrue(r['escapeSpecificTheftObserved']);self.assertEqual(r['producerCaseResult'],'fail')
 def test_missing_or_mutated_after_cannot_pass(self):
  with tempfile.TemporaryDirectory() as folder:
   case,path=self.data(folder);case['trace'][-1]['native']=dict(case['trace'][-1]['native'],nativeFocus=T);self.assertFalse(a.replay(Path(folder),case,dict(button=272,end='escape'))['evidenceIntegrity'])
if __name__=='__main__':unittest.main()
