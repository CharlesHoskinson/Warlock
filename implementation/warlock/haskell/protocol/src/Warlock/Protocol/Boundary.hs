-- Opaque decoded observations and lifecycle only: no native grant or issuer.
module Warlock.Protocol.Boundary
 (Direction(..), Reason(..), Envelope, Gate, GateStatus(..), dispatch, retire, gateStatus, rejectionReasons) where
import Warlock.Protocol.Boundary.Internal (Direction(..),Reason(..),Envelope,Gate,GateStatus(..),dispatch,retire,gateStatus,rejectionReasons)
