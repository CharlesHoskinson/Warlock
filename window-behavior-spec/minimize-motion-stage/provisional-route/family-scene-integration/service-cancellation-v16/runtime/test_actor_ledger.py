"""Real CPU groups, sealed Keeper source, lease files and fsynced ledgers.

The synthetic scene journal supplies protocol inputs only. It does not simulate
native return authority or claim a desktop cancellation implementation.
"""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from helper_supervisor import Keeper
from keeper_actor_ledger import ActorLedger, digest, read_anchored
from owned_commands import SealedFile
from owned_launch import OwnedLaunch
from service_runtime import JournalStore, RuntimeLease


class ActorLedgerKernelTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.env = dict(os.environ, XDG_RUNTIME_DIR=str(self.root),
                        HYPRLAND_INSTANCE_SIGNATURE='actor-ledger-cpu',
                        WAYLAND_DISPLAY='never-connect')
        self.lease = RuntimeLease(self.root, self.env['HYPRLAND_INSTANCE_SIGNATURE'])
        self.store = JournalStore(self.root, self.lease.session)
        self.records = []
        self.actor_records = []
        self.keeper = Keeper(self.root, self.env, self.records.append,
                             actor_record=self.actor_records.append)
        self.launches = []
        self.intent = {
            'actor': 1, 'receipt': 7, 'token': '0123456789ab-1',
            'captured': ['0x11', '11', os.getpid()],
            'scope': [['0x11', '11', os.getpid()]],
            'lease': {'pid': self.lease.owner['pid'],
                      'start': self.lease.owner['start'],
                      'nonce': self.lease.nonce,
                      'rootIdentity': list(self.lease.root_identity),
                      'lockIdentity': list(self.lease.lock_identity),
                      'session': self.lease.session}}
        self.body = {
            'version': 1, 'session': self.lease.session, 'snapshot': 1,
            'pending': [], 'receipts': [[self.intent['captured'], 7]],
            'scenes': [{'actor': 1, 'token': self.intent['token'],
                        'requested': self.intent['captured'],
                        'members': self.intent['scope'],
                        'profile': {'managerReceipt': 7,
                                    'liveCancelIntent': deepcopy(self.intent),
                                    'liveCancelReserved': True}}]}
        self.store.write(self.body)

    def tearDown(self):
        for launch in self.launches:
            if launch.process.poll() is None:
                launch.process.communicate('', timeout=2)
            if not launch.closed:
                try:
                    launch.complete()
                except Exception:
                    pass  # Refused jobs remain in the actual Keeper inventory.
            for stream in (launch.process.stdin, launch.process.stdout,
                           launch.process.stderr):
                if stream is not None:
                    stream.close()
        if not self.keeper.closed:
            if self.keeper.process.poll() is None:
                self.keeper.detach()
            self.keeper.process.wait(timeout=5)
            self.keeper.process.stderr.close()
        self.lease.close()
        self.temporary.cleanup()

    def launch(self, actor=1, kind='helper', argv=None):
        with SealedFile('/usr/bin/cat') as executable:
            launch = OwnedLaunch(argv or ['/usr/bin/cat'], env=self.env,
                                 keeper=self.keeper, actor=actor, kind=kind,
                                 executable_fd=executable.fd,
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True)
        self.launches.append(launch)
        return launch

    def finish(self, launch):
        output, error = launch.process.communicate('CPU witness\n', timeout=2)
        self.assertEqual(output, 'CPU witness\n')
        self.assertEqual(launch.process.returncode, 0, error)
        launch.complete()

    def ledger(self):
        return read_anchored(self.root, self.keeper.identity,
                             'actor-ledger-' + self.keeper.nonce + '.json',
                             limit=8*1024*1024)

    def test_selected_actor_attests_while_other_actor_group_stays_live(self):
        selected = self.launch()
        other = self.launch(actor=2)
        first = self.keeper.freeze_actor(self.intent)
        with self.assertRaises(ValueError):
            self.keeper.attest_actor(1, first)
        self.assertIsNone(other.process.poll())
        self.finish(selected)
        with self.assertRaises(ValueError):
            self.keeper.attest_actor(1, first)
        current = self.keeper.actor_witness(1)
        self.assertEqual(current['jobCount'], 1)
        self.assertEqual(self.keeper.attest_actor(1, current), current)
        self.assertIsNone(other.process.poll())
        self.assertEqual(self.ledger()['jobs'][selected.job]['phase'], 'closed')
        self.assertEqual(self.ledger()['jobs'][other.job]['phase'], 'released')
        self.finish(other)
        self.keeper.stop()
        terminal = self.keeper.read_terminal()
        self.assertTrue(terminal['normalStop'])
        self.assertEqual(terminal['actorLedgerSHA256'], digest(self.ledger()))
        self.assertEqual(len(terminal['jobs']), 2)

    def test_frozen_actor_new_gate_refused_other_actor_still_runs(self):
        selected = self.launch()
        self.keeper.freeze_actor(self.intent)
        with self.assertRaises(ValueError):
            self.launch()
        self.assertIsNone(selected.process.poll())
        other = self.launch(actor=2)
        self.finish(selected)
        self.finish(other)
        self.keeper.stop()
        self.assertEqual(len(self.ledger()['jobs']), 2)

    def test_new_current_receipt_revokes_existing_witness(self):
        selected = self.launch()
        self.finish(selected)
        witness = self.keeper.freeze_actor(self.intent)
        self.body['snapshot'] += 1
        self.body['receipts'][0][1] = 8
        self.store.write(self.body)
        with self.assertRaises(ValueError):
            self.keeper.attest_actor(1, witness)
        self.assertFalse(self.keeper.closed)
        self.keeper.stop()

    def test_owner_nonce_replacement_refuses_without_whole_keeper_stop(self):
        selected = self.launch()
        self.finish(selected)
        witness = self.keeper.freeze_actor(self.intent)
        original = deepcopy(self.lease.owner)
        self.lease.owner['nonce'] = 'f'*32
        self.lease.publish_owner()
        try:
            with self.assertRaises(ValueError):
                self.keeper.attest_actor(1, witness)
            self.assertIsNone(self.keeper.process.poll())
        finally:
            self.lease.owner = original
            self.lease.publish_owner()
        self.assertEqual(self.keeper.attest_actor(1, witness), witness)
        self.keeper.stop()

    def test_complete_group_does_not_prove_native_semantic_return(self):
        selected = self.launch(kind='native-effect')
        self.finish(selected)
        self.assertEqual(self.ledger()['jobs'][selected.job]['phase'], 'closed')
        self.assertIn(selected.job, self.keeper.jobs)
        self.assertNotEqual(self.keeper.jobs[selected.job]['phase'], 'closed')
        witness = self.keeper.freeze_actor(self.intent)
        with self.assertRaises(ValueError):
            self.keeper.attest_actor(1, witness)
        with self.assertRaises(ValueError):
            self.keeper.stop()

    def test_service_durable_actor_history_precedes_actual_release(self):
        selected = self.launch()
        self.assertTrue(any(row['jobs'].get(selected.job, {}).get('phase') == 'gated'
                            for row in self.actor_records))
        self.assertTrue(any(row['jobs'].get(selected.job, {}).get('phase') == 'released'
                            for row in self.actor_records))
        self.finish(selected)
        self.assertEqual(self.actor_records[-1]['jobs'][selected.job]['phase'], 'closed')
        self.keeper.stop()

    def test_service_durability_fault_keeps_gate_closed_and_latches(self):
        def fail(body):
            self.assertTrue(body['jobs'])
            raise OSError('injected service actor journal fsync failure')
        self.keeper.actor_record = fail
        with self.assertRaisesRegex(OSError, 'fsync failure'):
            self.launch()
        self.assertTrue(self.keeper.actor_fault)
        rows = self.ledger()['jobs']
        self.assertEqual(len(rows), 1)
        self.assertTrue(all(row['phase'] != 'released' for row in rows.values()))
        self.keeper.actor_record = self.actor_records.append
        with self.assertRaisesRegex(ValueError, 'durability failed'):
            self.launch(actor=2)
        with self.assertRaises(ValueError):
            self.keeper.freeze_actor(self.intent)

    def test_inventory_drop_and_source_issuer_change_refuse_witness(self):
        selected = self.launch()
        self.finish(selected)
        witness = self.keeper.freeze_actor(self.intent)
        forged = deepcopy(witness)
        forged['issuer']['sourceSHA256'] = 'f'*64
        with self.assertRaises(ValueError):
            self.keeper.attest_actor(1, forged)
        original = self.keeper.actor_jobs.pop(selected.job)
        try:
            with self.assertRaises(ValueError):
                self.keeper.attest_actor(1, witness)
        finally:
            self.keeper.actor_jobs[selected.job] = original
        self.assertEqual(self.keeper.attest_actor(1, witness), witness)
        self.keeper.stop()

    def test_namespace_replaced_lock_refuses_fresh_attestation(self):
        selected = self.launch()
        self.finish(selected)
        witness = self.keeper.freeze_actor(self.intent)
        lock = self.root/'runtime.lock'
        retained = self.root/'retained.lock'
        lock.rename(retained)
        lock.touch(mode=0o600)
        try:
            with self.assertRaises(ValueError):
                self.keeper.attest_actor(1, witness)
            self.assertIsNone(self.keeper.process.poll())
        finally:
            lock.unlink()
            retained.rename(lock)
        self.assertEqual(self.keeper.attest_actor(1, witness), witness)
        self.keeper.stop()

    def test_boolean_actor_in_journal_cannot_alias_typed_actor(self):
        selected = self.launch()
        self.finish(selected)
        self.body['scenes'][0]['actor'] = True
        self.body['snapshot'] += 1
        self.store.write(self.body)
        with self.assertRaises(ValueError):
            self.keeper.freeze_actor(self.intent)
        self.keeper.stop()

    def test_effect_syntax_cannot_be_registered_as_readonly_helper(self):
        # CPU cat is never given a desktop connection. Conservative refusal of
        # effect syntax is tested using the real observed gate argv.
        with self.assertRaises(ValueError):
            self.launch(argv=['/usr/bin/cat', 'dispatch'])

    def test_declared_target_argv_cannot_replace_actual_gate_argv(self):
        original = self.keeper.register
        def falsified(ownership, **options):
            ownership = deepcopy(ownership)
            ownership['targetArgv'] = ['/usr/bin/cat', 'clients', '-j']
            return original(ownership, **options)
        self.keeper.register = falsified
        with self.assertRaises(ValueError):
            self.launch()


class ActorLedgerFaultTests(unittest.TestCase):
    def test_failed_durability_latches_after_memory_transition(self):
        def fail(_):
            raise OSError('injected durable publication fault')
        ledger = ActorLedger({'source': 'CPU fixture'}, fail)
        with self.assertRaises(OSError):
            ledger.register('1'*32, 'helper', 1, {'pid': 1, 'start': 1})
        self.assertTrue(ledger.fault)
        ledger.persist = lambda _: None
        with self.assertRaises(ValueError):
            ledger.released('1'*32)
        self.assertEqual(len(ledger.jobs), 1)

    def test_uncertainty_cannot_be_cleared_by_matching_return(self):
        ledger = ActorLedger({'source': 'CPU fixture'}, lambda _: None)
        ledger.register('1'*32, 'native-effect', 1, {'pid': 1, 'start': 1})
        ledger.uncertain('1'*32)
        row = ledger.jobs['1'*32]
        proof = {k: row[k] for k in ('job', 'pid', 'start', 'sourceSHA256')}
        proof.update(journalSHA256='2'*64, resultSHA256='3'*64)
        with self.assertRaises(ValueError):
            ledger.returned('1'*32, proof)
        self.assertTrue(row['uncertain'])


if __name__ == '__main__':
    unittest.main()
