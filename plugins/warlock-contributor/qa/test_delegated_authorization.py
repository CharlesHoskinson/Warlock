"""Literal delegated-renewal controls. Root qualifies; author has not run these."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from test_delivery_flow import engine


class DelegatedAuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.module = engine()
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.record = {'workflowPolicy': 2, '_recordPath': '.warlock-contributor/test.json',
                       'owner': 'root', 'startedUTC': '2026-01-01T00:00:00Z',
                       'delivery': {'schema': 1, 'journey': 'test', 'clockOrigin': {'utc': '2026-01-01T00:00:00Z'},
                                    'authorizationExpiresUTC': '2026-01-01T02:00:00Z', 'guardHashes': {},
                                    'events': [{'kind': 'execution-started', 'sequence': 1}]}}
        self.identity = self.module.json_sha256(self.module.delivery_identity(self.record))
        self.grant = {'schema': 1, 'kind': 'actual-human-standing-orchestration-delegation',
                      'threadId': 'thread', 'actualHumanText': 'Run AFK. Have the existing delegate make routine calls.',
                      'observedAfterApprovalUTC': '2026-01-01T00:00:00Z'}
        self.grantref = self.ref('human', self.grant)
        self.scopes = {'root': {'did': 'existing-did', 'run': 'same-run', 'agent': 'root', 'role': 'lead',
                                'pair': None, 'channels': ['x'], 'claims': ['y'], 'standing': []}}
        self.definition = {'threadId': 'thread', 'createdAt': 1, 'objectiveSha256': 'a'*64}
        self.policy = {'schema': 1, 'kind': 'delegate-operating-renewal-policy',
                       'attribution': 'model-operating-policy-not-human-terms', 'humanDelegation': self.grantref,
                       'maxExtensionSeconds': 7200, 'noAttemptWindowsLimit': 2,
                       'notAfterUTC': '2026-01-02T00:00:00Z', 'delegateSession': 'existing-session',
                       'delegateModel': 'claude-opus-5-5', 'goalDefinition': self.definition,
                       'identityScopeBaseline': self.ref('baseline-scopes', self.scopes),
                       'actualPolicyDecision': self.ref('actual-policy', {'approved': True}),
                       'rootDisposition': self.ref('policy-disposition', {'disposition': 'accepted'})}
        self.request = {'schema': 1, 'requestId': 'renewal-one', 'decisionKind': 'window-selection',
                        'humanDelegationSha256': self.grantref['sha256'], 'question': 'Renew this same bounded work?',
                        'choices': [{'id': 'extend', 'payload': {'proposedUntilUTC': '2026-01-01T03:00:00Z'}}]}
        self.answer = {'schema': 1, 'requestId': self.request['requestId'],
                       'requestSha256': self.module.json_sha256(self.request),
                       'humanDelegationSha256': self.grantref['sha256'], 'decisionKind': 'window-selection',
                       'choiceId': 'extend', 'rationale': 'Continue the actual protected attempt.'}
        self.terminal = {'completed': True, 'exit': 0, 'failure': None, 'cleanupErrors': [], 'timedOut': False,
                         'resolvedModels': ['claude-opus-5-5'],
                         'actualResult': {'is_error': False, 'session_id': 'existing-session', 'result': json.dumps(self.answer)}}
        self.decision = dict(self.answer, selectedChoice=self.request['choices'][0], nativeAuthorized=False,
                             changesAuthority=False, rootMustValidateAuthority=True, rootSoleExecutor=True,
                             decisionId='decision-50', turn=50, session='existing-session',
                             operatingAuthorizationExpiresUTC='2026-01-01T02:00:00Z',
                             actualTerminal=self.ref('terminal', self.terminal))
        self.goal = {'schema': 1, 'status': 'active', 'observedUTC': '2026-01-01T01:00:01Z',
                     'goalDefinition': self.definition, 'humanPaused': False, 'humanHandoff': False,
                     'stopRequested': False}
        self.evidence = {'schema': 1, 'kind': 'human-delegated-authorization-renewal',
                         'recordPath': self.record['_recordPath'], 'owner': 'root', 'startedUTC': self.record['startedUTC'],
                         'deliveryIdentitySha256': self.identity, 'previousExpiresUTC': '2026-01-01T02:00:00Z',
                         'authorizationExpiresUTC': '2026-01-01T03:00:00Z', 'authorizedUTC': '2026-01-01T01:00:00Z',
                         'humanDelegation': self.grantref}
        self.event = {'kind': 'authorization-renewed', 'sequence': 2, 'atUTC': '2026-01-01T01:00:02Z',
                      'authorizationExpiresUTC': self.evidence['authorizationExpiresUTC']}

    def ref(self, name, value):
        p=self.root/(name+'.json'); p.write_text(json.dumps(value));
        return {'path': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

    def refresh(self):
        self.evidence['operatingPolicy'] = self.ref('policy', self.policy)
        self.evidence['policyReview'] = self.ref('review', {'schema': 1, 'scope': 'standing-delegated-renewal-policy',
            'disposition': 'accepted', 'reviewer': 'independent-peer', 'policySha256': self.evidence['operatingPolicy']['sha256'],
            'humanDelegationSha256': self.grantref['sha256']})
        self.evidence['decisionRequest'] = self.ref('request', self.request)
        self.evidence['delegateDecision'] = self.ref('decision', self.decision)
        self.evidence['goalObservation'] = self.ref('goal', self.goal)
        self.evidence['identityScopes'] = self.ref('current-scopes', self.scopes)
        self.event['evidence'] = self.ref('evidence', self.evidence)

    def validate(self):
        self.refresh()
        return self.module.validate_authorization_renewal(self.root,self.record,self.event,
            self.evidence['previousExpiresUTC'],None)

    def test_actual_delegated_decision_accepts_without_human_impersonation(self):
        self.assertEqual(self.validate(),self.evidence['authorizedUTC'])
        self.assertNotIn('humanRequest',self.evidence)

    def test_wrong_record_scope_prior_and_goal_refuse(self):
        for field,value in [('recordPath','other'),('owner','other'),('deliveryIdentitySha256','0'*64),('startedUTC','other')]:
            before=copy.deepcopy(self.evidence);self.evidence[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError): self.validate()
            self.evidence=before
        self.goal['goalDefinition']=dict(self.definition,createdAt=2)
        with self.assertRaises(ValueError):self.validate()

    def test_paused_handoff_stop_and_inactive_goal_refuse(self):
        for field,value in [('humanPaused',True),('humanHandoff',True),('stopRequested',True),('status','paused')]:
            before=dict(self.goal);self.goal[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):self.validate()
            self.goal=before

    def test_uncompleted_wrong_model_or_session_response_refuses(self):
        for field,value in [('completed',False),('exit',1),('timedOut',True),('resolvedModels',['other'])]:
            old=copy.deepcopy(self.terminal);self.terminal[field]=value
            self.decision['actualTerminal']=self.ref('terminal',self.terminal)
            with self.subTest(field=field),self.assertRaises(ValueError):self.validate()
            self.terminal=old
        self.decision['actualTerminal']=self.ref('terminal',self.terminal)
        self.decision['session']='other'
        with self.assertRaises(ValueError):self.validate()

    def test_request_or_actual_response_mismatch_refuses(self):
        self.request['question']='changed after response'
        with self.assertRaises(ValueError):self.validate()
        self.request['question']='Renew this same bounded work?'
        self.terminal['actualResult']['result']=json.dumps(dict(self.answer,choiceId='invented'))
        self.decision['actualTerminal']=self.ref('terminal',self.terminal)
        with self.assertRaises(ValueError):self.validate()

    def test_more_than_two_hours_and_delegate_cap_refuse(self):
        for key,value in [('maxExtensionSeconds',7201),('notAfterUTC','2026-01-02T00:00:01Z')]:
            before=dict(self.policy);self.policy[key]=value
            with self.subTest(field=key),self.assertRaises(ValueError):self.validate()
            self.policy=before
        self.evidence['authorizedUTC']='2026-01-01T00:59:59Z'
        with self.assertRaises(ValueError):self.validate()

    def test_model_or_queued_message_cannot_be_human_grant(self):
        self.grant['kind']='model-delegation';self.grantref=self.ref('human',self.grant)
        self.evidence['humanDelegation']=self.grantref
        with self.assertRaises(ValueError):self.validate()

    def test_one_no_attempt_window_requires_recorded_blocker(self):
        self.record['delivery']['events']=[];self.event['sequence']=1
        with self.assertRaises(ValueError):self.validate()
        self.record['delivery']['events']=[{'kind':'deferred','sequence':1,'reason':'Actual pinned preflight failure'}]
        self.event['sequence']=2
        self.assertEqual(self.validate(),self.evidence['authorizedUTC'])

    def test_two_consecutive_no_attempt_windows_refuse_even_with_blocker(self):
        self.record['delivery']['events']=[{'kind':'deferred','sequence':1,'reason':'first blocker'},
            {'kind':'authorization-renewed','sequence':2}, {'kind':'deferred','sequence':3,'reason':'second blocker'}]
        self.event['sequence']=4
        with self.assertRaises(ValueError):self.validate()

    def test_scope_widening_or_new_identity_refuses(self):
        self.scopes['root']['claims'].append('new')
        with self.assertRaises(ValueError):self.validate()

    def test_later_events_cannot_rewrite_historical_window_evidence(self):
        self.record['delivery']['events'].append({'kind':'authorization-renewed','sequence':3})
        self.assertEqual(self.validate(),self.evidence['authorizedUTC'])

    def test_reused_decision_authorization_time_refuses(self):
        self.refresh()
        with self.assertRaises(ValueError):self.module.validate_authorization_renewal(self.root,self.record,self.event,
            self.evidence['previousExpiresUTC'],self.evidence['authorizedUTC'])


if __name__=='__main__':unittest.main()
