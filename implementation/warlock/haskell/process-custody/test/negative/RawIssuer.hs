-- Must fail: a raw descriptor cannot issue a validated executable lease.
module RawIssuer where
import Warlock.Capture.Process.Bootstrap (issueVerified)
