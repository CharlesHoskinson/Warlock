-- Private proposal: no transition accepts a native outcome without the full key.
module Warlock.Protocol.Custody
  ( Operation(..), Intent, intent, intentBinding, Decision(..), Custody(..), IntentError(..) ) where

import Warlock.Protocol.Identity (Binding, Context, Counter, isZero, lifetime, frontend, contextLifetime, contextEpoch)

data Operation = Minimize | Restore | Activate deriving (Eq, Show)
data Intent = Intent Binding Counter Counter Counter Context Operation deriving (Eq, Show)
data IntentError = InvalidIdentity | WrongAuthority deriving (Eq, Show)
intent :: Binding -> Counter -> Counter -> Counter -> Context -> Operation -> Either IntentError Intent
intent b req generation incarnation ctx op
  | any isZero [req,generation,incarnation] = Left InvalidIdentity
  | lifetime b /= contextLifetime ctx || frontend b /= contextEpoch ctx = Left WrongAuthority
  | otherwise = Right (Intent b req generation incarnation ctx op)
intentBinding :: Intent -> Binding
intentBinding (Intent owner _ _ _ _ _) = owner
data Decision = Committed | Refused | Cancelled deriving (Eq, Show)
-- No settlement reducer is exported: Intent alone omits K/S/D/P and is not an
-- adequate authority to accept a terminal. Full correlation remains unimplemented.
data Custody = Pending | Unknown | Terminal Decision deriving (Eq, Show)
