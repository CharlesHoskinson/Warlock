{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Root-only selected executable: fd 0 is the already activated owned socket.
module Main (main) where
import Control.Monad (unless,forM_)
import Control.Exception (IOException,bracket,bracketOnError,catch,throwIO,try)
import Foreign.C.Error (Errno(..),eCONNRESET,throwErrnoIfMinus1_)
import Foreign.C.Types (CInt(..))
import GHC.IO.Exception (ioe_errno)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.List (isPrefixOf)
import Data.Char (isHexDigit)
import Numeric (showHex)
import System.Environment (lookupEnv)
import System.IO (Handle,IOMode(ReadMode),BufferMode(NoBuffering),hClose,hSetBinaryMode,hSetBuffering,hFlush,hPutStrLn,stdout,withBinaryFile)
import System.Exit (ExitCode(..))
import System.Posix.IO (OpenMode(WriteOnly),closeFd,creat,defaultFileFlags,exclusive,fdToHandle,openFd)
import System.Posix.Files (readSymbolicLink)
import System.Posix.Process (forkProcess,getProcessID,getProcessStatus,ProcessStatus(..),exitImmediately)
import System.Posix.User (getRealUserID,getEffectiveUserID,getRealGroupID,getEffectiveGroupID,setUserID)
import System.Posix.Types (Fd(..))
import Text.Read (readMaybe)
import Warlock.Protocol.Codec (decodeServerChecked)
import Warlock.Protocol.Framing (headerLength,prefix)

-- Linux-only controlled EOF stimulus. Borrow fd0 without duplicating or
-- closing its owner: SHUT_WR=1 ends sends while the child awaits host refusal.
foreign import ccall unsafe "shutdown" shutdownWrite :: CInt -> CInt -> IO CInt

prepare :: B.ByteString
prepare = "{\"version\":1,\"kind\":\"prepare\",\"body\":{\"binding\":{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"},\"intent\":{\"request\":\"6\",\"generation\":\"7\",\"incarnation\":\"9007199254740993\",\"operation\":\"restore\",\"context\":{\"lifetime\":\"1\",\"epoch\":\"3\",\"output\":\"4\",\"revision\":\"5\"}},\"selectionId\":\"0123456789abcdef0123456789abcdef\"}}"

-- A complete checked server frame is an explicit root-fixture control/ACK.
-- A host-side refusal closes its endpoint; EOF here means only that closure,
-- never that a retained peer FD has independently reached EOF.
readControl :: Handle -> IO (Maybe B.ByteString)
readControl h = do
 header <- B.hGet h 4
 if B.null header then pure Nothing else do
  n <- either (ioError . userError . show) pure (headerLength header)
  body <- B.hGet h n
  unless (B.length body == n) (ioError (userError "short fixture control"))
  either (ioError . userError . show) (const (pure (Just body))) (decodeServerChecked body)

-- Refusal fixtures alone allow the exact kernel reset produced when the
-- receiver closes with an unread request body. Every other I/O error propagates.
readExpectedRefusal :: Handle -> IO (Maybe B.ByteString)
readExpectedRefusal h = readControl h `catch` resetOnly
 where
  resetOnly :: IOException -> IO (Maybe B.ByteString)
  resetOnly err = case ioe_errno err of
   Just number | Errno number == eCONNRESET -> pure Nothing
   _ -> throwIO err

legacyMain :: IO ()
legacyMain = do
 h <- fdToHandle (Fd 0)
 hSetBinaryMode h True
 hSetBuffering h NoBuffering
 mode <- lookupEnv "DEL010_MODE"
 start <- case mode of
  Just "immediate" -> pure (Just "positive")
  Just "controlled" -> readControl h
  Just "controlled-refusal" -> do
   reply <- readExpectedRefusal h
   case reply of
    Nothing -> pure Nothing
    Just _ -> ioError (userError "unexpected control in foreign-refusal fixture")
  _ -> ioError (userError "fixed fixture mode required")
 case start of
  Nothing -> pure ()
  Just command -> do
   frame <- either (ioError . userError . show) pure (prefix prepare)
   B.hPut h frame
   let expectedRefusal = "\"session\":\"3\"" `B.isInfixOf` command
   ack <- if expectedRefusal then readExpectedRefusal h else readControl h
   unless (maybe expectedRefusal (const True) ack) (ioError (userError "positive ACK missing"))

-- Distinct checked effect requests; this is a controlled client, not a native
-- issuer. The public-library suite independently constructs its expected list.
persistentRequest :: Integer -> Int -> B.ByteString
persistentRequest seed index = C.pack $
 "{\"version\":1,\"kind\":\"prepare\",\"body\":{\"binding\":{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"},\"intent\":{\"request\":\"" ++ show request ++ "\",\"generation\":\"" ++ show (request+1000000) ++ "\",\"incarnation\":\"9007199254740993\",\"operation\":\"restore\",\"context\":{\"lifetime\":\"1\",\"epoch\":\"3\",\"output\":\"4\",\"revision\":\"5\"}},\"selectionId\":\"" ++ replicate (32-length token) '0' ++ token ++ "\"}}"
 where
  request = 9007199254742000 + seed*10 + toInteger index
  token = showHex (seed*17+toInteger index) ""

sendFixture :: Bool -> Handle -> B.ByteString -> IO ()
sendFixture fragmented h bytes = do
 framed <- either (ioError . userError . show) pure (prefix bytes)
 if fragmented then mapM_ (B.hPut h) (split framed [1,2,7,11]) else B.hPut h framed
 where
  split remaining [] = [remaining | not (B.null remaining)]
  split remaining (size:rest) = let (piece,tailBytes)=B.splitAt size remaining in piece:split tailBytes rest

sendBuffered :: Handle -> [B.ByteString] -> IO ()
sendBuffered h inputs = do
 frames <- mapM (either (ioError . userError . show) pure . prefix) inputs
 B.hPut h (B.concat frames)

requireAck :: Handle -> IO ()
requireAck h = readControl h >>= maybe (ioError (userError "persistent ACK missing")) (const (pure ()))
requireRefusal :: Handle -> IO ()
requireRefusal h = readExpectedRefusal h >>= maybe (pure ()) (const (ioError (userError "refused request unexpectedly acknowledged")))

-- QA metadata only. These fixed proc reads neither authenticate a sender nor
-- grant an effect. Probe failure is incomplete evidence, not a fabricated map.
contextLine :: String -> IO String
contextLine phaseName = do
 pid <- getProcessID
 uid <- getRealUserID
 euid <- getEffectiveUserID
 gid <- getRealGroupID
 egid <- getEffectiveGroupID
 uidMap <- boundedProc "/proc/self/uid_map" 4096
 gidMap <- boundedProc "/proc/self/gid_map" 4096
 userNs <- readSymbolicLink "/proc/self/ns/user"
 pidNs <- readSymbolicLink "/proc/self/ns/pid"
 unless (length userNs<=64 && length pidNs<=64) (ioError (userError "context namespace bound"))
 status <- boundedProc "/proc/self/status" 65536
 eff <- capability "CapEff:" status
 prm <- capability "CapPrm:" status
 pure ("fixture_context " ++ show ["1",phaseName,show pid,show uid,show euid,show gid,show egid,C.unpack uidMap,C.unpack gidMap,userNs,pidNs,eff,prm])
 where
  boundedProc path bound = withBinaryFile path ReadMode $ \handle -> do
   bytes <- B.hGet handle (bound+1)
   unless (B.length bytes<=bound) (ioError (userError "context proc bound"))
   pure bytes
  capability name status = case [C.unpack value | line <- C.lines status, [field,value] <- [C.words line],field==C.pack name] of
   [value] | length value==16 && all isHexDigit value -> pure value
   _ -> ioError (userError "context capability field")

withContextSink :: (Maybe Handle -> IO a) -> IO a
withContextSink = bracket acquire release
 where
  acquire = do
   selected <- lookupEnv "DEL010_CONTEXT_PATH"
   case selected of
    Nothing -> pure Nothing
    Just path | not (null path) && head path=='/' -> do
     result <- try (bracketOnError (openFd path WriteOnly defaultFileFlags {creat=Just 0o600,exclusive=True}) closeFd fdToHandle) :: IO (Either IOException Handle)
     case result of
      Right handle -> pure (Just handle)
      Left _ -> putStrLn "fixture_context_error phase=open class=IOException" >> pure Nothing
    _ -> putStrLn "fixture_context_error phase=open class=InvalidPath" >> pure Nothing
  release Nothing = pure ()
  release (Just handle) = hClose handle `catch` (\(_ :: IOException) -> putStrLn "fixture_context_error phase=close class=IOException")

emitContext :: Maybe Handle -> String -> IO ()
emitContext sink phaseName = do
 observed <- try (contextLine phaseName) :: IO (Either IOException String)
 let line=case observed of Right value -> value; Left _ -> "fixture_context_error phase=" ++ phaseName ++ " class=IOException"
 putStrLn line
 hFlush stdout
 case sink of
  Nothing -> pure ()
  Just handle -> (hPutStrLn handle line >> hFlush handle) `catch` (\(_ :: IOException) -> putStrLn ("fixture_context_error phase=" ++ phaseName ++ " class=WriteFailure"))

persistentMain :: String -> IO ()
persistentMain mode = do
 h <- fdToHandle (Fd 0)
 hSetBinaryMode h True
 hSetBuffering h NoBuffering
 seedText <- lookupEnv "DEL010_SEED"
 seed <- maybe (ioError (userError "fixed persistent seed required")) pure (seedText >>= readMaybe)
 let count = 3+fromInteger (seed `mod` 3)
     ascending = [0..count-1]
     order = if odd seed then reverse ascending else drop 1 ascending ++ take 1 ascending
     requests = map (persistentRequest seed) order
     fragmented = seed `mod` 2 == 0
 case mode of
  "persistent-empty-exit" -> do
   throwErrnoIfMinus1_ "fixture shutdown(SHUT_WR)" (shutdownWrite 0 1)
   requireRefusal h
  "persistent-seeded" -> forM_ requests (\bytes -> sendFixture fragmented h bytes >> requireAck h)
  "persistent-buffered-retire" -> do
   sendBuffered h requests
   requireAck h
   requireRefusal h
  "persistent-after-retire" -> do
   sendFixture False h (persistentRequest seed 0)
   -- The host retires the registration before sending this ACK. Therefore
   -- the second send occurs after expiry, unlike the buffered-input control.
   requireAck h
   sendFixture False h (persistentRequest seed 1)
   requireRefusal h
  "persistent-malformed" -> do
   sendFixture False h (persistentRequest seed 0)
   requireAck h
   sendBuffered h ["{\"version\":1,\"kind\":\"prepare\",\"body\":{\"binding\":{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"},\"unexpected\":true}}",persistentRequest seed 2]
   requireRefusal h
  "persistent-foreign-binding" -> do
   sendFixture False h (persistentRequest seed 0)
   requireAck h
   let wrong = C.pack (replaceSession (C.unpack (persistentRequest seed 1)))
   sendFixture False h wrong
   requireRefusal h
  "persistent-unrelated-fork" -> forkWriter h seed
  "persistent-cross-user-same-pid" -> do
   sendFixture False h (persistentRequest seed 0)
   requireAck h
   withContextSink $ \sink -> do
    emitContext sink "before-setuid"
    originalUid <- getRealUserID
    targetText <- lookupEnv "DEL010_WRITER_UID"
    target <- maybe (ioError (userError "actual delegated writer UID required")) pure (targetText >>= readMaybe)
    unless (target /= originalUid) (ioError (userError "cross-user fixture requires distinct UID"))
    setUserID target
    real <- getRealUserID
    effective <- getEffectiveUserID
    unless (real == target && effective == target) (ioError (userError "actual UID change failed"))
    pid <- getProcessID
    gid <- getRealGroupID
    putStrLn ("fixture_writer pid=" ++ show pid ++ " uid=" ++ show real ++ " gid=" ++ show gid)
    hFlush stdout
    emitContext sink "after-setuid"
   sendFixture False h (persistentRequest seed 1)
   requireRefusal h
  _ -> ioError (userError "unknown persistent fixture mode")
 where
  replaceSession input = case input of
   [] -> []
   _ | "\"session\":\"2\"" `isPrefixOf` input -> "\"session\":\"3\"" ++ drop (length ("\"session\":\"2\"" :: String)) input
   char:rest -> char:replaceSession rest
  forkWriter h seed = do
   sendFixture False h (persistentRequest seed 0)
   requireAck h
   writer <- forkProcess $ do
    pid <- getProcessID
    uid <- getRealUserID
    gid <- getRealGroupID
    putStrLn ("fixture_writer pid=" ++ show pid ++ " uid=" ++ show uid ++ " gid=" ++ show gid)
    hFlush stdout
    sendFixture False h (persistentRequest seed 1)
    requireRefusal h
    exitImmediately ExitSuccess
   observed <- getProcessStatus True False writer
   unless (observed == Just (Exited ExitSuccess)) (ioError (userError ("owned fixture writer failed: " ++ show observed)))

main :: IO ()
main = do
 mode <- lookupEnv "DEL010_MODE"
 case mode of
  Just selected | "persistent-" `isPrefixOf` selected -> persistentMain selected
  _ -> legacyMain
