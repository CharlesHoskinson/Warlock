"""CPU scroll receipt and lifetime faults; all desktop observations are fixtures."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import scroll_route as scroll
from input_control import PinnedInput

B=Path(__file__).resolve().parent;V9=B.parent/'toolkit-held-matrix-v9'
TARGET=dict(address='0xaa',stableId='1',pid=123)
SHELL=dict(pid=99,start='7')

def material():
    widget=dict(popupOpen=True,menuMode=False,keyboardMode=False,diagnosticPopupEpoch=2,popupKey='exact',popupIndex=0,wheelEvents=0,popupScrollY=0,
        previewItems=[dict(TARGET,x=26,y=537,width=288,height=149)],
        popupGeometry=dict(coordinateSpace='layer-window',maskMode='card',open=True,visible=True,layer=dict(x=0,y=0,width=1600,height=1000),card=dict(x=10,y=36,width=320,height=460),content=dict(x=26,y=52,width=288,height=428)),
        popupViewportBounds=dict(coordinateSpace='layer-window',x=26,y=52,width=288,height=428,clip=True,contentY=0,contentHeight=634))
    layer=dict(address='0xbeef',pid=99,namespace='hoskinson-taskbar-popup',mapped=True,visible=True,box=[0,26,1600,1000])
    native=dict(cursor=[53,13],pointerLayerOwner=None,windows=[dict(TARGET,mapped=True)],coreDragTarget=None,heldButtons=False,signalDownButtonIds=[],sessionLocked=False,exclusiveLayers=0,constrained=False,seatGrab=False,captured=False,dnd=False,layers=[layer])
    return widget,native,layer

class ScrollTests(unittest.TestCase):
    def test_actual_retained_clip_numbers_need_scroll_not_layer_center(self):
        w,n,l=material();p=scroll.selection(w,l,TARGET)
        self.assertFalse(p['fullyVisible']);self.assertEqual(p['point'],[170,637.5]);self.assertEqual(p['viewportPoint'],[170,292]);self.assertEqual(p['direction'],1)
        w['popupViewportBounds']['contentY']=206;w['previewItems'][0]['y']-=206;p=scroll.selection(w,l,TARGET);self.assertTrue(p['fullyVisible']);self.assertEqual(p['point'],[170,431.5])
    def test_fractional_native_origin_kept_and_half_open_intersection(self):
        w,n,l=material();l['box'][0]=.125;l['box'][1]=26.375;p=scroll.selection(w,l,TARGET);self.assertEqual(p['viewportPoint'],[170.125,292.375])
        with self.assertRaises(ValueError):scroll.intersection([0,0,10,10],[10,0,10,10])
    def test_hidden_card_with_invalid_clip_space_or_size_refuses(self):
        for mutation in (lambda w:w['popupViewportBounds'].update(clip=False),lambda w:w['popupViewportBounds'].update(coordinateSpace='screen'),lambda w:w['previewItems'][0].update(width=float('nan')),lambda w:w['previewItems'][0].update(height=999),lambda w:w.update(menuMode=True),lambda w:w.update(wheelEvents=True)):
            w,n,l=material();mutation(w)
            with self.assertRaises(ValueError):scroll.selection(w,l,TARGET)
    def test_exact_source_identity_and_complete_native_members_required(self):
        with patch.object(scroll.helper_observer,'still_live',return_value=True):
            for field in ('address','stableId','pid'):
                w,n,l=material();w['previewItems'][0][field]='changed' if field!='pid' else 124
                with self.assertRaises(ValueError):scroll.binding(w,l,TARGET,SHELL,n)
            w,n,l=material();n['windows'][0]['mapped']=False
            with self.assertRaises(ValueError):scroll.binding(w,l,TARGET,SHELL,n)
            w,n,l=material();n['signalDownButtonIds']=[272]
            with self.assertRaises(ValueError):scroll.binding(w,l,TARGET,SHELL,n)
    def harness(self,mutation=None):
        w,n,l=material();events=[];moves=[];detents=[]
        evidence=SimpleNamespace(emit=lambda event,body:events.append(dict(event=event,**copy.deepcopy(body))))
        pointer=SimpleNamespace(down=set(),trace=[])
        def absolute(point,extents):
            moves.append(list(point));n['cursor']=list(point);n['pointerLayerOwner']=l;pointer.trace.extend([dict(command='absolute'),dict(command='sync')])
        def wheel(direction):
            detents.append(direction);before=w['popupViewportBounds']['contentY'];after=min(206,max(0,before+40*direction));w['wheelEvents']+=1;w['popupViewportBounds']['contentY']=after;w['popupScrollY']=after;w['previewItems'][0]['y']-=after-before
            if mutation:mutation(w,n,l)
            pointer.trace.extend([dict(command='wheel '+str(direction)),dict(command='sync')])
        pointer.absolute=absolute;pointer.wheel=wheel
        def wait(callback,label):
            for _ in range(3):
                value=callback()
                if value:return value
            raise TimeoutError(label)
        route=SimpleNamespace(pointer=pointer,keyboard=SimpleNamespace(down=set()),window=lambda name:copy.deepcopy(TARGET),native=lambda:copy.deepcopy(n),wait=wait,extents=[1600,1000])
        frontend=SimpleNamespace(shell=SimpleNamespace(pid=99),ipc=lambda *args:json.dumps(w))
        return frontend,route,evidence,w,n,l,events,moves,detents
    def test_six_real_command_receipts_reveal_same_source_without_assigning_state(self):
        f,r,e,w,n,l,events,moves,detents=self.harness()
        with patch.object(scroll.helper_observer,'still_live',return_value=True):value,binding,count=scroll.reveal(f,r,TARGET,SHELL,copy.deepcopy(w),copy.deepcopy(n),copy.deepcopy(l),e)
        self.assertEqual(count,6);self.assertEqual(detents,[1]*6);self.assertEqual(len(moves),6);self.assertEqual(value[3]['point'],[170,431.5]);self.assertTrue(value[3]['fullyVisible']);self.assertEqual(binding['identities'],[TARGET]);self.assertEqual(len([x for x in events if x['event']=='wheel-receipt']),6)
    def test_epoch_key_index_source_layer_close_or_counter_fault_never_returns_selection(self):
        mutations=[lambda w,n,l:w.update(diagnosticPopupEpoch=3),lambda w,n,l:w.update(popupKey='other'),lambda w,n,l:w.update(popupIndex=1),lambda w,n,l:w.update(popupOpen=False),lambda w,n,l:w['previewItems'][0].update(pid=124),lambda w,n,l:l.update(address='0xdead'),lambda w,n,l:w.update(wheelEvents=w['wheelEvents']+1),lambda w,n,l:w['popupViewportBounds'].update(contentY=0)]
        for change in mutations:
            f,r,e,w,n,l,events,moves,detents=self.harness(change)
            with patch.object(scroll.helper_observer,'still_live',return_value=True):
                with self.assertRaises((ValueError,RuntimeError,TimeoutError)):scroll.reveal(f,r,TARGET,SHELL,copy.deepcopy(w),copy.deepcopy(n),copy.deepcopy(l),e)
            self.assertEqual(detents,[1])
    def test_lost_native_owner_during_wheel_refuses(self):
        f,r,e,w,n,l,*rest=self.harness(lambda w,n,l:n.update(pointerLayerOwner=None))
        with patch.object(scroll.helper_observer,'still_live',return_value=True):
            with self.assertRaisesRegex(RuntimeError,'input owner changed'):scroll.reveal(f,r,TARGET,SHELL,copy.deepcopy(w),copy.deepcopy(n),copy.deepcopy(l),e)
    def test_missing_or_opposed_wheel_progress_cannot_authorize_selection(self):
        for change in (lambda w,n,l:(w.update(wheelEvents=0),w['popupViewportBounds'].update(contentY=0)),lambda w,n,l:w['popupViewportBounds'].update(contentY=0)):
            f,r,e,w,n,l,*rest=self.harness(change)
            with patch.object(scroll.helper_observer,'still_live',return_value=True):
                with self.assertRaises((RuntimeError,TimeoutError)):scroll.reveal(f,r,TARGET,SHELL,copy.deepcopy(w),copy.deepcopy(n),copy.deepcopy(l),e)
    def test_bound_refuses_further_wheel_without_visible_source(self):
        f,r,e,w,n,l,events,moves,detents=self.harness()
        with patch.object(scroll.helper_observer,'still_live',return_value=True),patch.object(scroll,'MAX_DETENTS',2):
            with self.assertRaisesRegex(RuntimeError,'Bounded genuine wheel'):scroll.reveal(f,r,TARGET,SHELL,copy.deepcopy(w),copy.deepcopy(n),copy.deepcopy(l),e)
        self.assertEqual(detents,[1,1]);self.assertEqual(len(moves),2)
    def test_extra_counter_or_allocation_change_refuses_before_card_press(self):
        for change in (lambda w:w.update(wheelEvents=w['wheelEvents']+1),lambda w:w['popupGeometry']['card'].update(height=459)):
            f,r,e,w,n,l,*rest=self.harness()
            with patch.object(scroll.helper_observer,'still_live',return_value=True):
                value,bound,count=scroll.reveal(f,r,TARGET,SHELL,copy.deepcopy(w),copy.deepcopy(n),copy.deepcopy(l),e)
                allocation=scroll.stable_key(value);point=value[3]['point'];change(w)
                with self.assertRaisesRegex(RuntimeError,'allocation/counter changed'):scroll.validate_card(f,r,TARGET,SHELL,bound,e,point,allocation)
    def test_typed_released_wheel_control_exact_command_and_sync(self):
        c=PinnedInput.__new__(PinnedInput);c.kind='pointer';c.down=set();events=[];c.send=lambda command:events.append(command);c.sync=lambda:events.append('sync')
        c.wheel(1);c.wheel(-1);self.assertEqual(events,['wheel 1','sync','wheel -1','sync'])
        for value in (True,1.0,0,2,-2):
            with self.assertRaises(ValueError):c.wheel(value)
        c.down={272}
        with self.assertRaises(ValueError):c.wheel(1)
    def test_original_native_producer_source_reconstructed_exactly(self):
        source=(B/'native-pointer-wheel/native-pointer.c').read_text().replace('#include "wheel-command.h"\n','').replace('unsigned button,state;int wheel;','unsigned button,state;').replace('        } else if((wheel=pointer_qa_wheel(line,pointer))!=0) {\n            if(wheel<0)return 5;\n','')
        old=(B.parent/'recovery-audit/keyboard-monitor/production-native-proof-v4/native-fixture/native-pointer.c').read_text();self.assertEqual(source,old)
    def test_epoch_marker_only_handlers_reconstruct_frozen_v9(self):
        path=Path('payload/home/.config/omarchy/plugins/hoskinson.windows/widget_v65/Windows.qml')
        source=__import__('terminal_qml').reconstruct((B/path).read_text()).replace('  property int diagnosticPopupEpoch: 0\n','').replace('  onPopupOpenChanged: { diagnosticPopupEpoch++; if (!popupOpen) popupAccessibilityReady = false }','  onPopupOpenChanged: if (!popupOpen) popupAccessibilityReady = false').replace('    diagnosticPopupEpoch++\n','').replace('diagnosticPopupEpoch:root.diagnosticPopupEpoch, popupKey:root.popupKey, ','').replace('address:w.address,stableId:w.stableId,pid:w.pid,','address:w.address,')
        self.assertEqual(source,(V9/path).read_text())
    def test_source_route_has_no_direct_scroll_mutation_or_widget_action(self):
        source=(B/'scroll_route.py').read_text();self.assertNotIn('contentY =',source);self.assertNotIn('contentY=',source);self.assertNotIn('openGroup(',source);self.assertNotIn('scrollPopup(',source)

if __name__=='__main__':unittest.main(verbosity=2)
