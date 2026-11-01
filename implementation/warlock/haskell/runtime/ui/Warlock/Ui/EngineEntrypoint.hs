{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ForeignFunctionInterface #-}
-- PREPARATION ONLY: not wired, compiled, executed, or an acceptance claim.
--
-- Proposed integration locations:
-- * implementation/warlock/haskell/runtime/ui/Main.hs:14-25: move getArgs
--   and exact dispatch ahead of withPeerNetwork, then preserve the existing
--   BrokerConfig body. EngineOnly runs this module with no custody authority.
-- * runtime/ui/Warlock/Ui/EngineEntrypoint.hs, alongside WebKit for the
--   warlock-ui-owner executable (verify hs-source-dirs before integration).
-- * runtime/runtime.cabal executable warlock-ui-owner lines 28-34:
--   declare this module/EngineAdapter and network ==3.2.0.0. The currently
--   linked WebKit still makes a GTK-free broker unresolved; branch dispatch
--   alone cannot satisfy that requirement.
--
-- BLOCKERS: no production EngineProtocol, authenticated transport, selected-FD
-- facade, PID1 exec admission or event conversion exists yet. The draft
-- EngineProtocol's 4-byte prefix is a header length, not a whole-message
-- length. Root must select and review complete bounded framing and the exact
-- held-image/loader/namespace/credential route before wiring this module.
-- No fallback may manufacture a verified session, projection or EngineResult.
module Warlock.Ui.EngineEntrypoint
  ( Mode(..), EngineArgs, classifyMode, prepareEngine
  , EngineFailure(..), runEngineOnly ) where

import Control.Exception (SomeAsyncException, SomeException, finally, fromException, mask, throwIO, try)
import Control.Concurrent (forkIO, killThread, threadDelay)
import Data.IORef (newIORef, atomicModifyIORef')
import Control.Monad (unless)
import qualified Data.ByteString as B
import Data.Char (isDigit)
import Data.List (isPrefixOf)
import qualified Data.Text as T
import Foreign.C.Error (Errno(..), eAGAIN, eWOULDBLOCK, eBADF, getErrno, throwErrnoIfMinus1_)
import Foreign.C.Types (CInt(..), CLong(..))
import GHC.IO.Exception (ioe_errno)
import Foreign.Marshal.Alloc (allocaBytes)
import System.IO (IOMode(ReadMode), withBinaryFile)
import System.Exit (ExitCode(ExitFailure))
import System.Posix.Process (exitImmediately)
import GHC.Conc (threadWaitRead)
import System.Timeout (timeout)
import qualified Network.Socket as Socket
import qualified Network.Socket.ByteString as SocketBytes
import qualified Data.Text.Encoding as TE
import qualified Warlock.Protocol.EngineTransport as Transport
import qualified Warlock.Protocol.PeerCredential as Credential
import qualified Warlock.Protocol.StrictJson as J
import System.Posix.Files (deviceID, fileID, getFdStatus, getFileStatus, isNamedPipe, isSocket)
import System.Posix.IO (FdOption(CloseOnExec,NonBlockingRead), OpenMode(ReadWrite), closeFd,
                        defaultFileFlags, dupTo, fdReadBuf, openFd, setFdOption)
import System.Posix.Process (getProcessID)
import System.Posix.Signals (sigKILL)
import System.Posix.Types (Fd(..))
import Warlock.Capture.Process.Bootstrap
  ( AdmissionDeadline, deadlineFromAbsoluteNs, remainingMicros )
import qualified Warlock.Ui.EngineAdapter as Adapter
import qualified Warlock.Ui.EngineProtocol as Protocol
import Warlock.Ui.EngineProtocol
  ( Startup )
import Warlock.Ui.Owner (EngineResult, UiEndpoints(..))
import Warlock.Ui.WebKit (runWebKit)

-- This token is interpreted only by the eventual same-held-image dispatcher;
-- it alone is not proof of image identity, PID1, parent, peer or authority.
data EngineArgs = EngineArgs Fd Fd String String Integer Integer deriving (Eq, Show)
data Mode = BrokerConfig FilePath | EngineOnly EngineArgs | Reject deriving (Eq, Show)

classifyMode :: [String] -> Mode
classifyMode ["--engine-only",rpcText,lifeText,deadlineText,incarnation,uidText,gidText] =
  case (fdNumber rpcText,fdNumber lifeText,identityNumber uidText,identityNumber gidText) of
    (Just rpc,Just life,Just uid,Just gid) | rpc /= life && validDecimal deadlineText 20
      && either (const False) (const True) (Protocol.sessionId (T.pack incarnation)) ->
      EngineOnly (EngineArgs (Fd rpc) (Fd life) deadlineText incarnation uid gid)
    _ -> Reject
classifyMode [path] | not (null path) && head path == '/' = BrokerConfig path
classifyMode _ = Reject

validDecimal :: String -> Int -> Bool
validDecimal value limit = not (null value) && length value <= limit
  && head value /= '0' && all (\c -> isDigit c && c <= '9') value

-- Fixed spawn provides actual parent IDs as mapped in the shared private user
-- namespace; equality is a consistency check, not provenance or authority.
identityNumber :: String -> Maybe Integer
identityNumber value
  | value == "0" = Just 0
  | not (validDecimal value 10) = Nothing
  | otherwise = case reads value :: [(Integer,String)] of
      [(n,"")] | n <= 4294967295 -> Just n
      _ -> Nothing

fdNumber :: String -> Maybe CInt
fdNumber value
  | not (validDecimal value 10) = Nothing
  | otherwise = case reads value :: [(Integer,String)] of
      [(n,"")] | n >= 3 && n <= toInteger (maxBound :: CInt) -> Just (fromInteger n)
      _ -> Nothing

-- Linux PR_SET_PDEATHSIG and SIGKILL. This cannot alone prove parent life:
-- the outer broker may already have died before the prctl call and PID1 may
-- see its outside-namespace parent as PID 0. The lifeline must be checked after
-- setting PDEATHSIG and again immediately before READY and throughout runtime.
foreign import ccall unsafe "prctl" c_prctl :: CInt -> CLong -> CLong -> CLong -> CLong -> IO CInt
foreign import ccall unsafe "fcntl" c_fcntlGetFd :: CInt -> CInt -> IO CInt

-- Linux F_GETFD = 1. An open fd, or an error other than EBADF, is refusal.
-- Runtime/loader use of stdio before Haskell main still requires separate
-- proof; this late check cannot attest that no descriptor was ever inherited.
requireClosedStdio :: IO ()
requireClosedStdio = mapM_ check [0,1,2]
  where
    check fd = do
      result <- c_fcntlGetFd fd 1
      if result /= -1 then ioError (userError "unexpected inherited stdio")
      else do err <- getErrno
              require (err == eBADF)

require :: Bool -> IO ()
require condition = unless condition (ioError (userError "engine local admission refused"))

-- True only for a live, empty nonblocking lifeline; any bytes/EOF or any
-- unexpected error are a refusal. A failed read is not a parent identity proof.
checkLifeline :: Fd -> IO ()
checkLifeline fd = do
  result <- try (allocaBytes 1 (\buffer -> fdReadBuf fd buffer 1))
  case result of
    Left problem | let Errno again = eAGAIN
                       Errno wouldBlock = eWOULDBLOCK
                   in ioe_errno problem == Just again || ioe_errno problem == Just wouldBlock -> pure ()
    _ -> ioError (userError "engine lifeline closed or invalid")

-- This prepares only local facts. It does NOT authenticate the broker, bind a
-- selected image, establish a private mount or grant authority. In particular,
-- the owner still needs an independently reviewed mount/namespace witness and
-- the transport must authenticate each frame. No READY is sent by this draft.
prepareEngine :: EngineArgs -> IO (Either EngineFailure AdmissionDeadline)
prepareEngine (EngineArgs rpc life originalD _ _ _) = do
  outcome <- try $ do
    deadline <- deadlineFromAbsoluteNs originalD >>= either (const (ioError (userError "bad original deadline")) ) pure
    -- Close the post-exec parent-death race as early as possible. The
    -- lifeline is still required because an already-dead outside parent is
    -- not identified reliably through getppid in a PID namespace.
    throwErrnoIfMinus1_ "engine PDEATHSIG" (c_prctl 1 (fromIntegral sigKILL) 0 0 0)
    requireClosedStdio
    rpcStatus <- getFdStatus rpc
    lifeStatus <- getFdStatus life
    require (isSocket rpcStatus && isNamedPipe lifeStatus)
    setFdOption rpc CloseOnExec True
    setFdOption life CloseOnExec True
    setFdOption life NonBlockingRead True
    checkLifeline life
    pid <- getProcessID
    require (pid == 1)
    current <- getFileStatus "/proc/thread-self/ns/pid"
    children <- getFileStatus "/proc/thread-self/ns/pid_for_children"
    require ((deviceID current,fileID current) == (deviceID children,fileID children))
    statusBytes <- withBinaryFile "/proc/self/status" ReadMode (\h -> B.hGet h 65537)
    require (B.length statusBytes <= 65536)
    let status = lines (map (toEnum . fromEnum) (B.unpack statusBytes))
    let single prefix = case [drop (length prefix) row | row <- status, prefix `isPrefixOf` row] of
          [value] -> words value
          _ -> []
        zeroCap prefix = case single prefix of [value] -> not (null value) && all (== '0') value; _ -> False
    require (single "Pid:" == ["1"] && single "NoNewPrivs:" == ["1"])
    require (all zeroCap ["CapInh:","CapPrm:","CapEff:","CapBnd:","CapAmb:"])
    -- Do not preserve the original native endpoint as fd0 or any arbitrary
    -- inherited stdio. The fixed owned spawn manifest must exclude them first.
    nullFd <- openFd "/dev/null" ReadWrite defaultFileFlags
    mapM_ (\target -> dupTo nullFd (Fd target) >> pure ()) [0,1,2]
    if nullFd > Fd 2 then closeFd nullFd else pure ()
    checkLifeline life
    left <- remainingMicros deadline
    require (left > 0)
    pure deadline
  pure (either (const (Left StartupRefused)) Right (outcome :: Either IOError AdmissionDeadline))

data EngineFailure = StartupRefused | DeadlineExpired | ChannelFailed
                   | EngineFailed deriving (Eq, Show)

-- Invariant required of the fixed launcher, NOT proved by the numeric FDs:
-- this is the selected held executable; this socket is the exclusive inherited
-- AF_UNIX connected socketpair endpoint; only the broker owns the opposite
-- end; no helper inherits either RPC or the parent-only lifeline writer. PID 0
-- is expected for an outside-namespace parent and is NOT authentication by
-- itself. Independent mount/proc provenance and FD census remain required.
-- A single reader owns all ancillary data. It rejects rights and malformed
-- controls in the public credential reader and checks every fragment.
readFrame :: Transport.CredentialReader -> Socket.Socket -> AdmissionDeadline
          -> (B.ByteString -> Either e Int)
          -> Integer -> Integer -> Maybe Credential.PeerCredential
          -> IO (B.ByteString, Credential.PeerCredential)
readFrame reader socket deadline lengthOf expectedUid expectedGid expected = do
  (header, credential) <- pieces 4 expected []
  size <- either (const (ioError (userError "frame length refused"))) pure (lengthOf header)
  pieces size (Just credential) []
  where
    pieces 0 Nothing _ = ioError (userError "missing credentials")
    pieces 0 (Just credential) acc = pure (B.concat (reverse acc),credential)
    pieces count first acc = do
      available <- remainingMicros deadline
      unless (available > 0) (ioError (userError "deadline expired"))
      let wanted = min count 65536
      result <- Transport.receiveCredentialChunk reader socket wanted
      case result of
        Right (Transport.CredentialChunk chunk credential) -> do
          require (not (B.null chunk) && B.length chunk <= wanted)
          require (Credential.credentialPid credential == 0
                && Credential.credentialUid credential == expectedUid
                && Credential.credentialGid credential == expectedGid)
          require (maybe True (== credential) first)
          pieces (count - B.length chunk) (Just credential) (chunk:acc)
        _ -> ioError (userError "frame or credentials refused")

-- The timeout bounds transport operations only; no asynchronous timeout is
-- wrapped around GTK. A partial send/receive or deadline expiry poisons RPC.
withinDeadline :: AdmissionDeadline -> IO a -> IO a
withinDeadline deadline action = do
  left <- remainingMicros deadline
  require (left > 0)
  result <- timeout left action
  after <- remainingMicros deadline
  case result of
    Just value | after > 0 -> pure value
    _ -> ioError (userError "transport outcome uncertain")

data RpcState = Idle Protocol.Session | Busy Protocol.Session | Dead

-- Every request is admitted once, with no state lock held across IO. Concurrent
-- requests retire the channel, never replay, and cannot revive it afterward.
makeRpc :: Socket.Socket -> Transport.CredentialReader -> AdmissionDeadline
        -> Integer -> Integer -> Credential.PeerCredential -> Startup
        -> IO (Protocol.Request -> IO (Either Protocol.ProtocolError Protocol.Reply))
makeRpc socket reader deadline expectedUid expectedGid peer startup = do
  state <- newIORef (Idle (Protocol.newSession startup))
  pure $ \request -> mask $ \restore -> do
    current <- atomicModifyIORef' state $ \old -> case old of
      Idle session -> (Busy session,Just session)
      _ -> (Dead,Nothing)
    case current of
      Nothing -> pure (Left Protocol.InvalidState)
      Just session -> do
        let (pending, encoded) = Protocol.beginRequest session request
        outcome <- try $ restore $ withinDeadline deadline $ do
          raw <- either (const (ioError (userError "request refused"))) pure encoded
          framed <- either (const (ioError (userError "request too large"))) pure (Transport.enginePrefix raw)
          SocketBytes.sendAll socket framed
          (reply,_) <- readFrame reader socket deadline Transport.engineHeaderLength expectedUid expectedGid (Just peer)
          let (next,decoded) = Protocol.acceptReply pending reply
          answer <- either (const (ioError (userError "reply refused"))) pure decoded
          pure (next,answer)
        case outcome of
          Left problem -> do
            atomicModifyIORef' state (const (Dead,()))
            case fromException problem :: Maybe SomeAsyncException of
              Just _ -> throwIO (problem :: SomeException)
              Nothing -> pure (Left Protocol.InvalidState)
          Right (next,answer) -> do
            remaining <- remainingMicros deadline
            admitted <- atomicModifyIORef' state $ \old -> case old of
              Busy _ | remaining > 0 -> (Idle next,True)
              _ -> (Dead,False)
            pure (if admitted then Right answer else Left Protocol.InvalidState)

-- Terminate the engine, not the broker or any child, on loss of the parent
-- lifeline or original deadline. The broker's sole reaper records the actual
-- exit and cleanup result. These Haskell threads are logically independent of
-- RPC, but the current nonthreaded runtime may stop scheduling them while GTK
-- is in unsafe FFI. They DO NOT prove continuous monitoring until root reviews
-- the RTS/provider execution model or an OS-enforced alternative.
startMonitors :: Fd -> AdmissionDeadline -> IO (IO ())
startMonitors life deadline = do
  lifeThread <- forkIO $ let loop = do
                              observed <- try (threadWaitRead life >> checkLifeline life) :: IO (Either IOError ())
                              case observed of
                                Left _ -> exitImmediately (ExitFailure 127)
                                Right () -> loop
                         in loop
  deadlineThread <- forkIO $ let loop = do
                                  left <- remainingMicros deadline
                                  if left <= 0 then exitImmediately (ExitFailure 127)
                                    else threadDelay left >> loop
                             in loop
  pure (killThread lifeThread >> killThread deadlineThread)

runEngineOnly :: EngineArgs -> IO (Either EngineFailure EngineResult)
runEngineOnly args@(EngineArgs (Fd rpc) life originalD incarnation expectedUid expectedGid) = do
  prepared <- prepareEngine args
  case prepared of
    Left failure -> pure (Left failure)
    Right deadline -> do
      -- mkSocket adopts the selected FD; do not wrap it a second time.
      outcome <- try $ do
        socket <- Socket.mkSocket rpc
        (do
          -- Preserve existing flags; public helper verifies O_NONBLOCK and
          -- CLOEXEC after setting them. Must happen before any send or recv.
          Transport.configureSocketFlags socket
          Transport.enablePassCredentials socket
          reader <- Transport.newCredentialReader
          stopMonitors <- startMonitors life deadline
          (do
            let ready = TE.encodeUtf8 $ J.renderJson $ J.JObject
                  [("engineReady",J.JNumber "1"),("deadline",J.JString (T.pack originalD)),
                   ("incarnation",J.JString (T.pack incarnation))]
            frame <- either (const (ioError (userError "ready too large"))) pure (Transport.startupPrefix ready)
            (raw,peer) <- withinDeadline deadline $ do
              checkLifeline life
              SocketBytes.sendAll socket frame
              readFrame reader socket deadline Transport.startupHeaderLength expectedUid expectedGid Nothing
            startup <- either (const (ioError (userError "startup invalid"))) pure (Protocol.decodeStartup raw)
            sid <- either (const (ioError (userError "incarnation invalid"))) pure (Protocol.sessionId (T.pack incarnation))
            require (T.unpack (Protocol.startupDeadline startup) == originalD
                  && Protocol.startupIncarnation startup == sid)
            leftAfterDecode <- remainingMicros deadline
            require (leftAfterDecode > 0)
            checkLifeline life
            rpcCall <- makeRpc socket reader deadline expectedUid expectedGid peer startup
            let remote = Adapter.clientEndpoints startup rpcCall
                -- Observe the SAME immutable D locally during retirement.
                -- Begin GUI draining before the broker's final 500ms reserve;
                -- shutdown never depends on a final RPC at that cutoff.
                localStop = do
                  left <- remainingMicros deadline
                  if left <= 1000000 then pure True else uiShouldStop remote
                localRemaining = do
                  left <- remainingMicros deadline
                  if left <= 1000000 then pure left
                    else min left <$> uiRemainingMicros remote
                endpoints = remote {uiShouldStop=localStop,uiRemainingMicros=localRemaining}
            runWebKit endpoints (Adapter.emitEvent rpcCall)
            ) `finally` stopMonitors
          ) `finally` Socket.close socket
      case outcome of
        Left problem -> case fromException problem :: Maybe SomeAsyncException of
          Just _ -> throwIO (problem :: SomeException)
          Nothing -> pure (Left EngineFailed)
        Right result -> pure (Right result)

-- Review gates before integration: independent executable/socket lineage and
-- private mount witness, verified fixed spawn UID/GID provenance and shared
-- user-namespace mapping (argv values alone do not authenticate anything),
-- bounded cleanup ownership, FD census/stdio loader effects, exact errno and
-- provider behavior. No compile, tests, model, GUI, or acceptance run.
