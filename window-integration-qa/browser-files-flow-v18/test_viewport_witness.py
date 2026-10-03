import copy,ctypes,math,random,unittest
from fractions import Fraction
import viewport_witness as w

def fixture(point,client,sequence,before_seq):
 d={'inner':[890,563],'outer':[930,700],'rect':[135.953125,79.875,461,222],'ratio':1,'viewport':[890,563,1,0,0],'scroll':[0,0],'timeOrigin':1000,'now':10,'url':'file:///fixed-compose','title':'fixed','value':'','selection':[0,0],'active':'','clicks':0,'events':[],'pointerSequence':before_seq,'pointerMoves':[]}
 event={'sequence':sequence,'trusted':True,'type':'pointermove','pointerType':'mouse','pointerId':1,'primary':True,'buttons':0,'modifiers':[False]*4,'timestamp':11,'handled':12,'client':client}
 after={**copy.deepcopy(d),'now':13,'pointerSequence':sequence,'pointerMoves':[event]}
 ident={'address':'0x1','stableId':'abc','pid':41,'start':'200'};surface=[140,100,930,700]
 peer={k:v for k,v in ident.items()if k!='start'};peer['surfaceBox']=surface
 n={'cursor':point,'hitOwner':peer,'pointerOwner':peer,'pointerSurfacePresent':True,'nativeFocus':None,'clickMode':0,**{k:False for k in ['sessionLocked','exclusiveLayers','constrained','heldButtons','seatGrab','captured','dnd','dragTarget']}}
 return [d,after,n,copy.deepcopy(n),surface,ident,'session',w.key(d,surface,ident,'session'),None]

class Witness(unittest.TestCase):
 def setUp(self):self.a=fixture([605,450],[425,213],1,0);self.b=fixture([665,490],[485,253],2,1)
 def pair(self):return w.pair(w.sample(*self.a),w.sample(*self.b))
 def test_exact_two_observed_offsets_and_integer_inside(self):
  result=self.pair();self.assertEqual(result['insets'],[40,137,0,0]);self.assertEqual(result['translation'],[180,237]);self.assertEqual(result['integerPoint'],[546,427]);self.assertFalse(result['originalFeatureAcceptance'])
 def test_fractional_cursor_wire_quantization_exact(self):
  for a in (self.a,self.b):
   a[2]['cursor'][0]+=1/4096;a[3]['cursor'][0]+=1/4096
  self.assertEqual(self.pair()['translation'],[180,237])
 def test_libm_round_actual_binary64_half_boundaries(self):
  lib=ctypes.CDLL('libm.so.6');lib.round.argtypes=[ctypes.c_double];lib.round.restype=ctypes.c_double
  values=[]
  for integer in range(-1600,1601,3):
   for value in (integer+.5,math.nextafter(integer+.5,-math.inf),math.nextafter(integer+.5,math.inf)):
    values.append(value)
  rng=random.Random(20261002);values.extend(rng.uniform(-409600,409600)for _ in range(10000))
  for value in values:self.assertEqual(w.round_half_away(value),int(lib.round(value)))
 def test_binary_exact_fractional_rect_integer_point(self):
  p=w.integer_interior([285.953125,316.875,461,222],10);self.assertEqual(p,[516,427]);self.assertEqual(w.move_command(p),'move 516 427\n')
 def test_move_missing_or_extra_values_refused(self):
  for p in ([],[1],[1,2,3],None,'move 1 2\n'):
   with self.subTest(p=p),self.assertRaises(ValueError):w.move_command(p)
 def test_move_fractional_tokens_and_integral_floats_refused(self):
  for p in ([285.953125,316],[285,316.875],[285.0,316],[285,316.0]):
   with self.subTest(p=p),self.assertRaises(ValueError):w.move_command(p)
 def test_move_nonfinite_boolean_text_signed_range_refused(self):
  for p in ([math.inf,1],[1,math.nan],[True,1],['1',2],[-1,2],[1600,0],[0,1000]):
   with self.subTest(p=p),self.assertRaises(ValueError):w.move_command(p)
 def test_exact_complete_integer_command_bounds(self):
  for p in ([0,0],[1599,999],[605,450]):self.assertEqual(w.move_command(p),f'move {p[0]} {p[1]}\n')
 def test_integer_point_not_outside_small_interior(self):
  for r in ([.1,.1,.8,.8],[0,0,2,2],[-20,0,4,4]):
   with self.assertRaises(ValueError):w.integer_interior(r,1)
 def test_translation_difference_refused_without_epsilon(self):
  self.b[1]['pointerMoves'][0]['client'][0]=math.nextafter(485,math.inf)
  with self.assertRaisesRegex(ValueError,'exact translations'):self.pair()
 def test_moved_cursor_during_read_refused(self):
  self.a[3]['cursor'][0]+=1/256
  with self.assertRaisesRegex(ValueError,'cursor changed'):self.pair()
 def test_native_wrong_hit_and_pointer_owner_refused(self):
  for role in ('hitOwner','pointerOwner'):
   a=copy.deepcopy(self.a);a[2][role]['stableId']='reuse'
   with self.assertRaisesRegex(ValueError,'owner'):w.sample(*a)
 def test_focus_capture_and_pointer_surface_refused(self):
  for k,v in [('nativeFocus',{'pid':3}),('heldButtons',True),('pointerSurfacePresent',False),('dnd',True)]:
   a=copy.deepcopy(self.a);a[2][k]=v
   with self.assertRaisesRegex(ValueError,'input/focus'):w.sample(*a)
 def test_page_lifetime_session_time_origin_replacements_refused(self):
  for key,value in [('timeOrigin',1001),('url','file:///other'),('viewport',[890,563,1.1,0,0]),('scroll',[1,0])]:
   a=copy.deepcopy(self.a);a[1][key]=value
   with self.assertRaises(ValueError):w.sample(*a)
  a=copy.deepcopy(self.a);a[5]['start']='201'
  with self.assertRaises(ValueError):w.sample(*a)
  a=copy.deepcopy(self.a);a[6]='other'
  with self.assertRaises(ValueError):w.sample(*a)
 def test_draft_caret_dom_active_events_change_refused(self):
  for k,v in [('value','x'),('selection',[1,1]),('active','draft'),('clicks',1),('events',[{'type':'focus'}])]:
   a=copy.deepcopy(self.a);a[1][k]=v
   with self.assertRaises(ValueError):w.sample(*a)
 def test_untrusted_buttons_touch_nonprimary_modifiers_refused(self):
  for k,v in [('trusted',False),('buttons',1),('pointerType','touch'),('primary',False),('modifiers',[True,False,False,False])]:
   a=copy.deepcopy(self.a);a[1]['pointerMoves'][0][k]=v
   with self.assertRaises(ValueError):w.sample(*a)
 def test_original_event_timestamp_older_than_move_refused(self):
  self.a[1]['pointerMoves'][0].update(timestamp=9,handled=12)
  with self.assertRaisesRegex(ValueError,'Original event timestamp'):self.pair()
 def test_future_timestamp_or_handling_clock_refused(self):
  for k,v in [('timestamp',14),('handled',14)]:
   a=copy.deepcopy(self.a);a[1]['pointerMoves'][0][k]=v
   with self.assertRaises(ValueError):w.sample(*a)
 def test_stale_missing_gap_and_ambiguous_events_refused(self):
  for mutate in (lambda a:a[1].update(pointerSequence=0),lambda a:a[1].update(pointerMoves=[]),lambda a:a[1].update(pointerSequence=2)):
   a=copy.deepcopy(self.a);mutate(a)
   with self.assertRaises(ValueError):w.sample(*a)
  a=copy.deepcopy(self.a);a[1]['pointerSequence']=2;a[1]['pointerMoves'].append({**a[1]['pointerMoves'][0],'sequence':2,'client':[426,213]})
  with self.assertRaisesRegex(ValueError,'Ambiguous'):w.sample(*a)
 def test_distinct_axes_and_sequence_required(self):
  first=w.sample(*self.a)
  with self.assertRaises(ValueError):w.pair(first,first)
  self.b[2]['cursor'][0]=self.b[3]['cursor'][0]=605;self.b[1]['pointerMoves'][0]['client'][0]=425
  with self.assertRaises(ValueError):self.pair()
 def test_contained_viewport_and_nonfinite_rect_refused(self):
  for a in (self.a,self.b):a[1]['pointerMoves'][0]['client'][0]+=100
  with self.assertRaisesRegex(ValueError,'contained'):self.pair()
  a=copy.deepcopy(self.a);a[1]['rect'][0]=math.nan
  with self.assertRaises(ValueError):w.sample(*a)
 def test_protocol_edge_clipping_basis_refused(self):
  for p in ([140,450],[1069.999999,450],[605,100]):
   with self.assertRaises(ValueError):w.wire_point(p,[140,100,930,700])
 def test_outer_inner_no_assumed_side_alignment(self):
  for a in (self.a,self.b):a[1]['pointerMoves'][0]['client'][0]+=40
  self.assertEqual(self.pair()['insets'],[0,137,40,0])
 def test_scroll_zoom_ratio_and_missing_clock_refused(self):
  for k,v in [('ratio',2),('timeOrigin',0),('viewport',[890,563,1,1,0])]:
   a=copy.deepcopy(self.a);a[0][k]=a[1][k]=v
   with self.assertRaises(ValueError):w.sample(*a)
 def test_pointer_id_changes_between_observations_refused(self):
  self.b[1]['pointerMoves'][0]['pointerId']=2
  with self.assertRaisesRegex(ValueError,'serial samples'):self.pair()
 def test_boolean_metadata_never_numeric_authority(self):
  for k,v in [('buttons',False),('pointerId',True),('modifiers',[0,0,0,0])]:
   a=copy.deepcopy(self.a);a[1]['pointerMoves'][0][k]=v
   with self.assertRaises(ValueError):w.sample(*a)
 def test_fractional_caption_and_files_integer_selection(self):
  self.assertEqual(w.integer_interior([229.25,87.25,2,2],0),[230,88])
  self.assertEqual(w.integer_interior([900.375,280.625,24,24],1),[912,292])
 def test_event_sequence_bound_revokes_coordinate_authority(self):
  self.a[0]['pointerSequence']=65536;self.a[1]['pointerSequence']=65537;self.a[1]['pointerMoves'][0]['sequence']=65537
  with self.assertRaises(ValueError):self.pair()

if __name__=='__main__':unittest.main()
