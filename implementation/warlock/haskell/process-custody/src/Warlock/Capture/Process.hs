-- Opaque caller facade. Lease issuance and owner mutation remain package internal.
module Warlock.Capture.Process
 ( Owner, OwnerStatus(..), newOwner, status, Tool(..), ToolError(..), Captured(..), runTool
 , HeldExecutable, TransferTicket, TransferDisposition(..), TransferError(..)
 , closeCallerTransfer, transferDisposition, SelectedSpawn, selectedHeld, Session
 , AdmissionDeadline, deadlineAfter, remainingMicros, runSelectedUntil, SelectedResult(..)
 , awaitLeader, observeSession, SessionObservation(..) ) where
import Warlock.Capture.Process.Internal
import Warlock.Capture.Process.Transfer (TransferTicket, TransferDisposition(..), TransferError(..), closeCallerTransfer, transferDisposition)
