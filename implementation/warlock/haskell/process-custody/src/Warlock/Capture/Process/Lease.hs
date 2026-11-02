-- Compatibility import: one owner type exists in held-document.
module Warlock.Capture.Process.Lease
 (HeldExecutable, borrowHeld, borrowHeldInterruptible, borrowHeldWhile, retireHeld, LeaseError(..)) where
import Warlock.Platform.Executable (HeldExecutable, borrowHeld, borrowHeldInterruptible, borrowHeldWhile, retireHeld, LeaseError(..))
