"""Nongraphical protocol regressions for the actual V3 preparation failure."""
import copy
import hashlib
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import held_route
import helper_observer
import transport_check

def native(role='child',**changes):
    return dict(dict(address='0x'+{'owner':'a1','peer':'a2','child':'a3','nested':'a4','unknown':'a5'}[role],stableId='4',pid=123,title='Qt WindowModal QA '+role,mapped=True,xwayland=False),**changes)

def route(roles=('child',),rows=None):
    result=object.__new__(held_route.CaseRoute)
    result.guard=lambda:None;result.toolkit='QtWidgets';result.variant=dict(backend='wayland');result.source_name='nested'
    result.process=SimpleNamespace(pid=123);result.identities={};result.config=dict(allowed=[]);result.env={};result.report={}
    result.fixture=SimpleNamespace(state=lambda:dict(windows={role:{} for role in roles}))
    result.session=SimpleNamespace(data=lambda *args:rows if rows is not None else [native(role) for role in roles])
    return result

def append(env,config,rows):
    config['allowed'] += [helper_observer.operation(['forget-closed',row['address'],str(row['stableId']),str(row['pid'])]) for row in rows]

class Mapping(unittest.TestCase):
    def test_public_child_before_native_mapping_remains_pending_then_registers(self):
        target=route();seen=[];samples=iter([[],[native()]])
        target.session.data=lambda *args:next(samples)
        def bounded(function,label):
            self.assertIsNone(function());seen.append('pending')
            self.assertEqual(target.config['allowed'],[])
            return function()
        target.wait=bounded
        with patch.object(held_route.helper_setup,'allow_closes',side_effect=append) as registration:
            self.assertEqual(target.await_mapped('child')['address'],'0xa3');self.assertEqual(registration.call_count,1)
        self.assertEqual(seen,['pending']);self.assertEqual(len(target.config['allowed']),1)

    def test_public_role_absent_does_not_query_native_or_register(self):
        target=route(roles=());target.session.data=lambda *args:self.fail('public role not present')
        target.wait=lambda fn,label:self.assertIsNone(fn())
        with patch.object(held_route.helper_setup,'allow_closes') as registration:
            target.await_mapped('child');registration.assert_not_called()

    def test_unmapped_pending_only_creation_feature_lookup_remains_strict(self):
        target=route(rows=[native(mapped=False)])
        self.assertIsNone(target.window('child',pending=True))
        with self.assertRaises(RuntimeError):target.window('child')
        target.session.data=lambda *args:[]
        with self.assertRaises(RuntimeError):target.window('child')

    def test_duplicate_missing_schema_unknown_backend_refuse_immediately(self):
        missing=native();del missing['mapped']
        for rows in ([native(),native()], [missing], [native(mapped=1)], [native(xwayland=True)]):
            target=route(rows=rows)
            with self.assertRaises((RuntimeError,KeyError)):target.window('child',pending=True)
            self.assertFalse(target.identities)

    def test_captured_lifetime_change_and_guard_failure_are_not_pending(self):
        target=route();target.window('child');target.session.data=lambda *args:[native(stableId='5')]
        with self.assertRaises(RuntimeError):target.window('child',pending=True)
        target.guard=lambda:(_ for _ in ()).throw(RuntimeError('PID/start source environment drift'))
        with self.assertRaisesRegex(RuntimeError,'drift'):target.window('child',pending=True)

    def test_partial_quit_registers_each_exact_public_mapped_lifetime_once(self):
        target=route(roles=('owner','peer','child'));target.wait=lambda fn,label:fn()
        with patch.object(held_route.helper_setup,'allow_closes',side_effect=append):
            target.register_partial();old=copy.deepcopy(target.config['allowed']);target.register_partial()
        self.assertEqual(len(old),3);self.assertEqual(old,target.config['allowed'])
        self.assertEqual(set(target.identities),{'owner','peer','child'})

    def test_unknown_same_pid_window_cannot_gain_close_authorization(self):
        target=route();target.wait=lambda fn,label:fn()
        target.session.data=lambda *args:[native(),native(role='unknown')]
        with patch.object(held_route.helper_setup,'allow_closes',side_effect=append):
            with self.assertRaisesRegex(RuntimeError,'Unknown'):target.register_partial()
        self.assertEqual(len(target.config['allowed']),1)
        self.assertNotIn('0xa5',' '.join(target.config['allowed']))

    def test_final_partial_sample_cannot_replace_the_registered_lifetime(self):
        target=route();target.wait=lambda fn,label:fn();samples=iter([[native()],[native(stableId='99')]])
        target.session.data=lambda *args:next(samples)
        with patch.object(held_route.helper_setup,'allow_closes',side_effect=append):
            with self.assertRaisesRegex(RuntimeError,'changed before partial'):target.register_partial()
        self.assertEqual(len(target.config['allowed']),1)

class Transport(unittest.TestCase):
    def test_primary_ast_and_full_source_hash_authority(self):
        source=transport_check.SOURCE;actual=hashlib.sha256(source.read_bytes()).hexdigest()
        self.assertTrue(transport_check.verify_authority({str(source):actual}))
        with self.assertRaises(RuntimeError):transport_check.verify_authority({str(source):'0'*64})

    def test_required_real_markers_and_all_forbidden_diagnostics(self):
        text='Private AQ_BACKENDS=wayland: mandatory parent, no DRM or libseat backend\nOutput WAYLAND-1: configure surface with 1600'
        self.assertTrue(transport_check.transport_log_gate([text])['passed'])
        self.assertFalse(transport_check.transport_log_gate(['Output WAYLAND-1: configure surface with 1600'])['passed'])
        for problem in ('[libseat]','DRM Backend failed','Starting the DRM backend','enabling fallbacks','error 7:','Broken pipe','parent transport failed','xdg_surface was never configured'):
            self.assertFalse(transport_check.transport_log_gate([text,problem])['passed'])

if __name__=='__main__':unittest.main(verbosity=2)
