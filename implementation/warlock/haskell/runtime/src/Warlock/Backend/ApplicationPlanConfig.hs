{-# LANGUAGE OverloadedStrings #-}
-- Startup DATA only; decoding never grants launch authority.
module Warlock.Backend.ApplicationPlanConfig (decodeApplicationPlans) where

import Control.Monad (unless)
import qualified Data.ByteString as B
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Text.Read (readMaybe)
import Warlock.Backend.ApplicationExecutable (ApplicationPlan, applicationPlan)
import Warlock.Platform.Resolver (Identity(..), Kind(..), Pin(..), Link(..))
import Warlock.Protocol.Identity (parseCounter, renderCounter)
import Warlock.Protocol.StrictJson (Json(..), exactObject)

-- The caller has already decoded the bounded, duplicate-rejecting trusted
-- BackendConfig document. Missing optional applicationPlans means no plans.
decodeApplicationPlans :: Maybe Json -> Either Text [ApplicationPlan]
decodeApplicationPlans Nothing = Right []
decodeApplicationPlans (Just (JArray rows)) = do
  require (length rows <= 128) "application plan row capacity"
  plans <- mapM row rows
  let keys = map fst plans
  require (length keys == length (unique keys)) "duplicate application entry"
  pure (map snd plans)
decodeApplicationPlans _ = Left "applicationPlans must be an array"

row :: Json -> Either Text (Text, ApplicationPlan)
row value = do
  fields <- object ["entry","sourceSha256","exec","argv","root","rootDevice","rootInode","pins","path","links","size","sha256"] value
  entry <- text =<< get "entry" fields
  source <- bytes =<< get "sourceSha256" fields
  raw <- bytes =<< get "exec" fields
  args <- list =<< get "argv" fields
  argTexts <- mapM text args
  root <- bytes =<< get "root" fields
  device <- number True =<< get "rootDevice" fields
  inode <- number False =<< get "rootInode" fields
  pins <- list =<< get "pins" fields
  pinValues <- mapM pin pins
  path <- bytes =<< get "path" fields
  links <- list =<< get "links" fields
  linkValues <- mapM link links
  size <- number False =<< get "size" fields
  digest <- bytes =<< get "sha256" fields
  plan <- either (const (Left "invalid application plan")) Right $
    applicationPlan entry source raw (map T.unpack argTexts) root (Identity device inode) pinValues path linkValues size digest
  pure (entry,plan)

pin :: Json -> Either Text Pin
pin value = do
  fields <- object ["path","device","inode","kind"] value
  path <- bytes =<< get "path" fields
  dev <- number True =<< get "device" fields
  ino <- number False =<< get "inode" fields
  kindText <- text =<< get "kind" fields
  kind <- case kindText of
    "directory" -> Right Directory
    "regular" -> Right Regular
    _ -> Left "invalid pin kind"
  pure (Pin path (Identity dev ino) kind)

link :: Json -> Either Text Link
link value = do
  fields <- object ["path","target"] value
  path <- bytes =<< get "path" fields
  target <- bytes =<< get "target" fields
  pure (Link path target)

object :: [Text] -> Json -> Either Text [(Text,Json)]
object names = either (const (Left "unexpected or missing fields")) Right . exactObject names
get :: Text -> [(Text,Json)] -> Either Text Json
get name values = maybe (Left "missing field") Right (lookup name values)
text :: Json -> Either Text Text
text (JString value) = Right value
text _ = Left "string required"
bytes :: Json -> Either Text B.ByteString
bytes value = TE.encodeUtf8 <$> text value
list :: Json -> Either Text [Json]
list (JArray values) = Right values
list _ = Left "array required"
number :: Bool -> Json -> Either Text Integer
number zero value = do
  raw <- text value
  parsed <- either (const (Left "invalid integer")) Right (parseCounter zero raw)
  maybe (Left "integer conversion") Right (readMaybe (T.unpack (renderCounter parsed)))
require :: Bool -> Text -> Either Text ()
require condition problem = unless condition (Left problem)
unique :: Eq a => [a] -> [a]
unique [] = []
unique (x:xs) = x : unique (filter (/=x) xs)
