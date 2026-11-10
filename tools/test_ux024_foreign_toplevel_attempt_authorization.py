#!/usr/bin/env python3
"""Pure fixed authorization controls; no subprocess, socket or native effects."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch, MagicMock
import ux024_foreign_toplevel_attempt_authorization as a


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AttemptAuthorizationControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.core = load(a.CORE, 'test_attempt_core')
        self.base = load(a.BASE, 'test_attempt_base')
        self.now = 2000000000000000000
        self.expiry = '2033-05-18T03:35:00Z'
        self.record = {'schema': 1, 'owner': 'fixture', 'workflowPolicy': 2, 'startedUTC': '2033-05-18T03:30:00Z',
                       'delivery': {'authorizationExpiresUTC': '2033-05-18T03:33:00Z',
                                    'events': [{'kind': 'authorization-renewed', 'eventId': 'r1',
                                                'authorizationExpiresUTC': self.expiry,
                                                'atUTC': '2033-05-18T03:33:10Z', 'evidence': {'path': 'renewal', 'sha256': '1'*64}}]}}
        self.goal = {'threadId': 'existing-thread', 'createdAt': 1999999000, 'objective': 'Finish the original governed task', 'status': 'active'}
        self.evidence = {'startedUTC': self.record['startedUTC'], 'goalObservation': {'path': 'goal', 'sha256': '2'*64}}
        self.goal_receipt = {'status': 'active', 'threadId': 'existing-thread', 'actualRPC': {'goalResponse': {'result': {'goal': self.goal}}}}
        patcher = patch.object(self.core, 'delivery_ref', side_effect=lambda root, ref: json.dumps(self.evidence if ref['path']=='renewal' else self.goal_receipt))
        patcher.start(); self.addCleanup(patcher.stop)
        self.identity = self.core.record_identity(self.record, a.RECORD)
        self.body = {'schema': 1, 'kind': 'ux003-current-attempt-authorization',
                     'recordPath': a.RECORD, 'recordIdentitySha256': self.identity,
                     'participantStartedUTC': self.record['startedUTC'],
                     'goalDefinition': {'threadId': self.goal['threadId'], 'createdAt': self.goal['createdAt'], 'objectiveSha256': hashlib.sha256(self.goal['objective'].encode()).hexdigest()},
                     'selectionGeneration': 17, 'authorizationExpiresUTC': self.expiry,
                     'authorizationEventSha256': self.core.json_sha256(self.record['delivery']['events'][-1]),
                     'coreSha256': hashlib.sha256(Path(a.CORE).read_bytes()).hexdigest()}
        self.path = Path(self.tmp.name) / 'authorization.json'

    def write(self):
        self.path.write_text(json.dumps(self.body))
        self.path.chmod(0o600)
        return {'path': str(self.path), 'sha256': hashlib.sha256(self.path.read_bytes()).hexdigest()}

    def resolve(self):
        with patch.object(a.time, 'time_ns', return_value=self.now):
            return a.resolve_authorization(self.write(), self.record, self.identity, 17, self.core)

    def clock(self, authority):
        return a.seal_clock({'origin': 100, 'last': 100, 'deadline': 28000000100, 'boot': 'boot'}, authority)

    def test_current_canonical_authorization_resolves(self):
        result = self.resolve()
        self.assertEqual(result.expires_utc, self.expiry)
        self.assertGreater(result.expires_ns, self.now + 30000000000)

    def test_goal_definition_and_participant_binding_refuse_drift(self):
        for field, value in [('createdAt', 1999999001), ('objectiveSha256', '0'*64), ('threadId', 'other')]:
            original = dict(self.body['goalDefinition']); self.body['goalDefinition'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): self.resolve()
            self.body['goalDefinition'] = original
        self.body['participantStartedUTC'] = '2033-05-18T03:30:01Z'
        with self.assertRaises(ValueError): self.resolve()

    def test_missing_or_inactive_canonical_goal_evidence_refuses(self):
        self.goal['status'] = 'paused'
        with self.assertRaises(ValueError): self.resolve()
        self.goal['status'] = 'active'; del self.goal['createdAt']
        with self.assertRaises((ValueError, KeyError)): self.resolve()

    def test_goal_usage_updates_do_not_change_stable_definition(self):
        before = self.resolve()
        self.goal.update(updatedAt=123456, tokensUsed=987654, timeUsedSeconds=50)
        after = self.resolve()
        self.assertEqual(before.goal_definition, after.goal_definition)

    def test_exact_data_hash_required(self):
        ref = self.write(); ref['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            a.resolve_authorization(ref, self.record, self.identity, 17, self.core)

    def test_unknown_fields_wrong_identity_selection_and_core_refuse(self):
        for field, value in [('extra', True), ('recordPath', 'other'),
                             ('recordIdentitySha256', '0' * 64), ('selectionGeneration', True),
                             ('selectionGeneration', 18), ('coreSha256', '0' * 64)]:
            original = copy.deepcopy(self.body); self.body[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError): self.resolve()
            self.body = original

    def test_current_event_and_effective_expiry_must_match(self):
        for field, value in [('authorizationEventSha256', '0' * 64),
                             ('authorizationExpiresUTC', '2033-05-18T03:36:00Z')]:
            original = dict(self.body); self.body[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): self.resolve()
            self.body = original

    def test_expired_and_insufficient_window_refuse(self):
        good = self.resolve()
        for now in [good.expires_ns, good.expires_ns - 30000000000]:
            with patch.object(a.time, 'time_ns', return_value=now), self.assertRaises(TimeoutError):
                a.resolve_authorization(self.write(), self.record, self.identity, 17, self.core)

    def test_symlink_and_duplicate_json_refuse(self):
        ref = self.write(); link = self.path.with_name('link'); link.symlink_to(self.path)
        with self.assertRaises(ValueError): a.resolve_authorization(dict(ref, path=str(link)), self.record, self.identity, 17, self.core)
        self.path.write_text('{"schema":1,"schema":1}')
        ref['sha256'] = hashlib.sha256(self.path.read_bytes()).hexdigest()
        with self.assertRaises(ValueError): a.resolve_authorization(ref, self.record, self.identity, 17, self.core)

    def test_issued_authority_is_immutable_and_data_change_does_not_extend(self):
        authority = self.resolve(); clock = self.clock(authority)
        self.body['authorizationExpiresUTC'] = '2034-01-01T00:00:00Z'; self.write()
        self.assertEqual(a.authorization_deadline_ns(clock), authority.expires_ns)
        with self.assertRaises((AttributeError, TypeError)): authority.expires_ns += 100
        with self.assertRaises((AttributeError, TypeError)): clock._authority = None

    def test_copied_clock_retains_seal_and_deadline(self):
        clock = self.clock(self.resolve()); copied = clock.copy()
        self.assertEqual(a.authorization_deadline_ns(copied), a.authorization_deadline_ns(clock))
        self.assertEqual(copied['deadline'], clock['deadline'])
        with self.assertRaises(ValueError): a.authorization_deadline_ns(dict(clock))

    def test_clock_extension_and_reboot_refuse(self):
        authority = self.resolve(); effect = a.effect_base(self.base, authority)
        for field, value in [('deadline', 29000000100), ('origin', 0), ('boot', 'foreign'),
                             ('authorizationExpiresNs', authority.expires_ns + 1)]:
            clock = self.clock(authority); clock[field] = value
            with self.subTest(field=field), patch.object(a.time, 'time_ns', return_value=self.now), self.assertRaises(ValueError): effect.left(clock)

    def test_effect_left_uses_sealed_horizon_not_old_base_expiry(self):
        authority = self.resolve(); effect = a.effect_base(self.base, authority); clock = self.clock(authority)
        with patch.object(a.time, 'time_ns', return_value=self.now), patch.object(a.time, 'monotonic_ns', return_value=101), patch.object(a, '_boot', return_value='boot'), patch.object(self.base, 'left', side_effect=AssertionError('old left reached')):
            self.assertGreater(effect.left(clock), 0)
        with patch.object(a.time, 'time_ns', return_value=authority.expires_ns), self.assertRaises(TimeoutError): effect.left(clock)

    def test_unsealed_or_different_authority_clock_refuses(self):
        authority = self.resolve(); effect = a.effect_base(self.base, authority)
        with self.assertRaises(ValueError): effect.left({'deadline': 9, 'last': 0, 'boot': 'boot'})
        self.record['delivery']['events'][-1]['eventId'] = 'r2'
        self.body['authorizationEventSha256'] = self.core.json_sha256(self.record['delivery']['events'][-1])
        other = self.resolve()
        with self.assertRaises(ValueError): effect.left(self.clock(other))

    def test_registry_uses_adapter_left_before_connect(self):
        authority = self.resolve(); effect = a.effect_base(self.base, authority); clock = self.clock(authority)
        path = MagicMock(); info = MagicMock(st_mode=0o140600, st_uid=a.os.getuid()); path.lstat.return_value = info
        sock = MagicMock()
        with patch.object(self.base, 'check_process'), patch.object(a.socket, 'socket', return_value=sock), patch.object(a.time, 'time_ns', return_value=authority.expires_ns), self.assertRaises(TimeoutError):
            effect.registry(path, MagicMock(pid=12), 'birth', 'hash', clock)
        sock.__enter__.return_value.connect.assert_not_called()

    def test_old_main_and_expiry_are_not_delegated(self):
        effect = a.effect_base(self.base, self.resolve())
        for name in ['main', 'EXPIRES', 'packet_shape', 'registry_unknown']:
            with self.subTest(name=name), self.assertRaises(AttributeError): getattr(effect, name)
        self.assertIs(effect.check_process, self.base.check_process)

    def test_budget_is_original_28_seconds_not_new_clock(self):
        authority = self.resolve()
        with self.assertRaises(ValueError): a.seal_clock({'origin': 100, 'last': 100, 'deadline': 30000000100, 'boot': 'boot'}, authority)
        clock = self.clock(authority); self.assertEqual(clock['origin'], 100)


class ActualToolGoalControls(unittest.TestCase):
    write=AttemptAuthorizationControls.write
    resolve=AttemptAuthorizationControls.resolve
    def setUp(self):
        AttemptAuthorizationControls.setUp(self)
        self.goal_receipt.clear()
        self.goal_receipt.update(status='active',thread=self.goal['threadId'],objective=self.goal['objective'])
        self.tool={'actualToolResponse':{'goal':dict(self.goal)}}
        self.tool_path=Path(self.tmp.name)/'actual-tool-goal.json'
        self.pin_tool()
    def pin_tool(self):
        self.tool_path.write_text(json.dumps(self.tool));self.tool_path.chmod(0o600)
        self.body['goalObservation']={'path':str(self.tool_path),'sha256':hashlib.sha256(self.tool_path.read_bytes()).hexdigest()}
    def test_actual_tool_goal_and_unchanged_canonical_receipt_resolve(self):
        self.assertEqual(self.resolve().expires_utc,self.expiry)
        self.assertNotIn('actualRPC',self.goal_receipt)
    def test_wrong_actual_reference_hash_refuses(self):
        self.body['goalObservation']['sha256']='0'*64
        with self.assertRaises(ValueError):self.resolve()
    def test_wrong_thread_refuses(self):
        self.tool['actualToolResponse']['goal']['threadId']='foreign';self.pin_tool()
        with self.assertRaises(ValueError):self.resolve()
    def test_wrong_objective_refuses(self):
        self.tool['actualToolResponse']['goal']['objective']='foreign';self.pin_tool()
        with self.assertRaises(ValueError):self.resolve()
    def test_inactive_actual_goal_refuses(self):
        self.tool['actualToolResponse']['goal']['status']='paused';self.pin_tool()
        with self.assertRaises(ValueError):self.resolve()
    def test_inactive_canonical_goal_refuses(self):
        self.goal_receipt['status']='paused'
        with self.assertRaises(ValueError):self.resolve()
    def test_missing_created_at_refuses(self):
        del self.tool['actualToolResponse']['goal']['createdAt'];self.pin_tool()
        with self.assertRaises(ValueError):self.resolve()
    def test_wrong_participant_start_refuses(self):
        self.body['participantStartedUTC']='2033-05-18T03:30:01Z'
        with self.assertRaises(ValueError):self.resolve()
    def test_wrong_canonical_event_refuses(self):
        self.body['authorizationEventSha256']='0'*64
        with self.assertRaises(ValueError):self.resolve()
    def test_wrong_horizon_refuses(self):
        self.body['authorizationExpiresUTC']='2033-05-18T04:00:00Z'
        with self.assertRaises(ValueError):self.resolve()




class InitialStartAuthorizationControls(unittest.TestCase):
    write=AttemptAuthorizationControls.write
    resolve=AttemptAuthorizationControls.resolve
    clock=AttemptAuthorizationControls.clock
    def setUp(self):
        AttemptAuthorizationControls.setUp(self)
        self.record['delivery']['events']=[]
        self.record['delivery']['authorizationExpiresUTC']=self.expiry
        self.record['delivery']['clockOrigin']={'utc':self.record['startedUTC'],'bootId':'original-boot','monotonicNs':10,'boottimeNs':11}
        self.body['kind']='ux024-initial-attempt-authorization';self.body.pop('authorizationEventSha256')
        self.body['initialAuthorization']={'recordIdentitySha256':self.identity,'participantStartedUTC':self.record['startedUTC'],'authorizationExpiresUTC':self.expiry,'clockOrigin':copy.deepcopy(self.record['delivery']['clockOrigin'])}
        self.body['initialAuthorizationSha256']=self.core.json_sha256(self.body['initialAuthorization'])
        self.tool={'observedUTC':a.datetime.fromtimestamp(self.now/1e9,a.timezone.utc).isoformat().replace('+00:00','Z'),'actualToolResponse':{'goal':copy.deepcopy(self.goal)}}
        self.goal_path=Path(self.tmp.name)/'actual-goal.json';self.pin_goal()
    def pin_goal(self):
        self.goal_path.write_text(json.dumps(self.tool));self.goal_path.chmod(0o600)
        self.body['goalObservation']={'path':str(self.goal_path),'sha256':hashlib.sha256(self.goal_path.read_bytes()).hexdigest()}
    def test_actual_initial_start_authorization_without_fake_event(self):
        result=self.resolve()
        self.assertEqual(result.origin_kind,'initial');self.assertEqual(result.event_sha256,'')
        self.assertEqual(result.initial_sha256,self.body['initialAuthorizationSha256'])
        self.assertEqual(self.record['delivery']['events'],[])
        self.assertEqual(a.authorization_deadline_ns(self.clock(result)),result.expires_ns)
    def test_initial_refuses_any_renewal_including_expired(self):
        for expiry in ['2030-01-01T00:00:00Z',self.expiry]:
            self.record['delivery']['events']=[{'kind':'authorization-renewed','authorizationExpiresUTC':expiry}]
            with self.assertRaises(ValueError):self.resolve()
    def test_initial_exact_start_clock_and_identity(self):
        for field,value in [('participantStartedUTC','foreign'),('recordIdentitySha256','0'*64),('authorizationExpiresUTC','2034-01-01T00:00:00Z'),('clockOrigin',dict(self.record['delivery']['clockOrigin'],monotonicNs=12))]:
            before=copy.deepcopy(self.body);self.body['initialAuthorization'][field]=value
            self.body['initialAuthorizationSha256']=self.core.json_sha256(self.body['initialAuthorization'])
            with self.assertRaises(ValueError):self.resolve()
            self.body=before
    def test_initial_pin_and_no_silent_renewal_schema_fallback(self):
        self.body['initialAuthorizationSha256']='0'*64
        with self.assertRaises(ValueError):self.resolve()
        self.body.pop('initialAuthorization');self.body.pop('initialAuthorizationSha256');self.body['kind']='ux003-current-attempt-authorization';self.body['authorizationEventSha256']='0'*64
        with self.assertRaises(ValueError):self.resolve()
    def test_initial_requires_actual_active_goal_without_static_age_gate(self):
        for change in ['paused','missingactual']:
            before=copy.deepcopy(self.tool)
            if change=='paused':self.tool['actualToolResponse']['goal']['status']='paused'
            if change=='missingactual':self.tool.pop('actualToolResponse')
            self.pin_goal()
            with self.assertRaises(ValueError):self.resolve()
            self.tool=before;self.pin_goal()
        self.tool['observedUTC']=a.datetime.fromtimestamp(self.now/1e9-86400,a.timezone.utc).isoformat().replace('+00:00','Z');self.pin_goal()
        self.assertEqual(self.resolve().origin_kind,'initial')
    def test_initial_goal_definition_and_typed_creation_pin(self):
        for field,value in [('threadId','foreign'),('objectiveSha256','0'*64),('createdAt',True)]:
            before=copy.deepcopy(self.body['goalDefinition']);self.body['goalDefinition'][field]=value
            with self.assertRaises(ValueError):self.resolve()
            self.body['goalDefinition']=before
    def test_initial_expiry_and_unknown_fields_do_not_expand_authority(self):
        self.body['authorizationExpiresUTC']='2034-01-01T00:00:00Z'
        with self.assertRaises(ValueError):self.resolve()
        self.body['authorizationExpiresUTC']=self.expiry;self.body['authorizationEventSha256']='0'*64
        with self.assertRaises(ValueError):self.resolve()
    def test_initial_expired_window_and_sealed_clock_still_refuse(self):
        good=self.resolve()
        with patch.object(a.time,'time_ns',return_value=good.expires_ns):
            with self.assertRaises(TimeoutError):a.resolve_authorization(self.write(),self.record,self.identity,17,self.core)
        clock=self.clock(good);clock['deadline']+=1
        with self.assertRaises(ValueError):a.authorization_deadline_ns(clock)

if __name__ == '__main__':
    unittest.main()
