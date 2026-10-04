import importlib.machinery
import os
from pathlib import Path
import unittest
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1]
helper=importlib.machinery.SourceFileLoader('staged_switcher_helper',str(BASE/'hypr-window-menu')).load_module()

class HelperTests(unittest.TestCase):
    def test_builder_is_acquired_before_any_queries(self):
        order=[]
        def ipc(method,*args):
            order.append(method)
            return dict(accepted=True,builder=True,epoch='epoch',token='token')
        def prepare():order.append('queries');return {'mode':'switcher','candidates':[]}
        with patch.dict(os.environ,HYPRLAND_INSTANCE_SIGNATURE='session'),patch.object(helper,'switcher_ipc',ipc),patch.object(helper,'switcher_prepare',prepare):
            helper.switcher_protocol('switcher-step',['session','1','1','1'])
        self.assertEqual(order,['switchStep','queries','switchReady'])

    def test_nonbuilder_repeat_does_not_repeat_candidate_queries(self):
        with patch.dict(os.environ,HYPRLAND_INSTANCE_SIGNATURE='session'),patch.object(helper,'switcher_ipc',return_value={'accepted':True,'builder':False}),patch.object(helper,'switcher_prepare') as prepare:
            helper.switcher_protocol('switcher-step',['session','1','2','1'])
            prepare.assert_not_called()

    def test_release_uses_bound_generation_without_queries(self):
        with patch.dict(os.environ,HYPRLAND_INSTANCE_SIGNATURE='session'),patch.object(helper,'switcher_ipc',return_value={}) as ipc,patch.object(helper,'switcher_prepare') as prepare:
            helper.switcher_protocol('switcher-release',['session','3','4'])
            ipc.assert_called_once_with('switchRelease','session',3,4);prepare.assert_not_called()

    def test_query_failure_cancels_only_its_exact_builder(self):
        def ipc(method,*args):return dict(accepted=True,builder=True,epoch='epoch',token='token')
        with patch.dict(os.environ,HYPRLAND_INSTANCE_SIGNATURE='session'),patch.object(helper,'switcher_ipc',side_effect=ipc) as call,patch.object(helper,'switcher_prepare',side_effect=ValueError('query failed')):
            with self.assertRaises(ValueError):helper.switcher_protocol('switcher-step',['session','1','1','1'])
            self.assertEqual(call.call_args.args,('cancelSwitch',1,'token'))

    def test_foreign_session_cannot_start_builder(self):
        with patch.dict(os.environ,HYPRLAND_INSTANCE_SIGNATURE='session'),patch.object(helper,'switcher_ipc') as ipc:
            with self.assertRaises(ValueError):helper.switcher_protocol('switcher-step',['foreign','1','1','1'])
            ipc.assert_not_called()

    def test_claim_refusal_never_runs_restore(self):
        with patch.object(helper,'switcher_ipc',return_value=None),patch.object(helper,'restore_candidate') as restore:
            helper.switcher_protocol('switcher-restore-guarded',['epoch','1','token']);restore.assert_not_called()

    def test_claimed_exact_identity_reaches_existing_native_guard(self):
        candidate={'address':'0x123','pid':42,'stableId':'stable'}
        with patch.object(helper,'switcher_ipc',return_value=candidate),patch.object(helper,'run') as run:
            helper.switcher_protocol('switcher-restore-guarded',['epoch','1','token'])
            self.assertEqual(run.call_args.args,(helper.BIN/'hypr-windowctl','restore','0x123','stable',42))

    def test_incomplete_claim_identity_never_runs_restore(self):
        with patch.object(helper,'switcher_ipc',return_value={'address':'0x123','pid':42,'stableId':''}),patch.object(helper,'run') as run:
            with self.assertRaises(ValueError):helper.switcher_protocol('switcher-restore-guarded',['epoch','1','token'])
            run.assert_not_called()

if __name__=='__main__':unittest.main()
