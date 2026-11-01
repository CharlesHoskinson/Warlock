{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ForeignFunctionInterface #-}
module Main (main) where

import Control.Exception (finally)
import Control.Monad (forM_, unless)
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.IORef (modifyIORef',newIORef,readIORef)
import Data.List (isPrefixOf)
import qualified Data.Set as Set
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Foreign.C.Types (CInt(..))
import GHC.Clock (getMonotonicTimeNSec)
import Numeric (showHex)
import System.Directory (createDirectory,listDirectory)
import System.Environment (getArgs,getEnv)
import System.Exit (ExitCode(..))
import System.FilePath ((</>),takeDirectory,isAbsolute)
import System.Posix.Files (createLink,createSymbolicLink,deviceID,fileID,fileMode,fileSize,getSymbolicLinkStatus,isRegularFile,linkCount,setFileMode)
import System.Posix.IO (OpenMode(ReadWrite),closeFd,creat,defaultFileFlags,openFd)
import System.Posix.Types (Fd(..))
import System.Process (readProcessWithExitCode)
import Warlock.Backend
import qualified Warlock.Backend.Catalog as Catalog
import qualified Warlock.Backend.PinStore as P
import qualified Warlock.Protocol.Desktop as D
import Warlock.Protocol.Identity (Counter,parseCounter,binding)
import qualified Warlock.Protocol.StrictJson as J

foreign import ccall unsafe "flock" flock :: CInt -> CInt -> IO CInt

counter :: T.Text -> Counter
counter = either (error . show) id . parseCounter False
sha :: B.ByteString -> String
sha = concatMap (\x -> let s=showHex x "" in replicate (2-length s) '0' ++ s) . B.unpack . SHA.hash
must :: Show e => Either e a -> IO a
must = either (ioError . userError . show) pure
encoded :: J.Json -> B.ByteString
encoded = TE.encodeUtf8 . J.renderJson
obj :: [(T.Text,J.Json)] -> J.Json
obj = J.JObject
txt :: String -> J.Json
txt = J.JString . T.pack
bindingValue :: J.Json
bindingValue = obj [("lifetime",txt "9007199254740993"),("session",txt "9007199254740995"),("frontend",txt "9007199254740997")]
request :: String -> Int -> [(T.Text,J.Json)] -> J.Json
request kind identity extra = obj ([("protocolVersion",J.JNumber "3"),("kind",txt kind),("binding",bindingValue),("requestId",txt (show identity))] ++ extra)
commit :: [J.Json] -> B.ByteString
commit requests = encoded (obj [("viewProtocol",J.JNumber "1"),("kind",txt "view-commit"),("projection",obj []),("requests",J.JArray requests),("focus",J.JArray [])])
proposal :: String -> [String] -> J.Json
proposal revision identities = obj [("revision",txt revision),("identities",J.JArray (map txt identities))]
replaceField :: T.Text -> J.Json -> J.Json -> J.Json
replaceField key value (J.JObject fields) = J.JObject ((key,value):filter ((/=key) . fst) fields)
replaceField _ _ value = value

pinDirectory :: FilePath -> IO DirectoryPin
pinDirectory path = do
  s <- getSymbolicLinkStatus path
  pure (DirectoryPin path (toInteger (deviceID s)) (toInteger (fileID s)))
directoryJson :: DirectoryPin -> J.Json
directoryJson p = obj [("path",txt (directoryPath p)),("device",txt (show (directoryDevice p))),("inode",txt (show (directoryInode p)))]
fresh :: FilePath -> IO FilePath
fresh path = createDirectory path >> setFileMode path 0o700 >> pure path
writePrivate :: FilePath -> B.ByteString -> IO ()
writePrivate path bytes = B.writeFile path bytes >> setFileMode path 0o600
pinImage :: FilePath -> IO [String]
pinImage path = do
  s <- getSymbolicLinkStatus path
  bytes <- B.readFile path
  unless (isRegularFile s) (ioError (userError "nonregular trusted QA executable"))
  pure [show (deviceID s),show (fileID s),show (B.length bytes),sha bytes]

main :: IO ()
main = do
  args <- getArgs
  (backend,backendPins,child,childPins,root) <- case args of
    [b,bd,bi,bs,bh,c,cd,ci,cs,ch,r] -> pure (b,[bd,bi,bs,bh],c,[cd,ci,cs,ch],r)
    _ -> ioError (userError "expected BACKEND DEV INO SIZE SHA CHILD DEV INO SIZE SHA EMPTY_QA_ROOT")
  actualBackend <- pinImage backend
  actualChild <- pinImage child
  unless (actualBackend==backendPins && actualChild==childPins) (ioError (userError "independent executable pins differ"))
  count <- newIORef (0 :: Int)
  let check label good = do
        modifyIORef' count (+1)
        unless good (ioError (userError label))
      make label = fresh (root </> label)
  beforeRoot <- listDirectory root
  check "root supplied fresh private test directory" (null beforeRoot)
  applications <- make "applications"
  pinsRoot <- make "pins"
  let sentinel=root </> "must-not-spawn"
  writePrivate (applications </> "alpha.desktop") (C.pack ("[Desktop Entry]\nType=Application\nName=Alpha\nExec=/bin/sh -c 'touch " ++ sentinel ++ "'\n"))
  writePrivate (applications </> "beta.desktop") "[Desktop Entry]\nType=Application\nName=Beta\nExec=/bin/true\n"
  catalogPin <- pinDirectory applications
  storagePin <- pinDirectory pinsRoot
  let parents=reverse (takeWhile (/="/") (iterate takeDirectory (takeDirectory child)))
  ancestorPins <- mapM pinDirectory parents
  let config :: FilePath -> FilePath -> Integer -> J.Json
      config scriptFile repliesFile deadline = obj
        [("schema",J.JNumber "1"),("binding",bindingValue),("deadlineMonotonicNs",txt (show deadline))
        ,("ui",obj [("path",txt child),("device",txt (childPins!!0)),("inode",txt (childPins!!1)),("size",txt (childPins!!2)),("sha256",txt (childPins!!3)),("arguments",J.JArray [txt scriptFile,txt repliesFile]),("ancestors",J.JArray (map directoryJson ancestorPins))])
        ,("catalogRoots",J.JArray [directoryJson catalogPin]),("pinsRoot",directoryJson storagePin),("locale",txt "C")]
      framesJson :: [(B.ByteString,Int,Bool)] -> J.Json
      framesJson frames = obj [("schema",J.JNumber "1"),("frames",J.JArray [obj [("wire",J.JString (TE.decodeUtf8 wire)),("replies",J.JNumber (T.pack (show replies))),("refused",J.JBool refused)] | (wire,replies,refused) <- frames])]
      prepare :: String -> [(B.ByteString,Int,Bool)] -> IO (FilePath,FilePath,FilePath)
      prepare label frames = do
        directory <- make label
        let scriptFile=directory </> "script.json"; repliesFile=directory </> "replies.json"; configFile=directory </> "startup.json"
        writePrivate scriptFile (encoded (framesJson frames))
        now <- getMonotonicTimeNSec
        writePrivate configFile (encoded (config scriptFile repliesFile (toInteger now+5000000000)))
        pure (directory,configFile,repliesFile)
      readReplies :: FilePath -> IO [B.ByteString]
      readReplies path = do
        bytes <- B.readFile path
        limits <- must (J.bounds (8*1024*1024) 16)
        tree <- must (J.decodeStrict limits bytes)
        case tree of J.JArray values -> mapM (\v -> case v of J.JString s -> pure (TE.encodeUtf8 s); _ -> ioError (userError "reply log typed string")) values; _ -> ioError (userError "reply log array")
      logCLI :: FilePath -> FilePath -> IO ExitCode
      logCLI directory configFile = do
        (code,out,err) <- readProcessWithExitCode backend [configFile] ""
        writePrivate (directory </> "backend.stdout") (C.pack out)
        writePrivate (directory </> "backend.stderr") (C.pack err)
        pure code
      validateGateway :: Int -> B.ByteString -> IO J.Json
      validateGateway identity bytes = do
        reply <- must (D.decodeDesktopGateway bytes)
        check "actual gateway carries typed reply, not fake projection ACK" (D.replyBinding reply == either (error . show) id (binding (counter "9007199254740993") (counter "9007199254740995") (counter "9007199254740997")))
        limits <- must (J.bounds 1048704 16)
        tree <- must (J.decodeStrict limits bytes)
        let at key (J.JObject fields) = maybe J.JNull id (lookup key fields); at _ _ = J.JNull
        check "actual reply retains independent request identity" (at "requestId" (at "payload" tree)==txt (show identity))
        pure tree

  -- Public production library route, using the same startup loader and actors.
  (libraryDir,libraryConfig,libraryReplies) <- prepare "public-linked" [(commit [request "catalog-request" 7 []],1,False)]
  loaded <- loadBackendConfig libraryConfig >>= must
  libraryResult <- runBackend loaded
  writePrivate (libraryDir </> "result.txt") (C.pack (show libraryResult))
  check "ordinary public library runs real authenticated catalog callback" (backendPassed libraryResult && backendCleanup libraryResult && backendCallbackCount libraryResult==1 && backendOperationCount libraryResult==1 && backendSelectedPid libraryResult/=Nothing && not (null (backendCredentialTrace libraryResult)))
  replies1 <- readReplies libraryReplies
  check "one exact actual catalog reply" (length replies1==1)
  _ <- validateGateway (7 :: Int) (head replies1)

  -- Actual shipped executable path, followed by a separate process restart.
  (cliDir,cliConfig,cliReplies) <- prepare "production-cli" [(commit [request "catalog-request" 8 []],1,False),(commit [request "taskbar-pins-write" 9 [("proposal",proposal "1" ["alpha"])]],1,False)]
  cliCode <- logCLI cliDir cliConfig
  check "actual production executable completes without forced cleanup" (cliCode==ExitSuccess)
  cliResponses <- readReplies cliReplies
  check "two complete actual gateway replies" (length cliResponses==2)
  _ <- validateGateway (8 :: Int) (head cliResponses)
  savedTree <- validateGateway (9 :: Int) (cliResponses!!1)
  let at key (J.JObject fields) = maybe J.JNull id (lookup key fields); at _ _ = J.JNull
  check "production CLI Saved reflects real next revision" (at "status" (at "payload" savedTree)==txt "Saved" && at "revision" (at "preferences" (at "payload" savedTree))==txt "2")
  persisted <- B.readFile (pinsRoot </> "taskbar.json")
  check "actual fixed file contains independently expected order" (persisted=="{\"schema\":1,\"revision\":\"2\",\"identities\":[\"alpha\"]}")
  (restartDir,restartConfig,restartReplies) <- prepare "restart-cli" [(commit [request "catalog-request" 10 []],1,False)]
  restartCode <- logCLI restartDir restartConfig
  restartValues <- readReplies restartReplies
  restartTree <- validateGateway (10 :: Int) (head restartValues)
  check "restart reads actual persisted pins without replay" (restartCode==ExitSuccess && at "revision" (at "preferences" (at "payload" restartTree))==txt "2")
  afterRestart <- B.readFile (pinsRoot </> "taskbar.json")
  check "restart read preserves bytes" (afterRestart==persisted)

  let generatedStates=take 32 (tail (iterate (\n -> (1664525*n+1013904223) `mod` 4294967296) (20261101 :: Integer)))
      generatedHostile =
        [("runtime-LCG20261101-case-"++show index++"-state-"++show state,commit [request "catalog-request" 11 [],mutated])
        | (index,state) <- zip [0 :: Int ..] generatedStates
        , let valid=request "catalog-request" 12 []
              path="/tmp/forbidden-ui-"++show state
              mutated=case index `mod` 8 of
                0 -> request "catalog-request" 12 [("path",txt path)]
                1 -> request "shell-command" 12 [("command",txt ("touch "++sentinel++show state))]
                2 -> request ("unknown-"++show state) 12 []
                3 -> replaceField "binding" (obj [("lifetime",txt "0"),("session",txt "9007199254740995"),("frontend",txt "9007199254740997")]) valid
                4 -> replaceField "protocolVersion" (J.JNumber "2") valid
                5 -> request "taskbar-pins-write" 12 [("proposal",replaceField "path" (txt path) (proposal "2" ["alpha"]))]
                6 -> request "taskbar-pins-write" 12 [("proposal",proposal "2" [(if state `mod` 3==0 then "../escape-" else "file:escape-")++show state])]
                _ -> request "taskbar-pins-write" 12 [("proposal",replaceField "revision" (J.JNumber "2") (proposal "2" ["alpha"]))]]
      hostile =
        [("unknown-method",commit [request "shell-command" 11 [("command",txt ("touch "++sentinel))]])
        ,("path-extra",commit [request "catalog-request" 11 [("path",txt "/etc/passwd")]])
        ,("native-effect",commit [request "window-effect" 11 []])
        ,("server-forgery",commit [request "application-catalog" 11 [("snapshot",J.JNull),("preferences",J.JNull)]])
        ,("unknown-field",commit [request "catalog-request" 11 [("unexpected",J.JBool True)]])
        ,("native-profile",encoded (obj [("version",J.JNumber "1"),("kind",txt "hello"),("body",obj [("binding",bindingValue)])]))
        ,("gateway-as-client",encoded (obj [("bridgeProtocol",J.JNumber "1"),("kind",txt "native-event"),("payload",obj [])]))
        ,("duplicate-top-key","{\"viewProtocol\":1,\"viewProtocol\":1,\"kind\":\"view-commit\",\"projection\":{},\"requests\":[],\"focus\":[]}")
        ,("mixed-binding",commit [request "catalog-request" 11 [],obj [("protocolVersion",J.JNumber "3"),("kind",txt "catalog-request"),("binding",obj [("lifetime",txt "9007199254740993"),("session",txt "9007199254740996"),("frontend",txt "9007199254740997")]),("requestId",txt "12")]])]
        ++ [("nested-path-"++show n,commit [request "catalog-request" 11 [],request "taskbar-pins-write" 12 [("proposal",proposal "2" [selector])]]) | (n,selector) <- zip [0 :: Int ..] ["/etc/passwd","../outside","a/b","a\\b","file:///secret","$(touch sentinel)"]]
        ++ [("seeded-shell-"++show seed,commit [request "catalog-request" 11 [],request ("unknown-"++show seed) 12 [("command",txt ("touch "++sentinel))]]) | seed <- [20261101..20261108 :: Int]]
        ++ generatedHostile
  forM_ hostile $ \(label,wire) -> do
    (directory,configFile,replyFile) <- prepare label [(wire,0,True)]
    inputConfig <- loadBackendConfig configFile >>= must
    result <- runBackend inputConfig
    writePrivate (directory </> "result.txt") (C.pack (show result))
    writePrivate (directory </> "result.json") (backendResultJson result)
    check (label++" actual authenticated whole-frame rejection before ANY domain callback") (not (backendPassed result) && backendCleanup result && backendCallbackCount result==0 && backendOperationCount result==0)
    empty <- readReplies replyFile
    current <- B.readFile (pinsRoot </> "taskbar.json")
    check (label++" no reply or file write from rejected suffix") (null empty && current==persisted)
  names <- listDirectory root
  check "desktop metadata and hostile commands never spawn shell sentinel" (not (any ("must-not-spawn" `isPrefixOf`) names))

  -- Actual directory traversal/metadata producer at the original catalog bound.
  -- The output is inspected independently through the public encoded wire.
  largeDirectory <- make "catalog-2048"
  forM_ [1..2048 :: Int] $ \n -> writePrivate (largeDirectory </> ("app-"++show n++".desktop"))
    (C.pack ("[Desktop Entry]\nType=Application\nName="++replicate 80 'n'++"\nExec=/bin/true\n"))
  largePin <- pinDirectory largeDirectory
  large <- Catalog.newCatalog [largePin] "C" (counter "9007199254740993")
  (largeSnapshot,largeIdentities) <- Catalog.readCatalog large >>= must
  largeReply <- must (D.catalogReply (either (error . show) id (binding (counter "9007199254740993") (counter "9007199254740995") (counter "9007199254740997"))) (counter "7") (Just largeSnapshot) Nothing >>= D.encodeDesktopGateway)
  largeTree <- validateGateway (7 :: Int) largeReply
  let actualEntries=at "entries" (at "snapshot" (at "payload" largeTree))
  check "actual 2048-file scan yields complete >64KiB response" (Set.size largeIdentities==2048 && B.length largeReply>65536 && case actualEntries of J.JArray values -> length values==2048; _ -> False)
  writePrivate (root </> "actual-catalog-2048.json") largeReply
  writePrivate (largeDirectory </> "app-2049.desktop") "[Desktop Entry]\nType=Application\nName=Extra\nExec=/bin/true\n"
  tooMany <- Catalog.readCatalog large
  check "actual 2049-file scan refuses without returning truncated snapshot" (either (const True) (const False) tooMany)
  largeRetired <- Catalog.retireCatalog large
  check "large catalog independent owner retires" largeRetired

  -- Real public fixed-root persistence, not a mock callback implementation.
  storeDir <- make "physical-store"
  storePin <- pinDirectory storeDir
  store <- P.newPinStore storePin
  missing <- P.readPins store >>= must
  check "missing store has positive revision1 and no pins" (D.pinRevision missing==counter "1" && null (D.pinIdentities missing))
  first <- must (D.pinSnapshot (counter "1") ["alpha"])
  (status,snapshot) <- P.savePins store (Set.fromList ["alpha","beta"]) first
  check "real CAS commit produces Saved exact revision2" (status==D.PinSaved && maybe False (\s -> D.pinRevision s==counter "2" && D.pinIdentities s==["alpha"]) snapshot)
  bytes <- B.readFile (storeDir </> "taskbar.json")
  stat <- getSymbolicLinkStatus (storeDir </> "taskbar.json")
  check "saved file regular private single-link" (isRegularFile stat && linkCount stat==1 && fileMode stat `mod` 512==0o600 && fileSize stat==fromIntegral (B.length bytes))
  stale <- must (D.pinSnapshot (counter "1") ["beta"])
  (staleStatus,_) <- P.savePins store (Set.fromList ["alpha","beta"]) stale
  unchanged <- B.readFile (storeDir </> "taskbar.json")
  check "stale CAS refuses without changing actual file" (staleStatus==D.PinRefused && unchanged==bytes)
  noChange <- must (D.pinSnapshot (counter "2") ["alpha"])
  (noChangeStatus,noChangeSnapshot) <- P.savePins store (Set.fromList ["alpha","beta"]) noChange
  check "no-op proposal refuses and retains exact current revision" (noChangeStatus==D.PinRefused && maybe False ((==counter "2") . D.pinRevision) noChangeSnapshot)
  retired <- P.retirePinStore store
  check "physical store independently retires" retired
  reopened <- P.newPinStore storePin
  observed <- P.readPins reopened >>= must
  check "fresh actor observes persisted exact order" (D.pinIdentities observed==["alpha"] && D.pinRevision observed==counter "2")
  let lockPath=storeDir </> "taskbar.lock"
  fd@(Fd rawFd) <- openFd lockPath ReadWrite defaultFileFlags {creat=Just 0o600}
  lockResult <- flock rawFd 6
  check "independent kernel flock acquired" (lockResult==0)
  locked <- P.readPins reopened `finally` (flock rawFd 8 >> closeFd fd)
  check "actual busy lock refuses, no waiting/borrowed authority" (either (const True) (const False) locked)
  _ <- P.retirePinStore reopened
  unsafeDir <- make "symlink-store"
  outside <- make "outside"
  writePrivate (outside </> "canary") "private sentinel bytes"
  createSymbolicLink (outside </> "canary") (unsafeDir </> "taskbar.json")
  unsafePin <- pinDirectory unsafeDir
  unsafe <- P.newPinStore unsafePin
  unsafeResult <- P.readPins unsafe
  canary <- B.readFile (outside </> "canary")
  check "actual symlink state refuses and target bytes preserved" (either (const True) (const False) unsafeResult && canary=="private sentinel bytes")
  _ <- P.retirePinStore unsafe
  hardDir <- make "hardlink-store"
  createLink (outside </> "canary") (hardDir </> "taskbar.json")
  hardPin <- pinDirectory hardDir
  hard <- P.newPinStore hardPin
  hardResult <- P.readPins hard
  check "hardlinked state refuses" (either (const True) (const False) hardResult)
  _ <- P.retirePinStore hard
  malformedDir <- make "unknown-schema"
  writePrivate (malformedDir </> "taskbar.json") "{\"schema\":99,\"revision\":\"1\",\"identities\":[]}"
  malformedPin <- pinDirectory malformedDir
  malformed <- P.newPinStore malformedPin
  malformedRead <- P.readPins malformed
  (_,malformedSave) <- P.savePins malformed (Set.singleton "alpha") first
  malformedBytes <- B.readFile (malformedDir </> "taskbar.json")
  check "unknown schema refuses without destructive rewrite" (either (const True) (const False) malformedRead && malformedSave==Nothing && malformedBytes=="{\"schema\":99,\"revision\":\"1\",\"identities\":[]}")
  _ <- P.retirePinStore malformed
  exhaustedDir <- make "exhausted-counter"
  let exhaustedBytes="{\"schema\":1,\"revision\":\"18446744073709551615\",\"identities\":[\"alpha\"]}"
  writePrivate (exhaustedDir </> "taskbar.json") exhaustedBytes
  exhaustedPin <- pinDirectory exhaustedDir
  exhausted <- P.newPinStore exhaustedPin
  exhaustedProposal <- must (D.pinSnapshot (counter "18446744073709551615") ["beta"])
  (exhaustedStatus,exhaustedSnapshot) <- P.savePins exhausted (Set.fromList ["alpha","beta"]) exhaustedProposal
  exhaustedAfter <- B.readFile (exhaustedDir </> "taskbar.json")
  check "UInt64 revision exhaustion refuses without wrap or rewrite" (exhaustedStatus==D.PinRefused && exhaustedSnapshot/=Nothing && exhaustedAfter==exhaustedBytes)
  exhaustedRetired <- P.retirePinStore exhausted
  check "exhausted store independently retires" exhaustedRetired

  -- Root supplies the generated Elm artifact and the reviewed fixed Node
  -- harness. Only this exact three-image manifest selects the dev QA process;
  -- none of its paths/arguments originate in web content or bridge requests.
  frontendManifest <- getEnv "WARLOCK_UI_FRONTEND_MANIFEST"
  check "root frontend manifest absolute" (isAbsolute frontendManifest)
  frontendBytes <- B.readFile frontendManifest
  frontendLimits <- must (J.bounds 131072 16)
  frontendTree <- must (J.decodeStrict frontendLimits frontendBytes)
  frontendFields <- must (J.exactObject ["node","main","harness"] frontendTree)
  let artifact key = do
        value <- maybe (ioError (userError "frontend image absent")) pure (lookup key frontendFields)
        fields <- must (J.exactObject ["path","sha"] value)
        case (lookup "path" fields,lookup "sha" fields) of
          (Just (J.JString path),Just (J.JString digest)) -> do
            let file=T.unpack path
            check ("frontend "++T.unpack key++" pinned absolute regular image") (isAbsolute file && T.length digest==64)
            image <- pinImage file
            check ("frontend "++T.unpack key++" independent SHA256") (last image==T.unpack digest)
            pure (file,image)
          _ -> ioError (userError "frontend image typed facts")
  (node,nodeImage) <- artifact "node"
  (mainJs,mainImage) <- artifact "main"
  (harness,harnessImage) <- artifact "harness"
  frontendPinsDirectory <- make "frontend-pins"
  frontendPin <- pinDirectory frontendPinsDirectory
  let frontendConfig=obj [("schema",J.JNumber "1"),("binding",bindingValue),("catalogRoots",J.JArray [directoryJson catalogPin]),("pinsRoot",directoryJson frontendPin),("locale",txt "C")]
      imageJson file image=obj [("path",txt file),("pin",J.JArray (map txt image))]
      selectedManifest=root </> "frontend-selected.json"
      frontendReport=root </> "frontend-report.json"
  writePrivate selectedManifest (encoded (obj [("backend",imageJson backend backendPins),("ui",imageJson child childPins),("config",frontendConfig)]))
  (frontendCode,frontendOut,frontendErr) <- readProcessWithExitCode node [harness,mainJs,selectedManifest,root </> "actual-main",frontendReport] ""
  writePrivate (root </> "frontend.stdout") (C.pack frontendOut)
  writePrivate (root </> "frontend.stderr") (C.pack frontendErr)
  reportBytes <- B.readFile frontendReport
  reportLimits <- must (J.bounds (16*1024*1024) 32)
  reportTree <- must (J.decodeStrict reportLimits reportBytes)
  check "actual compiled Main to actual production CLI harness succeeds" (frontendCode==ExitSuccess && at "passed" reportTree==J.JBool True)
  check "actual Main report retains original architecture scenario receipt" (case at "scenarios" reportTree of J.JArray rows -> any (\row -> at "scenario" row==txt "architecture-003") rows; _ -> False)
  forM_ [(node,nodeImage),(mainJs,mainImage),(harness,harnessImage)] $ \(file,image) -> do
    after <- pinImage file
    check "root frontend image unchanged after actual invocation" (after==image)
  frontendAfter <- B.readFile frontendManifest
  check "root frontend manifest unchanged" (frontendAfter==frontendBytes)
  actualBackendAfter <- pinImage backend
  actualChildAfter <- pinImage child
  check "both independently pinned executables unchanged" (actualBackendAfter==backendPins && actualChildAfter==childPins)
  budget <- readIORef count
  putStrLn ("{\"schema\":1,\"suite\":\"ui-backend-controls\",\"passed\":true,\"checks\":"++show budget++",\"runtimeFuzzSeed\":20261101,\"runtimeGeneratedCases\":32,\"runtimeMutationClasses\":8,\"nativeAcceptance\":false,\"releaseAccepted\":false}")
