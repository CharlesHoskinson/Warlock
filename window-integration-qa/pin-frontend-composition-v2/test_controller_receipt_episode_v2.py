"""Additional actual unprojected controller receipt-loop CPU case; no native proof."""
import base64,copy,json,os,unittest
from unittest.mock import Mock
import test_composition as fixtures

class ReceiptLoop(unittest.TestCase):
 setUp=fixtures.Composition.setUp
 rows=fixtures.Composition.rows
 controller=fixtures.Composition.controller
 def test_controller_partial_then_complete_episode_inside_original_receipt_wait(self):
  c=self.controller();c.open_right=Mock(return_value=(self.token,[]));c.move_layer=Mock()
  projection={k:self.token[k]for k in('address','stableId','pid','session','incarnation','epoch','generation')}
  before=dict(projection,live=True,normal=True,floating=True,pinned=False,fullscreen=False);after=dict(before,pinned=True)
  result=dict(ok=True,phase='complete',actionsInvoked=True,possiblePartialOutcome=False,captured=self.token,desiredPinned=True,before=before,after=after)
  from root_pin_helper import command
  raw=json.dumps(result).encode();requester=dict(pid=11,start='777',parent=1,pgid=11);compositor=dict(pid=9,start='123',parent=1,pgid=9)
  receipt=dict(result='complete',nativeCompletionClaimed=True,automaticRetries=0,captured=self.token,authority=dict(frontend=dict(pid=12,start='888',parent=11,pgid=11),requester=requester,compositor=compositor,role='shell'),transport=dict(sendStarted=True,completeServerEOF=True,peer=dict(pid=9,uid=os.getuid(),gid=os.getgid()),commandBase64=base64.b64encode(command(self.token)).decode(),rawReplyBase64=base64.b64encode(raw).decode(),replyBytes=len(raw)),rawNativeResult=result)
  done=dict(copy.deepcopy(self.menu),status='complete',sent=True,button=dict(self.menu['button'],enabled=False),receipt=receipt)
  active=[self.menu]
  c.snapshots=Mock(side_effect=lambda:dict(menu=active[0],native=self.native,scope=self.scope));c.query=Mock(side_effect=lambda name:dict(active[0],open=False)if name=='pinMenuState'else{})
  def send(button,setup,before_press):before_press();active[0]=done;return dict(pressSent=True,releaseSent=True)
  c.buttons=Mock(side_effect=send);c.chord=Mock();c.input_rows=Mock(side_effect=[[],self.rows()[:1],self.rows()])
  c.config=dict(requestRoots=[dict(role='shell',identity=requester)],compositor=dict(identity=compositor))
  c.helper_observer=Mock(return_value=dict(actualOwnedDurableFile=True,exactActualHelperLifetime=True,normalProcessExit=True,registeredDescendantGone=True,rawReceiptExact=True))
  def scene(pinned):return dict(clients=[dict(address=self.token['address'],stableId=self.token['stableId'],pid=7,pinned=pinned)],stack=dict(planValid=True,satisfied=True,order=[]),native=dict(nativeFocus=None),seat=dict(keyboardOwner=None,coreNativeFocus=None,keyboardSurfacePresent=True,keyboardResourcePresent=True))
  c.route.scene=Mock(side_effect=[scene(False),scene(True)]);c.route.query=Mock(side_effect=[[],[result]])
  row=c.toggle('owner')
  self.assertEqual(c.input_rows.call_count,3);c.buttons.assert_called_once();c.helper_observer.assert_called_once()
  self.assertEqual(row['inputEpisode']['profile'],'b-popup-layer-input-v1');self.assertTrue(c.report['checks'][0]['passed'])

if __name__=='__main__':unittest.main()
