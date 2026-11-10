{-# LANGUAGE OverloadedStrings #-}
-- Passive application data. Decoding never grants native authority.
module Warlock.Protocol.WorkspaceNavigation
  ( NavigationRequest, NavigationIntent, WorkspaceRow
  , decodeWorkspaceNavigation, encodeWorkspaceNavigation
  , navigationBinding, navigationIntent, navigationRequest, navigationGeneration
  , navigationSource, navigationDestination, navigationContext
  , workspaceIdentity, workspaceGeneration, workspaceMonitor, workspaceOutputGeneration
  ) where

import qualified Data.ByteString as B
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Warlock.Protocol.Identity
import Warlock.Protocol.StrictJson
import Warlock.Protocol.Wire (parseBinding)

data WorkspaceRow = WorkspaceRow Text Counter Counter Counter deriving (Eq, Show)
data NavigationIntent = NavigationIntent Counter Counter WorkspaceRow WorkspaceRow Context deriving (Eq, Show)
data NavigationRequest = Navigate B.ByteString Binding NavigationIntent
                       | Recover B.ByteString Binding deriving (Eq, Show)

firstError :: Show a => Either a b -> Either Text b
firstError = either (Left . T.pack . show) Right

require :: Bool -> Text -> Either Text ()
require True _ = Right ()
require False reason = Left reason

fields :: [Text] -> Json -> Either Text [(Text, Json)]
fields names = firstError . exactObject names

field :: Text -> [(Text, Json)] -> Either Text Json
field key value = maybe (Left "missing navigation field") Right (lookup key value)

textValue :: Json -> Either Text Text
textValue (JString value) = Right value
textValue _ = Left "navigation string required"

counterValue :: Bool -> Json -> Either Text Counter
counterValue permitZero value = textValue value >>= firstError . parseCounter permitZero

ordinaryIdentity :: Json -> Either Text Text
ordinaryIdentity value = do
  identity <- textValue value
  _ <- firstError (parseCounter False identity)
  require (T.length identity < 19 ||
    (T.length identity == 19 && identity <= "9223372036854775807")) "ordinary workspace identity range"
  pure identity

parseRow :: Json -> Either Text WorkspaceRow
parseRow value = do
  row <- fields ["identity", "generation", "monitor", "outputOwnershipGeneration"] value
  WorkspaceRow <$> (field "identity" row >>= ordinaryIdentity)
    <*> (field "generation" row >>= counterValue False)
    <*> (field "monitor" row >>= counterValue True)
    <*> (field "outputOwnershipGeneration" row >>= counterValue False)

parseContext :: Binding -> Json -> Either Text Context
parseContext owner value = do
  row <- fields ["lifetime", "epoch", "output", "revision"] value
  life <- field "lifetime" row >>= counterValue False
  epoch <- field "epoch" row >>= counterValue False
  output <- field "output" row >>= counterValue False
  revision <- field "revision" row >>= counterValue False
  firstError (context owner life epoch output revision)

parseNavigationIntent :: Binding -> Json -> Either Text NavigationIntent
parseNavigationIntent owner value = do
  row <- fields ["request", "generation", "source", "destination", "context"] value
  NavigationIntent <$> (field "request" row >>= counterValue False)
    <*> (field "generation" row >>= counterValue False)
    <*> (field "source" row >>= parseRow)
    <*> (field "destination" row >>= parseRow)
    <*> (field "context" row >>= parseContext owner)

decodeWorkspaceNavigation :: B.ByteString -> Either Text NavigationRequest
decodeWorkspaceNavigation raw = do
  limit <- firstError (bounds 131072 16)
  value <- firstError (decodeStrict limit raw)
  source <- firstError (TE.decodeUtf8' raw)
  require (utf16Length source <= 131072) "navigation UTF16 capacity"
  -- Match the existing Desktop rendered-request bound inside its outer envelope.
  require (B.length (TE.encodeUtf8 (renderJson value)) <= 8192) "navigation rendered request capacity"
  common <- case value of
    JObject row -> Right row
    _ -> Left "navigation object required"
  version <- field "protocolVersion" common
  workspaceVersion <- field "workspaceProtocol" common
  require (version == JNumber "3" && workspaceVersion == JNumber "1") "navigation version"
  kind <- field "kind" common >>= textValue
  case kind of
    "workspace-navigation" -> do
      row <- fields ["protocolVersion", "kind", "workspaceProtocol", "binding", "intent"] value
      owner <- field "binding" row >>= parseBinding
      intent <- field "intent" row >>= parseNavigationIntent owner
      pure (Navigate raw owner intent)
    "workspace-navigation-recover" -> do
      row <- fields ["protocolVersion", "kind", "workspaceProtocol", "binding"] value
      owner <- field "binding" row >>= parseBinding
      pure (Recover raw owner)
    _ -> Left "unsupported navigation kind"

encodeWorkspaceNavigation :: NavigationRequest -> Either Text B.ByteString
encodeWorkspaceNavigation request = Right $ case request of
  Navigate raw _ _ -> raw
  Recover raw _ -> raw

navigationBinding :: NavigationRequest -> Binding
navigationBinding (Navigate _ owner _) = owner
navigationBinding (Recover _ owner) = owner

-- Recovery contains no request counter. No counter is synthesized here.
navigationIntent :: NavigationRequest -> Maybe NavigationIntent
navigationIntent (Navigate _ _ intent) = Just intent
navigationIntent (Recover _ _) = Nothing

navigationRequest, navigationGeneration :: NavigationIntent -> Counter
navigationRequest (NavigationIntent request _ _ _ _) = request
navigationGeneration (NavigationIntent _ generation _ _ _) = generation

navigationSource, navigationDestination :: NavigationIntent -> WorkspaceRow
navigationSource (NavigationIntent _ _ source _ _) = source
navigationDestination (NavigationIntent _ _ _ destination _) = destination

navigationContext :: NavigationIntent -> Context
navigationContext (NavigationIntent _ _ _ _ value) = value

workspaceIdentity :: WorkspaceRow -> Text
workspaceIdentity (WorkspaceRow identity _ _ _) = identity
workspaceGeneration, workspaceMonitor, workspaceOutputGeneration :: WorkspaceRow -> Counter
workspaceGeneration (WorkspaceRow _ generation _ _) = generation
workspaceMonitor (WorkspaceRow _ _ monitor _) = monitor
workspaceOutputGeneration (WorkspaceRow _ _ _ generation) = generation
