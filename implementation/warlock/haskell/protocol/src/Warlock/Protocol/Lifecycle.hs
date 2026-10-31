{-# LANGUAGE OverloadedStrings #-}
-- Pure bookkeeping proposal. Nothing here proves storage, native ownership,
-- authentication, deadlines, nor permission to execute an effect.
module Warlock.Protocol.Lifecycle
  ( Correlation, correlation, Tracker, initial, markCommitAttempt, markUnknown
  , observePrepared, commitAttempted, pendingState, LifecycleError(..) ) where
import Data.Text (Text)
import qualified Data.Text as T
import Warlock.Protocol.Identity (Binding, Counter, isZero)
import Warlock.Protocol.Custody (Intent, intentBinding)
import Warlock.Protocol.Wire (SelectionId)

data Correlation = Correlation Binding Intent Text SelectionId Counter Counter deriving (Eq, Show)
data LifecycleError = BadKey | Foreign | DuplicateCommit | NoAdmission deriving (Eq, Show)
correlation :: Binding -> Intent -> Text -> SelectionId -> Counter -> Counter -> Either LifecycleError Correlation
correlation owner intent key selection deadline prepared
  | owner /= intentBinding intent || isZero deadline || isZero prepared = Left Foreign
  | T.length key /= 64 || not (T.all hex key) = Left BadKey
  | otherwise = Right (Correlation owner intent key selection deadline prepared)
  where hex c = (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')
-- K's derivation is a separate required verification, not this shape check.
data Phase = Waiting | Uncertain deriving (Eq, Show)
data Tracker = Tracker Correlation Phase Bool deriving (Eq, Show)
initial :: Correlation -> Tracker
initial key = Tracker key Waiting False
commitAttempted :: Tracker -> Bool
commitAttempted (Tracker _ _ flag) = flag
pendingState :: Tracker -> Bool
pendingState (Tracker _ phase _) = phase == Waiting
markCommitAttempt :: Correlation -> Tracker -> Either LifecycleError Tracker
markCommitAttempt key (Tracker existing phase used)
  | key /= existing = Left Foreign
  | used = Left DuplicateCommit
  | phase /= Waiting = Left NoAdmission
  | otherwise = Right (Tracker existing Uncertain True)
markUnknown :: Correlation -> Tracker -> Either LifecycleError Tracker
markUnknown key (Tracker existing _ used)
  | key /= existing = Left Foreign
  | otherwise = Right (Tracker existing Uncertain used)
observePrepared :: Correlation -> Tracker -> Either LifecycleError Tracker
observePrepared key (Tracker existing _ used)
  | key /= existing = Left Foreign
  | otherwise = Right (Tracker existing Waiting used)
-- Returning to Waiting after a same-key prepared observation does not reset the
-- consumed bit. Durable monotonicity still requires the actual store and tests.
