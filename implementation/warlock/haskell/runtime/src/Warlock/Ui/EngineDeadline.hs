{-# LANGUAGE ScopedTypeVariables #-}
-- PREPARATION DRAFT. Root review and protected checks required.
-- This module plans using the ORIGINAL opaque absolute admission deadline; it
-- does not authenticate startup, perform IO, enforce timeouts, or prove cleanup.
module Warlock.Ui.EngineDeadline
  ( EngineDeadline, Stage(..), Budget(..), Completion(..)
  , fromOwner, fromAuthenticatedStartup, absoluteWire
  , plan, checkCompletion
  ) where

import Warlock.Capture.Process.Bootstrap
  ( AdmissionDeadline, ToolError, deadlineAbsoluteNs
  , deadlineFromAbsoluteNs, remainingMicros )

-- Constructor deliberately private. Every stage receives this same value.
newtype EngineDeadline = EngineDeadline AdmissionDeadline

data Stage = Startup | RpcRead | RpcWrite | Stop deriving (Eq, Show)
data Budget = Expired Stage | Available Stage Int deriving (Eq, Show)
data Completion = InTime Stage | DeadlinePassedOutcomeUnknown Stage
  deriving (Eq, Show)

-- Only the owner, which already holds the original opaque deadline, calls this.
fromOwner :: AdmissionDeadline -> EngineDeadline
fromOwner = EngineDeadline

-- Only after authenticating the held-executable peer and trusted startup frame;
-- a peer-supplied value is not authority. Both processes must share the same
-- CLOCK_MONOTONIC domain. The caller also binds this value to the original
-- owner's absoluteWire value, never to a peer-chosen replacement.
fromAuthenticatedStartup :: String -> IO (Either ToolError EngineDeadline)
fromAuthenticatedStartup raw = fmap (fmap EngineDeadline) (deadlineFromAbsoluteNs raw)

-- Canonical original absolute nanoseconds, not a relative duration. This
-- read-only operation is ALREADY exported by Bootstrap in the reviewed tree.
absoluteWire :: EngineDeadline -> String
absoluteWire (EngineDeadline deadline) = deadlineAbsoluteNs deadline

-- Call immediately before EACH interruptible channel/startup/stop operation;
-- pass at most this budget to the applicable reviewed transport primitive.
-- It is a plan, not a guarantee: scheduling can consume D before IO starts.
-- Do not apply asynchronous timeouts through GTK/native callbacks; their owner
-- observes stop and drains callbacks. The original parent still bounds D.
plan :: EngineDeadline -> Stage -> IO Budget
plan (EngineDeadline deadline) stage = do
  left <- remainingMicros deadline
  pure (if left <= 0 then Expired stage else Available stage left)

-- Recheck after every potentially blocking operation. If D passed, an IO
-- operation may already have taken effect; classify it as uncertain, poison
-- the channel where applicable, perform owned cleanup and NEVER replay it.
-- This check does not convert a failed operation into a success.
checkCompletion :: EngineDeadline -> Stage -> IO Completion
checkCompletion (EngineDeadline deadline) stage = do
  left <- remainingMicros deadline
  pure (if left <= 0 then DeadlinePassedOutcomeUnknown stage else InTime stage)

{-
Integration contract, NOT an implemented transport:
* Preserve one D across startup, every request/reply read and write, and stop.
  Never use deadlineAfter, now + remaining, a new per-operation deadline, or
  peer remaining values to construct/extend an EngineDeadline. On each partial
  read/write recompute plan from D; EOF/partial uncertainty poisons and no replay.
* Available Int is an upper bound sampled at a point in time, NOT a promise of
  time remaining later; syscall setup/scheduling and serial teardown consume it.
  Check completion after blocking IO. Ensure owned cleanup and accurately report
  uncertain termination even after expiration; don't claim cleanup succeeded.
* Startup must be authenticated/bound to the held executable, original owner,
  verified peer credentials and same monotonic clock domain. The importer's
  canonical/future/30-second validation is not authentication.
* No Owner scope/queue lock is held across an RPC. One process remains the sole
  reaper. This module creates no native authority, timer, worker, or service.

Source-patch text: NO patch is required at this source revision. The minimal
read-only API is already present in Warlock.Capture.Process.Bootstrap's export
and import lists:
  AdmissionDeadline, deadlineAbsoluteNs, deadlineFromAbsoluteNs, remainingMicros
and Internal.hsc already defines `deadlineAbsoluteNs :: AdmissionDeadline ->
String`. If a different branch lacks only the re-export, the minimal patch is
adding `deadlineAbsoluteNs` to BOTH Bootstrap's module export list and its
explicit Warlock.Capture.Process.Internal import list. Do not expose the opaque
constructor or add an accessor reconstructed from remainingMicros.

Root-owned verification: compile together with EngineDeadlineTest.hs; drive
actual interruptible IPC with controlled delays at every stage, original D,
partial write/read, EOF, cleanup and reaper state. Test expired before starting,
expired during write/read/stop, and successful no-expiry; verify no replay,
no added D and owner failure/cleanup reporting. No tests were run by the author.
-}
