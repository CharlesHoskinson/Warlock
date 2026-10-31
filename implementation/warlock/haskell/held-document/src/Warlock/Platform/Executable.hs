-- Opaque, resolver-validated executable ownership. No FD constructor or issuer.
module Warlock.Platform.Executable
 (ExecutableLease, HeldExecutable, LeaseRole(..), LeaseState(..), LeaseError(..)
 ,newExecutableLease, acquireExecutableLease, issueReadyExecutable, retireExecutableLease
 ,executableLeaseState, borrowHeld, retireHeld) where
import Warlock.Platform.Executable.Internal
