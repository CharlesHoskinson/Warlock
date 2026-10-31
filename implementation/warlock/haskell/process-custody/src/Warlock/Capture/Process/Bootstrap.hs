-- Bounded selected-process operations. A session observation is not peer
-- authentication, and a selected process is not native-effect authority.
module Warlock.Capture.Process.Bootstrap
 ( Owner, OwnerStatus(..), newOwner, status
 , HeldExecutable, TransferTicket, TransferDisposition(..), TransferError(..)
 , newTransferTicket, closeCallerTransfer, transferDisposition
 , SelectedSpawn, selectedHeld, selectedHeldNoInput
 , Session, SessionObservation(..), observeSession, awaitLeader
 , AdmissionDeadline, deadlineAfter, deadlineAbsoluteNs, deadlineFromAbsoluteNs, remainingMicros
 , ToolError(..), Captured(..), Containment(..), SelectedOutcome
 , selectedOperation, selectedContainment, selectedCustody, runSelectedDetailed
 ) where

import Warlock.Capture.Process.Internal
 ( Owner, OwnerStatus(..), newOwner, status, HeldExecutable, SelectedSpawn
 , selectedHeld, selectedHeldNoInput, Session, SessionObservation(..)
 , observeSession, awaitLeader, AdmissionDeadline, deadlineAfter
 , deadlineAbsoluteNs, deadlineFromAbsoluteNs, remainingMicros, ToolError(..)
 , Captured(..), Containment(..), SelectedOutcome, selectedOperation
 , selectedContainment, selectedCustody, runSelectedDetailed )
import Warlock.Capture.Process.Transfer
 ( TransferTicket, TransferDisposition(..), TransferError(..), newTransferTicket
 , closeCallerTransfer, transferDisposition )
