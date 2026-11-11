#!/usr/bin/env python3
"""Root protected controls only. No compositor, loader or compiler invocation."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

parser = argparse.ArgumentParser()
for argument in ('module', 'inputs', 'inputs-sha256', 'loader-proof', 'loader-proof-sha256'):
    parser.add_argument('--' + argument, required=True)
args, rest = parser.parse_known_args()

def digest(body):
    return hashlib.sha256(body).hexdigest()

def raw_pin(reference, cap):
    path = Path(reference['path'])
    if path.is_symlink() or not path.is_file():
        raise ValueError('regular immutable input required')
    body = path.read_bytes()
    if len(body) > cap or digest(body) != reference['sha256']:
        raise ValueError('input hash or bound differs')
    return body

inputs = json.loads(raw_pin({'path': args.inputs, 'sha256': args.inputs_sha256}, 4 * 1024 * 1024))
# The staged schema aliases are exact byte copies, not authority or replacement files.
def pinned(reference, cap):
    mapped = inputs['immutableRemap'].get(reference['path'])
    if mapped is not None:
        if mapped['sha256'] != reference['sha256']:
            raise ValueError('staged immutable schema alias hash differs')
        reference = mapped
    return raw_pin(reference, cap)

loader_ref = {'path': args.loader_proof, 'sha256': args.loader_proof_sha256}
historical = json.loads(pinned(inputs['historicalCorrespondence'], 4 * 1024 * 1024))
schema = json.loads(pinned(inputs['schemaCorrespondence'], 4 * 1024 * 1024))
provider = json.loads(pinned(inputs['schemaProvider'], 4 * 1024 * 1024))
qualification = json.loads(pinned(inputs['schemaQualification'], 4 * 1024 * 1024))
loader_proof = json.loads(pinned(loader_ref, 4 * 1024 * 1024))
loader = json.loads(pinned(loader_proof['actualReport'], 4 * 1024 * 1024))
loader_terminal = json.loads(pinned(loader_proof['actualProtectedTerminal'], 4 * 1024 * 1024))
loader_review = json.loads(pinned(loader_proof['independentReview'], 4 * 1024 * 1024))
cache = json.loads(pinned(inputs['cacheCorrespondence'], 4 * 1024 * 1024))
# Setup uses actual accepted source/data; mutation cases below do not claim data acceptance.
if loader_proof.get('disposition') != 'accepted' or loader_proof.get('reviewer') != 'build_audit':
    raise ValueError('actual independently accepted current loader witness required before controls')
if loader.get('loaderCache', {}).get('sha256') != cache['currentCacheSha256']:
    raise ValueError('actual loader/cache join differs before controls')
if qualification['currentSchema']['sha256'] != provider['inputs'][qualification['currentSchema']['path']]:
    raise ValueError('actual qualified schema/provider fixture join differs')
for reference in (inputs['source'], inputs['collector'], inputs['cacheCorrespondence']):
    pinned(reference, 16 * 1024 * 1024)
spec = importlib.util.spec_from_file_location('cursor_composition_subject', args.module)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class CursorComposition(unittest.TestCase):
    def setUp(self):
        self.nested = copy.deepcopy(historical['historicalNested'])
        self.nested['inputs'] = copy.deepcopy(provider['inputs'])
        self.nested['sourceReview'] = copy.deepcopy(schema['currentProviderReadiness'])
        self.before = copy.deepcopy(self.nested)
        self.wrapper = {
            'schema': 2, 'disposition': 'accepted', 'reviewer': 'build_audit',
            'scope': 'ui011-cursor-current-schema-loader-composition',
            'historicalCorrespondence': copy.deepcopy(inputs['historicalCorrespondence']),
            'currentSchemaCorrespondence': copy.deepcopy(inputs['schemaCorrespondence']),
            'currentProviderReadiness': copy.deepcopy(schema['currentProviderReadiness']),
            'currentLoaderCorrespondence': copy.deepcopy(loader_ref),
        }
        self.wrapper_ref = {'path': '/test-only-cursor-composition.json', 'sha256': digest(json.dumps(self.wrapper).encode())}
        self.documents = {
            inputs['historicalCorrespondence']['path']: copy.deepcopy(historical),
            inputs['schemaCorrespondence']['path']: copy.deepcopy(schema),
            schema['currentProviderReadiness']['path']: copy.deepcopy(provider),
            schema['qualification']['path']: copy.deepcopy(qualification),
            loader_ref['path']: copy.deepcopy(loader_proof),
            loader_proof['actualReport']['path']: copy.deepcopy(loader),
            loader_proof['actualProtectedTerminal']['path']: copy.deepcopy(loader_terminal),
            loader_proof['independentReview']['path']: copy.deepcopy(loader_review),
        }
        self.reads = []
        self.current = m.CurrentBoot(inputs['boot'], pinned)

    def read(self, reference, cap):
        self.reads.append(copy.deepcopy(reference))
        if reference == self.wrapper_ref:
            return json.dumps(self.wrapper).encode()
        original = pinned(reference, cap)
        if reference['path'] in self.documents:
            return json.dumps(self.documents[reference['path']]).encode()
        return original

    def run_case(self):
        with patch.object(self.current, 'pinned', side_effect=self.read):
            return m.cursor_inputs(self.current, self.nested, self.wrapper_ref)

    def refused(self):
        with self.assertRaises((ValueError, KeyError, TypeError, FileNotFoundError)):
            self.run_case()

    def test_actual_current_schema_and_loader_compose_exactly(self):
        actual = self.run_case()
        expected = copy.deepcopy(provider['inputs'])
        del expected[m.CURSOR_OLD['path']]
        expected[m.CURSOR_NEW['path']] = m.CURSOR_NEW['sha256']
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 205)
        self.assertEqual(self.nested, self.before)
        self.assertNotIn(m.CURSOR_CACHE, self.reads, 'historical cache path must not be reinterpreted as current')
        self.assertIn(loader['loaderCache'], self.reads)

    def test_absent_proof_preserves_legacy_exact_map_without_reads(self):
        with patch.object(self.current, 'pinned', side_effect=AssertionError('unexpected proof read')):
            self.assertIs(m.cursor_inputs(self.current, self.nested), self.nested['inputs'])

    def test_historical_v1_cannot_silently_accept_current_schema(self):
        with self.assertRaises(ValueError):
            m.cursor_inputs(self.current, self.nested, inputs['historicalCorrespondence'])

    def test_missing_current_schema_proof_refused(self):
        del self.wrapper['currentSchemaCorrespondence']
        self.refused()

    def test_missing_current_loader_proof_refused(self):
        del self.wrapper['currentLoaderCorrespondence']
        self.refused()

    def test_foreign_schema_refused(self):
        self.wrapper['currentSchemaCorrespondence']['sha256'] = '0' * 64
        self.refused()

    def test_foreign_provider_refused(self):
        self.wrapper['currentProviderReadiness']['sha256'] = '0' * 64
        self.refused()

    def test_provider_other_input_delta_refused(self):
        self.nested['inputs'][m.CURSOR_HYPRLAND['path']] = '0' * 64
        self.refused()

    def test_unqualified_schema_hash_refused(self):
        self.nested['inputs'][qualification['currentSchema']['path']] = '0' * 64
        self.refused()

    def test_historical_basis_tampered_refused(self):
        self.documents[inputs['historicalCorrespondence']['path']]['basisSha256'] = '0' * 64
        self.refused()

    def test_foreign_loader_cache_refused(self):
        self.documents[loader_proof['actualReport']['path']]['loaderCache']['sha256'] = '0' * 64
        self.refused()

    def test_foreign_loader_image_refused(self):
        self.documents[loader_proof['actualReport']['path']]['loader']['sha256'] = '0' * 64
        self.refused()

    def test_loader_missing_cursor_selection_refused(self):
        del self.documents[loader_proof['actualReport']['path']]['resolvedFiles'][m.CURSOR_NEW['path']]
        self.refused()

    def test_loader_changed_selection_refused(self):
        self.documents[loader_proof['actualReport']['path']]['resolvedFiles'][m.CURSOR_AQUAMARINE['path']] = '0' * 64
        self.refused()

    def test_foreign_reviewer_refused(self):
        self.wrapper['reviewer'] = 'author'
        self.refused()

    def test_stale_loader_boot_refused(self):
        self.documents[loader_proof['actualReport']['path']]['currentBootId'] = 'foreign'
        self.refused()

    def test_changed_library_directory_refused(self):
        self.documents[loader_proof['actualReport']['path']]['libraryDir'] = '/unqualified'
        self.refused()

    def test_schema_qualification_false_refused(self):
        self.documents[schema['qualification']['path']]['exactCurrentBytesReproduced'] = False
        self.refused()

    def test_missing_actual_loader_terminal_refused(self):
        del self.documents[loader_ref['path']]['actualProtectedTerminal']
        self.refused()

    def test_missing_independent_loader_review_refused(self):
        del self.documents[loader_ref['path']]['independentReview']
        self.refused()

    def test_wrong_loader_review_report_binding_refused(self):
        self.documents[loader_proof['independentReview']['path']]['actualReport'] = {'path': '/foreign', 'sha256': '0' * 64}
        self.refused()

    def test_loader_execution_failure_refused(self):
        self.documents[loader_proof['actualReport']['path']]['commands'][0]['exit'] = 1
        self.refused()

    def test_32_fixed_correspondence_refusals(self):
        for seed in range(32):
            self.setUp()
            if seed % 4 == 0:
                self.documents[loader_proof['actualReport']['path']]['resolvedFiles']['/unqualified-' + str(seed)] = '0' * 64
            elif seed % 4 == 1:
                self.nested['libraryDir'] = '/foreign-' + str(seed)
            elif seed % 4 == 2:
                self.documents[inputs['historicalCorrespondence']['path']]['old']['sha256'] = '0' * 64
            else:
                self.wrapper['unexpected'] = seed
            with self.subTest(seed=seed):
                self.refused()

if __name__ == '__main__':
    unittest.main(argv=[__file__] + rest)
