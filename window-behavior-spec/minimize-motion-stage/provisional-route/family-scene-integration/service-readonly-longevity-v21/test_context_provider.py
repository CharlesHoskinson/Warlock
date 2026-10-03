import copy
import unittest
from context_provider import NativeContextProvider
from test_scene_controller import Desktop

class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.d=Desktop();self.monitors=[dict(name='left',id=0,x=0,y=0,width=960,height=720,scale=1.5,transform=0,activeWorkspace={'id':1,'name':'1'})]
        self.d.monitors=lambda:copy.deepcopy(self.monitors)
        self.provider=NativeContextProvider(self.d,session='explicit-private-session')
        w=self.d.windows[0];self.request={k:w[k] for k in ('address','stableId','pid')}
    def test_same_current_desktop_fingerprint_allows_hidden_identity_without_native_writes(self):
        before=self.provider(self.request);self.d.windows[0]['workspace']['name']='special:win-minimized'
        after=self.provider(self.request);self.assertEqual(before,after);self.assertFalse(self.d.commits);self.assertFalse(self.d.destinations)
    def test_current_workspace_change_changes_fingerprint_even_when_window_is_minimized(self):
        before=self.provider(self.request);self.monitors[0]['activeWorkspace']={'id':2,'name':'2'}
        self.assertNotEqual(self.provider(self.request),before)
    def test_mid_observation_desktop_change_rejects_inconsistent_snapshot(self):
        count=0
        def monitors():
            nonlocal count
            count+=1;result=copy.deepcopy(self.monitors)
            if count==2:result[0]['activeWorkspace']={'id':2,'name':'2'}
            return result
        self.d.monitors=monitors
        with self.assertRaisesRegex(ValueError,'changed during'):self.provider(self.request)
    def test_same_address_reused_native_identity_never_produces_context(self):
        self.d.windows[0]['pid']+=1
        with self.assertRaisesRegex(ValueError,'missing/reused'):self.provider(self.request)
    def test_duplicate_and_nonfinite_outputs_refuse_context(self):
        self.monitors.append(copy.deepcopy(self.monitors[0]))
        with self.assertRaisesRegex(ValueError,'duplicate'):self.provider(self.request)
        self.monitors.pop();self.monitors[0]['scale']=float('nan')
        with self.assertRaisesRegex(ValueError,'nonfinite'):self.provider(self.request)

if __name__=='__main__':unittest.main()
