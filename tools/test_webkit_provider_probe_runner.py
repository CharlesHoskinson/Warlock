"""Literal runner result controls; no native image or subprocess is started."""
import unittest

from run_webkit_provider_probe import expected_observation, validate_observation


class ProbeResultTests(unittest.TestCase):
    def test_exact_fixed_observation(self):
        self.assertEqual(validate_observation(expected_observation()), expected_observation())

    def test_runtime_micro_change_refuses(self):
        value = expected_observation()
        value['runtimeVersion'] = [2, 54, 1]
        with self.assertRaises(ValueError):
            validate_observation(value)

    def test_header_layout_change_refuses(self):
        value = expected_observation()
        value['headerLayout'] = [24, 4, 0]
        with self.assertRaises(ValueError):
            validate_observation(value)

    def test_boolean_is_not_integer(self):
        value = expected_observation()
        value['schema'] = True
        with self.assertRaises(ValueError):
            validate_observation(value)

    def test_missing_and_extra_fields_refuse(self):
        value = expected_observation()
        del value['error']
        with self.assertRaises(ValueError):
            validate_observation(value)
        value = expected_observation()
        value['providerPass'] = True
        with self.assertRaises(ValueError):
            validate_observation(value)

    def test_no_authority_flags_can_change(self):
        for name in ('providerQualified', 'cleanupQualified', 'inputQualified',
                     'nativeAcceptance', 'originalAcceptance'):
            value = expected_observation()
            value[name] = True
            with self.assertRaises(ValueError):
                validate_observation(value)


if __name__ == '__main__':
    unittest.main()
