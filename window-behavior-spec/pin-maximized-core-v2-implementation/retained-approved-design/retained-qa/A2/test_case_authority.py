"""CPU actual parser/acceptance counterexamples, no GUI or protocol writes."""
import copy,unittest
from case_authority import *
TOKEN=dict(address='0xabc',stableId='18000000',pid=123,session='private_1',compositorPid=456,compositorStart='999',incarnation='a'*32,epoch='2',generation='3')
def snapshot(pinned):return {k:TOKEN[k] for k in ('address','stableId','pid','session','incarnation','epoch','generation')}|dict(live=True,normal=True,floating=True,pinned=pinned,fullscreen=False)
def receipt():return dict(ok=True,phase='complete',actionsInvoked=True,possiblePartialOutcome=False,captured=dict(TOKEN),before=snapshot(False),after=snapshot(True),desiredPinned=True)
class Proof(unittest.TestCase):
 def test_full_native_representation(self):
  self.assertEqual(token(TOKEN),TOKEN)
  for key,value in [('pid',True),('stableId',int('18000000',16)),('epoch',str(2**64)),('generation','0'),('address','0xABC'),('incarnation','a'*31)]:
   with self.subTest(key=key):
    bad=TOKEN|{key:value}
    with self.assertRaises(ValueError):token(bad)
 def test_boolean_never_projection_authority(self):
  self.assertTrue(complete(receipt(),TOKEN,False))
  for side in ('before','after'):
   for key in ('live','normal','floating','pinned','fullscreen','pid'):
    r=receipt();r[side][key]=int(r[side][key])
    if key=='pid':r[side][key]=True
    with self.subTest(side=side,key=key),self.assertRaises(ValueError):complete(r,TOKEN,False)
 def test_incomplete_postsend_not_acceptance(self):
  for k,v in [('ok',1),('phase','pin'),('actionsInvoked',1),('possiblePartialOutcome',0),('captured',None),('desiredPinned',1)]:
   with self.subTest(k=k),self.assertRaises(ValueError):complete(receipt()|{k:v},TOKEN,False)
 def test_captured_pid_one_bool_alias_refused(self):
  owner=TOKEN|{'pid':1};r=receipt();r['captured']=owner|{'pid':True};r['before']['pid']=1;r['after']['pid']=1
  with self.assertRaises(ValueError):complete(r,owner,False)
 def test_release_before_feature_required(self):
  c=Case(TOKEN);c.press(True,True);c.receipt=True;c.observed=True
  with self.assertRaises(ValueError):c.accept()
  c.release(True);self.assertTrue(c.accept());c.invalidate()
  with self.assertRaises(ValueError):c.accept()
 def test_typed_input_same_owner(self):
  for a,b in [(1,True),(True,1),(False,True),(True,False)]:
   with self.assertRaises(ValueError):Case(TOKEN).press(a,b)
 def test_exact_integer_witness_and_protocol(self):
  p=integer_point(['140.25','100.5','14','14'],1600,1000)
  self.assertEqual(move_command(p,1600,1000),'move 147 107\n')
  for bad in ([1.5,2],[1],[True,2],[1,'2'],[1600,2],[-1,2]):
   with self.assertRaises(ValueError):move_command(bad,1600,1000)
  for box in ([0,0,.1,.1],['NaN',0,10,10],[1590,0,20,10],[0,0,True,10]):
   with self.assertRaises(ValueError):integer_point(box,1600,1000)
 def test_cursor_exact_identity_and_grabs(self):
  n=dict(cursor=[1,2],hitOwner=public(TOKEN),sessionLocked=False,constrained=False,heldButtons=False,seatGrab=False,captured=False,dnd=False,dragTarget=False,exclusiveLayers=0,clickMode=0)
  self.assertTrue(cursor_owner(n,[1,2],TOKEN))
  for k,v in [('cursor',[1.1,2]),('hitOwner',public(TOKEN)|{'pid':True}),('heldButtons',0),('exclusiveLayers',False)]:
   with self.assertRaises(ValueError):cursor_owner(n|{k:v},[1,2],TOKEN)
 def test_real_band_and_parent_order(self):
  row=dict(address='0x1',parent='0x0',eligible=True,pinned=False,floating=True,fullscreen=False,modal=False,x11=False,workspace='0x7',monitor='0x8')
  peer=row|{'address':'0x2'};owner=row|{'address':'0x3','pinned':True};child=row|{'address':'0x4','parent':'0x3','modal':True}
  self.assertEqual(protected_order(dict(planValid=True,satisfied=True,order=[peer,owner,child])),['0x3','0x4'])
  for rows in ([owner,child,peer],[peer,child,owner],[peer,owner,owner]):
   with self.assertRaises(ValueError):protected_order(dict(planValid=True,satisfied=True,order=rows))
if __name__=='__main__':unittest.main()
