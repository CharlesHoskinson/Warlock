{-# LANGUAGE OverloadedStrings #-}
-- Canonical opaque identity data, not authentication or native permission.
-- Constructors stay internal; counters never pass through Float.
module Warlock.Protocol.Identity
  ( Counter, CounterError(..), parseCounter, renderCounter, isZero, addCounter
  , Binding, binding, lifetime, session, frontend, Context, context
  , contextLifetime, contextEpoch, contextOutput, contextRevision ) where

import Data.Char (ord)
import Data.Text (Text)
import qualified Data.Text as T
import Data.Word (Word64)

newtype Counter = Counter Word64 deriving (Eq, Ord, Show)
data CounterError = EmptyCounter | NonCanonical | CounterOverflow | ZeroIdentity
                  | ContextMismatch deriving (Eq, Show)
parseCounter :: Bool -> Text -> Either CounterError Counter
parseCounter permitZero text
  | T.null text = Left EmptyCounter
  | T.length text > 1 && T.take 1 text == "0" = Left NonCanonical
  | otherwise = do
      n <- T.foldl' step (Right 0) text
      if n == 0 && not permitZero then Left ZeroIdentity else Right (Counter n)
  where
    step result char = do
      n <- result
      if char < '0' || char > '9' then Left NonCanonical else do
        let digit = fromIntegral (ord char - ord '0') :: Word64
        if n > (maxBound - digit) `div` 10 then Left CounterOverflow
        else Right (n * 10 + digit)
renderCounter :: Counter -> Text
renderCounter (Counter n) = T.pack (show n)
isZero :: Counter -> Bool
isZero (Counter n) = n == 0
addCounter :: Counter -> Word64 -> Either CounterError Counter
addCounter (Counter n) delta
  | n > maxBound - delta = Left CounterOverflow
  | otherwise = Right (Counter (n + delta))

data Binding = Binding Counter Counter Counter deriving (Eq, Ord, Show)
binding :: Counter -> Counter -> Counter -> Either CounterError Binding
binding a b c | any isZero [a,b,c] = Left ZeroIdentity
              | otherwise = Right (Binding a b c)
lifetime, session, frontend :: Binding -> Counter
lifetime (Binding a _ _) = a
session (Binding _ b _) = b
frontend (Binding _ _ c) = c

data Context = Context Counter Counter Counter Counter deriving (Eq, Ord, Show)
context :: Binding -> Counter -> Counter -> Counter -> Counter -> Either CounterError Context
context owner life epoch output revision
  | any isZero [life,epoch,output,revision] = Left ZeroIdentity
  | life /= lifetime owner || epoch /= frontend owner = Left ContextMismatch
  | otherwise = Right (Context life epoch output revision)
contextLifetime, contextEpoch, contextOutput, contextRevision :: Context -> Counter
contextLifetime (Context a _ _ _) = a
contextEpoch (Context _ b _ _) = b
contextOutput (Context _ _ c _) = c
contextRevision (Context _ _ _ d) = d
