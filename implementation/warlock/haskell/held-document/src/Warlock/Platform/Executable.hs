-- Opaque, resolver-validated executable ownership. No FD constructor or issuer.
module Warlock.Platform.Executable
 (ExecutableLease, HeldExecutable, LeaseRole(..), LeaseState(..), LeaseError(..)
 ,newExecutableLease, acquireExecutableLease, issueReadyExecutable, retireExecutableLease
 ,executableLeaseState, observeHeldRole, HeldBorrow, prepareHeldBorrow, activateHeldBorrowWhile, tryHeldBorrowNotAcquired, tryReleaseHeld, releaseHeldBorrow, borrowHeld, borrowHeldInterruptible, borrowHeldWhile, retireHeld) where
import Warlock.Platform.Executable.Internal
