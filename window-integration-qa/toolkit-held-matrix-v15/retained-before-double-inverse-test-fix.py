"""Failure evidence and original motion/predicate conservation; no GUI/IPC."""
import copy
import ast
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
from frontend_route import FrontendLifecycle
from preview_evidence import PreviewEvidence

B=Path(__file__).resolve().parent;OLD=B.parent/'toolkit-held-matrix-v8'

class PreviewTests(unittest.TestCase):
    def route(self,folder):
        records=[];pointer=SimpleNamespace(identity=dict(pid=42,start='7'),down=set(),trace=[])
        return SimpleNamespace(folder=Path(folder),pointer=pointer,keyboard=SimpleNamespace(down=set()),extents=[1600,1000],record=lambda label,row:records.append(dict(label=label,**row))),records
    def test_owned_exclusive_journal_durably_records_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            route,records=self.route(folder)
            with self.assertRaisesRegex(TimeoutError,'exact preview'):
                with PreviewEvidence(route,dict(pid=99,start='8'),dict(address='0xaa')) as journal:
                    journal.emit('preview-proposed',dict(point=[170,637.5]));raise TimeoutError('exact preview')
            path=Path(folder)/'preview-motion-observation.jsonl';rows=[json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual([r['event'] for r in rows],['begin','preview-proposed','terminal']);self.assertEqual(rows[-1]['result'],'error');self.assertEqual(path.stat().st_mode&0o777,0o600)
            with self.assertRaises(FileExistsError):PreviewEvidence(route,{},{} )
    def test_nonfinite_or_partial_writes_never_authorize_a_decision(self):
        with tempfile.TemporaryDirectory() as folder:
            route,_=self.route(folder)
            with PreviewEvidence(route,{},{}) as journal:
                with self.assertRaises(ValueError):journal.emit('bad',dict(point=[float('nan'),1]))
                with patch('preview_evidence.os.write',return_value=0):
                    with self.assertRaises(OSError):journal.emit('bad',{})
            rows=[json.loads(line) for line in (Path(folder)/'preview-motion-observation.jsonl').read_text().splitlines()];self.assertEqual([r['event'] for r in rows],['begin','terminal'])
    def test_every_record_fsync_precedes_visible_record_and_decision(self):
        with tempfile.TemporaryDirectory() as folder:
            route,_=self.route(folder);order=[];route.record=lambda *args:order.append('record');original=os.fsync
            with patch('preview_evidence.os.fsync',side_effect=lambda fd:(original(fd),order.append('fsync'))):
                with PreviewEvidence(route,{},{}) as journal:journal.emit('sample',{})
            self.assertEqual(order,['fsync','record']*3)
    def test_private_parent_and_symlink_refuse(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'bad';path.mkdir(mode=0o755);route,_=self.route(path)
            with self.assertRaises(RuntimeError):PreviewEvidence(route,{},{})
            path.chmod(0o700);link=root/'link';link.symlink_to(path);route,_=self.route(link)
            with self.assertRaises(RuntimeError):PreviewEvidence(route,{},{})
    def test_diagnostic_copy_strips_to_exact_production_qml(self):
        f=B/'payload/home/.config/omarchy/plugins/hoskinson.windows/widget_v65'
        popup=(f/'TaskbarPopup.qml').read_text();start=popup.index('  // Read-only QA copy diagnostic.');end=popup.index('  function fittedContentWidth',start)
        self.assertEqual(popup[:start]+popup[end:],(OLD/'payload/home/.config/omarchy/plugins/hoskinson.windows/widget_v65/TaskbarPopup.qml').read_text())
        windows=__import__('terminal_qml').reconstruct((f/'Windows.qml').read_text()).replace('  property int diagnosticPopupEpoch: 0\n','').replace('  onPopupOpenChanged: { diagnosticPopupEpoch++; if (!popupOpen) popupAccessibilityReady = false }','  onPopupOpenChanged: if (!popupOpen) popupAccessibilityReady = false').replace('    diagnosticPopupEpoch++\n','').replace('diagnosticPopupEpoch:root.diagnosticPopupEpoch, popupKey:root.popupKey, ','').replace('address:w.address,stableId:w.stableId,pid:w.pid,','address:w.address,');start=windows.index('  function diagnosticPopupViewport()');end=windows.index('  function diagnosticState()',start)
        windows=(windows[:start]+windows[end:]).replace('popupGeometry:previewCard.diagnosticBounds(), popupViewportBounds:root.diagnosticPopupViewport(), ','')
        self.assertEqual(windows,(OLD/'payload/home/.config/omarchy/plugins/hoskinson.windows/widget_v65/Windows.qml').read_text())
        for token in ('card:rectangle(card)','content:rectangle(contentHolder)','item.mapToItem(null, 0, 0)','clip:popupFlickable.clip','popupFlickable.mapToItem(null,0,0)'):
            self.assertIn(token,popup+windows+(f/'Windows.qml').read_text())
    def test_all_original_native_ticket_controller_oracle_sources_exact(self):
        for name in ('helper_observer.py','helper_setup.py','evaluation_setup.py','held_route.py','run_native.py','held_controller.py','observations.py','input_control.py','evaluation_tickets.qnt'):
            current=__import__('source_conservation').reconstructed_v14(name).decode();previous=(OLD/name).read_text()
            if name in ('helper_observer.py','helper_setup.py'):current=__import__('source_conservation').reconstructed(name).decode()
            if name=='run_native.py':current=__import__('source_conservation').reconstructed_runner(current.encode()).decode().replace("B/'native-pointer-wheel/native-pointer'","PROOF/'native-pointer'")
            if name=='input_control.py':
                start=current.index('    def wheel(');end=current.index('    def close(',start);current=current[:start]+current[end:]
            self.assertEqual(current,previous,name)
        current=json.loads((B/'matrix.json').read_text().replace('private-weston-aq-bootstrap-host-v5','private-weston-aq-host-v4').replace('private-weston-x11-bootstrap-host-v3','private-weston-x11-host-v2'));old=json.loads((OLD/'matrix.json').read_text())
        self.assertEqual(current,old)
    def test_real_copied_payload_original_and_diagnostic_hashes_are_guarded(self):
        import private_shell
        descriptor=private_shell.verify_payload();self.assertTrue(descriptor['widgetModified']);self.assertFalse(descriptor['widgetDiagnosticsOnly']);self.assertTrue(descriptor['widgetTerminalQuiesceOnly']);self.assertEqual(len(descriptor['diagnosticCopies']),2)
        for relative,row in descriptor['diagnosticCopies'].items():self.assertEqual(hashlib.sha256((B/'payload'/relative).read_bytes()).hexdigest(),row['copySHA256'])
    def test_original_pointer_actions_strict_predicate_and_feature_gates_exact(self):
        def function(path,name):
            return next(node for node in ast.walk(ast.parse(path.read_text())) if isinstance(node,ast.FunctionDef) and node.name==name)
        old=function(OLD/'frontend_route.py','restore');new=function(B/'frontend_route.py','restore_observed')
        def calls(node,attribute):
            return [ast.dump(n,include_attributes=False) for n in ast.walk(node) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and ast.unparse(n.func).startswith(attribute)]
        self.assertEqual(calls(old,'route.pointer.'),calls(new,'route.pointer.'))
        self.assertEqual(calls(old,'route.gate'),calls(new,'route.gate'))
        old_arrived=next(n for n in ast.walk(old) if isinstance(n,ast.FunctionDef) and n.name=='arrived')
        new_arrived=next(n for n in ast.walk(new) if isinstance(n,ast.FunctionDef) and n.name=='arrived')
        def condition(node):return next(n for n in ast.walk(node) if isinstance(n,ast.IfExp)).test
        self.assertEqual(ast.dump(condition(old_arrived)),ast.dump(condition(new_arrived)))
    def test_original_preview_timeout_retains_proposal_and_every_failed_sample(self):
        with tempfile.TemporaryDirectory() as folder:
            route,records=self.route(folder);self.assertFalse(route.pointer.down)
            source=dict(address='0xaa',stableId='1',pid=5);shell=dict(pid=99,start='8');moves=[]
            def absolute(point,extents):
                self.assertTrue((Path(folder)/'preview-motion-observation.jsonl').exists())
                before=[json.loads(line) for line in (Path(folder)/'preview-motion-observation.jsonl').read_text().splitlines()]
                self.assertEqual(before[-1]['event'],'icon-proposed' if not moves else 'preview-proposed')
                moves.append(list(point));route.pointer.trace.extend([dict(command='absolute '+' '.join(format(v,'.12g') for v in [*point,*extents])),dict(command='sync')])
            route.pointer.absolute=absolute;route.pointer.button=lambda *args:self.fail('No click on wrong actual owner')
            bar=dict(pid=99,namespace='omarchy-bar',mapped=True,visible=True,box=[0,0,1600,26]);popup=dict(pid=99,namespace='hoskinson-taskbar-popup',mapped=True,visible=True,box=[0,0,1600,1000])
            n=[dict(cursor=[1230,264.5],pointerLayerOwner=None,layers=[bar]),dict(cursor=[53,13],pointerLayerOwner=bar,layers=[bar]),dict(cursor=[53,13],pointerLayerOwner=bar,layers=[bar,popup]),dict(cursor=[170,637.5],pointerLayerOwner=None,layers=[bar,popup])]
            route.native=lambda:copy.deepcopy(n.pop(0) if len(n)>1 else n[0])
            state=dict(taskbarItems=[dict(x=29,y=0,width=48,height=26,windows=['0xaa'])],popupOpen=True,menuMode=False,previewItems=[dict(address='0xaa',x=21,y=563,width=298,height=149)],popupGeometry=dict(card=dict(x=5,y=31,width=320,height=460),content=dict(x=21,y=47,width=288,height=428)),popupViewportBounds=dict(x=21,y=47,width=288,height=428,clip=True),popupViewportHeight=428,popupScrollY=0)
            lifecycle=FrontendLifecycle.__new__(FrontendLifecycle);lifecycle.shell=SimpleNamespace(pid=99);lifecycle.ipc=lambda *args:json.dumps(state)
            def wait(callback,label):
                for _ in range(2):
                    value=callback()
                    if value:return value
                raise TimeoutError(label)
            route.wait=wait
            with patch('frontend_route.helper_observer.process',return_value=shell),patch('frontend_route.scroll_route.reveal',return_value=((state,n[-1],popup,dict(item=state['previewItems'][0],wheelEvents=0)),{},0)),patch('frontend_route.scroll_route.validate_card',side_effect=lambda *args:(state,route.native(),popup,{})):
                with self.assertRaisesRegex(TimeoutError,'Actual pointer enters exact preview card layer'):lifecycle.restore(route,source,{})
            rows=[json.loads(line) for line in (Path(folder)/'preview-motion-observation.jsonl').read_text().splitlines()]
            self.assertEqual(moves,[[53,13],[170,637.5]])
            proposed=next(r for r in rows if r['event']=='preview-proposed');self.assertEqual(proposed['widgetState'],state)
            samples=[r for r in rows if r['event']=='arrival-sample' and r['namespace']=='hoskinson-taskbar-popup'];self.assertEqual(len(samples),2);self.assertTrue(all(not r['originalArrivalPredicate'] for r in samples));self.assertEqual(rows[-1]['result'],'error')

if __name__=='__main__':unittest.main(verbosity=2)
