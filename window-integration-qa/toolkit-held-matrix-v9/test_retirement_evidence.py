"""Durable actual-state evidence survives the original focus-oracle failure."""
from pathlib import Path
from types import SimpleNamespace
import json,stat,tempfile,unittest
from held_controller import retain_retirement
from observations import retired

PEER=dict(address='0xab',stableId='1',pid=123)
SOURCE=dict(address='0xcd',stableId='2',pid=123)

class RetirementEvidence(unittest.TestCase):
    def route(self,folder):
        records=[]
        return SimpleNamespace(folder=Path(folder),guard=lambda:None,fixture=SimpleNamespace(state=lambda:dict(pid=123,activeWindow='peer',windows={})),session=SimpleNamespace(data=lambda *args:[dict(SOURCE)]),pointer=SimpleNamespace(down={272}),keyboard=SimpleNamespace(down=set()),record=lambda label,row:records.append(dict(label=label,**row))),records
    def test_original_focus_refusal_retains_actual_before_after_and_raw_hold(self):
        with tempfile.TemporaryDirectory() as folder:
            route,records=self.route(folder);before=dict(coreDragTarget=SOURCE,nativeFocus=PEER,signalDownButtonIds=[272],groups=[]);after=dict(coreDragTarget=None,nativeFocus=SOURCE,signalDownButtonIds=[272],groups=[])
            result=retain_retirement(route,before,dict(activeWindow='peer'),after,PEER,SOURCE,dict(actualNativeEscape=True))
            with self.assertRaisesRegex(ValueError,'stole independent'):retired(before,after,PEER)
            path=Path(folder)/'retirement-observation.json';self.assertEqual(json.loads(path.read_bytes()),result);self.assertEqual(stat.S_IMODE(path.stat().st_mode),0o600)
            self.assertEqual(result['pointerKnownDown'],[272]);self.assertEqual(result['publicBefore']['activeWindow'],'peer');self.assertEqual(result['after'],after);self.assertEqual(records[0]['native'],after)
            with self.assertRaises(FileExistsError):retain_retirement(route,before,{},after,PEER,SOURCE,{})

    def test_guard_fault_retains_known_native_after_without_accepting_missing_data(self):
        with tempfile.TemporaryDirectory() as folder:
            route,records=self.route(folder);route.guard=lambda:(_ for _ in ()).throw(RuntimeError('Exact PID/start source changed'))
            after=dict(coreDragTarget=None,nativeFocus=SOURCE,signalDownButtonIds=[272],groups=[])
            with self.assertRaisesRegex(RuntimeError,'incomplete'):retain_retirement(route,{}, {},after,PEER,SOURCE,{})
            result=json.loads((Path(folder)/'retirement-observation.json').read_text());self.assertEqual(result['after'],after);self.assertTrue(result['errors']);self.assertNotIn('publicAfter',result);self.assertTrue(records[0]['observationErrors'])

if __name__=='__main__':unittest.main(verbosity=2)
