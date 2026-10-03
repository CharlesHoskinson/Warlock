"""Fabricated adversarial audit fixtures are never native outcome evidence."""
import copy
import unittest
from verify_c1 import verify,sample
from test_reversal import IDS,SOURCES,TOKENS

CAPTURED=[dict(s,atlasRect=dict(x=100+i*10,y=60,width=100,height=80),
               iconRect=dict(x=10+i*4,y=3,width=20,height=20)) for i,s in enumerate(SOURCES)]

def fixture(outputs=('WAYLAND-1',)):
    events=[dict(event='uploaded',digest=s['digest'],pixels=[100,80]) for s in SOURCES]
    events.append(dict(event='seeded',token=TOKENS[0],identities=IDS,sourceDigests=SOURCES,nativeAuthority=False))
    latest={};last_kin={};sequence=0
    for epoch,token in enumerate(TOKENS,1):
        if latest:
            origins=[{k:latest[name][k] for k in ('output','generation','sequence','timestampNs','rectangle','members')} for name in outputs]
            events.append(dict(event='retargetAccepted',token=token,identities=IDS,sourceDigests=SOURCES,nativeAuthority=False))
            events.append(dict(event='retargeted',token=token,origins=origins,startNs=str(epoch*1000000000),identities=IDS,sourceDigests=SOURCES,sourceReused=True,nativeAuthority=False,uploadCount=3))
            for name in sorted(outputs):events.append(dict(last_kin[name],event='frameKinematics',phase='retargetOrigin',accepted=True,nativeAuthority=False))
        retained=copy.deepcopy(last_kin)
        for elapsed in ([.04] if epoch<3 else [.04,.22]):
          for output_index,name in enumerate(outputs):
            actual_elapsed=elapsed+output_index*.002 if elapsed<.22 else elapsed
            sequence+=1;members=[];kin_members=[]
            for i,source in enumerate(CAPTURED):
                a=[source['atlasRect'][k] for k in ('x','y','width','height')] if epoch==1 else [retained[name]['members'][i]['rectangle'][k] for k in ('x','y','width','height')]
                v=[0]*4 if epoch==1 else retained[name]['members'][i]['velocity']
                target=source['iconRect'] if epoch%2 else source['atlasRect']
                p,speed=sample(a,v,[target[k] for k in ('x','y','width','height')],.22,actual_elapsed)
                rectangle=dict(zip(('x','y','width','height'),p))
                member=dict(SOURCES[i],rectangle=rectangle);members.append(member);kin_members.append(dict(member,velocity=speed))
            frame=dict(token=token,sequence=str(sequence),output=name,generation=6+output_index,members=members,rectangle=members[0]['rectangle'],progress=actual_elapsed/.22,timestampNs=str(epoch*1000000000+int(actual_elapsed*1e9)+100),endpoint=actual_elapsed>=.22)
            kin=dict(token=token,sequence=str(sequence),output=name,generation=6+output_index,epoch=str(epoch),sampleNs=str(epoch*1000000000+int(actual_elapsed*1e9)),startNs=str(epoch*1000000000),elapsedSeconds=actual_elapsed,durationSeconds=.22,progress=actual_elapsed/.22,endpoint=actual_elapsed>=.22,members=kin_members,nativeAuthority=False)
            events.extend([dict(frame,event='swap',success=True),dict(kin,event='frameKinematics',phase='swap',accepted=True),dict(frame,event='presented',accepted=True),dict(kin,event='frameKinematics',phase='presented',accepted=True)])
            latest[name]=frame
            # Last origin for an epoch stays fixed across its multiple samples.
            if elapsed==.04:last_kin[name]=kin
    events.append(dict(event='endpoint',token=TOKENS[-1],identities=IDS,sourceDigests=SOURCES,servicePromoted=True))
    return copy.deepcopy(events)

class C1Audit(unittest.TestCase):
    def audit(self,events):return verify(events,IDS,CAPTURED)
    def refuse(self,change):
        rows=fixture();change(rows)
        with self.assertRaises((ValueError,KeyError,TypeError)):self.audit(rows)
    def test_complete(self):
        result=self.audit(fixture());self.assertEqual(result['analyticT0Pairs'],2);self.assertEqual(result['acceptedAnalyticSamples'],4);self.assertFalse(result['nativeAuthorityGranted']);self.assertFalse(result['physicalCadenceAccepted'])
    def test_mixed_output_distinct_accepted_pairs(self):
        result=self.audit(fixture(('WAYLAND-1','ORACLE-SECOND')))
        self.assertEqual(result['analyticT0Pairs'],4);self.assertEqual(result['acceptedAnalyticSamples'],8)
        self.assertNotEqual(result['exactDisplayedOriginPairs'][0]['originKinematics']['members'],result['exactDisplayedOriginPairs'][1]['originKinematics']['members'])
    def test_mixed_output_common_duration_required(self):
        rows=fixture(('WAYLAND-1','ORACLE-SECOND'))
        for r in rows:
            if r.get('event')=='frameKinematics' and r.get('output')=='ORACLE-SECOND' and r.get('sequence')=='2':r['durationSeconds']=.2
        with self.assertRaisesRegex(ValueError,'Common output duration'):self.audit(rows)
    def test_missing_kinematics(self):self.refuse(lambda rs:rs.pop(next(i for i,r in enumerate(rs) if r.get('phase')=='presented')))
    def test_orphan_kinematics(self):self.refuse(lambda rs:rs.append(copy.deepcopy(next(r for r in rs if r.get('phase')=='presented'))))
    def test_duplicate_origin(self):self.refuse(lambda rs:rs.append(copy.deepcopy(next(r for r in rs if r.get('phase')=='retargetOrigin'))))
    def test_false_acceptance_binding(self):self.refuse(lambda rs:next(r for r in rs if r.get('phase')=='swap').update(accepted=False))
    def test_elapsed_clock_exact(self):
        def change(rs):
            for r in rs:
                if r.get('event')=='frameKinematics' and r.get('sequence')=='4':r['sampleNs']=str(int(r['sampleNs'])+1)
        self.refuse(change)
    def test_wrong_origin_velocity(self):self.refuse(lambda rs:next(r for r in rs if r.get('phase')=='retargetOrigin')['members'][0]['velocity'].__setitem__(0,999))
    def test_wrong_origin_epoch(self):self.refuse(lambda rs:next(r for r in rs if r.get('phase')=='retargetOrigin').update(epoch='99'))
    def test_wrong_origin_token(self):self.refuse(lambda rs:next(r for r in rs if r.get('phase')=='retargetOrigin').update(token=TOKENS[1]))
    def test_wrong_origin_source_order(self):self.refuse(lambda rs:next(r for r in rs if r.get('phase')=='retargetOrigin')['members'].reverse())
    def test_wrong_presented_velocity(self):self.refuse(lambda rs:next(r for r in rs if r.get('phase')=='presented')['members'][0]['velocity'].__setitem__(0,999))
    def test_wrong_presented_generation(self):self.refuse(lambda rs:next(r for r in rs if r.get('phase')=='presented').update(generation=99))
    def test_untrusted_telemetry_authority(self):self.refuse(lambda rs:next(r for r in rs if r.get('event')=='frameKinematics').update(nativeAuthority=True))
    def test_changed_double_clock(self):
        def change(rs):
            for r in rs:
                if r.get('event')=='frameKinematics' and r.get('sequence')=='4':r['startNs']='3000000001'
        self.refuse(change)
    def test_nonfinite(self):self.refuse(lambda rs:next(r for r in rs if r.get('phase')=='presented').update(durationSeconds=float('nan')))
    def test_zero_duration(self):self.refuse(lambda rs:next(r for r in rs if r.get('phase')=='presented').update(durationSeconds=0))
    def test_forged_analytic_pair(self):
        def change(rs):
            for r in rs:
                if r.get('event')=='frameKinematics' and r.get('sequence')=='4':r['members'][0]['velocity'][0]=777
        self.refuse(change)
    def test_wrong_captured_target(self):
        captured=copy.deepcopy(CAPTURED);captured[0]['iconRect']['x']+=1
        with self.assertRaises(ValueError):verify(fixture(),IDS,captured)
    def test_old_source_velocity_failure_retained(self):
        from pathlib import Path
        import json
        evidence=json.loads((Path(__file__).resolve().parent.parent/'family-continuous-reversal-v3/attempt-1/root-velocity-audit.json').read_text())
        self.assertFalse(evidence['velocityContinuityAccepted']);self.assertTrue(all(r['maxComponentJumpPixelsPerSecond']>0 for r in evidence['reversals']))

if __name__=='__main__':unittest.main()
