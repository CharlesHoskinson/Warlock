"""Explicit workflow-package custody candidates; no product/native authority."""
import copy
import datetime as dt
import hashlib
import json
import os
import unittest
from unittest import mock

import test_support_actor_binding as actors

policy = actors.policy


class WorkflowPackageCustodyTests(unittest.TestCase):
    def setUp(self):
        self.case = actors.GenericSupportActorBindingTests('test_generic_binding_keeps_record_identity_and_actual_actor')
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.support = self.case.case
        self.repo = self.support.repo
        # Restore support docs so this test changes only workflow-package paths.
        for name in self.support.names:
            if name == policy.STATE:
                state = json.loads((self.repo / name).read_text())
                state['supportNote'] = 'captured owner work'
                self.support.fixture.write(name, state)
            else:
                self.support.fixture.write(name, 'captured owner work\n')
        self.names = ['plugins/warlock-contributor/scripts/warlock.py',
                      'plugins/warlock-contributor/README.md',
                      'docs/warlock-build-loop/v2/INSTRUCTIONS.md']
        # Construct an old record that already captured unrelated package work.
        # Neither binding application nor replay may rewrite that record.
        record = json.loads(self.support.original)
        for name in self.names:
            self.support.fixture.write(name, 'captured workflow draft\n')
            record['foreignDirty'][name] = policy.fingerprint(self.repo, name)
        self.support.fixture.write(self.support.path, record)
        self.support.fixture.refresh_fixture_participant_index()
        self.support.original = (self.repo / self.support.path).read_bytes()
        self.support.record = dict(record, _recordPath=self.support.path)
        self.support.names = self.names
        for name in self.names:
            self.support.fixture.write(name, 'reviewed workflow successor\n')
        self.support.reqs, self.support.state = policy.context(self.repo)

    def prepare(self):
        # Build the existing support artifacts first, then explicitly add the
        # stronger purpose and independently reviewed authorization references.
        entries, args, proof = self.case.prepare()
        prefix = policy.SUPPORT_EVIDENCE + str(self.support.counter) + '-workflow-'
        instruction = 'Update this workflow package; preserve product and native gates.'
        auth = dict(schema=1, source='Actual human message in existing root thread',
            observedUTC=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(seconds=2)).isoformat(),
            thread='fixture-human-thread', instruction=instruction,
            instructionSha256=hashlib.sha256(instruction.encode()).hexdigest(),
            scope='Workflow package correction', previousPauseSupersededForThisWork=True,
            oldWindowsNotExtended=True, oldHistoryNotReset=True, noAcceptanceInferred=True)
        auth_path = prefix+'human.json'; self.support.fixture.write(auth_path, auth)
        source = dict(schema=1, purpose='workflow-package', files={n:dict(
            capturedSha256=self.support.record['foreignDirty'][n],
            previousSha256=self.support.record['foreignDirty'][n],
            currentSha256=policy.fingerprint(self.repo,n)) for n in self.names})
        manifest_path=prefix+'source.json';self.support.fixture.write(manifest_path,source)
        proof['actorBinding'].update(purpose='workflow-package',
            humanAuthorization={'path':auth_path,'sha256':policy.digest(self.repo/auth_path)},
            sourceManifest={'path':manifest_path,'sha256':policy.digest(self.repo/manifest_path)})
        self.refresh(entries,proof)
        return entries,args,proof

    def refresh(self,entries,proof):
        self.support.fixture.write(entries[0]['claimProof'],proof)
        for e in entries:
            review=policy.read(self.repo/e['reviewFile'])
            b=proof['actorBinding']
            review.update(actorBindingSha256=policy.json_sha256(b),
                claimProofSha256=policy.digest(self.repo/e['claimProof']),
                bindingPurpose='workflow-package', workflowPackageAuthorized=True,
                runtimeAuthorization=False, humanAuthorization=b['humanAuthorization'],
                sourceManifest=b['sourceManifest'])
            self.support.fixture.write(e['reviewFile'],review)

    def apply(self,args):
        return self.case.apply(args)

    def test_explicit_package_binding_preserves_participant_and_sidecar_prefix(self):
        entries,args,proof=self.prepare()
        identity=policy.record_identity(self.support.record,self.support.path)
        self.apply(args)
        self.support.assert_unchanged()
        self.assertEqual(policy.record_identity(self.support.record,self.support.path),identity)
        sidecar=policy.read(policy.support_sidecar(self.repo,self.support.record))
        self.assertEqual(len(sidecar['events']),3)
        self.assertEqual(sidecar['custodyBaseline']['foreignDirty'],self.support.record['foreignDirty'])
        with mock.patch.object(policy,'support_live_claims',side_effect=AssertionError('offline replay')):
            overlay,errors,_=policy.support_reconciliations(self.repo,self.support.record)
        self.assertEqual(errors,[])
        self.assertEqual(set(overlay),set(self.names))

    def test_metadata_binding_cannot_authorize_package_code(self):
        entries,args,proof=self.prepare()
        for key in ('purpose','humanAuthorization','sourceManifest'):proof['actorBinding'].pop(key)
        self.support.fixture.write(entries[0]['claimProof'],proof)
        with self.assertRaises(ValueError):self.apply(args)
        self.assertFalse(policy.support_sidecar(self.repo,self.support.record).exists())

    def test_missing_forged_or_model_authorization_rejected(self):
        for change in ('missing','hash','model','false-no-acceptance','future'):
            entries,args,proof=self.prepare();ref=proof['actorBinding']['humanAuthorization'];a=policy.read(self.repo/ref['path'])
            if change=='missing':(self.repo/ref['path']).unlink()
            elif change=='hash':ref['sha256']='0'*64
            else:
                if change=='model':a['source']='Model decision'
                elif change=='false-no-acceptance':a['noAcceptanceInferred']=False
                else:a['observedUTC']='2999-01-01T00:00:00+00:00'
                self.support.fixture.write(ref['path'],a);ref['sha256']=policy.digest(self.repo/ref['path'])
            self.refresh(entries,proof)
            with self.subTest(change=change),self.assertRaises((ValueError,OSError)):self.apply(args)
        self.support.assert_unchanged()

    def test_false_independent_authority_or_runtime_waiver_rejected(self):
        for field,value in [('workflowPackageAuthorized',False),('runtimeAuthorization',True),('bindingPurpose','metadata')]:
            entries,args,_=self.prepare();r=policy.read(self.repo/entries[0]['reviewFile']);r[field]=value
            self.support.fixture.write(entries[0]['reviewFile'],r)
            with self.subTest(field=field),self.assertRaises(ValueError):self.apply(args)

    def test_wrong_source_hash_extra_path_and_unbound_review_rejected(self):
        for change in ('capture','before','after','extra','review'):
            entries,args,proof=self.prepare();ref=proof['actorBinding']['sourceManifest'];s=policy.read(self.repo/ref['path'])
            if change=='capture':s['files'][self.names[0]]['capturedSha256']='0'*64
            elif change=='before':s['files'][self.names[0]]['previousSha256']='0'*64
            elif change=='after':s['files'][self.names[0]]['currentSha256']='0'*64
            elif change=='extra':s['files']['plugins/warlock-contributor/extra.py']=dict(s['files'][self.names[0]])
            else:
                r=policy.read(self.repo/entries[0]['reviewFile']);r.pop('sourceManifest');self.support.fixture.write(entries[0]['reviewFile'],r)
            if change!='review':
                self.support.fixture.write(ref['path'],s);ref['sha256']=policy.digest(self.repo/ref['path']);self.refresh(entries,proof)
            with self.subTest(change=change),self.assertRaises(ValueError):self.apply(args)

    def test_product_launchers_registers_tools_and_path_traversal_refused(self):
        for name in ['implementation/warlock/src/Desktop.elm','window-integration-qa/qa_run.py',
                'window-integration-qa/qa_launch.py',policy.BASE,'tools/root_bundle.py',
                'plugins/warlock-contributor/../../runtime.py','docs/other/INSTRUCTIONS.md',
                'plugins/warlock-contributor/.git/config']:
            with self.subTest(name=name):self.assertFalse(policy.workflow_package_path(name))
        self.assertTrue(policy.workflow_package_path('plugins/warlock-contributor/scripts/warlock.py'))
        self.assertTrue(policy.workflow_package_path('AGENTS.md'))
        self.assertTrue(policy.workflow_package_path('docs/warlock-build-loop/v2/INSTRUCTIONS.md'))

    def test_missing_wrong_live_claim_or_did_still_refuses(self):
        _,args,_=self.prepare();good=copy.deepcopy(self.support.live)
        for rows in [[],good[1:],[dict(x,holder_did='did:key:zOther') for x in good]]:
            self.support.live=rows
            with self.assertRaises(ValueError):self.apply(args)
        self.support.assert_unchanged()

    def test_human_or_manifest_change_after_live_probe_is_refused(self):
        entries,args,proof=self.prepare()
        def changed(*unused):
            (self.repo/proof['actorBinding']['humanAuthorization']['path']).write_text('{}\n')
            return self.support.live
        with mock.patch.dict(os.environ,AGENTBUS_AGENT=self.case.actor,AGENTBUS_RUN='fixture-run'),\
                mock.patch.object(policy,'support_live_claims',side_effect=changed),self.assertRaises(ValueError):
            policy.reconcile_support(self.repo,self.support.record,self.support.reqs,self.support.state,args)
        self.assertFalse(policy.support_sidecar(self.repo,self.support.record).exists())
        self.support.assert_unchanged()
