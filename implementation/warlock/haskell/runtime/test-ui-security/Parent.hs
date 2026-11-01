{-# LANGUAGE OverloadedStrings #-}
-- VM QA driver for the production backend and its pinned, authenticated child.
-- It records observations; it cannot issue an ARC024/DEL014 verdict.
module Main (main) where

import Control.Monad (unless, (>=>))
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Numeric (showHex)
import System.Directory (canonicalizePath, createDirectory, listDirectory, doesFileExist)
import System.Environment (getArgs, getExecutablePath)
import System.Exit (exitFailure)
import System.FilePath ((</>), isAbsolute, takeDirectory)
import System.Posix.Files (deviceID, fileID, fileMode, fileOwner, getSymbolicLinkStatus, isDirectory, isRegularFile, setFileMode)
import System.Posix.User (getEffectiveUserID)
import Data.Bits ((.&.))
import Warlock.Backend (loadBackendConfig, runBackend, backendResultJson, backendAuthObservation, backendCredentialTrace, backendSelectedPid, backendBootstrap)
import qualified Warlock.Protocol.StrictJson as J

must :: Show e => Either e a -> IO a
must = either (ioError . userError . show) pure

txt :: String -> J.Json
txt = J.JString . T.pack

object :: [(T.Text, J.Json)] -> J.Json
object = J.JObject

json :: J.Json -> B.ByteString
json = TE.encodeUtf8 . J.renderJson

parse :: B.ByteString -> IO J.Json
parse bytes = must (J.bounds (16 * 1024 * 1024) 32) >>= \bound -> must (J.decodeStrict bound bytes)

field :: T.Text -> J.Json -> IO J.Json
field name (J.JObject fields) = maybe (ioError (userError ("missing " ++ T.unpack name))) pure (lookup name fields)
field _ _ = ioError (userError "expected object")

lookupField :: T.Text -> J.Json -> Maybe J.Json
lookupField name (J.JObject fields) = lookup name fields
lookupField _ _ = Nothing

sourcePath :: J.Json -> IO FilePath
sourcePath value = do
  pathValue <- field "path" value
  case pathValue of J.JString text -> pure (T.unpack text); _ -> ioError (userError "source path")

imageFromFact :: J.Json -> IO J.Json
imageFromFact value = do
  path <- sourcePath value
  actual <- imageFact path
  unless (actual == value) (ioError (userError "source differs from independent pin"))
  pure actual

sha :: B.ByteString -> String
sha = concatMap (\byte -> let digits = showHex byte "" in replicate (2 - length digits) '0' ++ digits) . B.unpack . SHA.hash

privateWrite :: FilePath -> B.ByteString -> IO ()
privateWrite path bytes = B.writeFile path bytes >> setFileMode path 0o600

directoryFact :: FilePath -> IO J.Json
directoryFact path = do
  status <- getSymbolicLinkStatus path
  unless (isAbsolute path && isDirectory status) (ioError (userError "directory must be absolute and nonsymlink"))
  pure (object [("path", txt path), ("device", txt (show (deviceID status))), ("inode", txt (show (fileID status)))])

imageFact :: FilePath -> IO J.Json
imageFact path = do
  status <- getSymbolicLinkStatus path
  unless (isAbsolute path && isRegularFile status) (ioError (userError "image must be absolute, regular and nonsymlink"))
  bytes <- B.readFile path
  pure (object [("path", txt path), ("device", txt (show (deviceID status))), ("inode", txt (show (fileID status))),
                ("size", txt (show (B.length bytes))), ("sha256", txt (sha bytes))])

ancestors :: FilePath -> IO [J.Json]
ancestors path = mapM directoryFact (reverse (takeWhile (/= "/") (iterate takeDirectory (takeDirectory path))))

fresh :: FilePath -> IO J.Json
fresh path = createDirectory path >> setFileMode path 0o700 >> directoryFact path

observationBody :: String -> B.ByteString
observationBody tag = C.pack ("{\"qaSecurityObservation\":\"" ++ tag ++ "\"}")

traceMatches :: String -> J.Json -> Bool
traceMatches tag row =
  let body = observationBody tag
  in lookupField "role" row == Just (txt "Controller")
     && lookupField "route" row == Just (txt "Commit")
     && lookupField "sha256" row == Just (txt (sha body))
     && lookupField "bytes" row == Just (J.JNumber (T.pack (show (B.length body))))

-- Deterministic source-level check of the observer's role, route, length and
-- digest custody. It does not launch GTK and does not establish CSP behavior.
observerSelfCheck :: IO ()
observerSelfCheck = do
  let tag = "executed-eval"
      body = observationBody tag
      row role route digest size = object [("role", txt role), ("route", txt route),
        ("sha256", txt digest), ("bytes", J.JNumber (T.pack (show size)))]
      valid = row "Controller" "Commit" (sha body) (B.length body)
      altered = observationBody "enforced-script-eval"
      cases = [row "Bar" "Commit" (sha body) (B.length body),
               row "Controller" "Actions" (sha body) (B.length body),
               row "Controller" "Commit" (sha altered) (B.length body),
               row "Controller" "Commit" (sha body) (B.length body + 1),
               object [], J.JNull]
      generated = [let source = "qa-seed-20261101-" ++ show seed
                       bytes = observationBody source
                       exact = row "Controller" "Commit" (sha bytes) (B.length bytes)
                       mutated = row "Controller" "Commit" (sha bytes) (B.length bytes + 1)
                   in traceMatches source exact && not (traceMatches source mutated)
                      && not (traceMatches (source ++ "x") exact) | seed <- [0 :: Int .. 255]]
  unless (traceMatches tag valid && all (not . traceMatches tag) cases
          && not (traceMatches "executed-inline" valid) && and generated)
    (ioError (userError "security observer custody self-check failed"))
  C.putStrLn "observer custody controls and 256 seed-20261101 variations passed; no CSP execution or VM verdict"

main :: IO ()
main = getArgs >>= \args -> if args == ["--observer-self-check"] then observerSelfCheck else runParent args

runParent :: [String] -> IO ()
runParent args = do
  (storage, manifestPath, childPath, deadline) <- case args of
    [a,b,c,d] | all isAbsolute [a,b,c] && not (null d) && all (`elem` ['0'..'9']) d -> pure (a,b,c,d)
    _ -> ioError (userError "expected ABSOLUTE_EMPTY_PRIVATE_DIR ABSOLUTE_MANIFEST ABSOLUTE_CHILD ORIGINAL_DEADLINE_NS")
  status <- getSymbolicLinkStatus storage
  uid <- getEffectiveUserID
  canonical <- canonicalizePath storage
  unless (canonical == storage && isDirectory status && fileOwner status == uid && fileMode status .&. 0o777 == 0o700)
    (ioError (userError "evidence directory must be canonical, owned and 0700"))
  names <- listDirectory storage
  unless (null names) (ioError (userError "evidence directory must be empty"))
  manifestBytes <- B.readFile manifestPath
  manifest <- parse manifestBytes
  _ <- must (J.exactObject ["child", "documents", "binding", "sources"] manifest)
  expectedChild <- field "child" manifest
  actualChild <- imageFact childPath
  unless (expectedChild == actualChild) (ioError (userError "child differs from independent manifest pin"))
  binding <- field "binding" manifest
  documents <- field "documents" manifest
  sourceValue <- field "sources" manifest
  sourcePins <- case sourceValue of
    J.JArray values | not (null values) -> mapM imageFromFact values
    _ -> ioError (userError "independent nonempty source pins required")
  childParents <- ancestors childPath
  selfPath <- getExecutablePath
  self <- imageFact selfPath
  applications <- fresh (storage </> "applications")
  pins <- fresh (storage </> "pins")
  let uiPath = storage </> "ui.json"
      childResult = storage </> "child-result.json"
      backendPath = storage </> "backend.json"
      uiConfig = object [("schema", J.JNumber "1"), ("binding", binding), ("deadlineMonotonicNs", txt deadline), ("documents", documents)]
      imageFields = case actualChild of J.JObject fields -> fields; _ -> []
      selected = object (imageFields ++ [("arguments", J.JArray [txt uiPath, txt childResult]), ("ancestors", J.JArray childParents)])
      backendConfig = object [("schema", J.JNumber "1"), ("binding", binding), ("deadlineMonotonicNs", txt deadline),
                              ("ui", selected), ("catalogRoots", J.JArray [applications]), ("pinsRoot", pins), ("locale", txt "C")]
  privateWrite (storage </> "manifest.json") manifestBytes
  privateWrite uiPath (json uiConfig)
  privateWrite backendPath (json backendConfig)
  config <- loadBackendConfig backendPath >>= must
  -- The production actor itself launches the exact pinned child and owns its
  -- socket, original deadline, SO_PEERCRED verification and complete frames.
  result <- runBackend config
  privateWrite (storage </> "backend-result.json") (backendResultJson result)
  childExists <- doesFileExist childResult
  observedChild <- if childExists then B.readFile childResult >>= parse else pure J.JNull
  afterChild <- imageFact childPath
  afterSelf <- imageFact selfPath
  afterManifest <- B.readFile manifestPath
  afterSources <- mapM (sourcePath >=> imageFact) sourcePins
  let stable = afterChild == actualChild && afterSelf == self && afterManifest == manifestBytes && afterSources == sourcePins
      childPid = case observedChild of J.JObject values -> lookup "pid" values; _ -> Nothing
      selectedMatches = case backendSelectedPid result of
        Just selectedPid -> childPid == Just (txt (show selectedPid))
        Nothing -> False
      traceRows = case lookupField "owner" observedChild >>= lookupField "trace" of
        Just (J.JArray rows) -> rows
        _ -> []
      receiptFor tag =
        let body = observationBody tag
            digest = sha body
        in object [("tag", txt tag), ("bodySHA256", txt digest),
                   ("ownerTraceMatches", J.JNumber (T.pack (show (length (filter (traceMatches tag) traceRows)))))]
      receipt = object [("schema", J.JNumber "1"), ("kind", txt "vm-security-producer-observations"),
        ("parentImage", self), ("childImage", actualChild), ("manifestSHA256", txt (sha manifestBytes)),
        ("sourcePins", J.JArray sourcePins),
        ("originalDeadlineMonotonicNs", txt deadline), ("sourceInputsStable", J.JBool stable),
        ("selectedPid", maybe J.JNull (txt . show) (backendSelectedPid result)),
        ("authentication", txt (show (backendAuthObservation result))),
        ("credentialTrace", txt (show (backendCredentialTrace result))),
        ("bootstrap", txt (show (backendBootstrap result))),
        ("childResult", observedChild), ("childResultPresent", J.JBool childExists), ("selectedPidMatchesChild", J.JBool selectedMatches),
        ("ordinaryWorldSignals", J.JArray (map receiptFor ["approved-script-executed", "enforced-script-eval", "enforced-script-inline", "enforced-script-remote", "executed-eval", "executed-inline", "executed-remote"])),
        ("cspExecutionObserved", J.JBool False), ("arc024Accepted", J.JBool False),
        ("del014Accepted", J.JBool False), ("nativeAcceptance", J.JBool False), ("releaseAccepted", J.JBool False)]
  privateWrite (storage </> "producer.json") (json receipt)
  C.putStrLn "VM producer observations written; CSP execution and security acceptance are not established."
  -- Until the separate observer and controls exist this is not a passing test.
  exitFailure
