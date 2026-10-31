-- Caller-facing ticket: observation is not authority to close a raw handle.
module Warlock.Capture.Process.Transfer
 (TransferTicket, TransferDisposition(..), TransferError(..), newTransferTicket,
  closeCallerTransfer, transferDisposition) where
import Warlock.Capture.Process.Transfer.Internal
