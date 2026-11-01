{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- VM-only sensitivity control. This is a separate QA document and deliberately
-- permissive origin, never a product view, policy, native grant, or acceptance.
module Main (main) where

import Control.Concurrent (forkFinally, killThread, newEmptyMVar, putMVar, readMVar, tryReadMVar, threadDelay, runInBoundThread)
import Control.Exception (IOException, SomeException, bracket, finally, onException, try)
import Control.Monad (unless, when)
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.Char (toLower)
import Data.IORef (atomicModifyIORef', newIORef, readIORef)
import Data.Maybe (isNothing)
import Foreign.C.String (CString, peekCString)
import Foreign.C.Types (CInt(..), CUInt(..))
import Foreign.Ptr (Ptr, nullPtr)
import GHC.Clock (getMonotonicTimeNSec)
import qualified Network.Socket as S
import qualified Network.Socket.ByteString as N
import Numeric (showHex)
import System.Environment (getArgs, getEnvironment)
import System.Exit (exitFailure)
import System.FilePath (isAbsolute)
import System.IO (IOMode(ReadMode), withBinaryFile)
import System.Timeout (timeout)
import Text.Read (readMaybe)

data Object
foreign import ccall safe "gtk_init_check" gtkInit :: IO CInt
foreign import ccall safe "gtk_window_new" windowNew :: IO (Ptr Object)
foreign import ccall safe "gtk_window_set_child" windowChild :: Ptr Object -> Ptr Object -> IO ()
foreign import ccall safe "gtk_window_present" windowPresent :: Ptr Object -> IO ()
foreign import ccall safe "gtk_window_destroy" windowDestroy :: Ptr Object -> IO ()
foreign import ccall safe "webkit_web_view_new" webViewNew :: IO (Ptr Object)
foreign import ccall safe "webkit_web_view_load_uri" viewLoad :: Ptr Object -> CString -> IO ()
foreign import ccall unsafe "webkit_web_view_get_uri" viewUri :: Ptr Object -> IO CString
foreign import ccall unsafe "webkit_get_major_version" webkitMajor :: IO CUInt
foreign import ccall unsafe "webkit_get_minor_version" webkitMinor :: IO CUInt
foreign import ccall unsafe "webkit_get_micro_version" webkitMicro :: IO CUInt
foreign import ccall safe "g_main_context_iteration" iterateContext :: Ptr () -> CInt -> IO CInt

sha :: B.ByteString -> String
sha = concatMap (\byte -> let digits = showHex byte "" in replicate (2 - length digits) '0' ++ digits) . B.unpack . SHA.hash

listener :: IO S.Socket
listener = do
  socket <- S.socket S.AF_INET S.Stream S.defaultProtocol
  (do S.bind socket (S.SockAddrInet 0 (S.tupleToHostAddress (127,0,0,1)))
      S.listen socket 16
      pure socket) `onException` S.close socket

port :: S.Socket -> IO Int
port socket = do
  address <- S.getSocketName socket
  case address of
    S.SockAddrInet value _ -> pure (fromIntegral value)
    _ -> ioError (userError "unexpected control listener family")

response :: B.ByteString -> B.ByteString -> B.ByteString -> B.ByteString
response status headers body = "HTTP/1.1 " <> status <> "\r\nConnection: close\r\nContent-Length: "
  <> C.pack (show (B.length body)) <> "\r\n" <> headers <> "\r\n" <> body

-- QA server parser: finite bytes/time, canonical length, no keepalive or
-- attacker-controlled paths. The captured body is independent of JS DOM.
request :: S.Socket -> IO (B.ByteString, [(B.ByteString,B.ByteString)], B.ByteString)
request socket = do
  bounded <- timeout 2000000 (readHeaders B.empty)
  maybe (ioError (userError "control request timed out")) pure bounded
 where
  readHeaders bytes = do
    unless (B.length bytes <= 16384) (ioError (userError "control headers bound"))
    case B.breakSubstring "\r\n\r\n" bytes of
      (_,suffix) | B.null suffix -> do
        part <- N.recv socket 4096
        unless (not (B.null part)) (ioError (userError "control request truncated"))
        readHeaders (bytes <> part)
      (headers,suffix) -> do
        let rows = C.lines headers
        first <- case rows of line:_ -> pure (C.filter (/='\r') line); _ -> ioError (userError "control request line")
        let fields = [(C.map toLower key,C.dropWhile (==' ') (C.drop 1 value)) | line <- drop 1 rows,
              let (key,value) = C.break (==':') (C.filter (/='\r') line), not (B.null value)]
            lengths = [value | (key,value) <- fields, key == "content-length"]
        unless (not (any ((=="transfer-encoding") . fst) fields)) (ioError (userError "control transfer encoding"))
        size <- case lengths of
          [] -> pure 0
          [value] -> case readMaybe (C.unpack value) of
            Just number | number >= (0 :: Int) && number <= 8192 && C.pack (show number) == value -> pure number
            _ -> ioError (userError "control body length")
          _ -> ioError (userError "duplicate control length")
        let initial = B.drop 4 suffix
        unless (B.length initial <= size) (ioError (userError "control trailing bytes"))
        body <- readBody size initial
        pure (first,fields,body)
  readBody size bytes
    | B.length bytes == size = pure bytes
    | otherwise = do
        part <- N.recv socket (min 4096 (size - B.length bytes))
        unless (not (B.null part)) (ioError (userError "control body truncated"))
        readBody size (bytes <> part)

expected :: String -> B.ByteString
expected tag = "{\"qaSecurityObservation\":\"" <> C.pack tag <> "\"}"

main :: IO ()
main = S.withSocketsDo $ runInBoundThread $ do
  args <- getArgs
  (scriptPath, expectedHash, deadline) <- case args of
    [path,digest,raw] | isAbsolute path -> case readMaybe raw of
      Just value -> pure (path,digest,value :: Integer)
      Nothing -> ioError (userError "deadline must be monotonic nanoseconds")
    _ -> ioError (userError "expected ABSOLUTE_PROBES_JS SHA256 ORIGINAL_DEADLINE_NS")
  now <- toInteger <$> getMonotonicTimeNSec
  unless (deadline > now && deadline - now <= 30000000000) (ioError (userError "control original deadline out of range"))
  environment <- getEnvironment
  let forbidden (key,_) = take 7 key == "WEBKIT_" || key `elem`
        ["http_proxy","https_proxy","all_proxy","HTTP_PROXY","HTTPS_PROXY","ALL_PROXY","GIO_USE_PROXY_RESOLVER"]
  when (any forbidden environment) (ioError (userError "untrusted engine environment"))
  script <- B.readFile scriptPath
  unless (sha script == expectedHash && B.length script <= 262144 && not (B.isInfixOf "</script" (C.map toLower script)))
    (ioError (userError "probe source pin or shape refused"))
  version <- (,,) <$> webkitMajor <*> webkitMinor <*> webkitMicro
  initialized <- gtkInit
  unless (initialized /= 0) (ioError (userError "GTK display unavailable"))
  nonceBytes <- withBinaryFile "/dev/urandom" ReadMode (\handle -> B.hGet handle 24)
  unless (B.length nonceBytes == 24) (ioError (userError "control random route unavailable"))
  let token = C.pack (concatMap (\byte -> let digits = showHex byte "" in replicate (2-length digits) '0' ++ digits) (B.unpack nonceBytes))
  (finalReport,finalPassed) <- bracket listener S.close $ \local -> bracket listener S.close $ \remote -> do
    localPort <- port local
    remotePort <- port remote
    let origin = "http://127.0.0.1:" <> C.pack (show localPort)
        remoteOrigin = "http://127.0.0.1:" <> C.pack (show remotePort)
        documentPath = "/index/" <> token
        reportPath = "/commit/" <> token
        remotePath = "/probe/" <> token <> ".js"
        documentURI = origin <> documentPath
        remoteURI = remoteOrigin <> remotePath
        remoteBody = "window.__warlockRemoteExecuted=true;fetch('" <> reportPath
          <> "',{method:'POST',headers:{'Content-Type':'application/json','X-Warlock-Api':'1'},body:'{\"qaSecurityObservation\":\"remote-script-body-executed\"}'});"
        policy = "default-src 'none'; script-src 'unsafe-inline' 'unsafe-eval' " <> remoteOrigin <> "; connect-src " <> origin
        prelude = "globalThis.WARLOCK_QA_REPORT_ROUTE='" <> reportPath <> "';globalThis.WARLOCK_QA_REMOTE_URL='" <> remoteURI <> "';\n"
        document = "<!doctype html><html><head><meta charset=\"utf-8\"></head><body><script>\n"
          <> prelude <> script <> "\n</script></body></html>"
    observations <- newIORef ([] :: [B.ByteString])
    remoteHits <- newIORef (0 :: Int)
    let single name headers = case [value | (key,value) <- headers, key == name] of
          [value] -> Just value
          _ -> Nothing
        localHost = B.drop 7 origin
        remoteHost = B.drop 7 remoteOrigin
        serve socket route = do
          let loop = do
                (connection,_) <- S.accept socket
                _ <- try (bracket (pure connection) S.close $ \peer -> do
                  (line,headers,body) <- request peer
                  (reply,afterSend) <- route line headers body
                  N.sendAll peer reply
                  afterSend) :: IO (Either IOException ())
                loop
          loop
        refused = pure (response "404 Not Found" "" B.empty, pure ())
        localRoute line headers body
          | line == "GET " <> documentPath <> " HTTP/1.1" && single "host" headers == Just localHost =
              pure (response "200 OK" ("Content-Type: text/html; charset=utf-8\r\nContent-Security-Policy: " <> policy <> "\r\nX-Content-Type-Options: nosniff\r\n") document, pure ())
          | line == "POST " <> reportPath <> " HTTP/1.1" && single "host" headers == Just localHost
              && single "origin" headers == Just origin && single "x-warlock-api" headers == Just "1"
              && single "content-type" headers == Just "application/json" =
              pure (response "204 No Content" "" B.empty, atomicModifyIORef' observations (\rows -> (take 32 (body:rows),())))
          | otherwise = refused
        remoteRoute line headers _
          | line == "GET " <> remotePath <> " HTTP/1.1" && single "host" headers == Just remoteHost =
              pure (response "200 OK" "Content-Type: application/javascript; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n" remoteBody,
                    atomicModifyIORef' remoteHits (\count -> (count+1,())))
          | otherwise = refused
    doneA <- newEmptyMVar
    doneB <- newEmptyMVar
    serverA <- forkFinally (serve local localRoute) (putMVar doneA)
    serverB <- forkFinally (serve remote remoteRoute) (putMVar doneB)
      `onException` (killThread serverA >> readMVar doneA >> pure ())
    let stopServers = do
          priorA <- tryReadMVar doneA
          priorB <- tryReadMVar doneB
          time <- toInteger <$> getMonotonicTimeNSec
          let micros = max 0 (min 1500000 ((deadline-time) `div` 1000))
          stopped <- timeout (fromInteger micros) $ do
            killThread serverA
            killThread serverB
            _ <- readMVar doneA :: IO (Either SomeException ())
            _ <- readMVar doneB :: IO (Either SomeException ())
            pure ()
          unless (stopped == Just ()) (ioError (userError "control server retirement unconfirmed before original deadline"))
          unless (isNothing priorA && isNothing priorB) (ioError (userError "control server exited before retirement"))
    (report,passed) <- flip finally stopServers $ do
      window <- windowNew
      view <- webViewNew
      unless (window /= nullPtr && view /= nullPtr) (ioError (userError "control WebKit construction failed"))
      flip finally (windowDestroy window) $ do
        windowChild window view
        windowPresent window
        C.useAsCString documentURI (viewLoad view)
        let tags = ["approved-script-executed", "executed-eval", "executed-inline", "executed-remote", "remote-script-body-executed"]
            loop = do
              _ <- iterateContext nullPtr 0
              rows <- readIORef observations
              hits <- readIORef remoteHits
              time <- toInteger <$> getMonotonicTimeNSec
              let complete = all (\tag -> expected tag `elem` rows) tags && hits > 0 && time < deadline
              -- Keep the original D intact while reserving time to retire the
              -- owned HTTP servers. A timeout is not a successful observation.
              if complete || time + 500000000 >= deadline then pure (rows,hits,complete) else threadDelay 1000 >> loop
        (rows,hits,complete) <- loop
        actualPtr <- viewUri view
        actual <- if actualPtr == nullPtr then pure "" else peekCString actualPtr
        let matched = actual == C.unpack documentURI
            passed = complete && matched
            flag value = if value then "true" else "false"
            counts = [(tag,length (filter (==expected tag) rows)) | tag <- tags]
            countsJson = C.intercalate "," ["\"" <> C.pack tag <> "\":" <> C.pack (show count) | (tag,count) <- counts]
        pure ("{\"schema\":1,\"kind\":\"vm-webkit-permissive-control\",\"observationsReached\":" <> flag passed
          <> ",\"sameEngineVersion\":\"" <> C.pack (show version) <> "\",\"probeSHA256\":\"" <> C.pack (sha script)
          <> "\",\"documentSHA256\":\"" <> C.pack (sha document) <> "\",\"policySHA256\":\"" <> C.pack (sha policy)
          <> "\",\"controlPolicy\":\"" <> policy
          <> "\",\"remoteBodySHA256\":\"" <> C.pack (sha remoteBody) <> "\",\"documentURI\":\"" <> documentURI
          <> "\",\"remoteURI\":\"" <> remoteURI <> "\",\"finalURIMatches\":" <> flag matched
          <> ",\"remoteCorrectMimeRequests\":" <> C.pack (show hits) <> ",\"signals\":{" <> countsJson
          <> "},\"qaServersRetired\":true,\"browserPeerIdentityVerified\":false,\"productionPolicy\":false,\"engineCleanupQualified\":false,\"nativeAcceptance\":false,\"releaseAccepted\":false}", passed)
    pure (report,passed)
  closedAt <- toInteger <$> getMonotonicTimeNSec
  let within = closedAt < deadline
      finalStatus = finalPassed && within
      flag value = if value then "true" else "false"
  C.putStrLn (B.init finalReport <> ",\"withinOriginalDeadline\":" <> flag within <> ",\"passed\":" <> flag finalStatus <> "}")
  unless finalStatus exitFailure
