import base64,copy,json,os,unittest
from frontend_authority import binding,current,pointer,keyboard,helper,FrontendCase
from root_pin_helper import command

class Tests(unittest.TestCase):
 def setUp(self):
  self.token=dict(address='0x123',stableId='18000000',pid=7,session='qa_1',compositorPid=9,compositorStart='123',incarnation='a'*32,epoch='1',generation='1')
  self.scope=dict(pid=11,start='777',configSHA256='f'*64,engineEpoch=1)
  self.layer=dict(address='0xabc',pid=11,namespace='hoskinson-pin-window-menu',mapped=True,visible=True,box=[200,300,240,100])
  self.native=dict(layers=[self.layer],pointerSurfacePresent=True,pointerLayerOwner=self.layer,keyboardSurfacePresent=True,keyboardLayerOwner=self.layer,cursor=[310,315],nativeFocus=dict(address='0xf00',pid=7),sessionLocked=False,constrained=False,heldButtons=False,seatGrab=False,captured=False,dnd=False,dragTarget=False,exclusiveLayers=0,clickMode=0)
  self.menu=dict(open=True,status='ready',sent=False,nonce=1,publicIdentity={k:self.token[k]for k in('address','stableId','pid')},captured=self.token,layerNamespace='hoskinson-pin-window-menu',button=dict(x=0,y=0,width=220,height=30,visible=True,enabled=True,label='Toggle pin'))
  self.expected=binding(self.menu,self.native,self.scope);self.native['cursor']=self.expected['point']
  self.requester=dict(pid=11,start='777',parent=1,pgid=11);self.compositor=dict(pid=9,start='123',parent=1,pgid=9)
  projection={k:self.token[k]for k in('address','stableId','pid','session','incarnation','epoch','generation')}
  before=dict(projection,live=True,normal=True,floating=True,pinned=False,fullscreen=False);after=dict(before,pinned=True)
  result=dict(ok=True,phase='complete',actionsInvoked=True,possiblePartialOutcome=False,captured=self.token,desiredPinned=True,before=before,after=after)
  raw=json.dumps(result).encode()
  self.receipt=dict(result='complete',nativeCompletionClaimed=True,automaticRetries=0,captured=self.token,authority=dict(frontend=dict(pid=12,start='888',parent=11,pgid=11),requester=self.requester,compositor=self.compositor,role='shell'),transport=dict(sendStarted=True,completeServerEOF=True,peer=dict(pid=9,uid=os.getuid(),gid=os.getgid()),commandBase64=base64.b64encode(command(self.token)).decode(),rawReplyBase64=base64.b64encode(raw).decode(),replyBytes=len(raw)),rawNativeResult=result)
 def test_exact_integer_inside_actual_layer(self):
  self.assertEqual(self.expected['point'],[310,315]);self.assertTrue(pointer(self.native,self.expected))
 def test_same_menu_current(self):self.assertEqual(current(self.menu,self.native,self.scope,self.expected),self.expected)
 def test_complete_helper_raw_binding(self):self.assertEqual(helper(self.receipt,self.token,False,self.requester,self.compositor)['pid'],12)
 def test_core_focus_cannot_keyboard_authorize(self):
  self.native['keyboardLayerOwner']=None
  with self.assertRaises(ValueError):keyboard(self.native,self.expected)
 def test_pointer_other_layer_refuses(self):
  self.native['pointerLayerOwner']=dict(self.layer,address='0xdef')
  with self.assertRaises(ValueError):pointer(self.native,self.expected)
 def test_fractional_cursor_not_integer_authority(self):
  self.native['cursor'][0]+=.1
  with self.assertRaises(ValueError):pointer(self.native,self.expected)
 def test_menu_generation_change(self):
  self.menu['nonce']=2
  with self.assertRaises(ValueError):current(self.menu,self.native,self.scope,self.expected)
 def test_engine_reload_change(self):
  self.scope['engineEpoch']=2
  with self.assertRaises(ValueError):current(self.menu,self.native,self.scope,self.expected)
 def test_disabled_or_launcher_label(self):
  self.menu['button']['label']='Pin to taskbar'
  with self.assertRaises(ValueError):binding(self.menu,self.native,self.scope)
 def test_whole_row_must_fit_layer(self):
  self.menu['button']['width']=241
  with self.assertRaises(ValueError):binding(self.menu,self.native,self.scope)
 def test_numeric_boolean_identity_refused(self):
  self.menu['captured']=dict(self.token,pid=True)
  with self.assertRaises(ValueError):binding(self.menu,self.native,self.scope)
 def test_raw_native_replacement_refused(self):
  self.receipt['rawNativeResult']=dict(self.receipt['rawNativeResult'],desiredPinned=False)
  with self.assertRaises(ValueError):helper(self.receipt,self.token,False,self.requester,self.compositor)
 def test_wrong_helper_parent_refused(self):
  self.receipt['authority']['frontend']['parent']=13
  with self.assertRaises(ValueError):helper(self.receipt,self.token,False,self.requester,self.compositor)
 def test_missing_eof_refused(self):
  self.receipt['transport']['completeServerEOF']=False
  with self.assertRaises(ValueError):helper(self.receipt,self.token,False,self.requester,self.compositor)
 def test_no_accept_before_actual_release(self):
  c=FrontendCase(self.expected);c.press(self.menu,self.native,self.scope,'pointer');c.receipt=True;c.observed=True
  with self.assertRaises(ValueError):c.accept()
  c.release(True);self.assertTrue(c.accept())
 def test_invalidated_receipt_cannot_accept(self):
  c=FrontendCase(self.expected);c.press(self.menu,self.native,self.scope,'return');c.release(True);c.receipt=True;c.observed=True;c.invalidate()
  with self.assertRaises(ValueError):c.accept()
if __name__=='__main__':unittest.main()
