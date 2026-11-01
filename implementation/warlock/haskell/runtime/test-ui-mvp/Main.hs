{-# LANGUAGE OverloadedStrings #-}
-- Production authenticated bootstrap/credential handler, using the existing
-- trusted framed child; no browser, renderer stub or synthetic actor callback.
module Main (main) where

import Control.Monad (forM_, unless)
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import Data.List (sortOn)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import GHC.Clock (getMonotonicTimeNSec)
import Numeric (showHex)
import System.Directory (createDirectory, listDirectory)
import System.Environment (getArgs)
import System.FilePath ((</>), isAbsolute, takeDirectory)
import System.Posix.Files (deviceID, fileID, getSymbolicLinkStatus, isRegularFile, setFileMode)
import Warlock.Backend
import qualified Warlock.Protocol.StrictJson as J

must :: Show e => Either e a -> IO a
must = either (ioError . userError . show) pure
check :: String -> Bool -> IO ()
check label good = unless good (ioError (userError label))
obj :: [(T.Text,J.Json)] -> J.Json
obj = J.JObject
txt :: String -> J.Json
txt = J.JString . T.pack
encoded :: J.Json -> B.ByteString
encoded = TE.encodeUtf8 . J.renderJson
at :: T.Text -> J.Json -> J.Json
at key (J.JObject pairs) = maybe J.JNull id (lookup key pairs)
at _ _ = J.JNull
-- Strict decoding rejects duplicate keys. JSON object order is immaterial;
-- retain every field and preserve array order for the independent oracle.
canonical :: J.Json -> J.Json
canonical (J.JObject fields) = J.JObject (sortOn fst [(key,canonical value) | (key,value) <- fields])
canonical (J.JArray values) = J.JArray (map canonical values)
canonical value = value
owner :: J.Json
owner = obj [("lifetime",txt "9007199254740993"),("session",txt "9007199254740995"),("frontend",txt "9007199254740997")]
request :: J.Json -> J.Json
request bindingValue = obj [("protocolVersion",J.JNumber "3"),("kind",txt "catalog-request"),("binding",bindingValue),("requestId",txt "17")]
-- A closed, unscoped actual Owner-compatible view-frame, not an arbitrary
-- empty projection. It carries no domain request and does not mint authority.
projection :: J.Json
projection = obj [("viewProtocol",J.JNumber "1"),("kind",txt "view-frame"),("revision",txt "1"),
                  ("views",J.JArray []),("focusOwner",J.JNull),("popupOwner",J.JNull),
                  ("frame",obj [("surfaceProtocol",J.JNumber "2"),("publication",txt "1"),
                                ("lease",txt "0"),("mode",txt "closed"),("status",txt ""),
                                ("bar",J.JArray []),("popup",J.JArray [])]),
                  ("announcer",J.JNull),("announcement",J.JNull)]
commit :: [J.Json] -> B.ByteString
commit requests = encoded (obj [("viewProtocol",J.JNumber "1"),("kind",txt "view-commit"),("projection",projection),("requests",J.JArray requests),("focus",J.JArray [])])
sha :: B.ByteString -> String
sha = concatMap (\n -> let digits=showHex n "" in replicate (2-length digits) '0' ++ digits) . B.unpack . SHA.hash
privateWrite :: FilePath -> B.ByteString -> IO ()
privateWrite path bytes = B.writeFile path bytes >> setFileMode path 0o600
privateDirectory :: FilePath -> IO ()
privateDirectory path = createDirectory path >> setFileMode path 0o700
pin :: FilePath -> IO J.Json
pin path = do
 s <- getSymbolicLinkStatus path
 pure (obj [("path",txt path),("device",txt (show (deviceID s))),("inode",txt (show (fileID s)))])

main :: IO ()
main = do
 args <- getArgs
 (child, supplied, root) <- case args of
  [path,dev,ino,size,digest,directory] | isAbsolute path && isAbsolute directory -> pure (path,[dev,ino,size,digest],directory)
  _ -> ioError (userError "expected CHILD DEV INO SIZE SHA EMPTY_ABSOLUTE_ROOT")
 st <- getSymbolicLinkStatus child
 image <- B.readFile child
 check "real independently pinned child" (isRegularFile st && supplied == [show (deviceID st),show (fileID st),show (B.length image),sha image])
 check "fresh test root" . null =<< listDirectory root
 let catalog=root </> "catalog"; pins=root </> "pins"
 privateDirectory catalog
 privateDirectory pins
 privateWrite (catalog </> "alpha.desktop") "[Desktop Entry]\nType=Application\nName=Alpha\nExec=/bin/true\n"
 catalogPin <- pin catalog
 pinsPin <- pin pins
 let parents=reverse (takeWhile (/="/") (iterate takeDirectory (takeDirectory child)))
 ancestors <- mapM pin parents
 let run label opt frames = do
      let dir=root </> label; input=dir </> "script.json"; output=dir </> "replies.json"; config=dir </> "startup.json"
      privateDirectory dir
      let row (wire,count,refused) = obj [("wire",J.JString (TE.decodeUtf8 wire)),("replies",J.JNumber (T.pack (show (count :: Int)))),("refused",J.JBool refused)]
      privateWrite input (encoded (obj [("schema",J.JNumber "1"),("frames",J.JArray (map row frames))]))
      now <- getMonotonicTimeNSec
      let fields = [("schema",J.JNumber "1"),("binding",owner),("deadlineMonotonicNs",txt (show (toInteger now+5000000000)))
                   ,("ui",obj [("path",txt child),("device",txt (supplied!!0)),("inode",txt (supplied!!1)),("size",txt (supplied!!2)),("sha256",txt (supplied!!3)),("arguments",J.JArray [txt input,txt output]),("ancestors",J.JArray ancestors)])
                   ,("catalogRoots",J.JArray [catalogPin]),("pinsRoot",pinsPin),("locale",txt "C")]
      privateWrite config (encoded (obj (fields ++ opt)))
      loaded <- loadBackendConfig config >>= must
      result <- runBackend loaded
      raw <- B.readFile output
      limits <- must (J.bounds (8*1024*1024) 16)
      replies <- must (J.decodeStrict limits raw)
      case replies of
       J.JArray values -> do
        decoded <- mapM (\value -> case value of
         J.JString text -> must (J.decodeStrict limits (TE.encodeUtf8 text))
         _ -> ioError (userError "reply must be encoded string")) values
        pure (result,decoded)
       _ -> ioError (userError "expected reply array")
     enabled = [("applicationAttachment",J.JBool True)]
     empty = commit []
     catalogRequest = commit [request owner]
     attachment = obj [("protocolVersion",J.JNumber "3"),("kind",txt "application-attached"),("binding",owner),("nativeOperations",J.JArray [])]
     envelope payload = obj [("bridgeProtocol",J.JNumber "1"),("kind",txt "native-event"),("payload",payload)]
 (good, replies) <- run "positive" enabled [(empty,1,False),(empty,0,False),(catalogRequest,1,False)]
 check "real authenticated empty commit emits only one attachment across repeated commits" (backendPassed good && backendCleanup good && backendCallbackCount good==3 && backendOperationCount good==1 && length replies==2 && canonical (head replies)==canonical (envelope attachment))
 check "catalog reply still follows original route" (at "kind" (at "payload" (replies!!1))==txt "application-catalog" && at "requestId" (at "payload" (replies!!1))==txt "17")
 (combined, both) <- run "first-commit-with-request" enabled [(catalogRequest,2,False)]
 check "attachment precedes the first admitted catalog response" (backendPassed combined && backendOperationCount combined==1 && length both==2 && canonical (head both)==canonical (envelope attachment) && at "kind" (at "payload" (both!!1))==txt "application-catalog")
 (legacy, oldReplies) <- run "legacy" [] [(catalogRequest,1,False)]
 check "legacy configuration gets no unsolicited attachment" (backendPassed legacy && backendCallbackCount legacy==1 && backendOperationCount legacy==1 && length oldReplies==1 && at "kind" (at "payload" (head oldReplies))==txt "application-catalog")
 (disabled, disabledReplies) <- run "explicit-false" [("applicationAttachment",J.JBool False)] [(catalogRequest,1,False)]
 check "explicit false retains legacy behavior" (backendPassed disabled && length disabledReplies==1 && at "kind" (at "payload" (head disabledReplies))==txt "application-catalog")
 let malformed n = case n `mod` (5 :: Int) of
      0 -> commit [request owner,request (obj [("lifetime",txt "9007199254740993"),("session",txt (show (9007199254740996+n))),("frontend",txt "9007199254740997")])]
      1 -> commit [request owner,obj [("protocolVersion",J.JNumber "3"),("kind",txt "window-effect"),("binding",owner),("requestId",txt (show n))]]
      2 -> commit [request owner,obj [("protocolVersion",J.JNumber "2"),("kind",txt "catalog-request"),("binding",owner),("requestId",txt (show n))]]
      3 -> commit [request owner,obj [("protocolVersion",J.JNumber "3"),("kind",txt "catalog-request"),("binding",owner),("requestId",txt (show n)),("path",txt "/etc/passwd")]]
      _ -> "{\"viewProtocol\":1,\"viewProtocol\":1,\"kind\":\"view-commit\",\"projection\":{},\"requests\":[],\"focus\":[]}"
 forM_ [0..19 :: Int] $ \n -> do
  (bad, observed) <- run ("hostile-20261101-"++show n) enabled [(malformed n,0,True)]
  check ("whole frame refuses before attachment and domain IO seed 20261101 case "++show n) (not (backendPassed bad) && backendCleanup bad && backendCallbackCount bad==0 && backendOperationCount bad==0 && null observed)
 putStrLn "ui-mvp authenticated attachment controls passed"
