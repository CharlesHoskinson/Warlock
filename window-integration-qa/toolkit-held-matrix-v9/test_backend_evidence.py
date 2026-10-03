"""Exact backend byte authority and configured workload refusal regressions."""
from pathlib import Path
import json
import unittest
from public_toolkit import actual_backend,backend_observation
from helper_setup import workload_expectations

class BackendEvidence(unittest.TestCase):
    def test_wayland_missing_candidate_and_missing_closure_remain_fatal(self):
        state=dict(pid=123,platform='wayland');clients=[dict(pid=123,xwayland=False)];variant=dict(toolkit='QtWidgets',backend='wayland')
        path='/usr/lib/qt6/plugins/platforms/libqwayland.so'
        for loaded in ({},{path:'abc'}):
            evidence=backend_observation(state,clients,variant,123,loaded,{})
            self.assertFalse(evidence['allCandidateBytesExact'])
            with self.assertRaises(ValueError):actual_backend(state,clients,variant,123,loaded,{})
        self.assertFalse(backend_observation(state,clients,variant,123,{}, {})['candidateSetNonempty'])
        changed=backend_observation(state,clients,variant,123,{path:'changed'},{path:'frozen'})
        self.assertEqual(changed['candidates'][0]['loadedSHA256'],'changed');self.assertFalse(changed['candidates'][0]['exactBytes'])
        with self.assertRaises(ValueError):actual_backend(state,clients,variant,123,{path:'changed'},{path:'frozen'})

    def test_exact_new_loader_input_supports_original_candidate_predicate(self):
        frozen=json.loads((Path(__file__).resolve().parent/'qt-loader-inputs.json').read_text())['inputs'];path='/usr/lib/qt6/plugins/platforms/libqwayland.so'
        self.assertIn(path,frozen)
        state=dict(pid=123,platform='wayland');clients=[dict(pid=123,xwayland=False)];variant=dict(toolkit='QtWidgets',backend='wayland')
        loaded={path:frozen[path]}
        self.assertTrue(backend_observation(state,clients,variant,123,loaded,frozen)['allCandidateBytesExact'])
        self.assertEqual(actual_backend(state,clients,variant,123,loaded,frozen)['mappedBackendModules'],loaded)

    def test_xcb_gtk_and_wrong_public_native_backend_still_exact(self):
        for toolkit,backend,path in [('QtWidgets','xcb','/exact/libqxcb.so'),('GTK4','wayland','/exact/libgtk-4.so.1')]:
            state=dict(pid=123,platform=backend,backend='GdkWaylandDisplay',windows={'source':dict(surfaceType='GdkWaylandSurface')})
            clients=[dict(pid=123,xwayland=backend=='xcb')];variant=dict(toolkit=toolkit,backend=backend)
            self.assertEqual(actual_backend(state,clients,variant,123,{path:'exact'},{path:'exact'})['pid'],123)
            with self.assertRaises(ValueError):actual_backend(state,clients,variant,124,{path:'exact'},{path:'exact'})
            with self.assertRaises(ValueError):actual_backend(state,[dict(pid=123,xwayland=backend!='xcb')],variant,123,{path:'exact'},{path:'exact'})

class Workload(unittest.TestCase):
    def config(self):return dict(queryRoots={'service':{'identity':{'pid':123,'start':'1'}}},serviceMembers=[dict(address='0xa',stableId='1',pid=123)],serviceTargetLimitPerMember=2,serviceRefreshLimit=3)
    def test_partial_failure_without_service_is_not_keyerror_or_full_workload(self):
        result=workload_expectations(dict(queryRoots={}),False,False,False,False)
        self.assertEqual(result,dict(serviceRegistered=False,harnessSnapshotAttempted=False,fullWorkloadRequired=False))
        with self.assertRaises(RuntimeError):workload_expectations(dict(queryRoots={}),False,False,False,True)
    def test_actual_service_without_registration_or_partial_config_refuses(self):
        with self.assertRaises(RuntimeError):workload_expectations(dict(queryRoots={}),True,False,False,False)
        for missing in ('serviceMembers','serviceTargetLimitPerMember','serviceRefreshLimit','queryRoots'):
            config=self.config();del config[missing]
            with self.assertRaises(RuntimeError):workload_expectations(config,True,False,False,False)
    def test_full_workload_requires_registered_service_and_genuine_snapshot(self):
        config=self.config()
        with self.assertRaises(RuntimeError):workload_expectations(config,True,False,False,True)
        with self.assertRaises(RuntimeError):workload_expectations(config,True,False,True,True)
        self.assertTrue(workload_expectations(config,True,True,True,True)['fullWorkloadRequired'])
        self.assertTrue(workload_expectations(config,True,True,False,False)['harnessSnapshotAttempted'])

if __name__=='__main__':unittest.main(verbosity=2)
