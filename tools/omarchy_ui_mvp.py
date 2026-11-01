#!/usr/bin/env python3
"""QA-only staging, startup-pinning, and evidence helper for the Omarchy UI MVP.

Honesty & Scope Rules:
- Development/QA helper ONLY. Zero Python ships in Warlock production.
- Never reads VM credentials, never invokes compilers, and never starts/touches
  the Omarchy VM unless Root explicitly runs a subcommand in the target context.
- Uses O_NOFOLLOW held descriptors and before/after fstat identity checks across
  all directory creation, regular-file hashing, and catalog mirroring (no path
  chmod or lstat-then-open races).
- Every generated manifest or receipt marks ``nativeAccepted: false``,
  ``releaseAccepted: false``, and ``protectedQaAccepted: false``.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import stat
import sys
import time
from pathlib import Path
from typing import Any

DEFAULT_BINDING = {
    "lifetime": "9007199254740993",
    "session": "9007199254740995",
    "frontend": "9007199254740997",
}

ELM_OWNING_ROOTS = (
    "implementation/warlock/src/Main.elm",
    "implementation/warlock/src/Bar.elm",
    "implementation/warlock/src/Popup.elm",
    "implementation/warlock/src/HttpMain.elm",
    "implementation/warlock/src/HttpBar.elm",
    "implementation/warlock/src/HttpPopup.elm",
)

# Exact 73-module transitive import closure of the six owning Elm roots
# (Main, Bar, Popup, HttpMain, HttpBar, HttpPopup), including UI007 StatusScroll.elm.
ELM_SIX_ROOT_CLOSURE_PATHS = (
    "implementation/warlock/src/ActionProjection.elm",
    "implementation/warlock/src/AdapterNotice.elm",
    "implementation/warlock/src/Announcement.elm",
    "implementation/warlock/src/AnnouncementMessage.elm",
    "implementation/warlock/src/Bar.elm",
    "implementation/warlock/src/Binding.elm",
    "implementation/warlock/src/CapturedAction.elm",
    "implementation/warlock/src/Catalog.elm",
    "implementation/warlock/src/Desktop.elm",
    "implementation/warlock/src/DesktopPolicy.elm",
    "implementation/warlock/src/Effects.elm",
    "implementation/warlock/src/Files.elm",
    "implementation/warlock/src/GeometryProjection.elm",
    "implementation/warlock/src/GeometrySizePolicy.elm",
    "implementation/warlock/src/HttpBar.elm",
    "implementation/warlock/src/HttpMain.elm",
    "implementation/warlock/src/HttpPopup.elm",
    "implementation/warlock/src/JumpList.elm",
    "implementation/warlock/src/Launch.elm",
    "implementation/warlock/src/Main.elm",
    "implementation/warlock/src/Menu.elm",
    "implementation/warlock/src/MenuBridge.elm",
    "implementation/warlock/src/Motion.elm",
    "implementation/warlock/src/MotionPreferences.elm",
    "implementation/warlock/src/NativeActorRetirement.elm",
    "implementation/warlock/src/NativeFamilyPreviewSource.elm",
    "implementation/warlock/src/NativeOutcome.elm",
    "implementation/warlock/src/NativePreviewDetachment.elm",
    "implementation/warlock/src/NativePreviewProposalIngress.elm",
    "implementation/warlock/src/NativePreviewRealm.elm",
    "implementation/warlock/src/NativePreviewSource.elm",
    "implementation/warlock/src/NativeProvider.elm",
    "implementation/warlock/src/Notifications.elm",
    "implementation/warlock/src/OutcomeAnnouncements.elm",
    "implementation/warlock/src/OutputController.elm",
    "implementation/warlock/src/OverviewRecovery.elm",
    "implementation/warlock/src/Pins.elm",
    "implementation/warlock/src/PointerOwnership.elm",
    "implementation/warlock/src/Popup.elm",
    "implementation/warlock/src/Presentation.elm",
    "implementation/warlock/src/PreviewIdentity.elm",
    "implementation/warlock/src/PreviewLifecycle.elm",
    "implementation/warlock/src/PreviewPaintGate.elm",
    "implementation/warlock/src/PreviewPresenter.elm",
    "implementation/warlock/src/PreviewVisual.elm",
    "implementation/warlock/src/Provider.elm",
    "implementation/warlock/src/ReceiptRouter.elm",
    "implementation/warlock/src/ReconciliationFrame.elm",
    "implementation/warlock/src/ReconciliationTracking.elm",
    "implementation/warlock/src/RetainedPreviewPresenter.elm",
    "implementation/warlock/src/SearchFold.elm",
    "implementation/warlock/src/Settings.elm",
    "implementation/warlock/src/Shell.elm",
    "implementation/warlock/src/ShortcutPreferences.elm",
    "implementation/warlock/src/Shortcuts.elm",
    "implementation/warlock/src/Snap.elm",
    "implementation/warlock/src/StatusScroll.elm",
    "implementation/warlock/src/Surface.elm",
    "implementation/warlock/src/SurfaceController.elm",
    "implementation/warlock/src/SurfaceRenderer.elm",
    "implementation/warlock/src/SurfaceSnapshot.elm",
    "implementation/warlock/src/SurfaceTheme.elm",
    "implementation/warlock/src/Switcher.elm",
    "implementation/warlock/src/SystemMenu.elm",
    "implementation/warlock/src/TaskView.elm",
    "implementation/warlock/src/Taskbar.elm",
    "implementation/warlock/src/TaskbarShell.elm",
    "implementation/warlock/src/Transfer.elm",
    "implementation/warlock/src/UInt64.elm",
    "implementation/warlock/src/UiHttp.elm",
    "implementation/warlock/src/UnsentOperation.elm",
    "implementation/warlock/src/WorkspaceInventory.elm",
    "implementation/warlock/src/WorkspaceNavigation.elm",
)

MVP_SOURCE_PATHS = [
    "implementation/warlock/elm.json",
    "implementation/warlock-preview-provider-v143/qa/toolchain.json",
    "tools/elm-http-dependencies.json",
    "tools/haskell-dependencies.json",
    "implementation/warlock/haskell/cabal.project",
    "implementation/warlock/haskell/runtime/ui/Warlock/Ui/Mvp.hsc",
    "implementation/warlock/haskell/runtime/ui/Warlock/Ui/WebKit.hs",
    "implementation/warlock/haskell/runtime/ui/Warlock/Ui/WebKitABI.hsc",
    "implementation/warlock/haskell/runtime/ui/Warlock/Ui/EngineCustody.hsc",
    "implementation/warlock/haskell/runtime/ui/Main.hs",
    "implementation/warlock/haskell/runtime/app/Main.hs",
    "implementation/warlock/haskell/runtime/runtime.cabal",
    "implementation/warlock/haskell/runtime/test-ui-mvp/Main.hs",
    "implementation/warlock/haskell/runtime/test-ui-webkit/Main.hs",
    "implementation/warlock/haskell/runtime/src/Warlock/Backend.hs",
    "implementation/warlock/haskell/runtime/src/Warlock/Ui/Owner.hs",
    "implementation/warlock/haskell/runtime/src/Warlock/Ui/Config.hs",
    "implementation/warlock/haskell/runtime/src/Warlock/Ui/Display.hs",
    "implementation/warlock/haskell/runtime/src/Warlock/Ui/PrivateNetwork.hsc",
    "implementation/warlock/haskell/protocol/src/Warlock/Protocol/Desktop.hs",
    *ELM_SIX_ROOT_CLOSURE_PATHS,
]

DIR_OPEN_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
REG_READ_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
REG_CREATE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC


def stat_fingerprint(st: os.stat_result) -> tuple[int, int, int, int, int]:
    return (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)


def valid_segment(name: str) -> bool:
    if not name or name in (".", ".."):
        return False
    encoded = name.encode("utf-8")
    if len(encoded) > 255:
        return False
    return not any(ch == "\x00" or ch == "/" or ord(ch) < 32 or ord(ch) == 127 for ch in name)


def split_canonical_abs(raw_path: str) -> list[str]:
    if not raw_path.startswith("/") or len(raw_path) > 4096:
        raise ValueError(f"expected canonical absolute path: {raw_path}")
    if raw_path != "/" and raw_path.endswith("/"):
        raw_path = raw_path.rstrip("/")
    parts = [part for part in raw_path.split("/") if part]
    if len(parts) > 64 or not all(valid_segment(part) for part in parts):
        raise ValueError(f"invalid path components in trusted path: {raw_path}")
    if raw_path != "/" and "/" + "/".join(parts) != raw_path:
        raise ValueError(f"non-canonical slashes in trusted path: {raw_path}")
    return parts


def open_root_dir_fd() -> int:
    root_fd = os.open("/", DIR_OPEN_FLAGS)
    try:
        st = os.fstat(root_fd)
        if not stat.S_ISDIR(st.st_mode):
            raise ValueError("root '/' is not a real directory")
        return root_fd
    except Exception:
        os.close(root_fd)
        raise


def walk_open_existing_dir(abs_dir: Path) -> tuple[int, list[dict[str, str]], dict[str, str]]:
    """Walk from '/' with O_DIRECTORY | O_NOFOLLOW, returning (dir_fd, ancestor_pins, target_pin).
    Caller owns closing the returned dir_fd.
    """
    raw = str(abs_dir)
    parts = split_canonical_abs(raw)
    cur_fd = open_root_dir_fd()
    ancestors: list[dict[str, str]] = []
    prefix = ""
    try:
        if not parts:
            st = os.fstat(cur_fd)
            pin = {"path": "/", "device": str(st.st_dev), "inode": str(st.st_ino)}
            return cur_fd, [], pin
        for idx, part in enumerate(parts):
            next_fd = os.open(part, DIR_OPEN_FLAGS, dir_fd=cur_fd)
            os.close(cur_fd)
            cur_fd = next_fd
            st = os.fstat(cur_fd)
            if not stat.S_ISDIR(st.st_mode) or st.st_ino <= 0:
                raise ValueError(f"non-directory encountered at {prefix}/{part}")
            prefix = f"{prefix}/{part}"
            pin = {"path": prefix, "device": str(st.st_dev), "inode": str(st.st_ino)}
            if idx + 1 < len(parts):
                ancestors.append(pin)
            else:
                return cur_fd, ancestors, pin
        raise AssertionError("unreachable")
    except Exception:
        os.close(cur_fd)
        raise


def ensure_private_child_dir(parent_fd: int, child_name: str, child_abs_path: str) -> tuple[int, dict[str, str]]:
    """Create or open a private 0700 non-symlink directory relative to held parent_fd.
    Never calls chmod on a path; opens with O_DIRECTORY | O_NOFOLLOW before fstat + fchmod.
    """
    if not valid_segment(child_name):
        raise ValueError(f"invalid private directory name: {child_name}")
    try:
        os.mkdir(child_name, 0o700, dir_fd=parent_fd)
    except FileExistsError:
        pass
    child_fd = os.open(child_name, DIR_OPEN_FLAGS, dir_fd=parent_fd)
    try:
        st_before = os.fstat(child_fd)
        if not stat.S_ISDIR(st_before.st_mode):
            raise ValueError(f"expected real directory: {child_abs_path}")
        euid = os.geteuid()
        if st_before.st_uid != euid:
            raise ValueError(f"refusing directory not owned by effective uid ({euid}): {child_abs_path}")
        if (st_before.st_mode & 0o7777) != 0o700:
            os.fchmod(child_fd, 0o700)
        st_after = os.fstat(child_fd)
        if (
            not stat.S_ISDIR(st_after.st_mode)
            or st_after.st_uid != euid
            or (st_after.st_mode & 0o7777) != 0o700
            or st_after.st_dev != st_before.st_dev
            or st_after.st_ino != st_before.st_ino
        ):
            raise ValueError(f"private directory verification failed: {child_abs_path}")
        pin = {
            "path": child_abs_path,
            "device": str(st_after.st_dev),
            "inode": str(st_after.st_ino),
        }
        return child_fd, pin
    except Exception:
        os.close(child_fd)
        raise


def open_or_create_private_run_dir(run_dir: Path) -> tuple[int, dict[str, str]]:
    raw = str(run_dir)
    parts = split_canonical_abs(raw)
    if not parts:
        raise ValueError("run_dir cannot be '/'")
    parent_abs = Path("/" + "/".join(parts[:-1])) if len(parts) > 1 else Path("/")
    parent_fd, _, _ = walk_open_existing_dir(parent_abs)
    try:
        return ensure_private_child_dir(parent_fd, parts[-1], raw)
    finally:
        os.close(parent_fd)


def read_and_hash_regular_at(
    parent_fd: int,
    leaf_name: str,
    display_path: str,
    max_bytes: int = 64 * 1024 * 1024,
    retain_bytes: bool = False,
) -> tuple[os.stat_result, str, bytes]:
    """Open leaf_name relative to parent_fd with O_NOFOLLOW, verify regular file
    fstat before and after reading, and compute SHA-256 on the held descriptor.
    """
    if not valid_segment(leaf_name):
        raise ValueError(f"invalid filename: {display_path}")
    fd = os.open(leaf_name, REG_READ_FLAGS, dir_fd=parent_fd)
    try:
        st_before = os.fstat(fd)
        if not stat.S_ISREG(st_before.st_mode):
            raise ValueError(f"expected regular non-symlink file: {display_path}")
        if st_before.st_size < 0 or st_before.st_size > max_bytes:
            raise ValueError(f"regular file size out of bounds ({st_before.st_size}): {display_path}")
        digest = hashlib.sha256()
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                raise ValueError(f"file grew past byte bound during read: {display_path}")
            digest.update(chunk)
            if retain_bytes:
                chunks.append(chunk)
        st_after = os.fstat(fd)
        if stat_fingerprint(st_before) != stat_fingerprint(st_after) or total != st_after.st_size:
            raise ValueError(f"file identity or size changed during read: {display_path}")
        return st_after, digest.hexdigest(), (b"".join(chunks) if retain_bytes else b"")
    finally:
        os.close(fd)


def hash_regular_path(abs_file: Path, max_bytes: int = 64 * 1024 * 1024) -> tuple[os.stat_result, str, list[dict[str, str]]]:
    raw = str(abs_file)
    parts = split_canonical_abs(raw)
    if not parts:
        raise ValueError(f"expected file path, got root: {raw}")
    parent_abs = Path("/" + "/".join(parts[:-1])) if len(parts) > 1 else Path("/")
    parent_fd, parent_ancestors, parent_pin = walk_open_existing_dir(parent_abs)
    try:
        st, digest, _ = read_and_hash_regular_at(parent_fd, parts[-1], raw, max_bytes=max_bytes, retain_bytes=False)
        all_ancestors = parent_ancestors + ([] if str(parent_abs) == "/" else [parent_pin])
        if len(all_ancestors) > 64:
            raise ValueError(f"ancestor depth exceeds 64: {raw}")
        return st, digest, all_ancestors
    finally:
        os.close(parent_fd)


def pin_regular_asset(path: Path, max_bytes: int = 64 * 1024 * 1024) -> dict[str, Any]:
    st, digest, ancestors = hash_regular_path(path, max_bytes=max_bytes)
    if st.st_ino <= 0 or st.st_size <= 0:
        raise ValueError(f"asset must have positive inode and size: {path}")
    return {
        "path": str(path),
        "device": str(st.st_dev),
        "inode": str(st.st_ino),
        "size": str(st.st_size),
        "sha256": digest,
        "ancestors": ancestors,
    }


def write_private_bytes_at(parent_fd: int, leaf_name: str, payload: bytes, replace_existing: bool = False) -> None:
    if not valid_segment(leaf_name):
        raise ValueError(f"invalid private output filename: {leaf_name}")
    if replace_existing:
        try:
            st_existing = os.stat(leaf_name, dir_fd=parent_fd, follow_symlinks=False)
            if stat.S_ISDIR(st_existing.st_mode):
                raise ValueError(f"refusing to unlink directory: {leaf_name}")
            os.unlink(leaf_name, dir_fd=parent_fd)
        except FileNotFoundError:
            pass
    fd = os.open(leaf_name, REG_CREATE_FLAGS, 0o600, dir_fd=parent_fd)
    try:
        st = os.fstat(fd)
        euid = os.geteuid()
        if not stat.S_ISREG(st.st_mode) or st.st_uid != euid or st.st_nlink != 1:
            raise ValueError(f"unexpected created file status for {leaf_name}")
        os.fchmod(fd, 0o600)
        view = memoryview(payload)
        written = 0
        while written < len(payload):
            count = os.write(fd, view[written:])
            if count <= 0:
                raise OSError(f"short write on {leaf_name}")
            written += count
        os.fsync(fd)
    finally:
        os.close(fd)
    os.fsync(parent_fd)


def write_private_json_at(parent_fd: int, leaf_name: str, payload: Any, replace_existing: bool = False) -> None:
    encoded = (json.dumps(payload, indent=2, sort_keys=False) + "\n").encode("utf-8")
    write_private_bytes_at(parent_fd, leaf_name, encoded, replace_existing=replace_existing)


def scan_catalog_dir_fd(
    dir_fd: int,
    display_prefix: str,
    rel_parts: tuple[str, ...],
    depth: int,
    state: dict[str, int],
    symlinks_out: list[str],
    desktop_entries_out: list[tuple[tuple[str, ...], bytes]],
) -> None:
    if depth > 16:
        raise ValueError(f"catalog directory depth exceeds 16 at {display_prefix}")
    before_stamp = stat_fingerprint(os.fstat(dir_fd))
    dup_fd = os.dup(dir_fd)
    try:
        names = sorted(os.listdir(dup_fd))
    finally:
        os.close(dup_fd)
    if len(names) >= 8192:
        raise ValueError(f"catalog directory entry bound exceeded at {display_prefix}")
    for name in names:
        if not valid_segment(name):
            raise ValueError(f"invalid catalog filename in {display_prefix}: {name!r}")
        state["nodes"] += 1
        if state["nodes"] > 16384:
            raise ValueError("catalog inventory capacity exceeded (16384 nodes)")
        entry_display = f"{display_prefix}/{name}"
        lst = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
        if stat.S_ISLNK(lst.st_mode):
            symlinks_out.append(entry_display)
            continue
        if stat.S_ISDIR(lst.st_mode):
            child_fd = os.open(name, DIR_OPEN_FLAGS, dir_fd=dir_fd)
            try:
                scan_catalog_dir_fd(
                    child_fd,
                    entry_display,
                    rel_parts + (name,),
                    depth + 1,
                    state,
                    symlinks_out,
                    desktop_entries_out,
                )
            finally:
                os.close(child_fd)
        elif stat.S_ISREG(lst.st_mode) and name.endswith(".desktop"):
            _, _, content = read_and_hash_regular_at(
                dir_fd,
                name,
                entry_display,
                max_bytes=262144,
                retain_bytes=True,
            )
            state["bytes"] += len(content)
            if state["bytes"] > 16777216:
                raise ValueError("catalog total .desktop byte capacity exceeded (16 MiB)")
            desktop_entries_out.append((rel_parts + (name,), content))
    after_stamp = stat_fingerprint(os.fstat(dir_fd))
    if before_stamp != after_stamp:
        raise ValueError(f"catalog directory changed during scan: {display_prefix}")


def materialize_catalog_mirror(
    run_dir_fd: int,
    run_dir_path: Path,
    mirror_name: str,
    entries: list[tuple[tuple[str, ...], bytes]],
) -> dict[str, str]:
    mirror_abs = str(run_dir_path / mirror_name)
    mirror_fd, mirror_pin = ensure_private_child_dir(run_dir_fd, mirror_name, mirror_abs)
    try:
        for rel_parts, content in entries:
            cur_fd = os.dup(mirror_fd)
            cur_abs = mirror_abs
            try:
                for dir_seg in rel_parts[:-1]:
                    cur_abs = f"{cur_abs}/{dir_seg}"
                    next_fd, _ = ensure_private_child_dir(cur_fd, dir_seg, cur_abs)
                    os.close(cur_fd)
                    cur_fd = next_fd
                write_private_bytes_at(cur_fd, rel_parts[-1], content, replace_existing=False)
            finally:
                os.close(cur_fd)
        return mirror_pin
    finally:
        os.close(mirror_fd)


def prepare_catalog_roots(
    run_dir_fd: int,
    run_dir_path: Path,
    requested_roots: list[str],
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Inspect real catalog directories via O_DIRECTORY | O_NOFOLLOW descriptors.
    If a system root contains symlinks that Warlock.Backend.Store refuses, write
    the already descriptor-verified regular .desktop payloads into a fresh 0700
    mirror under run_dir_fd using O_CREAT | O_EXCL | O_NOFOLLOW (zero path races).
    """
    pins: list[dict[str, str]] = []
    provenance: list[dict[str, Any]] = []
    for idx, raw_root in enumerate(requested_roots):
        try:
            root_fd, _, root_pin = walk_open_existing_dir(Path(raw_root))
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                provenance.append({"requested": raw_root, "status": "absent"})
                continue
            raise
        try:
            symlinks_found: list[str] = []
            desktop_entries: list[tuple[tuple[str, ...], bytes]] = []
            state = {"nodes": 0, "bytes": 0}
            scan_catalog_dir_fd(
                root_fd,
                raw_root.rstrip("/") or "/",
                (),
                0,
                state,
                symlinks_found,
                desktop_entries,
            )
            if not symlinks_found:
                pins.append(root_pin)
                provenance.append(
                    {
                        "requested": raw_root,
                        "mode": "direct",
                        "effectivePath": root_pin["path"],
                        "desktopFileCount": len(desktop_entries),
                        "skippedSymlinks": [],
                    }
                )
            else:
                mirror_name = f"catalog-regular-{idx}"
                mirror_pin = materialize_catalog_mirror(
                    run_dir_fd,
                    run_dir_path,
                    mirror_name,
                    desktop_entries,
                )
                pins.append(mirror_pin)
                provenance.append(
                    {
                        "requested": raw_root,
                        "mode": "regular-file-snapshot-due-to-symlinks",
                        "effectivePath": mirror_pin["path"],
                        "desktopFileCount": len(desktop_entries),
                        "skippedSymlinks": symlinks_found,
                    }
                )
        finally:
            os.close(root_fd)
    return pins, {"roots": provenance}


def cmd_source_manifest(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root)
    if not str(repo_root).startswith("/"):
        raise ValueError("--repo-root must be an absolute non-symlink path")
    entries: list[dict[str, Any]] = []
    missing_paths: list[str] = []
    for rel in MVP_SOURCE_PATHS:
        full = repo_root / rel
        try:
            st, digest, _ = hash_regular_path(full)
        except FileNotFoundError:
            entries.append({"path": rel, "present": False})
            missing_paths.append(rel)
            continue
        entries.append(
            {
                "path": rel,
                "present": True,
                "size": st.st_size,
                "sha256": digest,
            }
        )
    manifest = {
        "schema": 1,
        "evidenceKind": "omarchy-mvp-source-manifest",
        "repoRoot": str(repo_root),
        "generatedAtEpochNs": time.time_ns(),
        "elmOwningRoots": list(ELM_OWNING_ROOTS),
        "elmClosureModuleCount": len(ELM_SIX_ROOT_CLOSURE_PATHS),
        "statusScrollIncluded": "implementation/warlock/src/StatusScroll.elm" in MVP_SOURCE_PATHS,
        "allMandatoryPresent": len(missing_paths) == 0,
        "missingPaths": missing_paths,
        "files": entries,
        "nativeAccepted": False,
        "releaseAccepted": False,
        "protectedQaAccepted": False,
    }
    output = json.dumps(manifest, indent=2) + "\n"
    if args.output:
        out_path = Path(args.output)
        out_parts = split_canonical_abs(str(out_path))
        parent_abs = Path("/" + "/".join(out_parts[:-1])) if len(out_parts) > 1 else Path("/")
        parent_fd, _, _ = walk_open_existing_dir(parent_abs)
        try:
            write_private_bytes_at(parent_fd, out_parts[-1], output.encode("utf-8"), replace_existing=True)
        finally:
            os.close(parent_fd)
    else:
        sys.stdout.write(output)
    if missing_paths:
        sys.stderr.write(f"missing mandatory MVP source inputs: {', '.join(missing_paths)}\n")
        return 2
    return 0


def cmd_guest_config(args: argparse.Namespace) -> int:
    if args.duration_seconds < 1 or args.duration_seconds > 28:
        raise ValueError(
            "duration_seconds must be in 1..28 (Warlock bootstrap enforces <= 30s CLOCK_MONOTONIC)"
        )
    run_dir = Path(args.run_dir)
    run_dir_fd, _ = open_or_create_private_run_dir(run_dir)
    try:
        pins_abs = str(run_dir / "pins")
        pins_fd, pins_pin = ensure_private_child_dir(run_dir_fd, "pins", pins_abs)
        os.close(pins_fd)

        controller_pin = pin_regular_asset(Path(args.controller_html), max_bytes=8 * 1024 * 1024)
        bar_pin = pin_regular_asset(Path(args.bar_html), max_bytes=8 * 1024 * 1024)
        popup_pin = pin_regular_asset(Path(args.popup_html), max_bytes=8 * 1024 * 1024)
        ui_owner_pin = pin_regular_asset(Path(args.ui_owner_bin))
        ui_backend_pin = pin_regular_asset(Path(args.ui_backend_bin))

        effective_roots = args.catalog_root if args.catalog_root else ["/usr/share/applications"]
        catalog_pins, catalog_meta = prepare_catalog_roots(run_dir_fd, run_dir, effective_roots)

        binding = {
            "lifetime": args.lifetime,
            "session": args.session,
            "frontend": args.frontend,
        }

        now_mono_ns = time.monotonic_ns()
        deadline_ns = str(now_mono_ns + int(args.duration_seconds * 1_000_000_000))

        ui_config_path = run_dir / "ui.json"
        backend_config_path = run_dir / "backend.json"

        ui_config = {
            "schema": 1,
            "binding": binding,
            "deadlineMonotonicNs": deadline_ns,
            "documents": {
                "controller": controller_pin,
                "bar": bar_pin,
                "popup": popup_pin,
            },
        }

        backend_ui_image = {
            "path": ui_owner_pin["path"],
            "device": ui_owner_pin["device"],
            "inode": ui_owner_pin["inode"],
            "size": ui_owner_pin["size"],
            "sha256": ui_owner_pin["sha256"],
            "arguments": [str(ui_config_path)],
            "ancestors": ui_owner_pin["ancestors"],
        }

        backend_config: dict[str, Any] = {
            "schema": 1,
            "binding": binding,
            "deadlineMonotonicNs": deadline_ns,
            "ui": backend_ui_image,
            "catalogRoots": catalog_pins,
            "pinsRoot": pins_pin,
            "locale": args.locale,
            "applicationAttachment": bool(args.application_attachment),
        }

        write_private_json_at(run_dir_fd, "ui.json", ui_config, replace_existing=False)
        write_private_json_at(run_dir_fd, "backend.json", backend_config, replace_existing=False)

        guest_manifest = {
            "schema": 1,
            "evidenceKind": "omarchy-vm-mvp-guest-config",
            "generatedMonotonicNs": str(now_mono_ns),
            "deadlineMonotonicNs": deadline_ns,
            "durationSeconds": args.duration_seconds,
            "applicationAttachment": bool(args.application_attachment),
            "uiConfigPath": str(ui_config_path),
            "backendConfigPath": str(backend_config_path),
            "pinsDir": pins_abs,
            "uiBackendBinary": ui_backend_pin,
            "uiOwnerBinary": ui_owner_pin,
            "documents": ui_config["documents"],
            "catalogProvenance": catalog_meta,
            "honestyNotes": [
                "applicationAttachment: true causes Backend to reply once with protocolVersion 3 application-attached (nativeOperations: []) on the initial presentation-only commit triggered by GDK topology.",
                "EngineResult remains False while WebKit filter-store callback retirement and provider confinement are unqualified.",
                "Native-on-VM MVP execution is component/beta evidence, not protected QA or ARC024/DEL014/release acceptance.",
            ],
            "nativeAccepted": False,
            "releaseAccepted": False,
            "protectedQaAccepted": False,
        }
        write_private_json_at(run_dir_fd, "mvp-guest-manifest.json", guest_manifest, replace_existing=False)
        sys.stdout.write(json.dumps(guest_manifest, indent=2) + "\n")
        return 0
    finally:
        os.close(run_dir_fd)


def cmd_evaluate_run(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    stdout_path = Path(args.backend_stdout)
    stdout_parts = split_canonical_abs(str(stdout_path))
    stdout_parent = Path("/" + "/".join(stdout_parts[:-1])) if len(stdout_parts) > 1 else Path("/")
    stdout_parent_fd, _, _ = walk_open_existing_dir(stdout_parent)
    try:
        _, _, raw_bytes = read_and_hash_regular_at(
            stdout_parent_fd,
            stdout_parts[-1],
            str(stdout_path),
            max_bytes=4 * 1024 * 1024,
            retain_bytes=True,
        )
    finally:
        os.close(stdout_parent_fd)

    raw_stdout = raw_bytes.decode("utf-8", errors="replace").strip()
    parsed_lines: list[Any] = []
    for line in raw_stdout.splitlines():
        line_stripped = line.strip()
        if line_stripped.startswith("{") and line_stripped.endswith("}"):
            try:
                parsed_lines.append(json.loads(line_stripped))
            except json.JSONDecodeError:
                pass

    backend_summary = parsed_lines[-1] if parsed_lines else None
    persisted_pins: Any = None
    pins_dir_path = run_dir / "pins"
    try:
        pins_fd, _, _ = walk_open_existing_dir(pins_dir_path)
    except OSError:
        pins_fd = -1
    if pins_fd >= 0:
        try:
            _, _, pin_bytes = read_and_hash_regular_at(
                pins_fd,
                "taskbar.json",
                str(pins_dir_path / "taskbar.json"),
                max_bytes=16384,
                retain_bytes=True,
            )
            persisted_pins = json.loads(pin_bytes.decode("utf-8"))
        except FileNotFoundError:
            persisted_pins = None
        except (ValueError, json.JSONDecodeError):
            persisted_pins = {"malformed": True}
        finally:
            os.close(pins_fd)

    receipt = {
        "schema": 1,
        "evidenceKind": "omarchy-vm-mvp-beta-run",
        "backendExitCode": args.backend_exit_code,
        "backendDiagnostic": backend_summary,
        "callbacksObserved": (
            backend_summary.get("callbacks", 0) if isinstance(backend_summary, dict) else 0
        ),
        "domainOperationsObserved": (
            backend_summary.get("operations", 0) if isinstance(backend_summary, dict) else 0
        ),
        "taskbarPinsPersisted": persisted_pins is not None,
        "taskbarPinsContent": persisted_pins,
        "expectedHonestEngineExit": (
            "warlock-ui-owner reports EngineResult False False because productionCleanupFacts "
            "keeps CallbackPending and ProviderUnqualified; non-zero backend exit with "
            "callbacks > 0 is expected until engine retirement is independently qualified."
        ),
        "nativeAccepted": False,
        "releaseAccepted": False,
        "protectedQaAccepted": False,
    }
    output = json.dumps(receipt, indent=2) + "\n"
    if args.output:
        out_path = Path(args.output)
        out_parts = split_canonical_abs(str(out_path))
        out_parent = Path("/" + "/".join(out_parts[:-1])) if len(out_parts) > 1 else Path("/")
        out_parent_fd, _, _ = walk_open_existing_dir(out_parent)
        try:
            write_private_bytes_at(out_parent_fd, out_parts[-1], output.encode("utf-8"), replace_existing=True)
        finally:
            os.close(out_parent_fd)
    else:
        sys.stdout.write(output)
    return 0


def cmd_print_root_plan(args: argparse.Namespace) -> int:
    evidence_dir = args.evidence_dir
    plan = f"""# Root-Serialized Omarchy MVP Execution Plan (QA-Only Helper Output; NOT-RUN by worker)
# Scope: Native-on-VM beta window trial ONLY. Not protected QA or release acceptance.
# Rule: Never read or print /home/charl/vm/omarchy/credentials.txt. Restore omarchy-shell idle state on exit.

# 1. Host: run protected offline Elm + Haskell UI-origin checks (compiles HttpMain/HttpBar/HttpPopup HTML)
cd /home/charl/code/Warlock
python3 -B docs/warlock-build-loop/v2/loop.py check
python3 -B window-integration-qa/qa_run.py -- python3 -B tools/check_haskell_cpu.py --ui-origin

mkdir -p {evidence_dir}
chmod 0700 {evidence_dir}
python3 -B /home/charl/code/Warlock/tools/omarchy_ui_mvp.py source-manifest \\
  --repo-root /home/charl/code/Warlock \\
  --output {evidence_dir}/source-manifest.json

# 2. Host: verify UI007 StatusScroll.elm + 6-root Elm closure freshness on FRONTEND_DIR, then stage HTML + 6-package Haskell workspace + QA helper to guest
CPU_REPORT_DIR="$(ls -1dt /home/charl/code/Warlock/.warlock-contributor/haskell-cpu-* | head -n 1)"
FRONTEND_DIR="$CPU_REPORT_DIR/haskell-build/frontend"
python3 -B - "$CPU_REPORT_DIR/report.json" "$FRONTEND_DIR" <<'PY'
import hashlib, json, pathlib, sys
repo = pathlib.Path("/home/charl/code/Warlock")
report = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
frontend = pathlib.Path(sys.argv[2])
ui_fe = report["build"]["uiFrontend"]
recorded_src = ui_fe["sourceHashes"]
if "StatusScroll.elm" not in recorded_src:
    raise SystemExit("Refusing stale FRONTEND_DIR missing UI007 StatusScroll.elm; rerun check_haskell_cpu.py --ui-origin first")
for elm_file in sorted((repo / "implementation/warlock/src").rglob("*.elm")):
    rel = str(elm_file.relative_to(repo / "implementation/warlock/src"))
    actual = hashlib.sha256(elm_file.read_bytes()).hexdigest()
    if recorded_src.get(rel) != actual:
        raise SystemExit("Refusing stale FRONTEND_DIR: " + rel + " hash mismatch")
elm_json_sha = hashlib.sha256((repo / "implementation/warlock/elm.json").read_bytes()).hexdigest()
if ui_fe["fileHashes"].get("implementation/warlock/elm.json") != elm_json_sha:
    raise SystemExit("Refusing stale FRONTEND_DIR: elm.json hash mismatch")
for role, doc in (("controller", "HttpMain.html"), ("bar", "HttpBar.html"), ("popup", "HttpPopup.html")):
    doc_sha = hashlib.sha256((frontend / doc).read_bytes()).hexdigest()
    if ui_fe["documents"][role]["sha256"] != doc_sha:
        raise SystemExit("Frontend artifact digest mismatch for " + doc)
PY
tar -C /home/charl/code/Warlock -czf {evidence_dir}/warlock-mvp-stage.tar.gz \\
  implementation/warlock/haskell/cabal.project \\
  implementation/warlock/haskell/held-document \\
  implementation/warlock/haskell/process-custody \\
  implementation/warlock/haskell/protocol \\
  implementation/warlock/haskell/elf-observation \\
  implementation/warlock/haskell/runtime \\
  implementation/warlock/haskell/native-authority \\
  tools/omarchy_ui_mvp.py

(cd /home/charl/vm/omarchy && ./ssh.sh 'mkdir -p /tmp/warlock-mvp-src /tmp/warlock-mvp-assets && rm -rf /tmp/warlock-mvp-src/* /tmp/warlock-mvp-assets/*')
(cd /home/charl/vm/omarchy && ./ssh.sh 'cat > /tmp/warlock-mvp-stage.tar.gz && tar -xzf /tmp/warlock-mvp-stage.tar.gz -C /tmp/warlock-mvp-src') \\
  < {evidence_dir}/warlock-mvp-stage.tar.gz
for DOC in HttpMain.html HttpBar.html HttpPopup.html; do
  (cd /home/charl/vm/omarchy && ./ssh.sh "cat > /tmp/warlock-mvp-assets/$DOC") < "$FRONTEND_DIR/$DOC"
done

# 3. Guest: offline build of warlock-ui-owner + warlock-ui-backend using staged ~/warlock-mvp-dependencies-20261101
(cd /home/charl/vm/omarchy && ./ssh.sh 'set -euo pipefail
  command -v ghc cabal pkg-config >/dev/null
  pkg-config --exists gtk4 webkitgtk-6.0
  DEPS_ROOT="$HOME/warlock-mvp-dependencies-20261101"
  CABAL_WORK="/tmp/warlock-mvp-cabal"
  rm -rf "$CABAL_WORK"
  mkdir -m 0700 "$CABAL_WORK" "$CABAL_WORK/cabal-home" "$CABAL_WORK/repo-cache"
  cat > "$CABAL_WORK/cabal.config" <<EOF
remote-repo-cache: $CABAL_WORK/repo-cache
store-dir: $CABAL_WORK/store
active-repositories: :none
EOF
  HS_SRC="/tmp/warlock-mvp-src/implementation/warlock/haskell"
  cp -f "$HS_SRC/cabal.project" "$HS_SRC/mvp.project"
  FOUND_DEPS=0
  for CABAL_FILE in "$DEPS_ROOT"/*/*.cabal; do
    if [ ! -f "$CABAL_FILE" ]; then
      echo "No staged .cabal packages found under $DEPS_ROOT" >&2
      exit 2
    fi
    printf "packages: %s\\n" "$(dirname "$CABAL_FILE")" >> "$HS_SRC/mvp.project"
    FOUND_DEPS=$((FOUND_DEPS + 1))
  done
  if [ "$FOUND_DEPS" -lt 3 ]; then
    echo "Expected 3 staged local dependency packages under $DEPS_ROOT, found $FOUND_DEPS" >&2
    exit 2
  fi
  cat >> "$HS_SRC/mvp.project" <<EOF
active-repositories: :none
package network
  tests: False
  benchmarks: False
package cryptohash-sha256
  tests: False
  benchmarks: False
package hsc2hs
  tests: False
  benchmarks: False
EOF
  export GHC_ENVIRONMENT=- CABAL_DIR="$CABAL_WORK/cabal-home"
  cd "$HS_SRC"
  if command -v hsc2hs >/dev/null 2>&1; then
    HSC2HS_BIN="$(command -v hsc2hs)"
  else
    cabal --config-file="$CABAL_WORK/cabal.config" build --offline --project-file="$HS_SRC/mvp.project" --builddir="$CABAL_WORK/dist-tools" hsc2hs:exe:hsc2hs
    HSC2HS_BIN="$(cabal --config-file="$CABAL_WORK/cabal.config" list-bin --offline --project-file="$HS_SRC/mvp.project" --builddir="$CABAL_WORK/dist-tools" hsc2hs:exe:hsc2hs)"
  fi
  cabal --config-file="$CABAL_WORK/cabal.config" build --offline --project-file="$HS_SRC/mvp.project" --builddir="$CABAL_WORK/dist" --with-hsc2hs="$HSC2HS_BIN" warlock-runtime:exe:warlock-ui-owner warlock-runtime:exe:warlock-ui-backend
  cp -f "$(cabal --config-file="$CABAL_WORK/cabal.config" list-bin --offline --project-file="$HS_SRC/mvp.project" --builddir="$CABAL_WORK/dist" warlock-runtime:exe:warlock-ui-owner)" /tmp/warlock-mvp-assets/warlock-ui-owner
  cp -f "$(cabal --config-file="$CABAL_WORK/cabal.config" list-bin --offline --project-file="$HS_SRC/mvp.project" --builddir="$CABAL_WORK/dist" warlock-runtime:exe:warlock-ui-backend)" /tmp/warlock-mvp-assets/warlock-ui-backend
  chmod 0755 /tmp/warlock-mvp-assets/warlock-ui-owner /tmp/warlock-mvp-assets/warlock-ui-backend')

# 4. Guest: wake display, verify Omarchy builtin shell unlocked, save idle state, create 0700 RUN_DIR, generate <=28s config (applicationAttachment: true), and run
(cd /home/charl/vm/omarchy && ./vm-wake.sh)
(cd /home/charl/vm/omarchy && ./ssh.sh 'set -euo pipefail
  export OMARCHY_PATH=/usr/share/omarchy LANG=C.UTF-8 LC_ALL=C.UTF-8
  export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1
  LOCKED="$(omarchy-shell lock isLocked || true)"
  if [ "$LOCKED" != "false" ]; then
    echo "Omarchy session is locked ($LOCKED); unlock before GUI run" >&2
    exit 2
  fi
  ORIG_IDLE="$(omarchy-shell idle status || true)"
  restore_idle() {{
    if echo "$ORIG_IDLE" | grep -qi "enabled"; then
      omarchy-shell idle enable >/dev/null 2>&1 || true
    fi
  }}
  trap restore_idle EXIT
  omarchy-shell idle disable >/dev/null 2>&1 || true
  omarchy-shell notifications dismissAll >/dev/null 2>&1 || true

  RUN_DIR="/tmp/warlock-mvp-run-$(date +%s)-$$"
  mkdir -m 0700 "$RUN_DIR"
  python3 -B /tmp/warlock-mvp-src/tools/omarchy_ui_mvp.py guest-config \\
    --run-dir "$RUN_DIR" \\
    --duration-seconds 25 \\
    --controller-html /tmp/warlock-mvp-assets/HttpMain.html \\
    --bar-html /tmp/warlock-mvp-assets/HttpBar.html \\
    --popup-html /tmp/warlock-mvp-assets/HttpPopup.html \\
    --ui-owner-bin /tmp/warlock-mvp-assets/warlock-ui-owner \\
    --ui-backend-bin /tmp/warlock-mvp-assets/warlock-ui-backend \\
    --catalog-root /usr/share/applications \\
    > "$RUN_DIR/guest-config.stdout"

  set +e
  /tmp/warlock-mvp-assets/warlock-ui-backend "$RUN_DIR/backend.json" \\
    > "$RUN_DIR/backend.stdout" 2> "$RUN_DIR/backend.stderr" &
  BACKEND_PID=$!
  sleep 4
  hyprctl clients -j > "$RUN_DIR/hyprctl-clients.json" 2>/dev/null || true
  grim "$RUN_DIR/window-live.png" 2>/dev/null || true
  wait "$BACKEND_PID"
  BACKEND_RC=$?
  set -e

  python3 -B /tmp/warlock-mvp-src/tools/omarchy_ui_mvp.py evaluate-run \\
    --run-dir "$RUN_DIR" \\
    --backend-stdout "$RUN_DIR/backend.stdout" \\
    --backend-exit-code "$BACKEND_RC" \\
    --output "$RUN_DIR/mvp-run-receipt.json"
  echo "$RUN_DIR"')
"""
    sys.stdout.write(plan)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="QA-only staging and startup configuration helper for the Omarchy UI MVP."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_manifest = sub.add_parser(
        "source-manifest",
        help="Write a SHA-256 JSON manifest of Warlock MVP Elm/Haskell source files.",
    )
    p_manifest.add_argument("--repo-root", default="/home/charl/code/Warlock")
    p_manifest.add_argument("--output", default="")
    p_manifest.set_defaults(func=cmd_source_manifest)

    p_guest = sub.add_parser(
        "guest-config",
        help="Generate 0600 pinned ui.json and backend.json inside the Omarchy guest immediately before launch.",
    )
    p_guest.add_argument("--run-dir", required=True)
    p_guest.add_argument("--duration-seconds", type=int, default=25)
    p_guest.add_argument("--controller-html", required=True)
    p_guest.add_argument("--bar-html", required=True)
    p_guest.add_argument("--popup-html", required=True)
    p_guest.add_argument("--ui-owner-bin", required=True)
    p_guest.add_argument("--ui-backend-bin", required=True)
    p_guest.add_argument(
        "--catalog-root",
        action="append",
        default=[],
        help="Repeatable absolute catalog root (defaults to /usr/share/applications).",
    )
    p_guest.add_argument("--locale", default="en_US.UTF-8")
    p_guest.add_argument(
        "--application-attachment",
        dest="application_attachment",
        action="store_true",
        default=True,
        help="Emit trusted applicationAttachment: true in backend.json (default: True).",
    )
    p_guest.add_argument(
        "--no-application-attachment",
        dest="application_attachment",
        action="store_false",
        help="Set applicationAttachment: false in backend.json.",
    )
    p_guest.add_argument("--lifetime", default=DEFAULT_BINDING["lifetime"])
    p_guest.add_argument("--session", default=DEFAULT_BINDING["session"])
    p_guest.add_argument("--frontend", default=DEFAULT_BINDING["frontend"])
    p_guest.set_defaults(func=cmd_guest_config)

    p_eval = sub.add_parser(
        "evaluate-run",
        help="Produce an honest beta run receipt from warlock-ui-backend stdout and persisted pins.",
    )
    p_eval.add_argument("--run-dir", required=True)
    p_eval.add_argument("--backend-stdout", required=True)
    p_eval.add_argument("--backend-exit-code", type=int, required=True)
    p_eval.add_argument("--output", default="")
    p_eval.set_defaults(func=cmd_evaluate_run)

    p_plan = sub.add_parser(
        "print-root-plan",
        help="Print Root-executed staging, guest build, bounded run, and evidence commands.",
    )
    p_plan.add_argument(
        "--evidence-dir",
        default="/home/charl/vm/omarchy/evidence/warlock-ui-mvp-20261101",
    )
    p_plan.set_defaults(func=cmd_print_root_plan)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
