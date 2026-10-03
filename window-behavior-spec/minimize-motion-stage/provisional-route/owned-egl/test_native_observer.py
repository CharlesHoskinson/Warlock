import unittest
from native_observer import accepted,cadence,handover

def frame(sequence,ns,progress=.3,output='left',token='abcdef123456-1'):
 return {'event':'presented','accepted':True,'token':token,'output':output,'generation':7,'sequence':str(sequence),'timestampNs':str(ns),'progress':progress,'rectangle':{'x':sequence,'y':20,'width':40,'height':50}}
class EvidenceTests(unittest.TestCase):
 def test_declared_without_accepted_presentation_is_not_pixels(self):
  self.assertFalse(accepted(dict(frame(1,100),event='swap')))
  self.assertFalse(accepted(dict(frame(1,100),accepted=False)))
 def test_exact_presented_interior_origin(self):
  rows=[frame(1,100),frame(2,200)]
  origin={k:rows[0][k] for k in ('output','generation','sequence','timestampNs','rectangle')}
  self.assertTrue(handover(rows,{'token':'abcdef123456-2','origins':[origin]})['passes'])
 def test_computed_or_endpoint_origin_rejected(self):
  row=frame(1,100,progress=1)
  origin={k:row[k] for k in ('output','generation','sequence','timestampNs','rectangle')}
  self.assertFalse(handover([row],{'token':'abcdef123456-2','origins':[origin]})['passes'])
  origin['rectangle']={**origin['rectangle'],'x':500}
  self.assertFalse(handover([frame(1,100)],{'token':'abcdef123456-2','origins':[origin]})['passes'])
 def test_steady_refresh_passes_but_metadata_pause_fails(self):
  outputs=[{'name':'left','refreshMilliHz':60000}]
  rows=[frame(i,1000000000+i*16666667) for i in range(20)]
  self.assertTrue(cadence(rows,outputs)['left']['passes'])
  for row in rows[10:]:row['timestampNs']=str(int(row['timestampNs'])+100000000)
  self.assertFalse(cadence(rows,outputs)['left']['passes'])
 def test_each_output_requires_ordered_sufficient_actual_samples(self):
  rows=[frame(i,1000000000+i*16666667) for i in range(20)]
  outputs=[{'name':'left','refreshMilliHz':60000},{'name':'right','refreshMilliHz':60000}]
  self.assertFalse(cadence(rows,outputs)['right']['passes'])
  rows[4]['timestampNs']=rows[3]['timestampNs']
  self.assertFalse(cadence(rows,outputs)['left']['passes'])
if __name__=='__main__':unittest.main()
