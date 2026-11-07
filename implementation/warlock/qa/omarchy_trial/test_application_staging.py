"""Filesystem staging controls only. No fixture ELF is executed or qualified.

Root selects exact baseline/candidate helper bytes with --helper. The synthetic
ELF header is data for this staging test, never evidence of a runnable image.
"""

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch


HELPER = Path(__file__).resolve().parents[4] / "tools/omarchy_ui_mvp.py"
VISIBLE = b"[Desktop Entry]\nType=Application\nName=Owned Recorder\nExec=fixture-recorder\nTerminal=false\n"
HIDDEN = b"[Desktop Entry]\nType=Application\nName=Hidden Recorder\nExec=fixture-recorder\nNoDisplay=true\nTerminal=false\n"
ARGV = ["two words", "", "caf\u00e9"]


def data_elf(machine=183):
    header = bytearray(64)
    header[:7] = b"\x7fELF\x02\x01\x01"
    header[16:18] = (2).to_bytes(2, "little")
    header[18:20] = machine.to_bytes(2, "little")
    header[20:24] = (1).to_bytes(4, "little")
    header[52:54] = (64).to_bytes(2, "little")
    return bytes(header) + b"STAGING-ONLY-NOT-AN-EXECUTABLE\n"


class StagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("reviewed_mvp_staging", HELPER)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load the exact selected staging helper")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.helper: ModuleType = module

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.assets = self.root / "assets"
        self.assets.mkdir(mode=0o700)
        self.documents = []
        for role in ("controller", "bar", "popup"):
            path = self.assets / (role + ".html")
            path.write_bytes(b"<!doctype html><html><body>staging-only</body></html>\n")
            self.documents.append(path)
        self.owner = self.assets / "owner-data"
        self.backend = self.assets / "backend-data"
        self.owner.write_bytes(b"owner pin data only\n")
        self.backend.write_bytes(b"backend pin data only\n")
        self.image = self.assets / "recorder;literal-name"
        self.image.write_bytes(data_elf())
        self.image.chmod(0o700)
        self.digest = hashlib.sha256(self.image.read_bytes()).hexdigest()
        self.legacy_catalog = self.root / "legacy-catalog"
        self.legacy_catalog.mkdir(mode=0o700)
        (self.legacy_catalog / "legacy.desktop").write_bytes(VISIBLE)

    def arguments(self, closed=True, **changes):
        values = dict(
            run_dir=str(self.root / "trial"), duration_seconds=25,
            controller_html=str(self.documents[0]), bar_html=str(self.documents[1]),
            popup_html=str(self.documents[2]), ui_owner_bin=str(self.owner),
            ui_backend_bin=str(self.backend), catalog_root=[] if closed else [str(self.legacy_catalog)],
            lifetime="1", session="2", frontend="3", locale="C.UTF-8",
            application_attachment=True,
            ux003_recorder_image=str(self.image) if closed else "",
            ux003_recorder_sha256=self.digest if closed else "",
        )
        values.update(changes)
        return argparse.Namespace(**values)

    def stage(self, args=None):
        args = args or self.arguments()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(self.helper.cmd_guest_config(args), 0)
        trial = Path(args.run_dir)
        return tuple(json.loads((trial / name).read_text()) for name in
                     ("backend.json", "ui.json", "mvp-guest-manifest.json"))

    def test_owned_fixture_and_decoder_shape(self):
        backend, _, manifest = self.stage()
        plans = backend["applicationPlans"]
        self.assertEqual(len(plans), 1)
        plan = plans[0]
        self.assertEqual(set(plan), {"entry", "sourceSha256", "exec", "argv", "root",
                                    "rootDevice", "rootInode", "pins", "path", "links", "size", "sha256"})
        self.assertEqual(plan["entry"], "ux003-recorder")
        self.assertEqual(plan["sourceSha256"], hashlib.sha256(VISIBLE).hexdigest())
        self.assertEqual(plan["exec"], "fixture-recorder")
        self.assertEqual(plan["argv"], ARGV)
        self.assertEqual(plan["links"], [])
        catalog = Path(backend["catalogRoots"][0]["path"])
        self.assertEqual(sorted(path.name for path in catalog.iterdir()),
                         ["ux003-hidden.desktop", "ux003-recorder.desktop"])
        self.assertEqual((catalog / "ux003-recorder.desktop").read_bytes(), VISIBLE)
        self.assertEqual((catalog / "ux003-hidden.desktop").read_bytes(), HIDDEN)
        self.assertEqual(manifest["applicationPlanProvenance"]["expectedArgv"], ARGV)

    def test_image_identity_and_literal_path_are_actual_pins(self):
        backend, _, _ = self.stage()
        plan = backend["applicationPlans"][0]
        root = self.assets.stat()
        image = self.image.stat()
        self.assertEqual((plan["root"], plan["rootDevice"], plan["rootInode"]),
                         (str(self.assets), str(root.st_dev), str(root.st_ino)))
        self.assertEqual((plan["path"], plan["size"], plan["sha256"]),
                         (self.image.name, str(image.st_size), self.digest))
        self.assertEqual(plan["pins"], [{"path": "/" + self.image.name,
                         "device": str(image.st_dev), "inode": str(image.st_ino), "kind": "regular"}])

    def test_single_existing_deadline_is_shared_without_refresh(self):
        with patch.object(self.helper.time, "monotonic_ns", return_value=4_000_000_000) as clock:
            backend, ui, manifest = self.stage()
        clock.assert_called_once_with()
        self.assertEqual(backend["deadlineMonotonicNs"], "29000000000")
        self.assertEqual(ui["deadlineMonotonicNs"], backend["deadlineMonotonicNs"])
        self.assertEqual(manifest["deadlineMonotonicNs"], backend["deadlineMonotonicNs"])

    def test_legacy_no_option_has_no_new_plan_or_fixture(self):
        backend, _, manifest = self.stage(self.arguments(closed=False))
        self.assertNotIn("applicationPlans", backend)
        self.assertNotIn("applicationPlanProvenance", manifest)
        self.assertEqual(backend["catalogRoots"][0]["path"], str(self.legacy_catalog))
        self.assertFalse((self.root / "trial" / "ux003-catalog").exists())

    def test_no_native_or_release_acceptance_from_staging(self):
        backend, _, manifest = self.stage()
        self.assertTrue(backend["applicationAttachment"])
        self.assertNotIn("nativeOperations", backend)
        for name in ("nativeAccepted", "releaseAccepted", "protectedQaAccepted"):
            self.assertIs(manifest[name], False)
        self.assertIs(manifest["applicationPlanProvenance"]["authorityGranted"], False)

    def test_private_fixture_and_outputs(self):
        backend, _, _ = self.stage()
        root = self.root / "trial"
        self.assertEqual(stat.S_IMODE(root.stat().st_mode), 0o700)
        catalog = Path(backend["catalogRoots"][0]["path"])
        self.assertEqual(stat.S_IMODE(catalog.stat().st_mode), 0o700)
        for path in [*catalog.iterdir(), *(root / name for name in
                     ("backend.json", "ui.json", "mvp-guest-manifest.json"))]:
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_missing_expected_hash_refuses_before_staging(self):
        with self.assertRaises(ValueError):
            self.stage(self.arguments(ux003_recorder_sha256=""))
        self.assertFalse((self.root / "trial").exists())

    def test_hash_without_image_refuses_before_staging(self):
        with self.assertRaises(ValueError):
            self.stage(self.arguments(ux003_recorder_image=""))
        self.assertFalse((self.root / "trial").exists())

    def test_malformed_hash_refuses(self):
        for digest in ("bad", "A" * 64, "0" * 63, "0" * 65):
            with self.subTest(digest=digest), self.assertRaises(ValueError):
                self.stage(self.arguments(ux003_recorder_sha256=digest))

    def test_relative_image_refuses(self):
        with self.assertRaises(ValueError):
            self.stage(self.arguments(ux003_recorder_image="recorder"))

    def test_unconfigured_attachment_refuses(self):
        with self.assertRaises(ValueError):
            self.stage(self.arguments(application_attachment=False))

    def test_mixed_catalog_roots_refuse(self):
        with self.assertRaises(ValueError):
            self.stage(self.arguments(catalog_root=[str(self.legacy_catalog)]))

    def test_wrong_image_hash_never_writes_startup(self):
        with self.assertRaises(ValueError):
            self.stage(self.arguments(ux003_recorder_sha256="0" * 64))
        self.assertFalse((self.root / "trial" / "backend.json").exists())
        self.assertFalse((self.root / "trial" / "ux003-catalog").exists())

    def test_symlink_image_is_not_followed(self):
        link = self.assets / "image-link"
        link.symlink_to(self.image)
        with self.assertRaises((OSError, ValueError)):
            self.stage(self.arguments(ux003_recorder_image=str(link)))

    def test_symlink_parent_is_not_followed(self):
        link = self.root / "asset-link"
        link.symlink_to(self.assets, target_is_directory=True)
        with self.assertRaises((OSError, ValueError)):
            self.stage(self.arguments(ux003_recorder_image=str(link / self.image.name)))

    def test_non_elf_is_refused(self):
        self.image.write_bytes(b"not an ELF image\n")
        digest = hashlib.sha256(self.image.read_bytes()).hexdigest()
        with self.assertRaises(ValueError):
            self.stage(self.arguments(ux003_recorder_sha256=digest))

    def test_other_architecture_is_refused(self):
        self.image.write_bytes(data_elf(machine=62))
        digest = hashlib.sha256(self.image.read_bytes()).hexdigest()
        with self.assertRaises(ValueError):
            self.stage(self.arguments(ux003_recorder_sha256=digest))

    def test_nonexecutable_and_setid_images_are_refused(self):
        for mode in (0o600, 0o4700):
            self.image.chmod(mode)
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                self.stage()

    def test_existing_fixture_directory_is_never_reused(self):
        trial = self.root / "trial"
        trial.mkdir(mode=0o700)
        catalog = trial / "ux003-catalog"
        catalog.mkdir(mode=0o700)
        canary = catalog / "unrelated.desktop"
        canary.write_bytes(b"preserve\n")
        with self.assertRaises(FileExistsError):
            self.stage()
        self.assertEqual(canary.read_bytes(), b"preserve\n")
        self.assertFalse((trial / "backend.json").exists())

    def test_existing_fixture_symlink_is_never_followed(self):
        trial = self.root / "trial"
        trial.mkdir(mode=0o700)
        (trial / "ux003-catalog").symlink_to(self.legacy_catalog, target_is_directory=True)
        with self.assertRaises(FileExistsError):
            self.stage()
        self.assertEqual([p.name for p in self.legacy_catalog.iterdir()], ["legacy.desktop"])

    def test_same_trial_is_not_overwritten(self):
        self.stage()
        files = {name: (self.root / "trial" / name).read_bytes() for name in
                 ("backend.json", "ui.json", "mvp-guest-manifest.json")}
        with self.assertRaises(FileExistsError):
            self.stage()
        self.assertEqual(files, {name: (self.root / "trial" / name).read_bytes() for name in files})

    def test_real_image_change_during_held_read_is_refused(self):
        read = os.read
        image_stat = self.image.stat()
        changed = False

        def changing_read(fd, size):
            nonlocal changed
            value = read(fd, size)
            current = os.fstat(fd)
            if not changed and value and (current.st_dev, current.st_ino) == (image_stat.st_dev, image_stat.st_ino):
                changed = True
                with self.image.open("ab") as stream:
                    stream.write(b"changed")
            return value

        with patch.object(self.helper.os, "read", side_effect=changing_read), self.assertRaises(ValueError):
            self.stage()
        self.assertTrue(changed)
        self.assertFalse((self.root / "trial" / "backend.json").exists())

    def test_original_duration_bound_is_preserved(self):
        for duration in (0, 29):
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                self.stage(self.arguments(duration_seconds=duration))
        self.assertFalse((self.root / "trial").exists())

    def test_cli_has_explicit_paired_recorder_options(self):
        args = self.helper.build_parser().parse_args([
            "guest-config", "--run-dir", str(self.root / "trial"),
            "--controller-html", str(self.documents[0]), "--bar-html", str(self.documents[1]),
            "--popup-html", str(self.documents[2]), "--ui-owner-bin", str(self.owner),
            "--ui-backend-bin", str(self.backend), "--ux003-recorder-image", str(self.image),
            "--ux003-recorder-sha256", self.digest,
        ])
        self.assertEqual(args.ux003_recorder_image, str(self.image))
        self.assertEqual(args.ux003_recorder_sha256, self.digest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--helper", type=Path)
    options, remaining = parser.parse_known_args()
    if options.helper is not None:
        HELPER = options.helper
    unittest.main(argv=[sys.argv[0], *remaining])
