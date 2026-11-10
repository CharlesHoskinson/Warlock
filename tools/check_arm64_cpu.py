#!/usr/bin/env python3
"""Fixed private ARM build profiles, admitted only by hash-reviewed qa_cpu."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from arm64_toolchain import digest, inventory, verify
from qa_cpu import arm64_inputs

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_NOTIFICATION_CONFIG = '("old-config-unconfigured",True)\n("explicit-private-address",True)\n("explicit-guid-preserved",True)\n("attachment-and-address",True)\n("old-attachment-unconfigured",True)\n("tcp-refused",True)\n("abstract-refused",True)\n("list-refused",True)\n("relative-refused",True)\n("parent-refused",True)\n("dot-refused",True)\n("empty-segment-refused",True)\n("trailing-slash-refused",True)\n("root-refused",True)\n("percent-refused",True)\n("space-refused",True)\n("control-refused",True)\n("unknown-key-refused",True)\n("guid-length-refused",True)\n("guid-uppercase-refused",True)\n("duplicate-guid-refused",True)\n("long-path-refused",True)\n("null-refused",True)\n("number-refused",True)\n("bool-refused",True)\n("array-refused",True)\n("object-refused",True)\n("unknown-config-field-refused",True)\n("duplicate-selection-refused",True)\n("trusted-path-data-boundary",True)\n'
sys.path.insert(0, str(ROOT / 'window-integration-qa'))
from qa_launch import require_qa_scope, runtime_base  # ty: ignore[import-not-found]


def image(path):
    if path.is_symlink() or not path.is_file():
        raise RuntimeError('Expected regular compiled image')
    status = path.stat()
    return {'path': str(path), 'device': str(status.st_dev), 'inode': str(status.st_ino),
                'size': str(status.st_size), 'sha256': digest(path)}


SUCCESSOR_FOCUS_CHECKS = {'SystemMenuReplay': ['sessionClosingClassifiedAndLogoutDenied', 'otherSessionTextLabelAndLogoutPreserved', 'sessionStateBoundsAndTypeRefused', 'networkPermissionsPreserveAdmission', 'powerCapabilitiesPreserveAdmission', 'foreignNetworkCapabilityRefused', 'foreignPowerPermissionRefused', 'powerCapabilityLabelsPreserved', 'systemMenuOpenerIntegrated', 'menuModeAcceptedByProductionRenderer', 'openingReadFocusMatchesCloseControl', 'originalUnavailableNetworkShown', 'remainingStateObserved', 'oneExplicitVolumeChange', 'pendingCannotRepeat', 'committedCannotRepeatOldRevision', 'unknownCannotReplay', 'readReconcilesChangedStateWithoutEffect', 'unavailableNeverSubmits', 'restartRequiresUIConfirmation', 'cancelHasNoNativeEffect', 'confirmedRestartSubmitsOnce', 'directConfirmationCannotBypassPrompt', 'wrongReceiptCannotSettle', 'staleViewCannotSubmit', 'closingFocusesOpenerWithoutNativeEffect', 'anotherPopupRetiresSystemWithoutLosingNativeState', 'allControlsHaveNames'], 'SolSystemMenuIntegratedReplay2114': ['seed-0/given-complete-domain', 'seed-0/positive-proposal-complete-domain-and-wire', 'seed-0/pending-duplicate-no-effect', 'seed-0/unknown-retains-complete-reservation', 'seed-0/unknown-duplicate-stable', 'seed-0/unknown-cannot-repeat', 'seed-0/foreign-request-preserves-complete-state', 'seed-0/foreign-service-preserves-complete-state', 'seed-0/invalid-status-preserves-complete-state', 'seed-0/late-committed-settles', 'seed-0/late-submitted-settles-without-invented-observation', 'seed-0/late-refused-retains-spent-intent', 'seed-0/same-revision-read-keeps-unconfirmed', 'seed-0/observation-preserves-typed-reservation', 'seed-0/older-outcome-after-new-observation-is-stale', 'seed-0/newer-read-settles-without-replay', 'seed-0/old-intent-cannot-be-replayed-after-read', 'seed-0/fresh-explicit-intent-can-follow-new-observation', 'seed-0/full-width-request-preserved', 'seed-1/given-complete-domain', 'seed-1/positive-proposal-complete-domain-and-wire', 'seed-1/pending-duplicate-no-effect', 'seed-1/unknown-retains-complete-reservation', 'seed-1/unknown-duplicate-stable', 'seed-1/unknown-cannot-repeat', 'seed-1/foreign-request-preserves-complete-state', 'seed-1/foreign-service-preserves-complete-state', 'seed-1/invalid-status-preserves-complete-state', 'seed-1/late-committed-settles', 'seed-1/late-submitted-settles-without-invented-observation', 'seed-1/late-refused-retains-spent-intent', 'seed-1/same-revision-read-keeps-unconfirmed', 'seed-1/observation-preserves-typed-reservation', 'seed-1/older-outcome-after-new-observation-is-stale', 'seed-1/newer-read-settles-without-replay', 'seed-1/old-intent-cannot-be-replayed-after-read', 'seed-1/fresh-explicit-intent-can-follow-new-observation', 'seed-1/full-width-request-preserved', 'seed-2/given-complete-domain', 'seed-2/positive-proposal-complete-domain-and-wire', 'seed-2/pending-duplicate-no-effect', 'seed-2/unknown-retains-complete-reservation', 'seed-2/unknown-duplicate-stable', 'seed-2/unknown-cannot-repeat', 'seed-2/foreign-request-preserves-complete-state', 'seed-2/foreign-service-preserves-complete-state', 'seed-2/invalid-status-preserves-complete-state', 'seed-2/late-committed-settles', 'seed-2/late-submitted-settles-without-invented-observation', 'seed-2/late-refused-retains-spent-intent', 'seed-2/same-revision-read-keeps-unconfirmed', 'seed-2/observation-preserves-typed-reservation', 'seed-2/older-outcome-after-new-observation-is-stale', 'seed-2/newer-read-settles-without-replay', 'seed-2/old-intent-cannot-be-replayed-after-read', 'seed-2/fresh-explicit-intent-can-follow-new-observation', 'seed-2/full-width-request-preserved', 'seed-3/given-complete-domain', 'seed-3/positive-proposal-complete-domain-and-wire', 'seed-3/pending-duplicate-no-effect', 'seed-3/unknown-retains-complete-reservation', 'seed-3/unknown-duplicate-stable', 'seed-3/unknown-cannot-repeat', 'seed-3/foreign-request-preserves-complete-state', 'seed-3/foreign-service-preserves-complete-state', 'seed-3/invalid-status-preserves-complete-state', 'seed-3/late-committed-settles', 'seed-3/late-submitted-settles-without-invented-observation', 'seed-3/late-refused-retains-spent-intent', 'seed-3/same-revision-read-keeps-unconfirmed', 'seed-3/observation-preserves-typed-reservation', 'seed-3/older-outcome-after-new-observation-is-stale', 'seed-3/newer-read-settles-without-replay', 'seed-3/old-intent-cannot-be-replayed-after-read', 'seed-3/fresh-explicit-intent-can-follow-new-observation', 'seed-3/full-width-request-preserved', 'seed-4/given-complete-domain', 'seed-4/positive-proposal-complete-domain-and-wire', 'seed-4/pending-duplicate-no-effect', 'seed-4/unknown-retains-complete-reservation', 'seed-4/unknown-duplicate-stable', 'seed-4/unknown-cannot-repeat', 'seed-4/foreign-request-preserves-complete-state', 'seed-4/foreign-service-preserves-complete-state', 'seed-4/invalid-status-preserves-complete-state', 'seed-4/late-committed-settles', 'seed-4/late-submitted-settles-without-invented-observation', 'seed-4/late-refused-retains-spent-intent', 'seed-4/same-revision-read-keeps-unconfirmed', 'seed-4/observation-preserves-typed-reservation', 'seed-4/older-outcome-after-new-observation-is-stale', 'seed-4/newer-read-settles-without-replay', 'seed-4/old-intent-cannot-be-replayed-after-read', 'seed-4/fresh-explicit-intent-can-follow-new-observation', 'seed-4/full-width-request-preserved', 'seed-5/given-complete-domain', 'seed-5/positive-proposal-complete-domain-and-wire', 'seed-5/pending-duplicate-no-effect', 'seed-5/unknown-retains-complete-reservation', 'seed-5/unknown-duplicate-stable', 'seed-5/unknown-cannot-repeat', 'seed-5/foreign-request-preserves-complete-state', 'seed-5/foreign-service-preserves-complete-state', 'seed-5/invalid-status-preserves-complete-state', 'seed-5/late-committed-settles', 'seed-5/late-submitted-settles-without-invented-observation', 'seed-5/late-refused-retains-spent-intent', 'seed-5/same-revision-read-keeps-unconfirmed', 'seed-5/observation-preserves-typed-reservation', 'seed-5/older-outcome-after-new-observation-is-stale', 'seed-5/newer-read-settles-without-replay', 'seed-5/old-intent-cannot-be-replayed-after-read', 'seed-5/fresh-explicit-intent-can-follow-new-observation', 'seed-5/full-width-request-preserved', 'seed-6/given-complete-domain', 'seed-6/positive-proposal-complete-domain-and-wire', 'seed-6/pending-duplicate-no-effect', 'seed-6/unknown-retains-complete-reservation', 'seed-6/unknown-duplicate-stable', 'seed-6/unknown-cannot-repeat', 'seed-6/foreign-request-preserves-complete-state', 'seed-6/foreign-service-preserves-complete-state', 'seed-6/invalid-status-preserves-complete-state', 'seed-6/late-committed-settles', 'seed-6/late-submitted-settles-without-invented-observation', 'seed-6/late-refused-retains-spent-intent', 'seed-6/same-revision-read-keeps-unconfirmed', 'seed-6/observation-preserves-typed-reservation', 'seed-6/older-outcome-after-new-observation-is-stale', 'seed-6/newer-read-settles-without-replay', 'seed-6/old-intent-cannot-be-replayed-after-read', 'seed-6/fresh-explicit-intent-can-follow-new-observation', 'seed-6/full-width-request-preserved', 'seed-7/given-complete-domain', 'seed-7/positive-proposal-complete-domain-and-wire', 'seed-7/pending-duplicate-no-effect', 'seed-7/unknown-retains-complete-reservation', 'seed-7/unknown-duplicate-stable', 'seed-7/unknown-cannot-repeat', 'seed-7/foreign-request-preserves-complete-state', 'seed-7/foreign-service-preserves-complete-state', 'seed-7/invalid-status-preserves-complete-state', 'seed-7/late-committed-settles', 'seed-7/late-submitted-settles-without-invented-observation', 'seed-7/late-refused-retains-spent-intent', 'seed-7/same-revision-read-keeps-unconfirmed', 'seed-7/observation-preserves-typed-reservation', 'seed-7/older-outcome-after-new-observation-is-stale', 'seed-7/newer-read-settles-without-replay', 'seed-7/old-intent-cannot-be-replayed-after-read', 'seed-7/fresh-explicit-intent-can-follow-new-observation', 'seed-7/full-width-request-preserved', 'seed-8/given-complete-domain', 'seed-8/positive-proposal-complete-domain-and-wire', 'seed-8/pending-duplicate-no-effect', 'seed-8/unknown-retains-complete-reservation', 'seed-8/unknown-duplicate-stable', 'seed-8/unknown-cannot-repeat', 'seed-8/foreign-request-preserves-complete-state', 'seed-8/foreign-service-preserves-complete-state', 'seed-8/invalid-status-preserves-complete-state', 'seed-8/late-committed-settles', 'seed-8/late-submitted-settles-without-invented-observation', 'seed-8/late-refused-retains-spent-intent', 'seed-8/same-revision-read-keeps-unconfirmed', 'seed-8/observation-preserves-typed-reservation', 'seed-8/older-outcome-after-new-observation-is-stale', 'seed-8/newer-read-settles-without-replay', 'seed-8/old-intent-cannot-be-replayed-after-read', 'seed-8/fresh-explicit-intent-can-follow-new-observation', 'seed-8/full-width-request-preserved', 'seed-9/given-complete-domain', 'seed-9/positive-proposal-complete-domain-and-wire', 'seed-9/pending-duplicate-no-effect', 'seed-9/unknown-retains-complete-reservation', 'seed-9/unknown-duplicate-stable', 'seed-9/unknown-cannot-repeat', 'seed-9/foreign-request-preserves-complete-state', 'seed-9/foreign-service-preserves-complete-state', 'seed-9/invalid-status-preserves-complete-state', 'seed-9/late-committed-settles', 'seed-9/late-submitted-settles-without-invented-observation', 'seed-9/late-refused-retains-spent-intent', 'seed-9/same-revision-read-keeps-unconfirmed', 'seed-9/observation-preserves-typed-reservation', 'seed-9/older-outcome-after-new-observation-is-stale', 'seed-9/newer-read-settles-without-replay', 'seed-9/old-intent-cannot-be-replayed-after-read', 'seed-9/fresh-explicit-intent-can-follow-new-observation', 'seed-9/full-width-request-preserved', 'seed-10/given-complete-domain', 'seed-10/positive-proposal-complete-domain-and-wire', 'seed-10/pending-duplicate-no-effect', 'seed-10/unknown-retains-complete-reservation', 'seed-10/unknown-duplicate-stable', 'seed-10/unknown-cannot-repeat', 'seed-10/foreign-request-preserves-complete-state', 'seed-10/foreign-service-preserves-complete-state', 'seed-10/invalid-status-preserves-complete-state', 'seed-10/late-committed-settles', 'seed-10/late-submitted-settles-without-invented-observation', 'seed-10/late-refused-retains-spent-intent', 'seed-10/same-revision-read-keeps-unconfirmed', 'seed-10/observation-preserves-typed-reservation', 'seed-10/older-outcome-after-new-observation-is-stale', 'seed-10/newer-read-settles-without-replay', 'seed-10/old-intent-cannot-be-replayed-after-read', 'seed-10/fresh-explicit-intent-can-follow-new-observation', 'seed-10/full-width-request-preserved', 'seed-11/given-complete-domain', 'seed-11/positive-proposal-complete-domain-and-wire', 'seed-11/pending-duplicate-no-effect', 'seed-11/unknown-retains-complete-reservation', 'seed-11/unknown-duplicate-stable', 'seed-11/unknown-cannot-repeat', 'seed-11/foreign-request-preserves-complete-state', 'seed-11/foreign-service-preserves-complete-state', 'seed-11/invalid-status-preserves-complete-state', 'seed-11/late-committed-settles', 'seed-11/late-submitted-settles-without-invented-observation', 'seed-11/late-refused-retains-spent-intent', 'seed-11/same-revision-read-keeps-unconfirmed', 'seed-11/observation-preserves-typed-reservation', 'seed-11/older-outcome-after-new-observation-is-stale', 'seed-11/newer-read-settles-without-replay', 'seed-11/old-intent-cannot-be-replayed-after-read', 'seed-11/fresh-explicit-intent-can-follow-new-observation', 'seed-11/full-width-request-preserved', 'seed-12/given-complete-domain', 'seed-12/positive-proposal-complete-domain-and-wire', 'seed-12/pending-duplicate-no-effect', 'seed-12/unknown-retains-complete-reservation', 'seed-12/unknown-duplicate-stable', 'seed-12/unknown-cannot-repeat', 'seed-12/foreign-request-preserves-complete-state', 'seed-12/foreign-service-preserves-complete-state', 'seed-12/invalid-status-preserves-complete-state', 'seed-12/late-committed-settles', 'seed-12/late-submitted-settles-without-invented-observation', 'seed-12/late-refused-retains-spent-intent', 'seed-12/same-revision-read-keeps-unconfirmed', 'seed-12/observation-preserves-typed-reservation', 'seed-12/older-outcome-after-new-observation-is-stale', 'seed-12/newer-read-settles-without-replay', 'seed-12/old-intent-cannot-be-replayed-after-read', 'seed-12/fresh-explicit-intent-can-follow-new-observation', 'seed-12/full-width-request-preserved', 'seed-13/given-complete-domain', 'seed-13/positive-proposal-complete-domain-and-wire', 'seed-13/pending-duplicate-no-effect', 'seed-13/unknown-retains-complete-reservation', 'seed-13/unknown-duplicate-stable', 'seed-13/unknown-cannot-repeat', 'seed-13/foreign-request-preserves-complete-state', 'seed-13/foreign-service-preserves-complete-state', 'seed-13/invalid-status-preserves-complete-state', 'seed-13/late-committed-settles', 'seed-13/late-submitted-settles-without-invented-observation', 'seed-13/late-refused-retains-spent-intent', 'seed-13/same-revision-read-keeps-unconfirmed', 'seed-13/observation-preserves-typed-reservation', 'seed-13/older-outcome-after-new-observation-is-stale', 'seed-13/newer-read-settles-without-replay', 'seed-13/old-intent-cannot-be-replayed-after-read', 'seed-13/fresh-explicit-intent-can-follow-new-observation', 'seed-13/full-width-request-preserved', 'seed-14/given-complete-domain', 'seed-14/positive-proposal-complete-domain-and-wire', 'seed-14/pending-duplicate-no-effect', 'seed-14/unknown-retains-complete-reservation', 'seed-14/unknown-duplicate-stable', 'seed-14/unknown-cannot-repeat', 'seed-14/foreign-request-preserves-complete-state', 'seed-14/foreign-service-preserves-complete-state', 'seed-14/invalid-status-preserves-complete-state', 'seed-14/late-committed-settles', 'seed-14/late-submitted-settles-without-invented-observation', 'seed-14/late-refused-retains-spent-intent', 'seed-14/same-revision-read-keeps-unconfirmed', 'seed-14/observation-preserves-typed-reservation', 'seed-14/older-outcome-after-new-observation-is-stale', 'seed-14/newer-read-settles-without-replay', 'seed-14/old-intent-cannot-be-replayed-after-read', 'seed-14/fresh-explicit-intent-can-follow-new-observation', 'seed-14/full-width-request-preserved', 'seed-15/given-complete-domain', 'seed-15/positive-proposal-complete-domain-and-wire', 'seed-15/pending-duplicate-no-effect', 'seed-15/unknown-retains-complete-reservation', 'seed-15/unknown-duplicate-stable', 'seed-15/unknown-cannot-repeat', 'seed-15/foreign-request-preserves-complete-state', 'seed-15/foreign-service-preserves-complete-state', 'seed-15/invalid-status-preserves-complete-state', 'seed-15/late-committed-settles', 'seed-15/late-submitted-settles-without-invented-observation', 'seed-15/late-refused-retains-spent-intent', 'seed-15/same-revision-read-keeps-unconfirmed', 'seed-15/observation-preserves-typed-reservation', 'seed-15/older-outcome-after-new-observation-is-stale', 'seed-15/newer-read-settles-without-replay', 'seed-15/old-intent-cannot-be-replayed-after-read', 'seed-15/fresh-explicit-intent-can-follow-new-observation', 'seed-15/full-width-request-preserved', 'seed-16/given-complete-domain', 'seed-16/positive-proposal-complete-domain-and-wire', 'seed-16/pending-duplicate-no-effect', 'seed-16/unknown-retains-complete-reservation', 'seed-16/unknown-duplicate-stable', 'seed-16/unknown-cannot-repeat', 'seed-16/foreign-request-preserves-complete-state', 'seed-16/foreign-service-preserves-complete-state', 'seed-16/invalid-status-preserves-complete-state', 'seed-16/late-committed-settles', 'seed-16/late-submitted-settles-without-invented-observation', 'seed-16/late-refused-retains-spent-intent', 'seed-16/same-revision-read-keeps-unconfirmed', 'seed-16/observation-preserves-typed-reservation', 'seed-16/older-outcome-after-new-observation-is-stale', 'seed-16/newer-read-settles-without-replay', 'seed-16/old-intent-cannot-be-replayed-after-read', 'seed-16/fresh-explicit-intent-can-follow-new-observation', 'seed-16/full-width-request-preserved', 'seed-17/given-complete-domain', 'seed-17/positive-proposal-complete-domain-and-wire', 'seed-17/pending-duplicate-no-effect', 'seed-17/unknown-retains-complete-reservation', 'seed-17/unknown-duplicate-stable', 'seed-17/unknown-cannot-repeat', 'seed-17/foreign-request-preserves-complete-state', 'seed-17/foreign-service-preserves-complete-state', 'seed-17/invalid-status-preserves-complete-state', 'seed-17/late-committed-settles', 'seed-17/late-submitted-settles-without-invented-observation', 'seed-17/late-refused-retains-spent-intent', 'seed-17/same-revision-read-keeps-unconfirmed', 'seed-17/observation-preserves-typed-reservation', 'seed-17/older-outcome-after-new-observation-is-stale', 'seed-17/newer-read-settles-without-replay', 'seed-17/old-intent-cannot-be-replayed-after-read', 'seed-17/fresh-explicit-intent-can-follow-new-observation', 'seed-17/full-width-request-preserved', 'seed-18/given-complete-domain', 'seed-18/positive-proposal-complete-domain-and-wire', 'seed-18/pending-duplicate-no-effect', 'seed-18/unknown-retains-complete-reservation', 'seed-18/unknown-duplicate-stable', 'seed-18/unknown-cannot-repeat', 'seed-18/foreign-request-preserves-complete-state', 'seed-18/foreign-service-preserves-complete-state', 'seed-18/invalid-status-preserves-complete-state', 'seed-18/late-committed-settles', 'seed-18/late-submitted-settles-without-invented-observation', 'seed-18/late-refused-retains-spent-intent', 'seed-18/same-revision-read-keeps-unconfirmed', 'seed-18/observation-preserves-typed-reservation', 'seed-18/older-outcome-after-new-observation-is-stale', 'seed-18/newer-read-settles-without-replay', 'seed-18/old-intent-cannot-be-replayed-after-read', 'seed-18/fresh-explicit-intent-can-follow-new-observation', 'seed-18/full-width-request-preserved', 'seed-19/given-complete-domain', 'seed-19/positive-proposal-complete-domain-and-wire', 'seed-19/pending-duplicate-no-effect', 'seed-19/unknown-retains-complete-reservation', 'seed-19/unknown-duplicate-stable', 'seed-19/unknown-cannot-repeat', 'seed-19/foreign-request-preserves-complete-state', 'seed-19/foreign-service-preserves-complete-state', 'seed-19/invalid-status-preserves-complete-state', 'seed-19/late-committed-settles', 'seed-19/late-submitted-settles-without-invented-observation', 'seed-19/late-refused-retains-spent-intent', 'seed-19/same-revision-read-keeps-unconfirmed', 'seed-19/observation-preserves-typed-reservation', 'seed-19/older-outcome-after-new-observation-is-stale', 'seed-19/newer-read-settles-without-replay', 'seed-19/old-intent-cannot-be-replayed-after-read', 'seed-19/fresh-explicit-intent-can-follow-new-observation', 'seed-19/full-width-request-preserved', 'seed-20/given-complete-domain', 'seed-20/positive-proposal-complete-domain-and-wire', 'seed-20/pending-duplicate-no-effect', 'seed-20/unknown-retains-complete-reservation', 'seed-20/unknown-duplicate-stable', 'seed-20/unknown-cannot-repeat', 'seed-20/foreign-request-preserves-complete-state', 'seed-20/foreign-service-preserves-complete-state', 'seed-20/invalid-status-preserves-complete-state', 'seed-20/late-committed-settles', 'seed-20/late-submitted-settles-without-invented-observation', 'seed-20/late-refused-retains-spent-intent', 'seed-20/same-revision-read-keeps-unconfirmed', 'seed-20/observation-preserves-typed-reservation', 'seed-20/older-outcome-after-new-observation-is-stale', 'seed-20/newer-read-settles-without-replay', 'seed-20/old-intent-cannot-be-replayed-after-read', 'seed-20/fresh-explicit-intent-can-follow-new-observation', 'seed-20/full-width-request-preserved', 'seed-21/given-complete-domain', 'seed-21/positive-proposal-complete-domain-and-wire', 'seed-21/pending-duplicate-no-effect', 'seed-21/unknown-retains-complete-reservation', 'seed-21/unknown-duplicate-stable', 'seed-21/unknown-cannot-repeat', 'seed-21/foreign-request-preserves-complete-state', 'seed-21/foreign-service-preserves-complete-state', 'seed-21/invalid-status-preserves-complete-state', 'seed-21/late-committed-settles', 'seed-21/late-submitted-settles-without-invented-observation', 'seed-21/late-refused-retains-spent-intent', 'seed-21/same-revision-read-keeps-unconfirmed', 'seed-21/observation-preserves-typed-reservation', 'seed-21/older-outcome-after-new-observation-is-stale', 'seed-21/newer-read-settles-without-replay', 'seed-21/old-intent-cannot-be-replayed-after-read', 'seed-21/fresh-explicit-intent-can-follow-new-observation', 'seed-21/full-width-request-preserved', 'seed-22/given-complete-domain', 'seed-22/positive-proposal-complete-domain-and-wire', 'seed-22/pending-duplicate-no-effect', 'seed-22/unknown-retains-complete-reservation', 'seed-22/unknown-duplicate-stable', 'seed-22/unknown-cannot-repeat', 'seed-22/foreign-request-preserves-complete-state', 'seed-22/foreign-service-preserves-complete-state', 'seed-22/invalid-status-preserves-complete-state', 'seed-22/late-committed-settles', 'seed-22/late-submitted-settles-without-invented-observation', 'seed-22/late-refused-retains-spent-intent', 'seed-22/same-revision-read-keeps-unconfirmed', 'seed-22/observation-preserves-typed-reservation', 'seed-22/older-outcome-after-new-observation-is-stale', 'seed-22/newer-read-settles-without-replay', 'seed-22/old-intent-cannot-be-replayed-after-read', 'seed-22/fresh-explicit-intent-can-follow-new-observation', 'seed-22/full-width-request-preserved', 'seed-23/given-complete-domain', 'seed-23/positive-proposal-complete-domain-and-wire', 'seed-23/pending-duplicate-no-effect', 'seed-23/unknown-retains-complete-reservation', 'seed-23/unknown-duplicate-stable', 'seed-23/unknown-cannot-repeat', 'seed-23/foreign-request-preserves-complete-state', 'seed-23/foreign-service-preserves-complete-state', 'seed-23/invalid-status-preserves-complete-state', 'seed-23/late-committed-settles', 'seed-23/late-submitted-settles-without-invented-observation', 'seed-23/late-refused-retains-spent-intent', 'seed-23/same-revision-read-keeps-unconfirmed', 'seed-23/observation-preserves-typed-reservation', 'seed-23/older-outcome-after-new-observation-is-stale', 'seed-23/newer-read-settles-without-replay', 'seed-23/old-intent-cannot-be-replayed-after-read', 'seed-23/fresh-explicit-intent-can-follow-new-observation', 'seed-23/full-width-request-preserved', 'seed-24/given-complete-domain', 'seed-24/positive-proposal-complete-domain-and-wire', 'seed-24/pending-duplicate-no-effect', 'seed-24/unknown-retains-complete-reservation', 'seed-24/unknown-duplicate-stable', 'seed-24/unknown-cannot-repeat', 'seed-24/foreign-request-preserves-complete-state', 'seed-24/foreign-service-preserves-complete-state', 'seed-24/invalid-status-preserves-complete-state', 'seed-24/late-committed-settles', 'seed-24/late-submitted-settles-without-invented-observation', 'seed-24/late-refused-retains-spent-intent', 'seed-24/same-revision-read-keeps-unconfirmed', 'seed-24/observation-preserves-typed-reservation', 'seed-24/older-outcome-after-new-observation-is-stale', 'seed-24/newer-read-settles-without-replay', 'seed-24/old-intent-cannot-be-replayed-after-read', 'seed-24/fresh-explicit-intent-can-follow-new-observation', 'seed-24/full-width-request-preserved', 'seed-25/given-complete-domain', 'seed-25/positive-proposal-complete-domain-and-wire', 'seed-25/pending-duplicate-no-effect', 'seed-25/unknown-retains-complete-reservation', 'seed-25/unknown-duplicate-stable', 'seed-25/unknown-cannot-repeat', 'seed-25/foreign-request-preserves-complete-state', 'seed-25/foreign-service-preserves-complete-state', 'seed-25/invalid-status-preserves-complete-state', 'seed-25/late-committed-settles', 'seed-25/late-submitted-settles-without-invented-observation', 'seed-25/late-refused-retains-spent-intent', 'seed-25/same-revision-read-keeps-unconfirmed', 'seed-25/observation-preserves-typed-reservation', 'seed-25/older-outcome-after-new-observation-is-stale', 'seed-25/newer-read-settles-without-replay', 'seed-25/old-intent-cannot-be-replayed-after-read', 'seed-25/fresh-explicit-intent-can-follow-new-observation', 'seed-25/full-width-request-preserved', 'seed-26/given-complete-domain', 'seed-26/positive-proposal-complete-domain-and-wire', 'seed-26/pending-duplicate-no-effect', 'seed-26/unknown-retains-complete-reservation', 'seed-26/unknown-duplicate-stable', 'seed-26/unknown-cannot-repeat', 'seed-26/foreign-request-preserves-complete-state', 'seed-26/foreign-service-preserves-complete-state', 'seed-26/invalid-status-preserves-complete-state', 'seed-26/late-committed-settles', 'seed-26/late-submitted-settles-without-invented-observation', 'seed-26/late-refused-retains-spent-intent', 'seed-26/same-revision-read-keeps-unconfirmed', 'seed-26/observation-preserves-typed-reservation', 'seed-26/older-outcome-after-new-observation-is-stale', 'seed-26/newer-read-settles-without-replay', 'seed-26/old-intent-cannot-be-replayed-after-read', 'seed-26/fresh-explicit-intent-can-follow-new-observation', 'seed-26/full-width-request-preserved', 'seed-27/given-complete-domain', 'seed-27/positive-proposal-complete-domain-and-wire', 'seed-27/pending-duplicate-no-effect', 'seed-27/unknown-retains-complete-reservation', 'seed-27/unknown-duplicate-stable', 'seed-27/unknown-cannot-repeat', 'seed-27/foreign-request-preserves-complete-state', 'seed-27/foreign-service-preserves-complete-state', 'seed-27/invalid-status-preserves-complete-state', 'seed-27/late-committed-settles', 'seed-27/late-submitted-settles-without-invented-observation', 'seed-27/late-refused-retains-spent-intent', 'seed-27/same-revision-read-keeps-unconfirmed', 'seed-27/observation-preserves-typed-reservation', 'seed-27/older-outcome-after-new-observation-is-stale', 'seed-27/newer-read-settles-without-replay', 'seed-27/old-intent-cannot-be-replayed-after-read', 'seed-27/fresh-explicit-intent-can-follow-new-observation', 'seed-27/full-width-request-preserved', 'seed-28/given-complete-domain', 'seed-28/positive-proposal-complete-domain-and-wire', 'seed-28/pending-duplicate-no-effect', 'seed-28/unknown-retains-complete-reservation', 'seed-28/unknown-duplicate-stable', 'seed-28/unknown-cannot-repeat', 'seed-28/foreign-request-preserves-complete-state', 'seed-28/foreign-service-preserves-complete-state', 'seed-28/invalid-status-preserves-complete-state', 'seed-28/late-committed-settles', 'seed-28/late-submitted-settles-without-invented-observation', 'seed-28/late-refused-retains-spent-intent', 'seed-28/same-revision-read-keeps-unconfirmed', 'seed-28/observation-preserves-typed-reservation', 'seed-28/older-outcome-after-new-observation-is-stale', 'seed-28/newer-read-settles-without-replay', 'seed-28/old-intent-cannot-be-replayed-after-read', 'seed-28/fresh-explicit-intent-can-follow-new-observation', 'seed-28/full-width-request-preserved', 'seed-29/given-complete-domain', 'seed-29/positive-proposal-complete-domain-and-wire', 'seed-29/pending-duplicate-no-effect', 'seed-29/unknown-retains-complete-reservation', 'seed-29/unknown-duplicate-stable', 'seed-29/unknown-cannot-repeat', 'seed-29/foreign-request-preserves-complete-state', 'seed-29/foreign-service-preserves-complete-state', 'seed-29/invalid-status-preserves-complete-state', 'seed-29/late-committed-settles', 'seed-29/late-submitted-settles-without-invented-observation', 'seed-29/late-refused-retains-spent-intent', 'seed-29/same-revision-read-keeps-unconfirmed', 'seed-29/observation-preserves-typed-reservation', 'seed-29/older-outcome-after-new-observation-is-stale', 'seed-29/newer-read-settles-without-replay', 'seed-29/old-intent-cannot-be-replayed-after-read', 'seed-29/fresh-explicit-intent-can-follow-new-observation', 'seed-29/full-width-request-preserved', 'seed-30/given-complete-domain', 'seed-30/positive-proposal-complete-domain-and-wire', 'seed-30/pending-duplicate-no-effect', 'seed-30/unknown-retains-complete-reservation', 'seed-30/unknown-duplicate-stable', 'seed-30/unknown-cannot-repeat', 'seed-30/foreign-request-preserves-complete-state', 'seed-30/foreign-service-preserves-complete-state', 'seed-30/invalid-status-preserves-complete-state', 'seed-30/late-committed-settles', 'seed-30/late-submitted-settles-without-invented-observation', 'seed-30/late-refused-retains-spent-intent', 'seed-30/same-revision-read-keeps-unconfirmed', 'seed-30/observation-preserves-typed-reservation', 'seed-30/older-outcome-after-new-observation-is-stale', 'seed-30/newer-read-settles-without-replay', 'seed-30/old-intent-cannot-be-replayed-after-read', 'seed-30/fresh-explicit-intent-can-follow-new-observation', 'seed-30/full-width-request-preserved', 'seed-31/given-complete-domain', 'seed-31/positive-proposal-complete-domain-and-wire', 'seed-31/pending-duplicate-no-effect', 'seed-31/unknown-retains-complete-reservation', 'seed-31/unknown-duplicate-stable', 'seed-31/unknown-cannot-repeat', 'seed-31/foreign-request-preserves-complete-state', 'seed-31/foreign-service-preserves-complete-state', 'seed-31/invalid-status-preserves-complete-state', 'seed-31/late-committed-settles', 'seed-31/late-submitted-settles-without-invented-observation', 'seed-31/late-refused-retains-spent-intent', 'seed-31/same-revision-read-keeps-unconfirmed', 'seed-31/observation-preserves-typed-reservation', 'seed-31/older-outcome-after-new-observation-is-stale', 'seed-31/newer-read-settles-without-replay', 'seed-31/old-intent-cannot-be-replayed-after-read', 'seed-31/fresh-explicit-intent-can-follow-new-observation', 'seed-31/full-width-request-preserved', 'desktop/given-counter-and-complete-child-pinned', 'desktop/given-proposal-full-ordered-effect', 'desktop/unknown-full-model-and-every-effect', 'desktop/duplicate-unknown-full-model-no-effect', 'desktop/unknown-no-replay-full-model', 'desktop/late-refused-full-model-and-every-effect', 'desktop/late-submitted-full-model-and-every-effect', 'desktop/wrong-request-preserves-full-model', 'desktop/foreign-binding-preserves-full-model', 'desktop/foreign-service-preserves-full-model', 'desktop/malformed-status-preserves-full-model', 'desktop/null-status-preserves-full-model', 'desktop/refresh-full-model-and-exact-read-effect', 'desktop/matching-newer-read-full-model-no-replay', 'capability/network-yes-complete-model-wire', 'capability/network-no-complete-model-wire', 'capability/network-auth-complete-model-wire', 'capability/power-suspend-yes-complete-model-wire', 'capability/power-reboot-yes-complete-model-wire', 'capability/power-poweroff-yes-complete-model-wire', 'capability/power-suspend-no-complete-model-wire', 'capability/power-reboot-no-complete-model-wire', 'capability/power-poweroff-no-complete-model-wire', 'capability/power-suspend-na-complete-model-wire', 'capability/power-reboot-na-complete-model-wire', 'capability/power-poweroff-na-complete-model-wire', 'capability/power-suspend-challenge-complete-model-wire', 'capability/power-reboot-challenge-complete-model-wire', 'capability/power-poweroff-challenge-complete-model-wire', 'capability/network-cross-domain-rejected', 'capability/power-cross-domain-rejected', 'session/closing-complete-model-no-wire', 'session/active-complete-model-and-wire', 'session/online-complete-model-and-wire', 'session/open-text-complete-model-and-wire', 'session/empty-complete-model-and-wire', 'session/case-sensitive-complete-model-and-wire', 'session/near-closing-complete-model-and-wire', 'session/maximum-text-complete-model-and-wire', 'session/overlong-text-rejected', 'session/control-text-rejected', 'session/non-string-rejected'], 'SystemMenuFocusPipeline': ['missingPointerObservationRefusesOpen', 'foreignIdleRefusesThenCurrentIdleAllows', 'confirmationPublishesSuccessorAndFocus', 'cancellationPublishesSuccessorAndFocus', 'literalFullModelsAndOrderedEffects', 'staleThenValid', 'duplicateCancelRefused', 'unavailableNetworkDisabled', 'observedVolumeDisplayed'], 'SuccessorFocusReplay': ['opened-current-available-snapshot', 'unavailable-network-refused-no-send', 'remaining-observed-state', 'prompt-focus-matches-literal-successor-and-enabled-row', 'cancel-focus-matches-literal-successor-and-enabled-row', 'stale-refused-then-valid-cancel', 'duplicate-cancel-stutters', 'foreign-binding-old-stamp-refused', 'exhaustion-emits-no-focus', 'close-requests-current-system-opener', 'renderer-rejects-foreign-and-stale-then-valid'], 'SystemMenuFocusExtended': ['sessionClosingClassifiedAndLogoutDenied', 'otherSessionTextLabelAndLogoutPreserved', 'sessionStateBoundsAndTypeRefused', 'networkPermissionsPreserveAdmission', 'powerCapabilitiesPreserveAdmission', 'foreignNetworkCapabilityRefused', 'foreignPowerPermissionRefused', 'powerCapabilityLabelsPreserved', 'systemMenuOpenerIntegrated', 'menuModeAcceptedByProductionRenderer', 'openingReadFocusMatchesCloseControl', 'originalUnavailableNetworkShown', 'remainingStateObserved', 'oneExplicitVolumeChange', 'pendingCannotRepeat', 'committedCannotRepeatOldRevision', 'unknownCannotReplay', 'readReconcilesChangedStateWithoutEffect', 'unavailableNeverSubmits', 'restartRequiresUIConfirmation', 'cancelHasNoNativeEffect', 'confirmedRestartSubmitsOnce', 'directConfirmationCannotBypassPrompt', 'wrongReceiptCannotSettle', 'staleViewCannotSubmit', 'closingFocusesOpenerWithoutNativeEffect', 'staleCloseRefusedThenCurrentCloseFocusesExactOpener', 'cancelConfirmationEmitsCloseFocus', 'confirmationExactFullModelAndSuccessorEffect', 'cancellationExactFullModelAndSuccessorEffect', 'oldConfirmationStampRefusedThenCurrentAccepted', 'oldRevisionRefusedThenCurrentAccepted', 'closedMenuRefusesConfirmation', 'confirmationFocusesCurrentEligibleCancel', 'cancelTargetIsCurrentEnabledCloseControl', 'staleCancelCannotRefocusThenValidCancelRestoresCurrentClose', 'duplicateCancelCannotRefocus', 'oldBindingStampCannotCancelForeignModel', 'exhaustedPresentationEmitsNoConfirmationFocus', 'disabledAndForeignActionsRefusedThenCurrentCloseAvailable', 'anotherPopupRetiresSystemWithoutLosingNativeState', 'allControlsHaveNames']}


def workspace_owner_baseline_frontend(output, env, packet, run):
    """Fixed isolated observer; expected semantic RED, no native acceptance."""
    frontend = output / 'workspace-owner-baseline'
    frontend.mkdir(mode=0o700)
    source = ROOT / 'implementation/warlock'
    before = inventory(source / 'src')
    cache_before = inventory(Path(packet['elmHome']))
    reviewed = json.loads((output / 'report.json').read_text())['sourceHashes']
    exact = {'docs/elm-roadmap/INTERACTION.md': '2a947a3aa56d7b7b9e7d2f5c1ceb100ac7b8c345a73fd7616c0c4c567d0e01c4', 'implementation/warlock/src/Desktop.elm': '2ef557760c8405dd5dce7172ca29a5d81525fc6738d017cec0008a09b10a08db', 'implementation/warlock/src/Surface.elm': '175d4432e2a28c18cfa18e72f2effc61bf8d551ddce0679e14e25681fc78ec1c', 'implementation/warlock/qa/WorkspaceOwnerLiteralReplay.elm': '5c16d6a1417227419a2ae3b47175197b6458b00021be2ee49b269c6087702309', 'implementation/warlock/qa/Desktop-test-observer.txt': 'f3cc8e83d12fa54d23b6ae1cd1a816b70847f143163382b5f29798b100f29ca0', 'implementation/warlock/qa/workspace-owner-literal-fixed.cjs': '27af6d45c562bad906693fc9270ba6b7c1884b0ac9999960a284b014dd6101db', 'implementation/warlock/qa/workspace-owner-baseline-fixed.cjs': '0556836f1fe1cc02c8b548f6c85492a80b6a172b51081a6260a58954e2b92746'}
    if any(reviewed.get(name) != expected for name, expected in exact.items()):
        raise RuntimeError('Baseline source, policy, fixture or overlay differs')
    shutil.copytree(source / 'src', frontend / 'src')
    shutil.copytree(Path(packet['elmHome']), frontend / 'elm-home')
    (frontend / 'qa').mkdir(mode=0o700)
    (frontend / 'assets').mkdir(mode=0o700)
    qa_files = sorted(name for name in arm64_inputs(ROOT, workspace_owner_baseline=True)
                      if name.startswith('implementation/warlock/qa/'))
    for name in qa_files:
        shutil.copyfile(ROOT / name, frontend / 'qa' / Path(name).name)
    desktop = frontend / 'src/Desktop.elm'
    if digest(desktop) != exact['implementation/warlock/src/Desktop.elm']:
        raise RuntimeError('Unexpected copied Desktop baseline')
    shutil.copyfile(frontend / 'qa/Desktop-test-observer.txt', desktop)
    isolated_source = inventory(frontend / 'src')
    config = json.loads((source / 'elm.json').read_text())
    config['source-directories'] = ['src', 'qa']
    (frontend / 'elm.json').write_text(json.dumps(config, sort_keys=True) + '\n')
    config_hash = digest(frontend / 'elm.json')
    def unchanged():
        return (inventory(source / 'src') == before and inventory(frontend / 'src') == isolated_source
                and inventory(Path(packet['elmHome'])) == cache_before
                and inventory(frontend / 'elm-home') == cache_before
                and digest(frontend / 'elm.json') == config_hash
                and all(digest(ROOT / name) == reviewed[name]
                        and digest(frontend / 'qa' / Path(name).name) == reviewed[name] for name in qa_files))
    if not unchanged():
        raise RuntimeError('Baseline source/cache closure differs')
    for key in ('node', 'elm'):
        with Path(packet[key]).open('rb') as stream:
            header = stream.read(20)
        if header[:6] != b'\x7fELF\x02\x01' or int.from_bytes(header[18:20], 'little') != 183:
            raise RuntimeError('Expected pinned ELF64 little-endian AArch64 ' + key)
    build_env = dict(env, ELM_HOME=str(frontend / 'elm-home'))
    target = frontend / 'assets/workspace-owner-literal-baseline.js'
    run('compile-WorkspaceOwnerLiteralReplay', [packet['elm'], 'make',
        'qa/WorkspaceOwnerLiteralReplay.elm', '--optimize', '--output=' + str(target)], frontend, 180, build_env)
    compiled = image(target)
    raw = run('workspace-owner-baseline', [packet['node'], frontend / 'qa/workspace-owner-baseline-fixed.cjs'], frontend, 180, build_env)
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeError('Duplicate terminal receipt key: ' + key)
            result[key] = value
        return result
    receipt = json.loads(raw, object_pairs_hook=unique_pairs)
    expected = ['literalFixturePreconditions', 'completeOpenedDesktopMatchesBaselinePlusLiteralChanges', 'orderedOpenEffectsArePublishThenLiteralFocus', 'completeClosedDesktopExceptOpaqueReturnFocus', 'orderedCloseEffectsArePublishThenOneRead', 'registeredOpenHasExactFocusAndNoRequests', 'registeredCloseHasExactReadAndNoMutation', 'matchedReadReturnsExactOriginalOpener', 'duplicateReadCannotRepeatFocus', 'overviewOwnerAndLiteralUnsupportedControls', 'keyboardAndPointerUnsupportedCallbacksStutter', 'foreignReplacementAndStaleCallbacksStutter', 'foreignEnabledCloseCannotDismiss', 'replacementEnabledCloseCannotDismiss', 'staleEnabledCloseCannotDismiss', 'validEnabledCloseAfterRefusalsWorks', 'duplicateEnabledCloseCannotReapply', 'policyRejectsInvalidScopesWithoutEffects', 'validEscapeAfterRefusalsClosesWithoutMutation', 'zeroOutputRetiresUnsupportedOwner', 'returnedOutputRejectsRetiredOwner', 'noOpEffectsDoNotRegisterCommand', 'topologyTransitionsDoNotMutateWorkspace', 'duplicateEscapeIsInert']
    if set(receipt) != {'classification','requirement','scenario','failed','checkNames','checks','nativeAcceptance','originalAcceptance'}:
        raise RuntimeError('Baseline receipt shape differs')
    if (receipt['classification'] != 'EXPECTED_COMPONENT_RED' or receipt['requirement'] != 'ELM-UI-006'
            or receipt['scenario'] != 'workspace-management-unavailable'
            or receipt['failed'] != ['overviewOwnerAndLiteralUnsupportedControls']
            or receipt['checkNames'] != expected or set(receipt['checks']) != set(expected)
            or any(receipt['checks'][name] is not (name != 'overviewOwnerAndLiteralUnsupportedControls') for name in expected)
            or receipt['nativeAcceptance'] is not False or receipt['originalAcceptance'] is not False):
        raise RuntimeError('Baseline RED differs or another check failed')
    if not unchanged() or image(target) != compiled:
        raise RuntimeError('Baseline source/cache/image changed')
    return {'classification':'EXPECTED_COMPONENT_RED','receipt':receipt,'compiled':compiled,
            'driverSha256':digest(frontend / 'qa/workspace-owner-baseline-fixed.cjs'),
            'stdoutSha256':digest(output / 'logs/workspace-owner-baseline.stdout'),
            'nativeAcceptance':False,'originalAcceptance':False,'releaseAccepted':False,
            'opaqueCmdASTObserved':False,'productionRootBehaviorExecuted':False}


def workspace_dom_frontend(output, env, packet, run):
    """Pinned controlled-DOM replay; no browser, native or AT evidence."""
    frontend = output / 'workspace-dom'
    frontend.mkdir(mode=0o700)
    source = ROOT / 'implementation/warlock'
    before = inventory(source / 'src')
    cache_before = inventory(Path(packet['elmHome']))
    reviewed = json.loads((output / 'report.json').read_text())['sourceHashes']
    exact = {
        'docs/elm-roadmap/INTERACTION.md': '2a947a3aa56d7b7b9e7d2f5c1ceb100ac7b8c345a73fd7616c0c4c567d0e01c4',
        'implementation/warlock/src/Desktop.elm': '2ef557760c8405dd5dce7172ca29a5d81525fc6738d017cec0008a09b10a08db',
        'implementation/warlock/src/Surface.elm': '9b49b673cde2d2a9252e3b461b1fb8d3229fb5a4d5ed0321af03f74178d5869e',
        'implementation/warlock/qa/WorkspaceUnsupportedDomReplay.elm': '3e0e22f15e35d766077fa48c4dbd41bfd9720eae7fab84007183786573a739d4',
        'implementation/warlock/qa/workspace-unsupported-dom-fixed.cjs': 'e35c5ef36dfe45cae8c9a22636bb98087c7e22edcbc47a4346ed6098c6cc3540',
        'implementation/warlock/qa/ui006-dom-guard.js': 'f91b7ee19600d4043d1ae1cf17f4ddff7e994e2bab5cf40bb671f04623f2b7cb',
        'implementation/warlock/qa/ui006-dom-guard.html': 'ae222696c9ea4bcdeec1b0e19e5e930ee81f33c0ff88a30f8bdeb16aace4026f',
    }
    if any(reviewed.get(name) != expected for name, expected in exact.items()):
        raise RuntimeError('Workspace DOM source/policy/fixture differs')
    shutil.copytree(source / 'src', frontend / 'src')
    shutil.copytree(Path(packet['elmHome']), frontend / 'elm-home')
    (frontend / 'qa').mkdir(mode=0o700)
    (frontend / 'assets').mkdir(mode=0o700)
    qa_files = sorted(name for name in arm64_inputs(ROOT, workspace_dom=True)
                      if name.startswith('implementation/warlock/qa/'))
    for name in qa_files:
        shutil.copyfile(ROOT / name, frontend / 'qa' / Path(name).name)
    isolated_source = inventory(frontend / 'src')
    if isolated_source != before:
        raise RuntimeError('Workspace DOM copied source differs from inventoried root source')
    src_prefix = 'implementation/warlock/src/'
    reviewed_elm = {name[len(src_prefix):]: sha for name, sha in reviewed.items()
                    if name.startswith(src_prefix) and name.endswith('.elm')}
    staged_elm = {str(path.relative_to(frontend / 'src')): digest(path)
                  for path in (frontend / 'src').rglob('*.elm')}
    if not reviewed_elm or staged_elm != reviewed_elm:
        raise RuntimeError('Workspace DOM staged Elm differs from reviewed source hashes')
    config_bytes = (source / 'elm.json').read_bytes()
    if hashlib.sha256(config_bytes).hexdigest() != reviewed['implementation/warlock/elm.json']:
        raise RuntimeError('Workspace DOM copied configuration differs from reviewed source')
    config = json.loads(config_bytes)
    config['source-directories'] = ['src', 'qa']
    (frontend / 'elm.json').write_text(json.dumps(config, sort_keys=True) + '\n')
    config_hash = digest(frontend / 'elm.json')
    def unchanged():
        return (inventory(source / 'src') == before and inventory(frontend / 'src') == isolated_source
                and inventory(Path(packet['elmHome'])) == cache_before
                and inventory(frontend / 'elm-home') == cache_before
                and digest(frontend / 'elm.json') == config_hash
                and all(digest(ROOT / name) == reviewed[name]
                        and digest(frontend / 'qa' / Path(name).name) == reviewed[name] for name in qa_files))
    if not unchanged():
        raise RuntimeError('Workspace DOM source/cache closure differs')
    for key in ('node', 'elm'):
        with Path(packet[key]).open('rb') as stream:
            header = stream.read(20)
        if header[:6] != b'\x7fELF\x02\x01' or int.from_bytes(header[18:20], 'little') != 183:
            raise RuntimeError('Expected pinned ELF64 little-endian AArch64 ' + key)
    build_env = dict(env, ELM_HOME=str(frontend / 'elm-home'))
    target = frontend / 'assets/workspace-unsupported-dom.js'
    run('compile-WorkspaceUnsupportedDomReplay', [packet['elm'], 'make',
        'qa/WorkspaceUnsupportedDomReplay.elm', '--optimize', '--output=' + str(target)], frontend, 180, build_env)
    compiled = image(target)
    raw = run('workspace-dom', [packet['node'], frontend / 'qa/workspace-unsupported-dom-fixed.cjs'], frontend, 180, build_env)
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeError('Duplicate terminal receipt key: ' + key)
            result[key] = value
        return result
    receipt = json.loads(raw, object_pairs_hook=unique_pairs)
    expected = ['literalOrder'] + [identity + '/' + suffix for identity in
        ['overview:workspace-create','overview:workspace-delete','overview:workspace-rename']
        for suffix in ['identity','label','detail','disabledRole','noClickHandler']] + [
        'closeContrast','packetAndStale','oneCloseAfterRefusal']
    if (set(receipt) != {'classification','checks','names','nativeAcceptance','originalAcceptance'}
            or receipt['classification'] != 'CONTROLLED_DOM_GREEN'
            or receipt['names'] != expected or set(receipt['checks']) != set(expected)
            or any(receipt['checks'][name] is not True for name in expected)
            or receipt['nativeAcceptance'] is not False or receipt['originalAcceptance'] is not False):
        raise RuntimeError('Controlled DOM receipt differs or any check failed')
    if not unchanged() or image(target) != compiled:
        raise RuntimeError('Workspace DOM source/cache/image changed')
    return {'classification':'CONTROLLED_DOM_GREEN','receipt':receipt,'compiled':compiled,
            'driverSha256':digest(frontend / 'qa/workspace-unsupported-dom-fixed.cjs'),
            'stdoutSha256':digest(output / 'logs/workspace-dom.stdout'),
            'nativeAcceptance':False,'originalAcceptance':False,'releaseAccepted':False,
            'browserObserved':False,'browserGuardExecuted':False,'nativeFocusObserved':False}


def workspace_owner_component_frontend(output, env, packet, run):
    """Fixed isolated observer; expected component GREEN, no native acceptance."""
    frontend = output / 'workspace-owner-component'
    frontend.mkdir(mode=0o700)
    source = ROOT / 'implementation/warlock'
    before = inventory(source / 'src')
    cache_before = inventory(Path(packet['elmHome']))
    reviewed = json.loads((output / 'report.json').read_text())['sourceHashes']
    exact = {'docs/elm-roadmap/INTERACTION.md': '2a947a3aa56d7b7b9e7d2f5c1ceb100ac7b8c345a73fd7616c0c4c567d0e01c4', 'implementation/warlock/src/Desktop.elm': '2ef557760c8405dd5dce7172ca29a5d81525fc6738d017cec0008a09b10a08db', 'implementation/warlock/src/Surface.elm': '9b49b673cde2d2a9252e3b461b1fb8d3229fb5a4d5ed0321af03f74178d5869e', 'implementation/warlock/qa/WorkspaceOwnerComponentReplay.elm': 'da9f4839fa32bb3f4c90a2e569d6bfcd76d80c39e197da4ed2557f2a959e00c0', 'implementation/warlock/qa/Desktop-test-observer.txt': 'f3cc8e83d12fa54d23b6ae1cd1a816b70847f143163382b5f29798b100f29ca0', 'implementation/warlock/qa/workspace-owner-component-fixed.cjs': '9559ca5ec6a5fce7733bc7158759d1be1f0c9ab98dbe0af0aebfe5eda50fffb5'}
    if any(reviewed.get(name) != expected for name, expected in exact.items()):
        raise RuntimeError('Baseline source, policy, fixture or overlay differs')
    shutil.copytree(source / 'src', frontend / 'src')
    shutil.copytree(Path(packet['elmHome']), frontend / 'elm-home')
    (frontend / 'qa').mkdir(mode=0o700)
    (frontend / 'assets').mkdir(mode=0o700)
    qa_files = sorted(name for name in arm64_inputs(ROOT, workspace_owner_component=True)
                      if name.startswith('implementation/warlock/qa/'))
    for name in qa_files:
        shutil.copyfile(ROOT / name, frontend / 'qa' / Path(name).name)
    desktop = frontend / 'src/Desktop.elm'
    if digest(desktop) != exact['implementation/warlock/src/Desktop.elm']:
        raise RuntimeError('Unexpected copied Desktop baseline')
    shutil.copyfile(frontend / 'qa/Desktop-test-observer.txt', desktop)
    isolated_source = inventory(frontend / 'src')
    config = json.loads((source / 'elm.json').read_text())
    config['source-directories'] = ['src', 'qa']
    (frontend / 'elm.json').write_text(json.dumps(config, sort_keys=True) + '\n')
    config_hash = digest(frontend / 'elm.json')
    def unchanged():
        return (inventory(source / 'src') == before and inventory(frontend / 'src') == isolated_source
                and inventory(Path(packet['elmHome'])) == cache_before
                and inventory(frontend / 'elm-home') == cache_before
                and digest(frontend / 'elm.json') == config_hash
                and all(digest(ROOT / name) == reviewed[name]
                        and digest(frontend / 'qa' / Path(name).name) == reviewed[name] for name in qa_files))
    if not unchanged():
        raise RuntimeError('Baseline source/cache closure differs')
    for key in ('node', 'elm'):
        with Path(packet[key]).open('rb') as stream:
            header = stream.read(20)
        if header[:6] != b'\x7fELF\x02\x01' or int.from_bytes(header[18:20], 'little') != 183:
            raise RuntimeError('Expected pinned ELF64 little-endian AArch64 ' + key)
    build_env = dict(env, ELM_HOME=str(frontend / 'elm-home'))
    target = frontend / 'assets/workspace-owner-component.js'
    run('compile-WorkspaceOwnerComponentReplay', [packet['elm'], 'make',
        'qa/WorkspaceOwnerComponentReplay.elm', '--optimize', '--output=' + str(target)], frontend, 180, build_env)
    compiled = image(target)
    raw = run('workspace-owner-component', [packet['node'], frontend / 'qa/workspace-owner-component-fixed.cjs'], frontend, 180, build_env)
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeError('Duplicate terminal receipt key: ' + key)
            result[key] = value
        return result
    receipt = json.loads(raw, object_pairs_hook=unique_pairs)
    expected = ['literalFixturePreconditions', 'completeOpenedDesktopMatchesBaselinePlusLiteralChanges', 'orderedOpenEffectsArePublishThenLiteralFocus', 'completeClosedDesktopExceptOpaqueReturnFocus', 'orderedCloseEffectsArePublishThenOneRead', 'registeredOpenHasExactFocusAndNoRequests', 'registeredCloseHasExactReadAndNoMutation', 'matchedReadReturnsExactOriginalOpener', 'duplicateReadCannotRepeatFocus', 'overviewOwnerAndLiteralUnsupportedControls', 'keyboardAndPointerUnsupportedCallbacksStutter', 'foreignReplacementAndStaleCallbacksStutter', 'foreignEnabledCloseCannotDismiss', 'replacementEnabledCloseCannotDismiss', 'staleEnabledCloseCannotDismiss', 'validEnabledCloseAfterRefusalsWorks', 'duplicateEnabledCloseCannotReapply', 'policyRejectsInvalidScopesWithoutEffects', 'validEscapeAfterRefusalsClosesWithoutMutation', 'zeroOutputRetiresUnsupportedOwner', 'returnedOutputRejectsRetiredOwner', 'noOpEffectsDoNotRegisterCommand', 'topologyTransitionsDoNotMutateWorkspace', 'duplicateEscapeIsInert']
    if set(receipt) != {'classification','requirement','scenario','failed','checkNames','checks','nativeAcceptance','originalAcceptance'}:
        raise RuntimeError('Baseline receipt shape differs')
    if (receipt['classification'] != 'COMPONENT_GREEN' or receipt['requirement'] != 'ELM-UI-006'
            or receipt['scenario'] != 'workspace-management-unavailable'
            or receipt['failed'] != []
            or receipt['checkNames'] != expected or set(receipt['checks']) != set(expected)
            or any(receipt['checks'][name] is not True for name in expected)
            or receipt['nativeAcceptance'] is not False or receipt['originalAcceptance'] is not False):
        raise RuntimeError('Component GREEN differs or any check failed')
    if not unchanged() or image(target) != compiled:
        raise RuntimeError('Baseline source/cache/image changed')
    return {'classification':'COMPONENT_GREEN','receipt':receipt,'compiled':compiled,
            'driverSha256':digest(frontend / 'qa/workspace-owner-component-fixed.cjs'),
            'stdoutSha256':digest(output / 'logs/workspace-owner-component.stdout'),
            'nativeAcceptance':False,'originalAcceptance':False,'releaseAccepted':False,
            'opaqueCmdASTObserved':False,'productionRootBehaviorExecuted':False}


def workspace_owner_component_red_frontend(output, env, packet, run):
    """Fixed isolated observer; expected component RED, no native acceptance."""
    frontend = output / 'workspace-owner-component-red'
    frontend.mkdir(mode=0o700)
    source = ROOT / 'implementation/warlock'
    before = inventory(source / 'src')
    cache_before = inventory(Path(packet['elmHome']))
    reviewed = json.loads((output / 'report.json').read_text())['sourceHashes']
    exact = {'docs/elm-roadmap/INTERACTION.md': '2a947a3aa56d7b7b9e7d2f5c1ceb100ac7b8c345a73fd7616c0c4c567d0e01c4', 'implementation/warlock/src/Desktop.elm': '2ef557760c8405dd5dce7172ca29a5d81525fc6738d017cec0008a09b10a08db', 'implementation/warlock/src/Surface.elm': '175d4432e2a28c18cfa18e72f2effc61bf8d551ddce0679e14e25681fc78ec1c', 'implementation/warlock/qa/WorkspaceOwnerComponentReplay.elm': 'da9f4839fa32bb3f4c90a2e569d6bfcd76d80c39e197da4ed2557f2a959e00c0', 'implementation/warlock/qa/Desktop-test-observer.txt': 'f3cc8e83d12fa54d23b6ae1cd1a816b70847f143163382b5f29798b100f29ca0', 'implementation/warlock/qa/workspace-owner-component-red-fixed.cjs': 'b957ff98dd32bc28db4743937602d4e52294ae653a89680bde0ba926ed098881'}
    if any(reviewed.get(name) != expected for name, expected in exact.items()):
        raise RuntimeError('Baseline source, policy, fixture or overlay differs')
    shutil.copytree(source / 'src', frontend / 'src')
    shutil.copytree(Path(packet['elmHome']), frontend / 'elm-home')
    (frontend / 'qa').mkdir(mode=0o700)
    (frontend / 'assets').mkdir(mode=0o700)
    qa_files = sorted(name for name in arm64_inputs(ROOT, workspace_owner_component_red=True)
                      if name.startswith('implementation/warlock/qa/'))
    for name in qa_files:
        shutil.copyfile(ROOT / name, frontend / 'qa' / Path(name).name)
    desktop = frontend / 'src/Desktop.elm'
    if digest(desktop) != exact['implementation/warlock/src/Desktop.elm']:
        raise RuntimeError('Unexpected copied Desktop baseline')
    shutil.copyfile(frontend / 'qa/Desktop-test-observer.txt', desktop)
    isolated_source = inventory(frontend / 'src')
    config = json.loads((source / 'elm.json').read_text())
    config['source-directories'] = ['src', 'qa']
    (frontend / 'elm.json').write_text(json.dumps(config, sort_keys=True) + '\n')
    config_hash = digest(frontend / 'elm.json')
    def unchanged():
        return (inventory(source / 'src') == before and inventory(frontend / 'src') == isolated_source
                and inventory(Path(packet['elmHome'])) == cache_before
                and inventory(frontend / 'elm-home') == cache_before
                and digest(frontend / 'elm.json') == config_hash
                and all(digest(ROOT / name) == reviewed[name]
                        and digest(frontend / 'qa' / Path(name).name) == reviewed[name] for name in qa_files))
    if not unchanged():
        raise RuntimeError('Baseline source/cache closure differs')
    for key in ('node', 'elm'):
        with Path(packet[key]).open('rb') as stream:
            header = stream.read(20)
        if header[:6] != b'\x7fELF\x02\x01' or int.from_bytes(header[18:20], 'little') != 183:
            raise RuntimeError('Expected pinned ELF64 little-endian AArch64 ' + key)
    build_env = dict(env, ELM_HOME=str(frontend / 'elm-home'))
    target = frontend / 'assets/workspace-owner-component-red.js'
    run('compile-WorkspaceOwnerComponentReplay', [packet['elm'], 'make',
        'qa/WorkspaceOwnerComponentReplay.elm', '--optimize', '--output=' + str(target)], frontend, 180, build_env)
    compiled = image(target)
    raw = run('workspace-owner-component-red', [packet['node'], frontend / 'qa/workspace-owner-component-red-fixed.cjs'], frontend, 180, build_env)
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeError('Duplicate terminal receipt key: ' + key)
            result[key] = value
        return result
    receipt = json.loads(raw, object_pairs_hook=unique_pairs)
    expected = ['literalFixturePreconditions', 'completeOpenedDesktopMatchesBaselinePlusLiteralChanges', 'orderedOpenEffectsArePublishThenLiteralFocus', 'completeClosedDesktopExceptOpaqueReturnFocus', 'orderedCloseEffectsArePublishThenOneRead', 'registeredOpenHasExactFocusAndNoRequests', 'registeredCloseHasExactReadAndNoMutation', 'matchedReadReturnsExactOriginalOpener', 'duplicateReadCannotRepeatFocus', 'overviewOwnerAndLiteralUnsupportedControls', 'keyboardAndPointerUnsupportedCallbacksStutter', 'foreignReplacementAndStaleCallbacksStutter', 'foreignEnabledCloseCannotDismiss', 'replacementEnabledCloseCannotDismiss', 'staleEnabledCloseCannotDismiss', 'validEnabledCloseAfterRefusalsWorks', 'duplicateEnabledCloseCannotReapply', 'policyRejectsInvalidScopesWithoutEffects', 'validEscapeAfterRefusalsClosesWithoutMutation', 'zeroOutputRetiresUnsupportedOwner', 'returnedOutputRejectsRetiredOwner', 'noOpEffectsDoNotRegisterCommand', 'topologyTransitionsDoNotMutateWorkspace', 'duplicateEscapeIsInert']
    if set(receipt) != {'classification','requirement','scenario','failed','checkNames','checks','nativeAcceptance','originalAcceptance'}:
        raise RuntimeError('Baseline receipt shape differs')
    if (receipt['classification'] != 'EXPECTED_COMPONENT_RED' or receipt['requirement'] != 'ELM-UI-006'
            or receipt['scenario'] != 'workspace-management-unavailable'
            or receipt['failed'] != ['overviewOwnerAndLiteralUnsupportedControls']
            or receipt['checkNames'] != expected or set(receipt['checks']) != set(expected)
            or any(receipt['checks'][name] is not (name != 'overviewOwnerAndLiteralUnsupportedControls') for name in expected)
            or receipt['nativeAcceptance'] is not False or receipt['originalAcceptance'] is not False):
        raise RuntimeError('Component RED differs or other check failed')
    if not unchanged() or image(target) != compiled:
        raise RuntimeError('Baseline source/cache/image changed')
    return {'classification':'EXPECTED_COMPONENT_RED','receipt':receipt,'compiled':compiled,
            'driverSha256':digest(frontend / 'qa/workspace-owner-component-red-fixed.cjs'),
            'stdoutSha256':digest(output / 'logs/workspace-owner-component-red.stdout'),
            'nativeAcceptance':False,'originalAcceptance':False,'releaseAccepted':False,
            'opaqueCmdASTObserved':False,'productionRootBehaviorExecuted':False}


def workspace_original_frontend(output, env, packet, run):
    """Fixed original three-worker source replay; no native acceptance."""
    frontend = output / 'workspace-original'
    frontend.mkdir(mode=0o700)
    source = ROOT / 'implementation/warlock'
    source_before = inventory(source / 'src')
    cache_before = inventory(Path(packet['elmHome']))
    reviewed = json.loads((output / 'report.json').read_text())['sourceHashes']
    expected_cache = packet['trees'][packet['elmHome']]
    if cache_before != expected_cache:
        raise RuntimeError('Workspace original cache differs from verified ARM manifest')
    src_prefix = 'implementation/warlock/src/'
    reviewed_src = {name[len(src_prefix):]: sha for name, sha in reviewed.items()
                    if name.startswith(src_prefix) and name.endswith('.elm')}
    def matches_reviewed_src(directory):
        files = {str(path.relative_to(directory)): path for path in directory.rglob('*.elm')}
        return set(files) == set(reviewed_src) and all(digest(files[name]) == sha for name, sha in reviewed_src.items())
    if not matches_reviewed_src(source / 'src'):
        raise RuntimeError('Workspace original source differs from reviewed closure')
    exact = {'docs/elm-roadmap/INTERACTION.md': '2a947a3aa56d7b7b9e7d2f5c1ceb100ac7b8c345a73fd7616c0c4c567d0e01c4', 'implementation/warlock/src/Surface.elm': '9b49b673cde2d2a9252e3b461b1fb8d3229fb5a4d5ed0321af03f74178d5869e', 'implementation/warlock/src/Desktop.elm': '2ef557760c8405dd5dce7172ca29a5d81525fc6738d017cec0008a09b10a08db', 'implementation/warlock/qa/TaskViewReplay.elm': '9f2a30aaecbd0069b1d297d029cfff9126c506dd39bcdcc6c871e6189c53c9b6', 'implementation/warlock/qa/TaskViewEscapeReplay.elm': '9f95642d106544223fcae61f3b81a684853276ed8b7de461437267d9dba33ac8', 'implementation/warlock/qa/WorkspaceNavigationReplay.elm': '92d2907941ebb0530b6f2d77b20fa1a8fe41bd516610daee993f352550284ffe', 'implementation/warlock/qa/OutputRetirementReplay.elm': 'fc288be90c83b37ad007bfe4fe8a7224bbd2359773aa599a2bc97bbeddb152b9', 'implementation/warlock/qa/NativePointerFixture.elm': 'b674baa48a0d0197d32e6bc400412465e3a83934d3a749ebc7cbba35e82c4124', 'implementation/warlock/qa/task-view-original-fixed.cjs': 'b7672f4d45e8eeb4cd2dad4cec9a158441e865fc068e665017903353895cfbc7'}
    if any(reviewed.get(name) != expected for name, expected in exact.items()):
        raise RuntimeError('Workspace original reviewed source differs')
    shutil.copytree(source / 'src', frontend / 'src')
    shutil.copytree(Path(packet['elmHome']), frontend / 'elm-home')
    (frontend / 'qa').mkdir(mode=0o700)
    (frontend / 'assets').mkdir(mode=0o700)
    qa_files = sorted(name for name in arm64_inputs(ROOT, workspace_original=True)
                      if name.startswith('implementation/warlock/qa/'))
    for name in qa_files:
        shutil.copyfile(ROOT / name, frontend / 'qa' / Path(name).name)
    config_bytes = (source / 'elm.json').read_bytes()
    if hashlib.sha256(config_bytes).hexdigest() != reviewed['implementation/warlock/elm.json']:
        raise RuntimeError('Workspace original config differs from reviewed closure')
    config = json.loads(config_bytes)
    config['source-directories'] = ['src', 'qa']
    (frontend / 'elm.json').write_text(json.dumps(config, sort_keys=True) + '\n')
    config_hash = digest(frontend / 'elm.json')
    def unchanged():
        return (inventory(source / 'src') == source_before and inventory(frontend / 'src') == source_before
                and matches_reviewed_src(source / 'src') and matches_reviewed_src(frontend / 'src')
                and digest(source / 'elm.json') == reviewed['implementation/warlock/elm.json']
                and inventory(Path(packet['elmHome'])) == expected_cache
                and inventory(frontend / 'elm-home') == expected_cache
                and digest(frontend / 'elm.json') == config_hash
                and all(digest(ROOT / name) == reviewed[name]
                        and digest(frontend / 'qa' / Path(name).name) == reviewed[name] for name in qa_files))
    if not unchanged():
        raise RuntimeError('Workspace original source/cache stage differs')
    for key in ('node', 'elm'):
        with Path(packet[key]).open('rb') as stream:
            header = stream.read(20)
        if header[:6] != b'\x7fELF\x02\x01' or int.from_bytes(header[18:20], 'little') != 183:
            raise RuntimeError('Expected pinned ELF64 little-endian AArch64 ' + key)
    build_env = dict(env, ELM_HOME=str(frontend / 'elm-home'))
    artifacts = {}
    for name in ('TaskViewReplay', 'TaskViewEscapeReplay', 'WorkspaceNavigationReplay'):
        target = frontend / 'assets' / (name + '.js')
        run('compile-' + name, [packet['elm'], 'make', 'qa/' + name + '.elm',
            '--optimize', '--output=' + str(target)], frontend, 180, build_env)
        artifacts[name] = image(target)
    driver = frontend / 'qa/task-view-original-fixed.cjs'
    run('task-view-original', [packet['node'], driver], frontend, 180, build_env)
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise RuntimeError('Duplicate terminal receipt key: ' + key)
            result[key] = value
        return result
    receipt_path = frontend / 'task-view-original-report.json'
    receipt = json.loads(receipt_path.read_text(), object_pairs_hook=unique_pairs)
    if set(receipt) != {'passed', 'fixtures', 'failures', 'runnerPathSha256AtReport'}:
        raise RuntimeError('Workspace original receipt shape differs')
    rows = receipt['fixtures']
    expected = {'TaskViewReplay': ['cancelTransferReturnsSameCurrentEligibleMoveControl', 'duplicateAndStaleTransferCancellationAreInert', 'unavailableTransferOriginReturnsCurrentFilter', 'incoherentTransferOriginReturnsAlwaysAvailableAll', 'removedTransferCapabilityReturnsCurrentFilter', 'filteredOutTransferOriginNeverReceivesFocus', 'retiredTransferOriginNeverSubstitutes', 'unknownReservedTransferOriginIsNotFocusedOrReplayed', 'closedTransferCancelNeverRefocuses', 'allWorkspaceCancelStillReturnsExactOrigin', 'retiredTransferReturnsCurrentRetainedWorkspaceFocus', 'retiredTransferChooserHasVisibleBrowseAndDismissal', 'retiredTransferDoesNotRepeatFocus', 'retiredTransferAndWorkspaceReturnAll', 'incoherentTransferObservationCannotRetireSelection', 'existingUnavailableExactMemberKeepsTransferChooser', 'closedTransferNeverRefocuses', 'sameApplicationNewIncarnationNeverSubstitutes', 'matchedRefusalWaitsForFreshRead', 'exactRefusalRestoresFilteredOverview', 'differentUnknownDuringRefusedReadDoesNotResumeOldOrigin', 'restoredEligibleFamilyGetsCurrentFocus', 'duplicateRefusalCannotReopenOrReplay', 'emittedRestoreCarriesExactFullIntentKey', 'pendingRestoreShowsCorrelatedLabel', 'pendingDuplicateDispatchIsSuppressed', 'refusedRestoreShowsCorrelatedLabel', 'committedChoiceStaysClosed', 'unknownChoiceStaysClosedWithoutReplay', 'unknownRestoreShowsCorrelatedLabel', 'unknownRefreshUsesReadOnlyWireKinds', 'staleUnknownProjectionCannotSettleOrReplay', 'unknownReservationPersistsAcrossFreshRead', 'unknownReadRecoveryReopensExactWorkspaceWithoutReplay', 'unknownReadRecoveryRepeatedOpenPreservesWorkspaceAndFocus', 'unknownReadRecoveryFallsBackToAllWhenWorkspaceDisappears', 'unknownMissingWorkspaceOverviewOpened', 'unknownMissingWorkspaceSelectionCleared', 'unknownMissingWorkspaceFocusTargetsAll', 'unknownMissingWorkspaceNoMutation', 'foreignIntentCannotReturn', 'anotherInterfaceCancelsReturn', 'replacementAuthorityCannotReturn', 'retiredFamilyReturnsToAllWindows', 'unconfirmedTransferRetainsSourceFamilyWithoutInventingNativeOwner', 'emptyInventoryComesThroughExactRootReceipt', 'nativeActiveEmptyMarkerDoesNotNeedFocusedWindow', 'emptyWorkspaceOpensAndBrowsesWithoutEffects', 'emptyWorkspaceKeepsVisibleDismissal', 'emptySelectionHasExplicitNotice', 'emptyWorkspaceDismissalIsReadOnly', 'foreignGeometryCannotInventEmptyWorkspace', 'duplicateWorkspacePacketRejectedByRoot', 'differentGeometrySequenceCannotJoinInventory', 'retiredEmptySelectionFallsBackToAll', 'groupsMatchMembership', 'activeWorkspaceNamed', 'openingIsObservationOnly', 'workspaceBrowseIsLocal', 'overviewInitialAccessibleFilterSelection', 'overviewAccessibleFilterFollowsReadOnlyBrowse', 'staleSelectionInert', 'unavailableWorkspaceNeverActivates', 'retiredIdentityNeverSubstitutes', 'selectionRefreshesBeforeEffect', 'duplicateChoiceInert', 'dismissalDoesNotMutate', 'dismissalDefersDOMFocusUntilFreshRead', 'independentRevisionNamespacesRemainBrowsable', 'mixedOutputMembershipWithheld', 'mixedFocusMembershipWithheld', 'mixedMinimizedMembershipWithheld', 'ordinaryRendererAcceptsTaskView', 'offWorkspaceSelectionRequiresFreshObservation', 'freshObservationRestoresExactWorkspaceTwoRootOnce', 'staleNavigationObservationNeverMutates', 'retiredNavigationRootNeverSubstitutes', 'duplicateNavigationObservationNeverReplays'], 'TaskViewEscapeReplay': ['CurrentOverviewEscapeDismissesWithoutNativeMutation', 'StaleEscapePublicationCannotDismiss', 'StaleEscapeLeaseCannotDismiss', 'ReplacedEscapeOwnerCannotDismiss', 'NumericEscapeCounterCannotDismiss', 'UnexpectedEscapeFieldCannotDismiss', 'DuplicateOldEscapeCannotRemintFocus'], 'WorkspaceNavigationReplay': ['goEmptyWorkspaceControl', 'populatedDestinationCannotGo', 'activeDestinationCannotGo', 'oneTypedNavigation', 'pendingFeedback', 'duplicateSuppressed', 'deadlineUnknownNoReplay', 'unknownCanReopenAndDismiss', 'unknownCannotMutateWindow', 'unknownHasReadOnlyRecovery', 'unknownTaskbarRecoversWithoutNavigation', 'recoveryDoesNotDuplicateRead', 'committedExactReceipt', 'refusedRetainsDestinationContext', 'foreignCannotSettle', 'disconnectNeverReplays']}
    if (receipt['passed'] is not True or receipt['failures'] != []
            or receipt['runnerPathSha256AtReport'] != digest(driver)
            or not isinstance(rows, list) or [row.get('name') for row in rows] != list(expected)):
        raise RuntimeError('Workspace original receipt differs')
    for row in rows:
        name = row['name']
        checks = row.get('checks')
        payload = row.get('payload')
        if (set(row) != {'name', 'sha256', 'checks', 'payload', 'passed'}
                or row['passed'] is not True or row['sha256'] != artifacts[name]['sha256']
                or not isinstance(checks, list) or [c.get('name') for c in checks] != expected[name]
                or any(set(c) != {'name', 'passed'} or c['passed'] is not True for c in checks)
                or not isinstance(payload, dict) or set(payload.get('checks', {})) != set(expected[name])
                or any(v is not True for v in payload['checks'].values())):
            raise RuntimeError('Workspace original case inventory differs: ' + name)
    if not unchanged() or any(image(Path(item['path'])) != item for item in artifacts.values()):
        raise RuntimeError('Workspace original source/cache/image changed')
    return {'scope': 'Three original synthetic component workers only', 'receipt': receipt,
            'receiptSha256': digest(receipt_path), 'artifacts': artifacts,
            'driverSha256': digest(driver), 'nativeAcceptance': False,
            'originalAcceptance': False, 'releaseAccepted': False,
            'opaqueCmdASTObserved': False, 'productionRootBehaviorExecuted': False}


def successor_focus_frontend(output, env, packet, run):
    """Fixed synthetic successor focus checks; no native/AT or Cmd-AST proof."""
    frontend = output / 'successor-focus'
    frontend.mkdir(mode=0o700)
    source = ROOT / 'implementation/warlock'
    source_before = inventory(source / 'src')
    cache_before = inventory(Path(packet['elmHome']))
    reviewed = json.loads((output / 'report.json').read_text())['sourceHashes']
    shutil.copytree(source / 'src', frontend / 'src')
    shutil.copytree(Path(packet['elmHome']), frontend / 'elm-home')
    (frontend / 'qa').mkdir(mode=0o700)
    qa_files = [name for name in arm64_inputs(ROOT, successor_focus=True)
                if name.startswith('implementation/warlock/qa/')]
    for name in qa_files:
        shutil.copyfile(ROOT / name, frontend / 'qa' / Path(name).name)
    def stages_match():
        return (inventory(frontend / 'src') == source_before and inventory(source / 'src') == source_before
                and inventory(Path(packet['elmHome'])) == cache_before
                and inventory(frontend / 'elm-home') == cache_before
                and all(digest(frontend / 'qa' / Path(name).name) == reviewed[name] for name in qa_files))
    if not stages_match():
        raise RuntimeError('Successor focus reviewed source/cache stage differs')
    config = json.loads((source / 'elm.json').read_text())
    config['source-directories'] = ['src', 'qa']
    (frontend / 'elm.json').write_text(json.dumps(config, sort_keys=True) + '\n')
    config_hash = digest(frontend / 'elm.json')
    build_env = dict(env, ELM_HOME=str(frontend / 'elm-home'))
    elf = {}
    for key in ('node', 'elm'):
        with Path(packet[key]).open('rb') as stream:
            header = stream.read(20)
        if header[:6] != b'\x7fELF\x02\x01' or int.from_bytes(header[18:20], 'little') != 183:
            raise RuntimeError('Expected pinned ELF64 little-endian AArch64 ' + key)
        elf[key] = {'sha256': digest(Path(packet[key])), 'class': 64, 'machine': 183}
    artifacts = {}
    for name in SUCCESSOR_FOCUS_CHECKS:
        target = frontend / (name + '.js')
        run('compile-' + name, [packet['elm'], 'make', 'qa/' + name + '.elm',
            '--optimize', '--output=' + str(target)], frontend, 180, build_env)
        artifacts[name] = image(target)
    campaigns = (
        ('original-system-menu', 'system-menu-typed-state.cjs', ('SystemMenuReplay', 'SolSystemMenuIntegratedReplay2114')),
        ('successor-focus', 'successor-focus-harness.cjs', ('SystemMenuFocusPipeline', 'SuccessorFocusReplay', 'SystemMenuFocusExtended')))
    receipts = {}
    for label, driver_name, workers in campaigns:
        receipt_path = frontend / (label + '-receipt.json')
        driver = frontend / 'qa' / driver_name
        run(label, [packet['node'], driver, *[artifacts[name]['path'] for name in workers], receipt_path], frontend, 180, build_env)
        receipt = json.loads(receipt_path.read_text())
        rows = receipt.get('fixtures', [])
        if (receipt.get('schema') != 1 or receipt.get('passed') is not True
                or receipt.get('settleWindowMs') != 25 or receipt.get('originalAccepted') is not False
                or receipt.get('nativeAccepted') is not False or [row.get('name') for row in rows] != list(workers)):
            raise RuntimeError('Fixed focus campaign terminal receipt differs: ' + label)
        for row in rows:
            name = row['name']
            checks = row.get('payload', {}).get('checks', {})
            if (row.get('passed') is not True or row.get('file') != artifacts[name]['path']
                    or row.get('sha256') != artifacts[name]['sha256']
                    or set(checks) != set(SUCCESSOR_FOCUS_CHECKS[name])
                    or any(value is not True for value in checks.values())):
                raise RuntimeError('Exact complete focus check/image receipt differs: ' + name)
        if label == 'original-system-menu':
            if receipt.get('runnerPathSha256AtReport') != digest(driver):
                raise RuntimeError('Original fixed harness receipt hash differs')
            for row in rows:
                if ([check.get('name') for check in row.get('checks', [])] != SUCCESSOR_FOCUS_CHECKS[row['name']]
                        or any(check.get('passed') is not True for check in row['checks'])):
                    raise RuntimeError('Original complete ordered check receipt differs')
            modern = rows[1]['payload']
            if (modern.get('checkCount') != 650 or modern.get('requiredCheckCount') != 650
                    or modern.get('seeds') != list(range(32)) or modern.get('originalAccepted') is not False
                    or modern.get('nativeAccepted') is not False):
                raise RuntimeError('Original 650 seed/count/acceptance contract differs')
        receipts[label] = {'receipt': receipt, 'path': str(receipt_path),
                           'sha256': digest(receipt_path), 'driverSha256': digest(driver)}
    if (not stages_match() or digest(frontend / 'elm.json') != config_hash
            or any(image(Path(item['path'])) != item for item in artifacts.values())):
        raise RuntimeError('Successor focus source/cache/image changed during execution')
    return {'scope': 'Compiled synthetic successor-focus/system-menu component only',
            'receipts': receipts, 'artifacts': artifacts, 'runtimeELF': elf,
            'nativeAcceptance': False, 'originalAcceptance': False, 'releaseAccepted': False,
            'opaqueCmdASTObserved': False, 'productionRootBehaviorExecuted': False}


def consumption_frontend(output, env, packet, run):
    """Fixed actual Elm component route; original joined HTTP oracles stay open."""
    frontend = output / 'frontend'
    frontend.mkdir(mode=0o700)
    source = ROOT / 'implementation/warlock'
    before = inventory(source / 'src')
    shutil.copytree(source / 'src', frontend / 'src')
    shutil.copytree(Path(packet['elmHome']), frontend / 'elm-home')
    (frontend / 'qa').mkdir(mode=0o700)
    qa_files = [name for name in arm64_inputs(ROOT, consumption=True)
                if name.startswith('implementation/warlock/qa/')]
    for name in sorted(qa_files):
        shutil.copyfile(ROOT / name, frontend / 'qa' / Path(name).name)
    reviewed_sources = json.loads((output / 'report.json').read_text())['sourceHashes']
    for name in qa_files:
        if digest(frontend / 'qa' / Path(name).name) != reviewed_sources[name]:
            raise RuntimeError('Reviewed consumption QA stage differs: ' + name)
    config = json.loads((source / 'elm.json').read_text())
    config['source-directories'] = ['src', 'qa']
    (frontend / 'elm.json').write_text(json.dumps(config, sort_keys=True) + '\n')
    staged_config = digest(frontend / 'elm.json')
    if inventory(frontend / 'src') != before:
        raise RuntimeError('Consumption frontend source stage differs')
    build_env = dict(env, ELM_HOME=str(frontend / 'elm-home'))
    for name in ('preview-consumption.cjs', 'typed-state.cjs'):
        run('syntax-' + name, [packet['node'], '--check', frontend / 'qa' / name], frontend, 30, build_env)
    typed = ('NotificationsReplay', 'JumpListReplay', 'NotificationRelevanceReplay',
             'RetirementProofReplay', 'LocalFieldReplay')
    entries = [('PreviewConsumptionReplay', 'qa'), ('RetainedPreviewPresenterReplay', 'src')]
    entries += [(name, 'qa') for name in typed]
    roots = ('Main', 'Bar', 'Popup', 'HttpMain', 'HttpBar', 'HttpPopup',
             'NativePreviewAdmission', 'NativePreviewRenderer')
    entries += [(name, 'src') for name in roots]
    artifacts = {}
    for name, directory in entries:
        target = frontend / (name + '.js')
        run('compile-' + name, [packet['elm'], 'make', directory + '/' + name + '.elm',
            '--optimize', '--output=' + str(target)], frontend, 180, build_env)
        artifacts[name] = image(target)
    typed_path = frontend / 'typed-state.json'
    run('typed-state', [packet['node'], frontend / 'qa/typed-state.cjs',
                       *[artifacts[name]['path'] for name in typed], typed_path], frontend, 90, build_env)
    observed = json.loads(typed_path.read_text())
    typed_counts = {'NotificationsReplay': 24, 'JumpListReplay': 30, 'NotificationRelevanceReplay': 20,
              'RetirementProofReplay': 20, 'LocalFieldReplay': 43}
    rows = observed.get('fixtures', [])
    if (observed.get('schema') != 1 or observed.get('passed') is not True or observed.get('failures') != []
            or observed.get('runnerSha256') != digest(frontend / 'qa/typed-state.cjs')
            or [row.get('name') for row in rows] != list(typed)
            or len(observed.get('checks', [])) != sum(typed_counts.values())
            or any(row.get('passed') is not True or row.get('failures') != []
                   or row.get('sha256') != artifacts[row['name']]['sha256']
                   or len(row.get('checks', [])) != typed_counts[row['name']]
                   or any(check.get('passed') is not True for check in row.get('checks', [])) for row in rows)):
        raise RuntimeError('Exact existing typed lifecycle/local-field regression report differs')
    budgets: dict = {'cases': {'min': 7, 'max': 7}, 'steps': {'min': 4280, 'max': 4500},
               'assertions': {'min': 5300, 'max': 10000}, 'seeds': {'min': 3, 'max': 3},
               'responseMs': 20000, 'totalMs': 180000}
    fixture_hashes = {'compiled': artifacts['PreviewConsumptionReplay']['sha256'],
                      'oracle': digest(frontend / 'qa/preview-consumption.cjs'),
                      'elmFixture': digest(frontend / 'qa/PreviewConsumptionReplay.elm')}
    receipts = []
    for index in range(2):
        receipt = json.loads(run('preview-consumption-fresh-' + str(index),
            [packet['node'], frontend / 'qa/preview-consumption.cjs', artifacts['PreviewConsumptionReplay']['path']],
            frontend, 210, build_env))
        counts = receipt.get('counts', {})
        if (set(receipt) != {'status', 'counts', 'budgets', 'seeds', 'hashes', 'lastSequence'}
                or receipt.get('status') != 'passed' or receipt.get('budgets') != budgets
                or receipt.get('seeds') != [20261105, 20261106, 20261107]
                or receipt.get('hashes') != fixture_hashes or set(counts) != {'cases', 'steps', 'assertions', 'seeds'}
                or any(type(counts[name]) is not int or not budgets[name]['min'] <= counts[name] <= budgets[name]['max']
                       for name in ('cases', 'steps', 'assertions', 'seeds'))
                or type(receipt.get('lastSequence')) is not int or receipt['lastSequence'] != counts['steps']):
            raise RuntimeError('Consumption fixture terminal receipt is missing, incomplete or mismatched')
        receipts.append(receipt)
    if receipts[0] != receipts[1]:
        raise RuntimeError('Two fresh consumption executions differ')
    for artifact in artifacts.values():
        if image(Path(artifact['path'])) != artifact:
            raise RuntimeError('Compiled consumption/compatibility artifact changed')
    if (inventory(frontend / 'src') != before or inventory(source / 'src') != before
            or digest(frontend / 'elm.json') != staged_config
            or any(digest(frontend / 'qa' / Path(name).name) != reviewed_sources[name] for name in qa_files)):
        raise RuntimeError('Consumption source, staged manifest or fixture changed during execution')
    return {'scope': 'Actual compiled Elm Popup/ingress consumption component and existing typed regressions only',
            'artifacts': artifacts, 'optimizedProductionRoots': list(roots), 'productionRootBehaviorExecuted': False,
            'consumption': {'freshRuns': 2, 'receipts': receipts},
            'typedState': {'path': str(typed_path), 'sha256': digest(typed_path), 'checks': sum(typed_counts.values()),
                           'fixtures': list(typed)},
            'retainedPresenter': {'compiled': True, 'behaviorExecuted': False},
            'originalHttpFiveAndEleven': {'executed': False, 'status': 'Pending separate current-source oracle derivative review'},
            'nativeAcceptance': False, 'originalAcceptance': False, 'releaseAccepted': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ('subscriptions', 'owner-build', 'owner', 'preview-control', 'protocol', 'preview-consumption', 'preview-schema', 'held-executable', 'peer-role', 'successor-focus', 'workspace-owner-baseline', 'workspace-owner-component', 'workspace-owner-component-red', 'workspace-original', 'workspace-dom', 'workspace-navigation-protocol', 'ux031-daemon-only', 'notification-config', 'notification-issuer', 'catalog-nodisplay', 'catalog-source-revision', 'catalog-publication', 'application-owner-route', 'application-availability', 'native-stage-build', 'provider-probe-build', 'provider-callback-build', 'physical-context-owner-build', 'physical-context-owner-bridge', 'physical-context-owner-backing', 'virtual-pointer-build', 'ux003-journey-build', 'aquamarine-build'):
        modes.add_argument('--' + mode, action='store_true')
    parser.add_argument('--inside-private', type=Path)
    args = parser.parse_args()
    args.native_stage_build = args.native_stage_build or args.provider_probe_build
    protocol_profile = args.protocol or args.preview_schema or args.workspace_navigation_protocol
    haskell_profile = protocol_profile or args.held_executable or args.peer_role or args.notification_config or args.notification_issuer or args.catalog_nodisplay or args.catalog_source_revision or args.catalog_publication or args.application_owner_route
    scope = require_qa_scope()
    if args.inside_private is not None:
        private_runtime = Path('/run/user') / str(os.getuid())
        private_runtime.mkdir(parents=True, mode=0o700)
    runtime_base()
    mode = ('--peer-role' if args.peer_role else ('--held-executable' if args.held_executable else ('--preview-schema' if args.preview_schema else ('--preview-consumption' if args.preview_consumption else
            ('--subscriptions' if args.subscriptions else ('--owner-build' if args.owner_build else
             ('--preview-control' if args.preview_control else ('--protocol' if args.protocol else '--owner'))))))))
    if args.successor_focus:
        mode = '--successor-focus'
    if args.workspace_owner_baseline:
        mode = '--workspace-owner-baseline'
    if args.workspace_owner_component:
        mode = '--workspace-owner-component'
    if args.workspace_owner_component_red:
        mode = '--workspace-owner-component-red'
    if args.workspace_original:
        mode = '--workspace-original'
    elif args.workspace_dom:
        mode = '--workspace-dom'
    if args.workspace_navigation_protocol:
        mode = '--workspace-navigation-protocol'
    if args.ux031_daemon_only:
        mode = '--ux031-daemon-only'
    if args.notification_config:
        mode = '--notification-config'
    if args.notification_issuer:
        mode = '--notification-issuer'
    if args.catalog_nodisplay:
        mode = '--catalog-nodisplay'
    if args.application_owner_route:
        mode = '--application-owner-route'
    if args.application_availability:
        mode = '--application-availability'
    if args.native_stage_build:
        mode = '--native-stage-build'
    if args.provider_probe_build:
        mode = '--provider-probe-build'
    if args.provider_callback_build:
        mode = '--provider-callback-build'
    if args.physical_context_owner_build:
        mode = '--physical-context-owner-build'
    if args.physical_context_owner_bridge:
        mode = '--physical-context-owner-bridge'
    if args.physical_context_owner_backing:
        mode = '--physical-context-owner-backing'
    if args.virtual_pointer_build:
        mode = '--virtual-pointer-build'
    if args.ux003_journey_build:
        mode = '--ux003-journey-build'
    if args.aquamarine_build:
        mode = '--aquamarine-build'
    if args.catalog_publication:
        mode = '--catalog-publication'
    if args.catalog_source_revision:
        mode = '--catalog-source-revision'
    if args.inside_private is None:
        output = ROOT / '.warlock-contributor' / ('arm64-cpu-' + str(time.time_ns()))
        output.mkdir(parents=True, mode=0o700)
        sources = {name: digest(ROOT / name) for name in sorted(arm64_inputs(
            ROOT, args.subscriptions, args.preview_control, haskell_profile, args.preview_consumption, args.successor_focus, args.workspace_owner_baseline, args.workspace_owner_component, args.workspace_owner_component_red, args.workspace_original, args.workspace_dom, daemon_only=args.ux031_daemon_only, native_stage_build=args.native_stage_build, provider_probe_build=args.provider_probe_build, provider_callback_build=args.provider_callback_build, physical_context_owner_build=args.physical_context_owner_build, physical_context_owner_bridge=args.physical_context_owner_bridge, physical_context_owner_backing=args.physical_context_owner_backing, virtual_pointer_build=args.virtual_pointer_build, ux003_journey_build=args.ux003_journey_build, aquamarine_build=args.aquamarine_build))}
        packet = verify(full=True)
        report = {'schema': 1, 'passed': False, 'mode': mode, 'protectedScope': scope, 'sourceHashes': sources,
                      'toolchainManifestSHA256': packet['manifestSHA256'], 'commands': [],
                      'scope': 'ARM component build/replay only; no original scenario or native acceptance',
                      'nativeAcceptance': False, 'originalAcceptance': False, 'releaseAccepted': False}
        if args.provider_callback_build:
            report['scope'] = 'Two new fixed callback fixture images compiled/linked only; no fixture execution or native acceptance'
        if args.physical_context_owner_build:
            report['scope'] = 'Four fixed physical-context targets compiled/linked only; no fixture or GTK execution'
        if args.physical_context_owner_bridge:
            report['scope'] = 'Six fixed targets; only ordinary protocol and Unix-socket/mock-guard CPU fixtures execute; no GTK/owner execution'
        if args.physical_context_owner_backing:
            report['scope'] = 'Seven fixed targets compiled; only codec/socket and owned-filesystem CPU controls execute'
        if args.ux003_journey_build:
            report['scope'] = 'Nine fixed targets compiled; observer and application route are compile-only; only three CPU fixtures run'
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        # Hide host runtime sockets and network. All compiler writes are confined
        # to the new output; SDK, source, system inputs and caches remain read-only.
        command = ['/usr/bin/bwrap', '--die-with-parent', '--unshare-net', '--unshare-pid',
                   '--ro-bind', '/usr', '/usr', '--symlink', 'usr/bin', '/bin',
                   '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib', '/lib64',
                   '--dir', '/etc']
        for name in ('ld.so.cache', 'passwd', 'group', 'nsswitch.conf'):
            command += ['--ro-bind', '/etc/' + name, '/etc/' + name]
        command += ['--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp', '--tmpfs', '/run',
                    '--ro-bind', str(ROOT), str(ROOT)]
        mounts = set(packet['trees']) | {name for name in packet['files'] if name.startswith('/home/hoskinson/')}
        for name in sorted(mounts):
            command += ['--ro-bind', name, name]
        command += ['--bind', str(output), str(output),
                   '--chdir', str(ROOT), '--', sys.executable, '-B', str(Path(__file__).resolve()),
                   mode, '--inside-private', str(output)]
        clean = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
                 'PYTHONDONTWRITEBYTECODE': '1', 'HOME': str(output / 'home'), 'TMPDIR': '/tmp'}
        # qa_launch reads the systemd scope through /proc, not an environment bypass.
        try:
            child = subprocess.run(command, cwd=ROOT, env=clean, timeout=3500, check=False)
            report = json.loads((output / 'report.json').read_text())
            verify(full=True)
            if set(arm64_inputs(ROOT, args.subscriptions, args.preview_control, haskell_profile,
                                args.preview_consumption, args.successor_focus, args.workspace_owner_baseline, args.workspace_owner_component, args.workspace_owner_component_red, args.workspace_original, args.workspace_dom, daemon_only=args.ux031_daemon_only, native_stage_build=args.native_stage_build, provider_probe_build=args.provider_probe_build, provider_callback_build=args.provider_callback_build, physical_context_owner_build=args.physical_context_owner_build, physical_context_owner_bridge=args.physical_context_owner_bridge, physical_context_owner_backing=args.physical_context_owner_backing, virtual_pointer_build=args.virtual_pointer_build, ux003_journey_build=args.ux003_journey_build, aquamarine_build=args.aquamarine_build)) != set(sources) or any(digest(ROOT / name) != sha for name, sha in sources.items()):
                raise RuntimeError('ARM source closure changed during execution')
            if child.returncode or not report['passed']:
                raise RuntimeError('Private ARM profile failed; retained logs')
        except Exception as error:  # noqa: BLE001 -- retain failure evidence before exiting
            if isinstance(report.get('error'), str) and report['error']:
                report.update(passed=False, outerError=str(error))
            else:
                report.update(passed=False, error=str(error))
        finally:
            (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps({'passed': report['passed'], 'report': str(output / 'report.json')}), flush=True)
        return 0 if report['passed'] else 1

    output = args.inside_private
    if output.parent != ROOT / '.warlock-contributor' or not re.fullmatch('arm64-cpu-[0-9]+', output.name) or output.is_symlink():
        raise RuntimeError('Unexpected ARM private output')
    report = json.loads((output / 'report.json').read_text())
    packet = verify(full=True)
    env = dict(os.environ, PATH=str(Path(packet['ghcPrefix']) / 'bin') + ':/usr/bin:/bin',
               GHC_ENVIRONMENT='-', CABAL_DIR=str(output / 'cabal-home'), NO_COLOR='1')
    logs = output / 'logs'
    logs.mkdir(mode=0o700)

    def run(name, command, cwd=ROOT, timeout=900, extra_env=None):
        with (logs / (name + '.stdout')).open('wb') as stdout, (logs / (name + '.stderr')).open('wb') as stderr:
            child = subprocess.run([str(arg) for arg in command], cwd=cwd, env=extra_env or env,
                                   stdout=stdout, stderr=stderr, timeout=timeout, check=False)
        report['commands'].append({'name': name, 'argv': [str(arg) for arg in command], 'exit': child.returncode})
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        if child.returncode:
            raise RuntimeError(name + ' failed; see retained logs')
        return (logs / (name + '.stdout')).read_text()

    try:
        if args.provider_probe_build:
            run('provider-probe-parser-controls', [sys.executable, '-B', ROOT / 'tools/test_webkit_provider_probe_runner.py'], timeout=120)
        if args.native_stage_build:
            run('ux003-staging-contract-tests', [sys.executable, '-B',
                ROOT / 'implementation/warlock/qa/omarchy_trial/test_application_staging.py',
                '--helper', ROOT / 'tools/omarchy_ui_mvp.py'], timeout=120)
            run('native-stage-contract-tests', [sys.executable, '-B', ROOT / 'tools/test_arm64_native_stage.py'], timeout=120)
        if args.preview_control:
            # Fixed source syntax preflight prevents expensive recompilation
            # when a declared QA fixture cannot be parsed by the pinned Node.
            for name in ('http-preview-control-replay.cjs', 'http-preview-control-literals.cjs',
                         'sol-http-root-observer-0535.cjs', 'sol-http-popup-literals-0525.cjs',
                         'tea-contract-cases.cjs'):
                run('syntax-' + name, [packet['node'], '--check',
                    ROOT / 'implementation/warlock/qa' / name], timeout=30)
        if args.aquamarine_build:
            from aquamarine_build import run_profile
            run('aquamarine-build-controls', [sys.executable, '-B',
                ROOT / 'tools/test_aquamarine_build.py', '--root', ROOT], timeout=120)
            report['aquamarineBuild'] = run_profile(ROOT, output, packet, run)
        elif args.virtual_pointer_build:
            from virtual_pointer_build import run_profile
            run('virtual-pointer-build-controls', [sys.executable, '-B',
                ROOT / 'tools/test_virtual_pointer_build.py', '--root', ROOT], timeout=120)
            report['virtualPointerBuild'] = run_profile(ROOT, output, packet, run)
        elif args.physical_context_owner_build or args.physical_context_owner_bridge or args.physical_context_owner_backing or args.ux003_journey_build:
            from physical_context_build import pin_image, run_profile
            run('physical-context-profile-controls', [sys.executable, '-B',
                ROOT / 'tools/test_physical_context_build.py', '--root', ROOT], timeout=120)
            if args.ux003_journey_build:
                run('ux003-journey-runner-controls', [sys.executable, '-B',
                    ROOT / 'tools/test_ux003_native_journey.py'], timeout=120)
            def execute_bridge_cpu(suite, original, stage):
                sentinels = {
                    'ui-engine-protocol-controls':
                        'desktop idle transport controls: same-process SCM fixture; no native acceptance\n'
                        'engine protocol valid JSON boundaries: depth 14/15/16, bytes 393215/393216/393217\n'
                        'engine protocol replay draft seed=20261101\n',
                    'ui-engine-broker-controls':
                        'engine broker socketpair controls passed; mock guard is not owned-process evidence\n',
                }
                if args.physical_context_owner_backing or getattr(args, 'ux003_journey_build', False):
                    sentinels['filter-backing-root-controls'] = 'filter-backing-root-controls: complete\n'
                if not (args.physical_context_owner_bridge or args.physical_context_owner_backing or getattr(args, 'ux003_journey_build', False)) or suite not in sentinels:
                    raise RuntimeError('Only two fixed CPU bridge fixtures may execute')
                if pin_image(Path(original['path']), output / 'dist', suite) != original:
                    raise RuntimeError('Bridge original image changed before copy')
                copies = output / 'dist' / 'bridge-cpu-images'
                runs = output / 'bridge-cpu-runs'
                for directory in (copies, runs):
                    directory.mkdir(mode=0o700, exist_ok=True)
                    if (directory.is_symlink() or directory.stat().st_uid != os.getuid()
                            or directory.stat().st_mode & 0o777 != 0o700):
                        raise RuntimeError('Unsafe bridge CPU private directory')
                copied = copies / suite
                if copied.exists() or copied.is_symlink():
                    raise RuntimeError('Bridge CPU image destination reused')
                shutil.copy2(Path(original['path']), copied)
                copied_pin = pin_image(copied, output / 'dist', suite)
                if (copied_pin['size'], copied_pin['sha256']) != (original['size'], original['sha256']):
                    raise RuntimeError('Bridge CPU copied image differs')
                dispatch = output / ('bridge-' + suite + '-dispatch.json')
                with dispatch.open('x') as stream:
                    json.dump({'suites': {str(copied): {
                        'suite': suite, 'test': {'path': str(copied),
                            'pin': [copied_pin[k] for k in ('device', 'inode', 'size', 'sha256')]},
                        'fixtures': {}, 'runRoot': str(runs / suite)}}}, stream)
                run('bridge-cpu-' + suite, [sys.executable, '-B', ROOT / 'tools/haskell_test_wrapper.py', copied],
                    stage, 240, dict(env, WARLOCK_HASKELL_DISPATCH=str(dispatch)))
                if (pin_image(copied, output / 'dist', suite) != copied_pin
                        or pin_image(Path(original['path']), output / 'dist', suite) != original):
                    raise RuntimeError('Bridge CPU image changed during execution')
                result_path = runs / suite / 'results.json'
                if result_path.is_symlink() or not result_path.is_file() or result_path.stat().st_size > 16384:
                    raise RuntimeError('Missing fixed bridge wrapper receipt')
                results = json.loads(result_path.read_text())
                log = runs / suite / 'default.log'
                if (len(results) != 1 or results[0].get('mode') != 'default'
                        or results[0].get('argv') != [] or results[0].get('exit') != 0
                        or results[0].get('timeout') is not False
                        or results[0].get('forcedCleanup') is not False
                        or results[0].get('log') != str(log)
                        or log.is_symlink() or not log.is_file() or log.stat().st_size > 16384
                        or log.read_text() != sentinels[suite]):
                    raise RuntimeError('Bridge CPU normal receipt or exact sentinel differs')
                return {'originalImage': original, 'copiedImage': copied_pin,
                        'dispatchSHA256': digest(dispatch), 'results': str(result_path),
                        'resultsSHA256': digest(result_path), 'logSHA256': digest(log),
                        'noArguments': True, 'normalExit': True, 'scope': ('CPU owned-filesystem fixture only' if suite == 'filter-backing-root-controls' else 'CPU codec/socket fixture only')}
            report['physicalContextBuild'] = run_profile(ROOT, output, packet, run,
                bridge=(args.physical_context_owner_bridge or args.physical_context_owner_backing or args.ux003_journey_build),
                backing=(args.physical_context_owner_backing or args.ux003_journey_build), journey=args.ux003_journey_build, execute=execute_bridge_cpu)
        elif args.ux031_daemon_only:
            from ux031_daemon_only import run_daemon_only
            report['daemonOnly'] = run_daemon_only(output)
        elif args.workspace_original:
            report['workspaceOriginal'] = workspace_original_frontend(output, env, packet, run)
        elif args.workspace_dom:
            report['workspaceDom'] = workspace_dom_frontend(output, env, packet, run)
        elif args.workspace_owner_component_red:
            report['workspaceOwnerComponentRed'] = workspace_owner_component_red_frontend(output, env, packet, run)
        elif args.workspace_owner_component:
            report['workspaceOwnerComponent'] = workspace_owner_component_frontend(output, env, packet, run)
        elif args.workspace_owner_baseline:
            report['workspaceOwnerBaseline'] = workspace_owner_baseline_frontend(output, env, packet, run)
        elif args.successor_focus:
            report['successorFocus'] = successor_focus_frontend(output, env, packet, run)
        elif args.preview_consumption:
            report['previewConsumption'] = consumption_frontend(output, env, packet, run)
        elif args.application_availability:
            selected_output = output / 'application-availability'
            run('application-availability', [sys.executable, '-B', ROOT / 'tools/check_elm_cpu.py',
                    '--application-availability', '--arm64', '--arm64-output', selected_output], timeout=3300)
            summary = json.loads((selected_output / 'report.json').read_text())
            if summary.get('passed') is not True:
                raise RuntimeError('Application availability lacks successful terminal report')
            report['applicationAvailabilityReport'] = {'path': str(selected_output / 'report.json'),
                                                        'sha256': digest(selected_output / 'report.json')}
        elif args.subscriptions:
            subscription_output = output / 'subscriptions'
            run('subscriptions', [sys.executable, '-B', ROOT / 'tools/check_elm_cpu.py',
                                  '--subscriptions', '--arm64', '--arm64-output', subscription_output], timeout=3300)
            summary = json.loads((subscription_output / 'report.json').read_text())
            if not summary['passed']:
                raise RuntimeError('ARM subscription replay has no successful report')
            report['subscriptionsReport'] = {'path': str(subscription_output / 'report.json'),
                                                'sha256': digest(subscription_output / 'report.json')}
        elif args.provider_callback_build:
            from provider_callback_build import run_profile
            run('provider-callback-profile-controls', [sys.executable, '-B',
                ROOT / 'tools/test_provider_callback_build.py', '--root', ROOT], timeout=120)
            report['providerCallbackBuild'] = run_profile(ROOT, output, packet, run)
        else:
            source = ROOT / 'implementation/warlock/haskell'
            before = inventory(source)
            stage = output / 'haskell'
            shutil.copytree(source, stage, ignore=shutil.ignore_patterns('dist-newstyle', '__pycache__'))
            if inventory(stage) != before:
                raise RuntimeError('Haskell stage differs')
            dependencies = output / 'dependencies'
            shutil.copytree(Path(packet['dependencies']), dependencies)
            if inventory(dependencies) != packet['trees'][packet['dependencies']]:
                raise RuntimeError('ARM dependency stage differs')
            manifest = json.loads((ROOT / 'tools/haskell-dependencies.json').read_text())
            for dependency in manifest['packages']:
                metadata = dependencies / dependency['directory'] / (dependency['name'] + '.cabal')
                if digest(metadata) != dependency['metadataSHA256']:
                    raise RuntimeError('Exact Haskell dependency metadata revision differs')
            project = stage / 'cabal.project'
            project.write_text(project.read_text() + '\npackages: ' + ' '.join(
                str(dependencies / p['directory']) for p in manifest['packages']) + '\nactive-repositories: :none\n')
            config = output / 'cabal.config'
            config.write_text('active-repositories: :none\nstore-dir: ' + str(output / 'store') + '\nremote-repo-cache: ' + str(output / 'repo-cache') + '\n')
            ghc = Path(packet['ghcPrefix']) / 'bin'
            common = [packet['cabal'], '--config-file=' + str(config)]
            flags = ['--offline', '--project-file=' + str(project), '--builddir=' + str(output / 'dist'),
                     '--with-compiler=' + str(ghc / 'ghc'), '--with-hc-pkg=' + str(ghc / 'ghc-pkg'),
                     '--with-hsc2hs=' + str(ghc / 'hsc2hs'), '--with-gcc=/usr/bin/gcc',
                     '--with-ar=/usr/bin/ar', '--with-ld=/usr/bin/ld', '--with-pkg-config=/usr/bin/pkg-config', '--jobs=2']
            target = 'warlock-runtime:test:ui-origin-controls'
            protocol_suites = (('workspace-navigation-controls', 'desktop-boundary-controls') if args.workspace_navigation_protocol else
                               (('preview-control', 'desktop-boundary-controls') if args.preview_schema else
                                ('desktop-boundary-controls',)))
            protocol_targets = [(suite, 'warlock-protocol:test:' + suite) for suite in protocol_suites]
            backend = 'warlock-runtime:exe:warlock-ui-backend'
            if args.application_owner_route:
                metadata = (stage / 'runtime/runtime.cabal').read_text()
                catalog_cases = (
                    ('catalog-nodisplay-controls', 'test-catalog-nodisplay', '6463ae3d439fa99517522cca8837bd52a0e3b52d899d17c98e84937130b4cecd'),
                    ('catalog-source-revision-adversarial', 'test-catalog-source-revision-adversarial', '2d4d858dcaeaaf494016b31a0cbd6bc0cb491d9d756570facb51ec3b77a0ea67'),
                    ('catalog-publication-controls', 'test-catalog-publication', '1d31248918b047422448cbf0a1c97070680b9ba92fa1079cf099a61db6a68885'))
                for suite, directory, fixture_sha in catalog_cases:
                    pieces = metadata.split('\ntest-suite ' + suite + '\n')
                    if len(pieces) != 2:
                        raise RuntimeError('Expected one ordinary-linked catalog suite: ' + suite)
                    stanza = re.split(r'\n(?:test-suite|executable|library|common|flag)\b', pieces[1], maxsplit=1)[0]
                    expected = ['  type: exitcode-stdio-1.0', '  hs-source-dirs: ' + directory,
                                '  main-is: Main.hs', '  build-depends: base >=4.18 && <5, bytestring, text, containers, unix, directory, filepath, warlock-runtime, warlock-protocol',
                                '  default-language: Haskell2010', '  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -with-rtsopts=-V0']
                    if suite == 'catalog-publication-controls':
                        expected[3] = '  build-depends: base >=4.18 && <5, bytestring, containers, directory, filepath, unix, warlock-runtime, warlock-protocol'
                    actual = [line for line in stanza.splitlines() if line.strip() and not line.lstrip().startswith('--')]
                    if actual != expected:
                        raise RuntimeError('Unexpected catalog suite declarations: ' + suite)
                    fixture_root = stage / 'runtime' / directory
                    files = {str(p.relative_to(fixture_root)) for p in fixture_root.rglob('*') if p.is_file() and p.suffix in ('.hs', '.hsc')}
                    if files != {'Main.hs'} or digest(fixture_root / 'Main.hs') != fixture_sha:
                        raise RuntimeError('Unexpected fixed catalog fixture sources: ' + suite)
                selected_targets = [(suite, 'warlock-runtime:test:' + suite) for suite, _, _ in catalog_cases]
                build_targets = ['warlock-runtime:lib:warlock-runtime', *[target for _, target in selected_targets]]
                application_targets = (('application-owner-peer-fixture', 'executable', 'fixture-application-owner-peer'),
                                       ('application-argv-fixture', 'executable', 'fixture-application-argv'),
                                       ('application-owner-route-controls', 'test-suite', 'test-application-owner-route'))
                exact_stanzas = {'application-owner-peer-fixture': '  hs-source-dirs: fixture-application-owner-peer\n  main-is: Main.hs\n  build-depends: base >=4.18 && <5, bytestring, text, unix, warlock-protocol\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -with-rtsopts=-V0', 'application-argv-fixture': '  hs-source-dirs: fixture-application-argv\n  main-is: Main.hs\n  build-depends: base >=4.18 && <5\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -with-rtsopts=-V0', 'application-owner-route-controls': '  type: exitcode-stdio-1.0\n  hs-source-dirs: test-application-owner-route\n  main-is: Main.hs\n  build-depends: base >=4.18 && <5, bytestring, text, directory, filepath, unix, cryptohash-sha256 ==0.11.102.1, warlock-runtime, warlock-process-custody, warlock-protocol\n  default-language: Haskell2010\n  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -with-rtsopts=-V0'}
                for name, kind, directory in application_targets:
                    pieces = metadata.split('\n' + kind + ' ' + name + '\n')
                    if len(pieces) != 2 or pieces[1].split('\n\n', 1)[0].rstrip() != exact_stanzas[name]:
                        raise RuntimeError('Unexpected ordinary application declarations: ' + name)
                    directory_root = stage / 'runtime' / directory
                    if {str(p.relative_to(directory_root)) for p in directory_root.rglob('*') if p.is_file() and p.suffix in ('.hs', '.hsc')} != {'Main.hs'}:
                        raise RuntimeError('Unexpected application home sources: ' + name)
                    if digest(directory_root / 'Main.hs') != {'application-owner-peer-fixture': 'bc32dc9b97d99c64001dbcbc8410070ff4ac236978c5b89e11147f228962e767', 'application-argv-fixture': 'd44def2256ddc027e90c0f4d6d2f11796b5672d431942b2afbd453b62b90c5bf', 'application-owner-route-controls': '0e692ed4c90e850fc24132b9052e7e9db797251fb02aee737e5edd2c9f8ff227'}[name]:
                        raise RuntimeError('Application literal source pin differs: ' + name)
                    selected_targets.append((name, 'warlock-runtime:' + ('test:' if kind == 'test-suite' else 'exe:') + name))
                build_targets = ['warlock-held-document-proposal:lib:warlock-held-document-proposal',
                                 'warlock-process-custody:lib:warlock-process-custody',
                                 'warlock-protocol:lib:warlock-protocol', 'warlock-runtime:lib:warlock-runtime',
                                 *[target for _, target in selected_targets]]
                build_label = 'application-owner-route-build'
                protocol_suites = ()
                report['applicationOwnerRoute'] = {'ordinaryLibraryTarget': 'warlock-runtime:lib:warlock-runtime',
                    'suites': [suite for suite, _, _ in catalog_cases], 'scope': 'Catalog regression and ordinary controlled application-owner IO only',
                    'nativeAcceptance': False, 'originalAcceptance': False}
            elif args.catalog_publication:
                metadata = (stage / 'runtime/runtime.cabal').read_text()
                catalog_cases = (
                    ('catalog-nodisplay-controls', 'test-catalog-nodisplay', '6463ae3d439fa99517522cca8837bd52a0e3b52d899d17c98e84937130b4cecd'),
                    ('catalog-source-revision-adversarial', 'test-catalog-source-revision-adversarial', '2d4d858dcaeaaf494016b31a0cbd6bc0cb491d9d756570facb51ec3b77a0ea67'),
                    ('catalog-publication-controls', 'test-catalog-publication', '1d31248918b047422448cbf0a1c97070680b9ba92fa1079cf099a61db6a68885'))
                for suite, directory, fixture_sha in catalog_cases:
                    pieces = metadata.split('\ntest-suite ' + suite + '\n')
                    if len(pieces) != 2:
                        raise RuntimeError('Expected one ordinary-linked catalog suite: ' + suite)
                    stanza = re.split(r'\n(?:test-suite|executable|library|common|flag)\b', pieces[1], maxsplit=1)[0]
                    expected = ['  type: exitcode-stdio-1.0', '  hs-source-dirs: ' + directory,
                                '  main-is: Main.hs', '  build-depends: base >=4.18 && <5, bytestring, text, containers, unix, directory, filepath, warlock-runtime, warlock-protocol',
                                '  default-language: Haskell2010', '  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -with-rtsopts=-V0']
                    if suite == 'catalog-publication-controls':
                        expected[3] = '  build-depends: base >=4.18 && <5, bytestring, containers, directory, filepath, unix, warlock-runtime, warlock-protocol'
                    actual = [line for line in stanza.splitlines() if line.strip() and not line.lstrip().startswith('--')]
                    if actual != expected:
                        raise RuntimeError('Unexpected catalog suite declarations: ' + suite)
                    fixture_root = stage / 'runtime' / directory
                    files = {str(p.relative_to(fixture_root)) for p in fixture_root.rglob('*') if p.is_file() and p.suffix in ('.hs', '.hsc')}
                    if files != {'Main.hs'} or digest(fixture_root / 'Main.hs') != fixture_sha:
                        raise RuntimeError('Unexpected fixed catalog fixture sources: ' + suite)
                selected_targets = [(suite, 'warlock-runtime:test:' + suite) for suite, _, _ in catalog_cases]
                build_targets = ['warlock-runtime:lib:warlock-runtime', *[target for _, target in selected_targets]]
                build_label = 'catalog-publication-build'
                protocol_suites = ()
                report['catalogPublication'] = {'ordinaryLibraryTarget': build_targets[0],
                    'suites': [suite for suite, _, _ in catalog_cases], 'scope': 'NoDisplay, source-root revision and local publication components only',
                    'nativeAcceptance': False, 'originalAcceptance': False}
            elif args.catalog_source_revision:
                metadata = (stage / 'runtime/runtime.cabal').read_text()
                catalog_cases = (
                    ('catalog-nodisplay-controls', 'test-catalog-nodisplay', '6463ae3d439fa99517522cca8837bd52a0e3b52d899d17c98e84937130b4cecd'),
                    ('catalog-source-revision-adversarial', 'test-catalog-source-revision-adversarial', '2d4d858dcaeaaf494016b31a0cbd6bc0cb491d9d756570facb51ec3b77a0ea67'))
                for suite, directory, fixture_sha in catalog_cases:
                    pieces = metadata.split('\ntest-suite ' + suite + '\n')
                    if len(pieces) != 2:
                        raise RuntimeError('Expected one ordinary-linked catalog suite: ' + suite)
                    stanza = re.split(r'\n(?:test-suite|executable|library|common|flag)\b', pieces[1], maxsplit=1)[0]
                    expected = ['  type: exitcode-stdio-1.0', '  hs-source-dirs: ' + directory,
                                '  main-is: Main.hs', '  build-depends: base >=4.18 && <5, bytestring, text, containers, unix, directory, filepath, warlock-runtime, warlock-protocol',
                                '  default-language: Haskell2010', '  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -with-rtsopts=-V0']
                    actual = [line for line in stanza.splitlines() if line.strip() and not line.lstrip().startswith('--')]
                    if actual != expected:
                        raise RuntimeError('Unexpected catalog suite declarations: ' + suite)
                    fixture_root = stage / 'runtime' / directory
                    files = {str(p.relative_to(fixture_root)) for p in fixture_root.rglob('*') if p.is_file() and p.suffix in ('.hs', '.hsc')}
                    if files != {'Main.hs'} or digest(fixture_root / 'Main.hs') != fixture_sha:
                        raise RuntimeError('Unexpected fixed catalog fixture sources: ' + suite)
                selected_targets = [(suite, 'warlock-runtime:test:' + suite) for suite, _, _ in catalog_cases]
                build_targets = ['warlock-runtime:lib:warlock-runtime', *[target for _, target in selected_targets]]
                build_label = 'catalog-source-revision-build'
                protocol_suites = ()
                report['catalogSourceRevision'] = {'ordinaryLibraryTarget': build_targets[0],
                    'suites': [suite for suite, _, _ in catalog_cases], 'scope': 'NoDisplay and source-root revision components only',
                    'nativeAcceptance': False, 'originalAcceptance': False}
            elif args.catalog_nodisplay:
                metadata = (stage / 'runtime/runtime.cabal').read_text()
                pieces = metadata.split('\ntest-suite catalog-nodisplay-controls\n')
                if len(pieces) != 2:
                    raise RuntimeError('Expected one ordinary-linked catalog NoDisplay suite')
                stanza = re.split(r'\n(?:test-suite|executable|library|common|flag)\b', pieces[1], maxsplit=1)[0]
                expected = ['  type: exitcode-stdio-1.0', '  hs-source-dirs: test-catalog-nodisplay',
                            '  main-is: Main.hs', '  build-depends: base >=4.18 && <5, bytestring, text, containers, unix, directory, filepath, warlock-runtime, warlock-protocol',
                            '  default-language: Haskell2010', '  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates -with-rtsopts=-V0']
                actual = [line for line in stanza.splitlines() if line.strip() and not line.lstrip().startswith('--')]
                if actual != expected:
                    raise RuntimeError('Unexpected catalog NoDisplay suite declarations')
                fixture_root = stage / 'runtime/test-catalog-nodisplay'
                files = {str(p.relative_to(fixture_root)) for p in fixture_root.rglob('*') if p.is_file() and p.suffix in ('.hs', '.hsc')}
                if files != {'Main.hs'} or digest(fixture_root / 'Main.hs') != '6463ae3d439fa99517522cca8837bd52a0e3b52d899d17c98e84937130b4cecd':
                    raise RuntimeError('Unexpected catalog NoDisplay fixture sources')
                selected_targets = [('catalog-nodisplay-controls', 'warlock-runtime:test:catalog-nodisplay-controls')]
                build_targets = ['warlock-runtime:lib:warlock-runtime', selected_targets[0][1]]
                build_label = 'catalog-nodisplay-build'
                protocol_suites = ()
                report['catalogNoDisplay'] = {'ordinaryLibraryTarget': build_targets[0],
                    'scope': 'NoDisplay catalog component only', 'nativeAcceptance': False, 'originalAcceptance': False}
            elif args.notification_issuer:
                metadata = (stage / 'runtime/runtime.cabal').read_text()
                pieces = metadata.split('\ntest-suite notification-issuer-controls\n')
                if len(pieces) != 2:
                    raise RuntimeError('Expected one ordinary-linked issuer suite')
                stanza = re.split(r'\n(?:test-suite|executable|library|common|flag)\b', pieces[1], maxsplit=1)[0]
                expected = ['  type: exitcode-stdio-1.0', '  hs-source-dirs: test-notification-issuer',
                            '  main-is: Main.hs', '  build-depends: base >=4.18 && <5, bytestring, directory, filepath, unix, warlock-runtime',
                            '  default-language: Haskell2010', '  ghc-options: -Wall -Werror -Wcompat']
                actual = [line for line in stanza.splitlines() if line.strip() and not line.lstrip().startswith('--')]
                if actual != expected:
                    raise RuntimeError('Unexpected issuer suite declarations')
                fixture_root = stage / 'runtime/test-notification-issuer'
                files = {str(p.relative_to(fixture_root)) for p in fixture_root.rglob('*') if p.is_file() and p.suffix in ('.hs', '.hsc')}
                if files != {'Main.hs'} or digest(fixture_root / 'Main.hs') != '2a1b3ba1593bed25a68744e9408d209c613230e3d94ae4171abfe08882ffa711':
                    raise RuntimeError('Unexpected issuer fixture sources')
                selected_targets = [('notification-issuer-controls', 'warlock-runtime:test:notification-issuer-controls')]
                build_targets = ['warlock-runtime:lib:warlock-runtime', selected_targets[0][1]]
                build_label = 'notification-issuer-build'
                protocol_suites = ()
                report['notificationIssuer'] = {'ordinaryLibraryTarget': build_targets[0],
                    'scope': 'Private storage issuer fixture only', 'nativeAcceptance': False, 'originalAcceptance': False}
            elif args.notification_config:
                metadata = (stage / 'runtime/runtime.cabal').read_text()
                pieces = metadata.split('\ntest-suite notification-config-controls\n')
                if len(pieces) != 2:
                    raise RuntimeError('Expected one ordinary-linked notification config suite')
                stanza = re.split(r'\n(?:test-suite|executable|library|common|flag)\b', pieces[1], maxsplit=1)[0]
                expected = ['  type: exitcode-stdio-1.0', '  hs-source-dirs: test-notification-config',
                            '  main-is: Main.hs', '  build-depends: base >=4.18 && <5, bytestring, text, unix, filepath, warlock-runtime',
                            '  default-language: Haskell2010', '  ghc-options: -Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates']
                actual = [line for line in stanza.splitlines() if line.strip() and not line.lstrip().startswith('--')]
                if actual != expected:
                    raise RuntimeError('Unexpected notification config suite declarations')
                fixture_root = stage / 'runtime/test-notification-config'
                files = {str(p.relative_to(fixture_root)) for p in fixture_root.rglob('*') if p.is_file() and p.suffix in ('.hs', '.hsc')}
                if files != {'Main.hs'} or digest(fixture_root / 'Main.hs') != '75acf70ffbb678c0679bbb23e7ca4be86e9d9859b5888b9fbf040327c3c5f72f':
                    raise RuntimeError('Unexpected notification config fixture sources')
                selected_targets = [('notification-config-controls', 'warlock-runtime:test:notification-config-controls')]
                build_targets = ['warlock-runtime:lib:warlock-runtime', selected_targets[0][1]]
                build_label = 'notification-config-build'
                protocol_suites = ()
                report['notificationConfig'] = {'ordinaryLibraryTarget': build_targets[0],
                    'scope': 'Optional trusted startup data only', 'nativeAcceptance': False, 'originalAcceptance': False}
            elif args.peer_role:
                library_targets = ['warlock-process-custody:lib:warlock-process-custody',
                                   'warlock-runtime:lib:warlock-runtime']
                for package, suite, directory in (('process-custody', 'bootstrap-facade-controls', 'test'),
                                                  ('runtime', 'persistent-bootstrap-controls', 'test-persistent')):
                    cabal_name = 'process-custody.cabal' if package == 'process-custody' else 'runtime.cabal'
                    stanza = (stage / package / cabal_name).read_text().split('\ntest-suite ' + suite + '\n', 1)[1]
                    stanza = re.split(r'\n(?:test-suite|executable|library|common|flag)\b', stanza, maxsplit=1)[0]
                    directories = re.search(r'^  hs-source-dirs: (.+)$', stanza, re.M)
                    if (not directories or directories.group(1).split() != [directory]
                            or re.search(r'^  cpp-options:', stanza, re.M)
                            or 'warlock-' + package not in stanza):
                        raise RuntimeError('Peer-role suite is not the declared ordinary-linked client: ' + suite)
                selected_targets = [('bootstrap-facade-controls', 'warlock-process-custody:test:bootstrap-facade-controls'),
                                    ('persistent-bootstrap-controls', 'warlock-runtime:test:persistent-bootstrap-controls'),
                                    ('bootstrap-facade-child', 'warlock-process-custody:exe:bootstrap-facade-child'),
                                    ('credential-peer-child', 'warlock-runtime:exe:credential-peer-child')]
                build_targets = [*library_targets, *[selected for _, selected in selected_targets]]
                build_label = 'peer-role-build'
                protocol_suites = ()
                report['peerRoleProfile'] = {'ordinaryLibraryTargets': library_targets,
                    'ordinaryLinkedSuiteDeclarationsChecked': True, 'testsUseHomeModules': False,
                    'authProfile': 'common', 'crossUserQualified': False, 'nativeAcceptance': False,
                    'scope': 'Same-user/current/replayed public bootstrap and ordinary API controls only; no native/whole-original acceptance'}
            elif args.held_executable:
                library_target = 'warlock-held-document-proposal:lib:warlock-held-document-proposal'
                library = (stage / 'held-document/held-document.cabal').read_text().split('\nlibrary\n', 1)[1].split('\ntest-suite ', 1)[0]
                exposed = re.search(r'^  exposed-modules: (.+)$', library, re.M)
                if not exposed or exposed.group(1).replace(',', '').split() != [
                        'Warlock.Platform.Resolver', 'Warlock.Platform.Executable', 'Warlock.Http.Document']:
                    raise RuntimeError('Ordinary held library module opacity differs')
                selected_targets = [('held-executable-controls', 'warlock-held-document-proposal:test:held-executable-controls'),
                                    ('custody-child', 'warlock-process-custody:exe:custody-child')]
                build_targets = [library_target, *[selected for _, selected in selected_targets]]
                build_label = 'held-executable-build'
                protocol_suites = ()
                report['heldExecutableProfile'] = {'ordinaryLibraryTarget': library_target,
                    'declaredOrdinaryInternalModulesExposed': False, 'testsUseHomeModules': True,
                    'publicLinkedTestProof': False, 'externalImportOpacityProbeExecuted': False, 'fixture': 'custody-child',
                    'scope': 'Held executable lease/process fixture only; no native desktop or original acceptance'}
            elif args.native_stage_build:
                from arm64_native_stage import TARGETS
                selected_targets = list(TARGETS)
                if args.provider_probe_build:
                    suite = 'webkit-provider-probe-contract-controls'
                    pure_target = 'warlock-runtime:test:' + suite
                    run('provider-pure-controls-build', common + ['build'] + flags + [pure_target], stage)
                    lines = run('list-provider-pure-controls', common + ['list-bin'] + flags + [pure_target], stage).splitlines()
                    if len(lines) != 1 or not Path(lines[0]).is_relative_to(output / 'dist') or Path(lines[0]).name != suite:
                        raise RuntimeError('Unexpected provider pure control image')
                    pure_image = image(Path(lines[0]))
                    runs = output / 'provider-pure-runs'
                    runs.mkdir(mode=0o700)
                    dispatch_path = output / 'provider-pure-dispatch.json'
                    dispatch_path.write_text(json.dumps({'suites': {pure_image['path']: {
                        'suite': suite, 'test': {'path': pure_image['path'], 'pin': [pure_image[k] for k in ('device', 'inode', 'size', 'sha256')]},
                        'fixtures': {}, 'runRoot': str(runs / suite)}}}) + '\n')
                    run('provider-pure-controls', [sys.executable, '-B', ROOT / 'tools/haskell_test_wrapper.py', pure_image['path']],
                        stage, 120, dict(env, WARLOCK_HASKELL_DISPATCH=str(dispatch_path)))
                    receipt = json.loads((runs / suite / 'results.json').read_text())
                    if (len(receipt) != 1 or receipt[0]['exit'] != 0 or receipt[0]['forcedCleanup']
                            or (runs / suite / 'default.log').read_text() != 'webkit-provider-probe-contract-controls: 13 complete\n'):
                        raise RuntimeError('Provider pure controls receipt differs')
                    report['providerPureControls'] = {'checks': 13, 'image': pure_image, 'metadataFFIExecuted': False}
                    selected_targets.append(('webkit-provider-probe', 'warlock-runtime:exe:webkit-provider-probe'))
                build_targets = ['warlock-held-document-proposal:lib:warlock-held-document-proposal',
                                 'warlock-process-custody:lib:warlock-process-custody',
                                 'warlock-protocol:lib:warlock-protocol',
                                 'warlock-runtime:lib:warlock-runtime',
                                 *[selected for _, selected in selected_targets]]
                build_label = 'native-stage-build'
                protocol_suites = ()
            else:
                build_targets = ([selected for _, selected in protocol_targets] if protocol_profile else
                                 [target, *[selected for _, selected in protocol_targets], backend])
                build_label = 'preview-schema-build' if args.preview_schema else ('protocol-build' if args.protocol else 'owner-build')
                selected_targets = (protocol_targets if protocol_profile else
                                    [('ui-origin-controls', target), *protocol_targets, ('warlock-ui-backend', backend)])
            if args.workspace_navigation_protocol:
                metadata = (stage / 'protocol/protocol.cabal').read_text()
                for suite, directory in (('workspace-navigation-controls', 'test-workspace-navigation'),
                                         ('desktop-boundary-controls', 'test-desktop')):
                    pieces = metadata.split('\ntest-suite ' + suite + '\n')
                    if len(pieces) != 2:
                        raise RuntimeError('Expected one ordinary-linked protocol suite: ' + suite)
                    stanza = re.split(r'\n(?:test-suite|executable|library|common|flag)\b', pieces[1], maxsplit=1)[0]
                    declarations = {}
                    for line in stanza.splitlines():
                        if not line.strip() or line.lstrip().startswith('--'):
                            continue
                        declaration = re.fullmatch(r'  ([a-z][a-z-]*): (.+)', line)
                        if not declaration or declaration.group(1) in declarations:
                            raise RuntimeError('Noncanonical or continued protocol suite field: ' + suite)
                        declarations[declaration.group(1)] = declaration.group(2)
                    required = {'type', 'hs-source-dirs', 'main-is', 'build-depends', 'default-language', 'ghc-options'}
                    if not required <= declarations.keys() or declarations.keys() - required - {'other-modules'}:
                        raise RuntimeError('Unexpected ordinary-linked protocol suite declarations: ' + suite)
                    dependencies = [item.strip() for item in declarations['build-depends'].split(',')]
                    extras = declarations.get('other-modules', '').replace(',', ' ').split()
                    allowed_extras = ['WorkspaceStandaloneLiterals'] if suite == 'workspace-navigation-controls' else []
                    if (declarations['type'] != 'exitcode-stdio-1.0'
                            or declarations['hs-source-dirs'] != directory
                            or declarations['main-is'] != 'Main.hs'
                            or declarations['default-language'] != 'Haskell2010'
                            or dependencies != ['base >=4.18 && <5', 'bytestring', 'text', 'warlock-protocol']
                            or declarations['ghc-options'] != '-Wall -Werror -Wcompat -Wincomplete-uni-patterns -Wincomplete-record-updates'
                            or (extras and extras != allowed_extras)):
                        raise RuntimeError('Protocol suite does not link the fixed ordinary library: ' + suite)
                    expected_files = {'Main.hs'} | {name + '.hs' for name in extras}
                    actual_files = {str(path.relative_to(stage / 'protocol' / directory))
                                    for path in (stage / 'protocol' / directory).rglob('*')
                                    if path.is_file() and path.suffix in ('.hs', '.hsc')}
                    if actual_files != expected_files:
                        raise RuntimeError('Protocol test source directory contains unreviewed home modules: ' + suite)
                build_targets = ['warlock-protocol:lib:warlock-protocol', *build_targets]
                build_label = 'workspace-navigation-protocol-build'
                report['workspaceNavigationProtocol'] = {
                    'ordinaryLibraryTarget': 'warlock-protocol:lib:warlock-protocol',
                    'suites': list(protocol_suites), 'testsUseHomeModules': False,
                    'ordinaryLinkedSuiteDeclarationsChecked': True,
                    'nativeDispatchQualified': False, 'originalAcceptance': False}
            run(build_label, common + ['build'] + flags + build_targets, stage)
            binaries = {}
            for name, selected in selected_targets:
                lines = run('list-' + name, common + ['list-bin'] + flags + [selected], stage).splitlines()
                if len(lines) != 1:
                    raise RuntimeError('Unexpected compiled binary path')
                path = Path(lines[0])
                if not path.is_relative_to(output / 'dist') or path.name != name:
                    raise RuntimeError('Unexpected compiled binary location')
                binaries[name] = image(path)
            documents, plain = {}, {}
            if not haskell_profile:
                frontend = output / 'frontend'
                frontend.mkdir(mode=0o700)
                shutil.copytree(ROOT / 'implementation/warlock/src', frontend / 'src')
                shutil.copytree(Path(packet['elmHome']), frontend / 'elm-home')
                shutil.copyfile(ROOT / 'implementation/warlock/elm.json', frontend / 'elm.json')
                elm_env = dict(env, ELM_HOME=str(frontend / 'elm-home'))
                documents, plain = {}, {}
                for role, entry in (('controller', 'HttpMain'), ('bar', 'HttpBar'), ('popup', 'HttpPopup')):
                    html = frontend / (entry + '.html')
                    run('compile-' + entry, [packet['elm'], 'make', 'src/' + entry + '.elm', '--optimize', '--output=' + str(html)], frontend, 180, elm_env)
                    info = image(html)
                    info['ancestors'] = [{'path': str(p), 'device': str(p.stat().st_dev), 'inode': str(p.stat().st_ino)}
                                         for p in reversed(html.parents) if str(p) != '/']
                    documents[role] = info
                    js = frontend / (entry + '.plain.js')
                    run('compile-plain-' + entry, [packet['elm'], 'make', 'src/' + entry + '.elm', '--output=' + str(js)], frontend, 180, elm_env)
                    plain[role] = image(js)
            report.update(executables=binaries, uiDocuments=documents, plainRoots=plain)
            if args.native_stage_build:
                from arm64_native_stage import collect
                report['nativeBuildStageManifest'] = collect(output, packet, binaries, documents, run, provider_probe=args.provider_probe_build)
            if args.preview_control:
                qa = ROOT / 'implementation/warlock/qa'
                result = json.loads(run('http-preview-control', [packet['node'],
                    qa / 'http-preview-control-replay.cjs', ROOT, plain['popup']['path']], timeout=180))
                expected = [('HttpPopup-native-control-closed-realm-lifetime', 8),
                            ('HttpPopup-matching-quarantine-retains-unconfirmed-reconcile', 4),
                            ('HttpPopup-restart-enrolls-new-realm-without-old-effect-replay', 2)]
                state = 20261105
                for index in range(32):
                    state = (1664525 * state + 1013904223) & 0xffffffff
                    expected.append((f'HttpPopup-control-LCG20261105-{index}-{state}', 7))
                results = result.get('results', [])
                coverage = result.get('coverage', {})
                if (set(result) != {'ok', 'results', 'imageSha256', 'fixtureSha256', 'observerSha256',
                                    'tool', 'fuzz', 'coverage', 'originalAcceptanceClaim'}
                        or result.get('ok') is not True or result.get('originalAcceptanceClaim') is not False
                        or [(row.get('name'), row.get('steps')) for row in results] != expected
                        or any(set(row) != {'name', 'steps', 'freshRuns', 'negative', 'instrumentation'}
                               or row.get('freshRuns') != 2 or row.get('negative') != 'grant-retention-model-altered'
                               for row in results)
                        or result.get('tool') != {'node': 'v26.13.0'}
                        or result.get('fuzz') != {'seed': 20261105, 'cases': 32,
                            'generator': 'LCG32 1664525/1013904223; 32 seven-step realm sequences'}
                        or result.get('imageSha256') != plain['popup']['sha256']
                        or result.get('fixtureSha256') != digest(qa / 'http-preview-control-literals.cjs')
                        or result.get('observerSha256') != digest(qa / 'sol-http-root-observer-0535.cjs')
                        or any(coverage.get(k) is not False for k in ('complete', 'originalAccepted', 'nativeAccepted'))):
                    raise RuntimeError('Fixed preview-control replay report differs')
                report['previewControl'] = result
            if args.owner or args.preview_control or protocol_profile or args.held_executable or args.peer_role or args.notification_config or args.notification_issuer or args.catalog_nodisplay or args.catalog_source_revision or args.catalog_publication or args.application_owner_route:
                runs = output / 'runs'
                runs.mkdir(mode=0o700)
                def wrapped(item):
                    return {'path': item['path'], 'pin': [item[k] for k in ('device', 'inode', 'size', 'sha256')]}
                dispatch = {'suites': {}}
                if args.application_owner_route:
                    for suite in ('catalog-nodisplay-controls', 'catalog-source-revision-adversarial', 'catalog-publication-controls', 'application-owner-route-controls'):
                        dispatch['suites'][binaries[suite]['path']] = {'suite': suite, 'test': wrapped(binaries[suite]),
                            'fixtures': ({name: wrapped(binaries[name]) for name in ('application-owner-peer-fixture', 'application-argv-fixture')}
                                         if suite == 'application-owner-route-controls' else {}), 'runRoot': str(runs / suite)}
                elif args.catalog_publication:
                    for suite in ('catalog-nodisplay-controls', 'catalog-source-revision-adversarial', 'catalog-publication-controls'):
                        dispatch['suites'][binaries[suite]['path']] = {'suite': suite, 'test': wrapped(binaries[suite]),
                            'fixtures': {}, 'runRoot': str(runs / suite)}
                elif args.catalog_source_revision:
                    for suite in ('catalog-nodisplay-controls', 'catalog-source-revision-adversarial'):
                        dispatch['suites'][binaries[suite]['path']] = {'suite': suite, 'test': wrapped(binaries[suite]),
                            'fixtures': {}, 'runRoot': str(runs / suite)}
                elif args.catalog_nodisplay:
                    suite = 'catalog-nodisplay-controls'
                    dispatch['suites'][binaries[suite]['path']] = {'suite': suite, 'test': wrapped(binaries[suite]),
                        'fixtures': {}, 'runRoot': str(runs / suite)}
                elif args.notification_issuer:
                    suite = 'notification-issuer-controls'
                    dispatch['suites'][binaries[suite]['path']] = {'suite': suite, 'test': wrapped(binaries[suite]),
                        'fixtures': {}, 'runRoot': str(runs / suite)}
                elif args.notification_config:
                    suite = 'notification-config-controls'
                    dispatch['suites'][binaries[suite]['path']] = {'suite': suite, 'test': wrapped(binaries[suite]),
                        'fixtures': {}, 'runRoot': str(runs / suite)}
                elif args.peer_role:
                    for suite, fixture in (('bootstrap-facade-controls', 'bootstrap-facade-child'),
                                           ('persistent-bootstrap-controls', 'credential-peer-child')):
                        dispatch['suites'][binaries[suite]['path']] = {
                            'suite': suite, 'test': wrapped(binaries[suite]),
                            'fixtures': {fixture: wrapped(binaries[fixture])}, 'authProfile': 'common',
                            'runRoot': str(runs / suite)}
                elif args.held_executable:
                    dispatch['suites'][binaries['held-executable-controls']['path']] = {
                        'suite': 'held-executable-controls', 'test': wrapped(binaries['held-executable-controls']),
                        'fixtures': {'custody-child': wrapped(binaries['custody-child'])},
                        'runRoot': str(runs / 'held-executable-controls')}
                elif not protocol_profile:
                    dispatch['suites'][binaries['ui-origin-controls']['path']] = {
                        'suite': 'ui-origin-controls', 'test': wrapped(binaries['ui-origin-controls']),
                        'fixtures': {'warlock-ui-backend': wrapped(binaries['warlock-ui-backend'])},
                        'uiDocuments': documents, 'runRoot': str(runs / 'ui-origin-controls')}
                for suite in protocol_suites:
                    dispatch['suites'][binaries[suite]['path']] = {
                        'suite': suite, 'test': wrapped(binaries[suite]),
                        'fixtures': {}, 'runRoot': str(runs / suite)}
                dispatch_path = output / 'dispatch.json'
                dispatch_path.write_text(json.dumps(dispatch, indent=2) + '\n')
                test_env = dict(env, WARLOCK_HASKELL_DISPATCH=str(dispatch_path))
                report['suiteReceipts'] = {}
                suites = (('catalog-nodisplay-controls', 'catalog-source-revision-adversarial', 'catalog-publication-controls', 'application-owner-route-controls') if args.application_owner_route else
                          (('catalog-nodisplay-controls', 'catalog-source-revision-adversarial', 'catalog-publication-controls') if args.catalog_publication else
                          (('catalog-nodisplay-controls', 'catalog-source-revision-adversarial') if args.catalog_source_revision else
                          (('catalog-nodisplay-controls',) if args.catalog_nodisplay else
                          (('notification-issuer-controls',) if args.notification_issuer else
                          (('notification-config-controls',) if args.notification_config else
                           (('bootstrap-facade-controls', 'persistent-bootstrap-controls') if args.peer_role else
                            (('held-executable-controls',) if args.held_executable else
                             (protocol_suites if protocol_profile else (*protocol_suites, 'ui-origin-controls'))))))))))
                for suite in suites:
                    run(suite, [sys.executable, '-B', ROOT / 'tools/haskell_test_wrapper.py',
                                binaries[suite]['path']], stage, 900, test_env)
                    receipt = json.loads((runs / suite / 'results.json').read_text())
                    if len(receipt) != 1 or receipt[0]['exit'] != 0 or receipt[0]['forcedCleanup']:
                        raise RuntimeError(suite + ' lacks successful terminal receipt')
                    if args.application_owner_route:
                        item = receipt[0]
                        fixed_image = runs / suite / 'image' / suite
                        fixed_storage = runs / suite / 'storage'
                        actual_image = image(fixed_image)
                        if (item.get('mode') != 'default' or item.get('timeout') is not False
                                or item.get('forcedCleanup') is not False or item.get('argv') != ([str(fixed_storage), str(runs / suite / 'image' / 'application-owner-peer-fixture'), str(runs / suite / 'image' / 'application-argv-fixture')] if suite == 'application-owner-route-controls' else [str(fixed_storage)])
                                or item.get('image') != str(fixed_image)
                                or item.get('imagePin') != [actual_image['device'], actual_image['inode'], actual_image['size'], actual_image['sha256']]
                                or actual_image['size'] != binaries[suite]['size'] or actual_image['sha256'] != binaries[suite]['sha256']):
                            raise RuntimeError('Catalog source-revision COPY receipt differs')
                        sentinel = {'catalog-nodisplay-controls': 'catalog-nodisplay-controls: complete\n',
                                    'catalog-source-revision-adversarial': 'catalog-source-revision-adversarial: complete\n',
                                    'catalog-publication-controls': 'catalog-publication-controls: complete\n', 'application-owner-route-controls': 'application-owner-route-controls: complete\n'}[suite]
                        log = runs / suite / 'default.log'
                        if log.is_symlink() or not log.is_file() or log.stat().st_size > 16384 or log.read_text() != sentinel:
                            raise RuntimeError('Catalog source-revision terminal output differs')
                        if suite == 'application-owner-route-controls':
                            expected_copies = []
                            for name in ('application-owner-peer-fixture', 'application-argv-fixture'):
                                copied = image(runs / suite / 'image' / name)
                                if (copied['size'], copied['sha256']) != (binaries[name]['size'], binaries[name]['sha256']):
                                    raise RuntimeError('Application controlled image differs')
                                expected_copies.append({'path': copied['path'], 'pin': [copied[k] for k in ('device', 'inode', 'size', 'sha256')]})
                            if item.get('fixtureImages') != expected_copies:
                                raise RuntimeError('Application controlled image receipt differs')
                    if args.catalog_publication:
                        item = receipt[0]
                        fixed_image = runs / suite / 'image' / suite
                        fixed_storage = runs / suite / 'storage'
                        actual_image = image(fixed_image)
                        if (item.get('mode') != 'default' or item.get('timeout') is not False
                                or item.get('forcedCleanup') is not False or item.get('argv') != [str(fixed_storage)]
                                or item.get('image') != str(fixed_image)
                                or item.get('imagePin') != [actual_image['device'], actual_image['inode'], actual_image['size'], actual_image['sha256']]
                                or actual_image['size'] != binaries[suite]['size'] or actual_image['sha256'] != binaries[suite]['sha256']):
                            raise RuntimeError('Catalog source-revision COPY receipt differs')
                        sentinel = {'catalog-nodisplay-controls': 'catalog-nodisplay-controls: complete\n',
                                    'catalog-source-revision-adversarial': 'catalog-source-revision-adversarial: complete\n',
                                    'catalog-publication-controls': 'catalog-publication-controls: complete\n'}[suite]
                        log = runs / suite / 'default.log'
                        if log.is_symlink() or not log.is_file() or log.stat().st_size > 16384 or log.read_text() != sentinel:
                            raise RuntimeError('Catalog source-revision terminal output differs')
                    if args.catalog_source_revision:
                        item = receipt[0]
                        fixed_image = runs / suite / 'image' / suite
                        fixed_storage = runs / suite / 'storage'
                        actual_image = image(fixed_image)
                        if (item.get('mode') != 'default' or item.get('timeout') is not False
                                or item.get('forcedCleanup') is not False or item.get('argv') != [str(fixed_storage)]
                                or item.get('image') != str(fixed_image)
                                or item.get('imagePin') != [actual_image['device'], actual_image['inode'], actual_image['size'], actual_image['sha256']]
                                or actual_image['size'] != binaries[suite]['size'] or actual_image['sha256'] != binaries[suite]['sha256']):
                            raise RuntimeError('Catalog source-revision COPY receipt differs')
                        sentinel = {'catalog-nodisplay-controls': 'catalog-nodisplay-controls: complete\n',
                                    'catalog-source-revision-adversarial': 'catalog-source-revision-adversarial: complete\n'}[suite]
                        log = runs / suite / 'default.log'
                        if log.is_symlink() or not log.is_file() or log.stat().st_size > 16384 or log.read_text() != sentinel:
                            raise RuntimeError('Catalog source-revision terminal output differs')
                    if args.catalog_nodisplay:
                        item = receipt[0]
                        fixed_image = runs / suite / 'image' / suite
                        fixed_storage = runs / suite / 'storage'
                        actual_image = image(fixed_image)
                        if (item.get('mode') != 'default' or item.get('timeout') is not False
                                or item.get('forcedCleanup') is not False or item.get('argv') != [str(fixed_storage)]
                                or item.get('image') != str(fixed_image)
                                or item.get('imagePin') != [actual_image['device'], actual_image['inode'], actual_image['size'], actual_image['sha256']]
                                or actual_image['size'] != binaries[suite]['size'] or actual_image['sha256'] != binaries[suite]['sha256']):
                            raise RuntimeError('Catalog NoDisplay COPY receipt differs')
                        log = runs / suite / 'default.log'
                        if log.is_symlink() or not log.is_file() or log.stat().st_size > 16384 or log.read_text() != 'catalog-nodisplay-controls: complete\n':
                            raise RuntimeError('Catalog NoDisplay terminal output differs')
                    if args.notification_issuer:
                        item = receipt[0]
                        fixed_image = runs / suite / 'image' / suite
                        fixed_storage = runs / suite / 'storage'
                        actual_image = image(fixed_image)
                        if (item.get('mode') != 'default' or item.get('timeout') is not False
                                or item.get('forcedCleanup') is not False or item.get('argv') != [str(fixed_storage)]
                                or item.get('image') != str(fixed_image)
                                or item.get('imagePin') != [actual_image['device'], actual_image['inode'], actual_image['size'], actual_image['sha256']]
                                or actual_image['size'] != binaries[suite]['size'] or actual_image['sha256'] != binaries[suite]['sha256']):
                            raise RuntimeError('Issuer fixture COPY receipt differs')
                        log = runs / suite / 'default.log'
                        if log.is_symlink() or not log.is_file() or log.stat().st_size > 16384 or log.read_text() != 'notification issuer fixture complete\n':
                            raise RuntimeError('Issuer fixture terminal output differs')
                    if args.notification_config:
                        item = receipt[0]
                        fixed_image = runs / suite / 'image' / suite
                        fixed_storage = runs / suite / 'storage'
                        actual_image = image(fixed_image)
                        if (item.get('mode') != 'default' or item.get('timeout') is not False
                                or item.get('forcedCleanup') is not False or item.get('argv') != [str(fixed_storage)]
                                or item.get('image') != str(fixed_image)
                                or item.get('imagePin') != [actual_image['device'], actual_image['inode'], actual_image['size'], actual_image['sha256']]
                                or actual_image['size'] != binaries[suite]['size'] or actual_image['sha256'] != binaries[suite]['sha256']):
                            raise RuntimeError('Notification config COPY receipt differs')
                        log = runs / suite / 'default.log'
                        if log.is_symlink() or not log.is_file() or log.stat().st_size > 16384 or log.read_text() != EXPECTED_NOTIFICATION_CONFIG:
                            raise RuntimeError('Notification config ordered literal results differ')
                        report['notificationConfig']['fixtureChecks'] = 30
                    if args.held_executable and (receipt[0].get('mode') != 'default' or receipt[0].get('timeout') is not False
                            or receipt[0].get('argv') != [str(runs / suite / 'image'), 'custody-child',
                                                        binaries['custody-child']['size'], binaries['custody-child']['sha256']]):
                        raise RuntimeError('Held executable disposable COPY receipt differs')
                    if args.peer_role:
                        fixture = 'bootstrap-facade-child' if suite == 'bootstrap-facade-controls' else 'credential-peer-child'
                        item = binaries[fixture]
                        expected_argv = ([str(runs / suite / 'image'), fixture, item['size'], item['sha256']]
                                         if suite == 'bootstrap-facade-controls' else
                                         [item['path'], item['device'], item['inode'], item['size'], item['sha256'], 'common'])
                        if (receipt[0].get('mode') != 'default' or receipt[0].get('timeout') is not False
                                or receipt[0].get('argv') != expected_argv):
                            raise RuntimeError('Peer-role exact COPY/CHILD normal receipt differs: ' + suite)
                        if suite == 'persistent-bootstrap-controls':
                            records = [json.loads(line) for line in (runs / suite / 'default.log').read_text().splitlines()
                                       if line.startswith('{')]
                            verdicts = [row for row in records if row.get('kind') == 'persistent-auth-verdict']
                            if (len(verdicts) != 1 or verdicts[0].get('schema') != 1 or verdicts[0].get('mode') != 'common'
                                    or verdicts[0].get('passed') is not True or verdicts[0].get('cases') != 16
                                    or any(verdicts[0].get(key) is not False for key in
                                           ('crossUserIncluded', 'completeOriginalEvidence', 'nativeExecutionAcceptance'))):
                                raise RuntimeError('Original same-user persistent controls verdict differs')
                            report['peerRoleProfile']['persistentAuthVerdict'] = verdicts[0]
                    report['suiteReceipts'][suite] = receipt
            for item in [*binaries.values(), *documents.values(), *plain.values()]:
                if image(Path(item['path'])) != {k: item[k] for k in ('path', 'device', 'inode', 'size', 'sha256')}:
                    raise RuntimeError('Compiled ARM artifact changed during profile')
        verify(full=True)
        if any(digest(ROOT / name) != sha for name, sha in report['sourceHashes'].items()):
            raise RuntimeError('ARM input source changed')
        report['passed'] = True
    except Exception as error:  # noqa: BLE001 -- retain failure evidence before exiting
        report.update(passed=False, error=str(error))
    finally:
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
