"""A settled pause is not a stalled animation; an unchanged active frame is."""
import unittest
from analyze import analyze

def capture(rows):
    frames=[[t,x,0,100,100,target,0,100,100,1,0,0,x!=target] for t,x,target in rows]
    return {'frames':frames,'presentations':[[t,t,i,7,16666666,0,True,i] for i,(t,_,_) in enumerate(rows)],
            'inputs':[],'unmatched':0,'ambiguous':0}

class Cadence(unittest.TestCase):
    def test_settled_pause_separates_transitions(self):
        result=analyze(capture([(0,0,30),(10,10,30),(20,20,30),(30,30,30),
                                (200,30,30),(210,40,70),(220,50,70),(230,70,70)]))
        self.assertEqual(result['maxGeometryGapMs'],10)
        self.assertEqual(result['geometryGapsOver33ms'],0)
    def test_unchanged_active_frame_keeps_stall(self):
        result=analyze(capture([(0,0,100),(10,10,100),(40,10,100),(70,20,100),(80,100,100)]))
        self.assertEqual(result['maxGeometryGapMs'],60)
        self.assertEqual(result['geometryGapsOver33ms'],1)

if __name__=='__main__':unittest.main()
