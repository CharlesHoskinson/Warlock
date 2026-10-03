"""Refuse mismatched actual sampler metadata before accepting pixel evidence."""
import copy
import unittest
from sampler_evidence import POLICY, verify_sampler


class SamplerBinding(unittest.TestCase):
    def evidence(self):
        sources = [{'digest': str(i + 1) * 64, 'pixels': [96 // (i + 1), 80 // (i + 1)]} for i in range(3)]
        events = [{'event': 'samplingExperiment', 'policy': POLICY, 'fragmentSHA256': 'a' * 64,
                   'rasterDiagnostic': True, 'nativeAuthority': False, 'pixelProof': False}]
        for index, source in enumerate(sources + [{'digest': '', 'pixels': [1, 1]}] * 3):
            events.append({'event': 'samplingConfigured', 'policy': POLICY, 'textureId': index + 1,
                           'sourceDigest': source['digest'], 'pixels': source['pixels'],
                           'controlIndex': -1 if index < 3 else index - 3, 'minFilter': 9728,
                           'magFilter': 9728, 'wrapS': 33071, 'wrapT': 33071,
                           'extentUniform': source['pixels'], 'inspectionError': 0,
                           'nativeAuthority': False, 'pixelProof': False})
        return events, sources

    def test_metadata_never_grants_pixel_proof(self):
        events, sources = self.evidence()
        self.assertFalse(verify_sampler(events, sources, 'a' * 64)['pixelProof'])

    def test_mismatched_upload_uniform_state_and_shader_refuse(self):
        events, sources = self.evidence()
        for field, value in [('sourceDigest', 'b' * 64), ('extentUniform', [1, 1]),
                             ('minFilter', 9729), ('textureId', 2), ('pixelProof', True)]:
            altered = copy.deepcopy(events)
            altered[1][field] = value
            with self.assertRaises(ValueError):
                verify_sampler(altered, sources, 'a' * 64)
        with self.assertRaises(ValueError):
            verify_sampler(events, sources, 'b' * 64)
        for field, value in [('rasterDiagnostic', False), ('nativeAuthority', True), ('pixelProof', True)]:
            altered = copy.deepcopy(events)
            altered[0][field] = value
            with self.assertRaises(ValueError):
                verify_sampler(altered, sources, 'a' * 64)

    def test_missing_control_and_changed_member_order_refuse(self):
        events, sources = self.evidence()
        with self.assertRaises(ValueError):
            verify_sampler(events[:-1], sources, 'a' * 64)
        with self.assertRaises(ValueError):
            verify_sampler(events, list(reversed(sources)), 'a' * 64)
