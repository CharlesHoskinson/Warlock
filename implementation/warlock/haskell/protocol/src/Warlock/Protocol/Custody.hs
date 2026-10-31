-- Canonical opaque intent data. Constructing an identity grants no native authority.
module Warlock.Protocol.Custody
  ( Operation(..), Intent, intent, intentBinding, intentRequest, intentGeneration
  , intentIncarnation, intentContext, intentOperation, Decision(..), Custody(..), IntentError(..) ) where

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
intentRequest, intentGeneration, intentIncarnation :: Intent -> Counter
intentRequest (Intent _ request _ _ _ _) = request
intentGeneration (Intent _ _ generation _ _ _) = generation
intentIncarnation (Intent _ _ _ incarnation _ _) = incarnation
intentContext :: Intent -> Context
intentContext (Intent _ _ _ _ ctx _) = ctx
intentOperation :: Intent -> Operation
intentOperation (Intent _ _ _ _ _ operation) = operation
data Decision = Committed | Refused | Cancelled deriving (Eq, Show)
-- No settlement reducer is exported: Intent alone omits K/S/D/P and is not an
-- adequate authority to accept a terminal. Full correlation remains unimplemented.
data Custody = Pending | Unknown | Terminal Decision deriving (Eq, Show)
