"""Finite pure controls. No provider, socket or process is started."""
import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location('foundation', Path(__file__).with_name('run_arm_gl_foundation.py'))
if spec is None or spec.loader is None:
    raise RuntimeError('missing foundation source')
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)


def global_event(name, interface, version):
    word = interface.encode() + b'\0'
    body = struct.pack('<II', name, len(word)) + word + b'\0' * (-len(word) % 4) + struct.pack('<I', version)
    return struct.pack('<II', 2, (8 + len(body)) << 16) + body


class FoundationControls(unittest.TestCase):
    def test_actual_literal_registry_roundtrip(self):
        payload = global_event(8, 'wl_seat', 9) + struct.pack('<III', 3, 12 << 16, 44)
        result, done = f.parse_registry(payload)
        self.assertEqual(result, {'wl_seat': 9})
        self.assertTrue(done)

    def test_fragmented_unknown_and_malformed_messages_refused(self):
        for data in (b'x', struct.pack('<II', 2, 4 << 16), struct.pack('<II', 7, 8 << 16), global_event(8, 'wl_seat', 9)[:-1]):
            with self.assertRaises(ValueError): f.parse_registry(data)

    def test_duplicate_protocol_and_display_error_refused(self):
        for data in (global_event(8, 'wl_seat', 9) * 2, struct.pack('<III', 1, 12 << 16, 1)):
            with self.assertRaises(ValueError): f.parse_registry(data)

    def test_pixman_missing_dmabuf_is_not_nested_ready(self):
        globals_ = {'wl_seat': 9, 'xdg_wm_base': 6, 'wl_compositor': 6, 'wl_shm': 1}
        self.assertEqual(f.missing_protocols(globals_), ['zwp_linux_dmabuf_v1>=4'])
        globals_['zwp_linux_dmabuf_v1'] = 3
        self.assertEqual(f.missing_protocols(globals_), ['zwp_linux_dmabuf_v1>=4'])
        globals_['zwp_linux_dmabuf_v1'] = 4
        self.assertEqual(f.missing_protocols(globals_), [])

    def test_old_seat_cannot_be_bound_at_new_version(self):
        self.assertIn('wl_seat>=9', f.missing_protocols({'wl_seat': 8}))

    def test_no_inherited_display_or_loader_or_host_bus(self):
        env = f.clean_environment(Path('/private/run'), Path('/private/root'))
        for name in ('DISPLAY', 'WAYLAND_DISPLAY', 'WAYLAND_SOCKET', 'LD_PRELOAD', 'LD_AUDIT', 'LD_LIBRARY_PATH', 'XAUTHORITY', 'HYPRLAND_INSTANCE_SIGNATURE'):
            self.assertNotIn(name, env)
        self.assertEqual(env['DBUS_SESSION_BUS_ADDRESS'], 'unix:path=/private/run/no-bus')
        self.assertEqual(env['HYPRLAND_NO_SD_VARS'], '1')

    def test_one_original_deadline_no_reset(self):
        clock = {'deadline': 200, 'last': 100, 'boot': 'b'}
        self.assertEqual(f.remaining(clock, 150, 'b'), 50)
        self.assertEqual(clock['deadline'], 200)
        for now, boot in ((149, 'b'), (200, 'b'), (151, 'c')):
            with self.assertRaises((ValueError, TimeoutError)): f.remaining(dict(clock), now, boot)

    def test_fixed_gl_host_no_drm_or_external_socket(self):
        args = f.host_argv('/fixed/weston', Path('/private/output'))
        for value in ('--backend=headless', '--renderer=gl', '--fake-seat', '--width=1280', '--height=800', '--socket=host-wayland', '--shell=kiosk-shell.so'):
            self.assertIn(value, args)
        self.assertFalse(any('drm' in x or 'use-gl' in x or 'x11' in x for x in args))

    def test_unarmed_or_expanded_packet_refused(self):
        for packet in ({}, {'schema': 1, 'armed': False}, {'schema': 1, 'armed': True, 'command': ['/bin/sh']}):
            with self.assertRaises(ValueError): f.packet_shape(packet)

    def test_fixed_config_has_no_exec_plugin_or_xwayland(self):
        text = f.HYPR_CONFIG
        self.assertNotIn('exec', text)
        self.assertNotIn('plugin', text)
        self.assertIn('enabled = false', text)
        self.assertIn('1280x800@60', text)

    def test_cleanup_ceiling_single_not_per_process(self):
        self.assertEqual(f.cleanup_ceiling(100), 2000000100)
        self.assertEqual(f.cleanup_ceiling(100), f.cleanup_ceiling(100))

    def test_child_file_output_limit_is_fixed_not_core_override(self):
        from unittest.mock import patch
        with patch.object(f.resource, 'setrlimit') as setting:
            f.bound_output()
        setting.assert_called_once_with(f.resource.RLIMIT_FSIZE, (65536, 65536))

    def test_mandatory_provider_private_source_selection(self):
        source = Path(__file__).parent / 'aquamarine-0.16.0/src/backend/Backend.cpp'
        text = source.read_text()
        self.assertIn('backend->implementationOptions = {selected};', text)
        self.assertIn('selected.backendType        = AQ_BACKEND_WAYLAND;', text)
        self.assertIn('selected.backendRequestMode = AQ_BACKEND_REQUEST_MANDATORY;', text)
        self.assertIn('for (auto const& b : backend->implementationOptions)', text)
        self.assertIn('if (backends.size() <= 0)', text)
        self.assertNotIn('getenv("AQ_BACKENDS")', text)

    def test_exact_private_soname15_required_and_no_system_fallback(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); body = root / 'libaquamarine.so.0.16.0'; body.write_bytes(b'private-body')
            for name in ('libaquamarine.so', 'libaquamarine.so.0'):
                (root / name).symlink_to(body.name)
            with self.assertRaises(ValueError): f.private_soname(root, body)
            (root / 'libaquamarine.so.15').symlink_to(body.name)
            self.assertEqual(f.private_soname(root, body), root / 'libaquamarine.so.15')
            (root / 'libaquamarine.so.15').unlink()
            (root / 'libaquamarine.so.15').symlink_to('/usr/lib/libaquamarine.so.0.16.0')
            with self.assertRaises(ValueError): f.private_soname(root, body)

    def test_unknown_private_soname_candidate_refused(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); body = root / 'libaquamarine.so.0.16.0'; body.write_bytes(b'private-body')
            (root / 'libaquamarine.so.15').symlink_to(body.name)
            (root / 'libaquamarine.so.99').write_bytes(b'unknown')
            with self.assertRaises(ValueError): f.private_soname(root, body)

    def test_actual_aquamarine_build_schema_not_top_level_guess(self):
        import copy
        image = {'path': '/private/libaquamarine.so.0.16.0', 'sha256': 'a' * 64, 'size': 5000, 'device': 58, 'inode': 9, 'mode': 493}
        nested = {'backend': image['path'], 'compositor': '/usr/bin/Hyprland', 'libraryDir': '/private',
                  'inputs': {image['path']: image['sha256'], '/usr/bin/Hyprland': f.COMPOSITOR_SHA}}
        report = {'passed': True, 'mode': '--aquamarine-build',
                  'sourceHashes': {f.AQ_SOURCE: f.AQ_SOURCE_SHA},
                  'aquamarineBuild': {'target': 'aquamarine', 'sourcePatchSha256': f.AQ_SOURCE_SHA,
                    'supplementalManifestSha256': f.AQ_MANIFEST_SHA, 'image': image, 'executed': False}}
        self.assertEqual(f.provider_build_binding(nested, report), image)
        for key, value in (('target', 'other'), ('sourcePatchSha256', 'b' * 64), ('supplementalManifestSha256', 'c' * 64)):
            bad = copy.deepcopy(report); bad['aquamarineBuild'][key] = value
            with self.assertRaises(ValueError): f.provider_build_binding(nested, bad)
        for key, value in (('path', '/foreign/lib.so'), ('sha256', 'c' * 64), ('size', 0), ('device', -1), ('inode', 0)):
            bad = copy.deepcopy(report); bad['aquamarineBuild']['image'][key] = value
            with self.assertRaises(ValueError): f.provider_build_binding(nested, bad)
        with self.assertRaises(ValueError): f.provider_build_binding(nested, {'passed': True, 'backendSha256': 'a' * 64})

    def test_missing_soname_is_refused_before_any_main_popen(self):
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); body = root / 'libaquamarine.so.0.16.0'; body.write_bytes(b'private-body')
            nested = {'compositor': '/usr/bin/Hyprland', 'backend': str(body), 'inputs': {},
                      'libraryDir': str(root), 'buildReport': {}, 'sourceReview': {}}
            packet = {'schema': 1, 'kind': 'arm-private-gl-foundation-v1', 'armed': True,
                      'expiresUTC': '2026-11-07T20:23:00Z', 'host': f.HOST,
                      'hostInputs': dict(f.GRAPHICS['files']), 'sourceInputs': {'/fixed/source': 'b' * 64},
                      'readiness': {'path': '/fixed/review', 'sha256': 'c' * 64}, 'nested': nested, 'graphics': f.GRAPHICS}
            review = dict(packet, disposition='accepted', scope='arm-private-gl-foundation')
            with patch.object(f.sys, 'argv', ['foundation', '--sha256', 'd' * 64]), patch.object(f, 'regular'), patch.object(f, 'verify_graphics'), patch.object(Path, 'read_text', return_value='{}'), patch.object(f.json, 'loads', side_effect=[packet, review]), patch.object(f, 'verify_private_provider', side_effect=lambda value: f.private_soname(Path(value['libraryDir']), Path(value['backend']))), patch.object(f.subprocess, 'Popen') as spawn:
                with self.assertRaises(ValueError): f.main()
            spawn.assert_not_called()


    def test_gl_explicit_vendor_no_environment_inheritance(self):
        env = f.graphics_environment(Path('/private/run'), Path('/private/root'))
        self.assertEqual(env['__EGL_VENDOR_LIBRARY_FILENAMES'], '/usr/share/glvnd/egl_vendor.d/10_nvidia.json')
        self.assertEqual(env['EGL_PLATFORM'], 'surfaceless')
        self.assertNotIn('DISPLAY', env)
        self.assertNotIn('LIBGL_ALWAYS_SOFTWARE', env)
        self.assertNotIn('MESA_LOADER_DRIVER_OVERRIDE', env)

    def test_gl_renderer_module_is_fixed(self):
        self.assertTrue(f.HOST['gl'].endswith('/lib/libweston-15/gl-renderer.so'))
        self.assertEqual(f.HOST['gl'], f.GRAPHICS['renderer'])
        self.assertIn(f.HOST['gl'], f.GRAPHICS['files'])

    def test_graphics_identity_exact_no_alternative_vendor(self):
        import copy
        for key, value in (('vendorJson', '/usr/share/glvnd/egl_vendor.d/50_mesa.json'), ('renderer', '/tmp/gl.so'), ('devices', {})):
            wrong = copy.deepcopy(f.GRAPHICS); wrong[key] = value
            with self.assertRaises(ValueError): f.graphics_shape(wrong, f.GRAPHICS['files'])
        self.assertIsNone(f.graphics_shape(f.GRAPHICS, f.GRAPHICS['files']))

    def test_graphics_library_missing_or_changed_refused(self):
        for key in f.GRAPHICS['files']:
            wrong = dict(f.GRAPHICS['files']); wrong.pop(key)
            with self.assertRaises(ValueError): f.graphics_shape(f.GRAPHICS, wrong)
            wrong[key] = '0' * 64
            with self.assertRaises(ValueError): f.graphics_shape(f.GRAPHICS, wrong)

    def test_device_identity_drift_refused_without_open(self):
        from unittest.mock import patch
        with patch.object(f, 'device_identity', return_value={}), patch.object(f, 'regular'), patch.object(f.subprocess, 'Popen') as spawn:
            with self.assertRaises(ValueError): f.verify_graphics(f.GRAPHICS, f.GRAPHICS['files'])
        spawn.assert_not_called()

    def test_bad_graphics_refused_before_any_popen(self):
        from unittest.mock import patch
        packet = {'schema': 1, 'kind': 'arm-private-gl-foundation-v1', 'armed': True,
                  'expiresUTC': '2026-11-07T20:23:00Z', 'host': f.HOST,
                  'hostInputs': f.GRAPHICS['files'], 'sourceInputs': {'/fixed/source': 'b' * 64},
                  'readiness': {}, 'nested': None, 'graphics': {}}
        with patch.object(f.sys, 'argv', ['gl', '--sha256', 'd' * 64]), patch.object(f, 'regular'), patch.object(Path, 'read_text', return_value='{}'), patch.object(f.json, 'loads', return_value=packet), patch.object(f.subprocess, 'Popen') as spawn:
            with self.assertRaises(ValueError): f.main()
        spawn.assert_not_called()

    def test_gl_no_protocol_presumption(self):
        self.assertIn('zwp_linux_dmabuf_v1>=4', f.missing_protocols({'wl_seat': 9}))
        self.assertEqual(f.missing_protocols(dict(f.REQUIRED)), [])

    def test_no_card0_readiness_or_device_open(self):
        self.assertIn('/dev/dri/renderD128', f.GRAPHICS['devices'])
        self.assertNotIn('/dev/dri/card0', f.GRAPHICS['devices'])
        import ast, inspect
        tree = ast.parse(inspect.getsource(f.device_identity))
        self.assertFalse(any(isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr == 'open' for x in ast.walk(tree)))


    def test_gpu_mapping_checks_metadata_without_mmap_device(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        p = '/dev/nvidia0'; item = f.GRAPHICS['devices'][p]
        dev = format(f.os.major(item['device']), '02x') + ':' + format(f.os.minor(item['device']), '02x')
        line = '1000-2000 rw-s 00000000 ' + dev + ' ' + str(item['inode']) + ' ' + p
        with patch.object(Path, 'read_text', return_value=line), patch.object(f, 'device_identity', return_value=item), patch.object(f, 'regular') as regular:
            self.assertEqual(f.mapped(SimpleNamespace(pid=7), {}, []), [p])
        regular.assert_not_called()
        with patch.object(Path, 'read_text', return_value=line), patch.object(f, 'device_identity', return_value={}):
            with self.assertRaises(ValueError): f.mapped(SimpleNamespace(pid=7), {}, [])


if __name__ == '__main__':
    unittest.main()
