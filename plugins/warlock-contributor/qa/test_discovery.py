"""Capability discovery and bounded inspection preserve exact original obligations."""
import json
import unittest

import test_warlock as fixtures


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.ContributionPolicyTests('test_fresh_start_status_check_record')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.repo, self.cli = self.fixture.repo, self.fixture.cli
        self.originals = {r['id']: r for r in self.fixture.original['requirements']}

    def test_capabilities_preserve_all_original_identities_and_recorded_counts(self):
        packet = json.loads(self.cli('capabilities').stdout)
        names = [r['capability'] for r in packet['capabilities']]
        self.assertEqual(names, sorted({r['capability'] for r in self.originals.values()}))
        self.assertEqual(sum(r['requirementCount'] for r in packet['capabilities']), 242)
        self.assertEqual(sum(r['scenarioCount'] for r in packet['capabilities']), 417)
        for row in packet['capabilities']:
            expected = {i for i, r in self.originals.items() if r['capability'] == row['capability']}
            self.assertEqual(set(row['requirements']), expected)
            self.assertEqual(row['scenarioCount'], sum(len(self.originals[i]['scenarios']) for i in expected))
        self.assertTrue(packet['recordedOnly'])
        self.assertFalse(packet['releaseAccepted'])

    def test_capability_filter_preserves_complete_originals_and_pagination(self):
        all_rows = json.loads(self.cli('remaining', '--capability', 'elm-taskbar').stdout)
        first = json.loads(self.cli('remaining', '--capability', 'elm-taskbar', '--limit', '1').stdout)
        second = json.loads(self.cli('remaining', '--capability', 'elm-taskbar', '--limit', '1', '--offset', '1').stdout)
        self.assertGreater(all_rows['matchingScenarios'], 1)
        self.assertEqual(first['scenarios'] + second['scenarios'], all_rows['scenarios'][:2])
        self.assertEqual(first['ledgerSha256'], second['ledgerSha256'])
        self.assertEqual(first['nextOffset'], 1)
        for row in all_rows['scenarios']:
            original = self.originals[row['requirement']]
            self.assertEqual(original['capability'], 'elm-taskbar')
            self.assertIn(row['original'], original['scenarios'])
            self.assertEqual(row['verificationScope'], original['verification'])

    def test_capability_and_requirement_filters_intersect_without_implying_completion(self):
        original = self.originals['ELM-UI-007']
        packet = json.loads(self.cli('remaining', '--capability', original['capability'],
                                     '--requirement', original['id']).stdout)
        self.assertEqual(packet['requirementsConsidered'], 1)
        other = next(r['capability'] for r in self.originals.values() if r['capability'] != original['capability'])
        empty = json.loads(self.cli('remaining', '--capability', other, '--requirement', original['id']).stdout)
        self.assertEqual(empty['requirementsConsidered'], 0)
        self.assertEqual(empty['matchingScenarios'], 0)
        self.assertFalse(empty['releaseAccepted'])

    def test_multiple_capabilities_are_a_union_and_summary_counts_do_not_paginate(self):
        chosen = ['elm-taskbar', 'elm-switcher']
        packet = json.loads(self.cli('remaining', '--capability', chosen[0], '--capability', chosen[1], '--summary').stdout)
        expected = [r for r in self.originals.values() if r['capability'] in chosen]
        self.assertEqual(packet['requirementsConsidered'], len(expected))
        self.assertEqual(sum(packet['scenarioCountsByRecordedStatus'].values()), sum(len(r['scenarios']) for r in expected))
        self.assertEqual(packet['scenarios'], [])
        self.assertEqual(packet['filters']['capabilities'], chosen)

    def test_unknown_and_duplicate_capabilities_fail_instead_of_silent_empty_backlog(self):
        self.cli('remaining', '--capability', 'elm-made-up', ok=False)
        self.cli('remaining', '--capability', 'elm-taskbar', '--capability', 'elm-taskbar', ok=False)

    def test_unfiltered_inspect_keeps_complete_original_and_ledger(self):
        packet = json.loads(self.cli('inspect', '--requirement', 'ELM-UI-007').stdout)
        row = packet['requirements'][0]
        self.assertEqual(row['original'], self.originals['ELM-UI-007'])
        self.assertEqual(row['omittedScenarios'], 0)
        self.assertEqual(packet['scenarioFilter'], [])

    def test_scenario_inspection_preserves_statement_verification_and_selected_ledger(self):
        packet = json.loads(self.cli('inspect', '--requirement', 'ELM-UI-007', '--scenario', 'restore-pending').stdout)
        row = packet['requirements'][0]
        original = self.originals['ELM-UI-007']
        expected = next(s for s in original['scenarios'] if s['name'] == 'restore-pending')
        self.assertEqual(row['original']['scenarios'], [expected])
        for key in original.keys() - {'scenarios'}:
            self.assertEqual(row['original'][key], original[key])
        self.assertEqual([s['name'] for s in row['ledger']['scenarios']], ['restore-pending'])
        self.assertEqual(row['originalScenarioCount'], len(original['scenarios']))
        self.assertEqual(row['omittedScenarios'], len(original['scenarios']) - 1)
        self.assertEqual(packet['scenarioFilter'], ['restore-pending'])

    def test_scenario_inspection_refuses_unknown_duplicate_or_unmatched_requirements(self):
        self.cli('inspect', '--requirement', 'ELM-UI-007', '--scenario', 'search-no-match', ok=False)
        self.cli('inspect', '--requirement', 'ELM-UI-007', '--scenario', 'restore-pending', '--scenario', 'restore-pending', ok=False)
        self.cli('inspect', '--requirement', 'ELM-UI-007', '--requirement', 'ELM-UI-005', '--scenario', 'restore-pending', ok=False)
        packet = json.loads(self.cli('inspect', '--requirement', 'ELM-UI-007', '--requirement', 'ELM-UI-005',
                                    '--scenario', 'restore-pending', '--scenario', 'search-no-match').stdout)
        self.assertEqual([len(r['original']['scenarios']) for r in packet['requirements']], [1, 1])

    def test_discovery_does_not_mutate_records_ledger_state_index_or_sources(self):
        self.fixture.start()
        paths = ['.warlock-contributor/slice.json', '.git/index', 'implementation/warlock/src/Desktop.elm',
                 'docs/warlock-build-loop/v2/STATE.json', 'docs/warlock-build-loop/v2/requirement-ledger.json']
        before = [(self.repo / p).read_bytes() for p in paths]
        self.cli('capabilities')
        self.cli('remaining', '--capability', 'elm-taskbar', '--limit', '1')
        self.cli('inspect', '--requirement', 'ELM-UI-007', '--scenario', 'restore-pending')
        self.assertEqual(before, [(self.repo / p).read_bytes() for p in paths])


if __name__ == '__main__':
    unittest.main()
