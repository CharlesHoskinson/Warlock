-- Compatibility import: one owner type exists in held-document.
module Warlock.Capture.Process.Lease
 (HeldExecutable, borrowHeld, retireHeld, LeaseError(..)) where
import Warlock.Platform.Executable (HeldExecutable, borrowHeld, retireHeld, LeaseError(..))
