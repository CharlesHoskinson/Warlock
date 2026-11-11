"""Advisory exact-provider lookup controls. No provider is executed."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import importlib.util

MODULE = Path(__file__).resolve().parents[1] / 'scripts/provider_capability_preflight.py'
SPEC = importlib.util.spec_from_file_location('provider_capability_preflight', MODULE)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)
SHA = 'd40e2edab24c2032a7a77b4d44c3d738e5003256d7d4199950dc7001fee9b6ba'
REQ = 'ELM-UI-011'
SCENARIO = 'focus-scope-opener minimize'

class ProviderCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        evidence = {}
        for name in ('findings', 'review', 'nativeFailure'):
            body = ('modeled ' + name).encode()
            (self.root / (name + '.json')).write_bytes(body)
            evidence[name] = {'path': name + '.json', 'sha256': hashlib.sha256(body).hexdigest()}
        self.row = {'providerSha256': SHA, 'requirement': REQ, 'scenario': SCENARIO,
                    'status': 'unsupported', 'reason': 'No committed minimized publication.',
                    'evidence': evidence}
        self.registry = {'schema': 1, 'entries': [self.row]}

    def assess(self, registry=None, sha=SHA, requirement=REQ, scenario=SCENARIO):
        return checker.assess(self.root, self.registry if registry is None else registry,
                              sha, requirement, scenario)

    def unknown(self, **kwargs):
        result = self.assess(**kwargs)
        self.assertEqual(result['status'], 'unknown')
        self.assertFalse(result['executionAuthorized'])
        self.assertFalse(result['nativeAcceptance'])

    def test_exact_known_limitation(self):
        result = self.assess()
        self.assertEqual(result['status'], 'unsupported')
        self.assertEqual(result['evidence'], self.row['evidence'])

    def test_other_binary_is_unknown(self):
        self.unknown(sha='0' * 64)

    def test_other_requirement_is_unknown(self):
        self.unknown(requirement='ELM-UI-012')

    def test_other_scenario_is_unknown(self):
        self.unknown(scenario='focus-scope-opener closure')

    def test_empty_registry_is_unknown(self):
        self.unknown(registry={'schema': 1, 'entries': []})

    def test_missing_registry_is_unknown(self):
        self.unknown(registry={})

    def test_supported_label_never_grants(self):
        self.row['status'] = 'supported'
        self.unknown()

    def test_missing_evidence_is_unknown(self):
        del self.row['evidence']['review']
        self.unknown()

    def test_changed_evidence_is_unknown(self):
        (self.root / 'findings.json').write_text('different')
        self.unknown()

    def test_missing_evidence_file_is_unknown(self):
        (self.root / 'nativeFailure.json').unlink()
        self.unknown()

    def test_absolute_evidence_ref_is_unknown(self):
        self.row['evidence']['review']['path'] = str(self.root / 'review.json')
        self.unknown()

    def test_parent_path_evidence_is_unknown(self):
        self.row['evidence']['review']['path'] = '../review.json'
        self.unknown()

    def test_symlink_evidence_is_unknown(self):
        (self.root / 'alias.json').symlink_to(self.root / 'review.json')
        self.row['evidence']['review']['path'] = 'alias.json'
        self.unknown()

    def test_duplicate_key_is_unknown(self):
        self.registry['entries'].append(copy.deepcopy(self.row))
        self.unknown()

    def test_no_authority_for_any_result(self):
        for value in (SHA, '0' * 64):
            result = self.assess(sha=value)
            for key in ('executionAuthorized', 'nativeAcceptance', 'sourceReady', 'executionPerformed'):
                self.assertIs(result[key], False)
            self.assertIs(result['advisoryOnly'], True)

    def test_64_fixed_digest_mutations_never_match(self):
        for index in range(64):
            char = '0' if SHA[index] != '0' else '1'
            with self.subTest(index=index):
                self.unknown(sha=SHA[:index] + char + SHA[index + 1:])

    def test_malformed_query_is_unknown(self):
        for value in (None, 7, '', SHA.upper(), SHA + '0'):
            with self.subTest(value=value):
                self.unknown(sha=value)

    def test_inputs_are_not_mutated(self):
        before = copy.deepcopy(self.registry)
        self.assess()
        self.assertEqual(self.registry, before)

if __name__ == '__main__':
    unittest.main()
