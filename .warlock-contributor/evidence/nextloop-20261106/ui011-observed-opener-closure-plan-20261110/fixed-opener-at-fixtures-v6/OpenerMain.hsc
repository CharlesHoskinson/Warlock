{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Separate, blank native QA window. Receipts are not native acceptance.
module Main (main) where

#include <fcntl.h>

import Control.Concurrent (threadDelay)
import Control.Exception (SomeException, bracket, finally, mask_, onException, try)
import Control.Monad (unless, when, void)
import qualified Crypto.Hash.SHA256 as SHA256
import Data.Bits ((.&.), (.|.))
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as BC
import Data.IORef
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Foreign.C.String (CString, withCString)
import Foreign.C.Types (CInt(..), CULong(..))
import Foreign.Ptr (Ptr, FunPtr, nullPtr, nullFunPtr, castFunPtr, freeHaskellFunPtr)
import GHC.Clock (getMonotonicTimeNSec)
import Numeric (showHex)
import System.Environment (getArgs, setEnv)
import System.IO (BufferMode(NoBuffering), Handle, hClose, hReady, hSetBuffering, stdin, stdout)
import System.Posix.Files
  (FileStatus, deviceID, fileID, fileMode, fileOwner, fileSize, getFdStatus,
   getSymbolicLinkStatus, isRegularFile, linkCount, modificationTimeHiRes)
import System.Posix.IO (fdToHandle, closeFd)
import System.Posix.Process (getProcessID)
import System.Posix.Types (Fd(..))
import System.Posix.User (getRealUserID)
import qualified Warlock.Protocol.Identity as I
import Warlock.Protocol.StrictJson (Json(..), renderJson)
import Warlock.Ui.DefaultContextOwner
  (withPhysicalDefaultContextOwner, requirePhysicalDefaultContextOwner)
import Warlock.Ui.Display (captureDisplayEnvironment)
import Warlock.Ui.PrivateNetwork (enterPrivateNetwork)
import OpenerAdmission

foreign import ccall unsafe "open" openReadOnly :: CString -> CInt -> IO CInt
foreign import ccall unsafe "g_set_prgname" setProgramName :: CString -> IO ()
foreign import ccall safe "gtk_init_check" gtkInit :: IO CInt
foreign import ccall safe "gtk_window_new" windowNew :: IO (Ptr ())
foreign import ccall safe "gtk_window_set_title" windowTitle :: Ptr () -> CString -> IO ()
foreign import ccall safe "gtk_window_set_default_size" windowSize :: Ptr () -> CInt -> CInt -> IO ()
foreign import ccall safe "gtk_window_present" windowPresent :: Ptr () -> IO ()
foreign import ccall safe "gtk_window_close" windowClose :: Ptr () -> IO ()
foreign import ccall safe "gtk_window_destroy" windowDestroy :: Ptr () -> IO ()
foreign import ccall unsafe "gtk_widget_get_mapped" windowMapped :: Ptr () -> IO CInt
foreign import ccall unsafe "g_object_ref_sink" refSink :: Ptr () -> IO (Ptr ())
foreign import ccall safe "g_object_unref" unref :: Ptr () -> IO ()
foreign import ccall safe "g_main_context_iteration" contextIteration :: Ptr () -> CInt -> IO CInt
foreign import ccall unsafe "g_signal_connect_data" connectSignal
  :: Ptr () -> CString -> FunPtr () -> Ptr () -> FunPtr () -> CInt -> IO CULong
foreign import ccall unsafe "g_signal_handler_is_connected" signalConnected :: Ptr () -> CULong -> IO CInt
foreign import ccall safe "g_signal_handler_disconnect" disconnectSignal :: Ptr () -> CULong -> IO ()
foreign import ccall "wrapper" simpleCallback :: (Ptr () -> Ptr () -> IO ()) -> IO (FunPtr (Ptr () -> Ptr () -> IO ()))
foreign import ccall "wrapper" closeCallback :: (Ptr () -> Ptr () -> IO CInt) -> IO (FunPtr (Ptr () -> Ptr () -> IO CInt))

require :: Bool -> String -> IO ()
require value reason = unless value (ioError (userError reason))

monotonic :: IO Integer
monotonic = toInteger <$> getMonotonicTimeNSec

identity :: FileStatus -> (Integer,Integer,Integer,Integer,Integer,Integer,Rational)
identity status = (toInteger (deviceID status),toInteger (fileID status),
  toInteger (fileOwner status),toInteger (fileMode status),toInteger (linkCount status),
  toInteger (fileSize status),toRational (modificationTimeHiRes status))

secureConfiguration :: FilePath -> String -> Integer -> IO Configuration
secureConfiguration path expected inherited = do
  uid <- getRealUserID
  before <- getSymbolicLinkStatus path
  require (isRegularFile before && fileOwner before == uid && linkCount before == 1
    && fileMode before .&. 0o777 == 0o600 && fileSize before <= 4096) "configuration custody refused"
  bracket (withCString path $ \name -> do
      fd <- openReadOnly name (#{const O_RDONLY} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC})
      require (fd >= 0) "configuration open refused"
      pure (Fd fd)) closeFd $ \fd -> do
    opened <- getFdStatus fd
    require (identity opened == identity before) "configuration changed before open"
    -- Only a duplicate transfers to a Handle; the verified descriptor remains
    -- open through both post-read custody checks.
    body <- readExact fd
    after <- getFdStatus fd
    named <- getSymbolicLinkStatus path
    require (identity after == identity before && identity named == identity before) "configuration changed during read"
    let digest = concatMap (\byte -> let h=showHex byte "" in replicate (2-length h) '0' ++ h) (B.unpack (SHA256.hash body))
    require (digest == expected && length expected == 64) "configuration hash differs"
    now <- monotonic
    either (ioError . userError) pure (decodeConfiguration now inherited body)

-- fdReadBuf keeps the verified descriptor's ownership with the caller.
readExact :: Fd -> IO B.ByteString
readExact fd = bracket (duplicateHandle fd) hClose $ \handle -> do
  body <- B.hGet handle 4097
  require (B.length body <= 4096) "configuration exceeds byte bound"
  pure body

duplicateHandle :: Fd -> IO Handle
duplicateHandle fd = do
  duplicate <- duplicateFd fd
  fdToHandle duplicate `onException` closeFd duplicate

foreign import ccall unsafe "dup" rawDup :: CInt -> IO CInt
duplicateFd :: Fd -> IO Fd
duplicateFd (Fd original) = do
  fd <- rawDup original
  require (fd >= 0) "configuration duplicate refused"
  pure (Fd fd)

receipt :: Configuration -> String -> IO ()
receipt config kind = do
  now <- monotonic
  pid <- getProcessID
  let owner=configurationBinding config
      encoded=JObject [("schema",JNumber "1"),("kind",JString (T.pack kind)),
        ("nonce",JString (configurationNonce config)),("pid",JString (T.pack (show pid))),
        ("monotonicNs",JString (T.pack (show now))),
        ("binding",JObject [("lifetime",JString (I.renderCounter (I.lifetime owner))),
          ("session",JString (I.renderCounter (I.session owner))),
          ("frontend",JString (I.renderCounter (I.frontend owner)))]),
        ("nativeAcceptance",JBool False)]
  BC.putStrLn (TE.encodeUtf8 (renderJson encoded))

main :: IO ()
main = do
  args <- getArgs
  (path,digest,inherited) <- case args of
    [name,hash,deadline] -> case reads deadline of
      [(value,"")] | show (value :: Integer)==deadline -> pure (name,hash,value)
      _ -> ioError (userError "canonical original deadline required")
    _ -> ioError (userError "configuration path, hash and original deadline required")
  config <- secureConfiguration path digest inherited
  display <- captureDisplayEnvironment
  either (ioError . userError . T.unpack) (const (pure ())) display
  enterPrivateNetwork
  mapM_ (uncurry setEnv) [("GIO_USE_VFS","local"),("GSETTINGS_BACKEND","memory"),
    ("GTK_USE_PORTAL","0"),("NO_AT_BRIDGE","1"),("GTK_A11Y","none")]
  hSetBuffering stdout NoBuffering
  hSetBuffering stdin NoBuffering
  withCString "org.warlock.Ui011Opener" setProgramName
  let remaining = do
        now <- monotonic
        pure (fromInteger (max 0 (min 28000000 ((inherited-now) `div` 1000))))
  withPhysicalDefaultContextOwner remaining $ \owner -> do
    initialized <- gtkInit
    require (initialized /= 0) "GTK private display initialization failed"
    window <- windowNew
    require (window /= nullPtr) "GTK window allocation failed"
    void (refSink window)
    let dispose = windowDestroy window `finally` unref window
    (do
      withCString "Warlock UI011 independent opener" (windowTitle window)
      windowSize window 320 180
      mapped <- newIORef False
      closed <- newIORef False
      closing <- newIORef False
      errorSlot <- newIORef Nothing
      let guard action = mask_ $ do
            attempted <- try action
            case attempted of
              Left (problem :: SomeException) -> writeIORef errorSlot (Just (show problem))
              Right () -> pure ()
          onMap = guard $ do
            old <- readIORef mapped
            require (not old) "duplicate map refused"
            actual <- windowMapped window
            require (actual /= 0) "map receipt without mapped window"
            writeIORef mapped True
          onUnmap = guard $ do
            intentional <- readIORef closing
            require intentional "unexpected native opener close"
            writeIORef closed True
          onClose = guard $ readIORef closing >>= \intentional -> require intentional "unrequested native opener close"
      bracket (mask_ $ do
        mapPtr <- simpleCallback (\_ _ -> onMap)
        unmapPtr <- simpleCallback (\_ _ -> onUnmap) `onException` freeHaskellFunPtr mapPtr
        closePtr <- closeCallback (\_ _ -> mask_ (onClose >> pure 0))
          `onException` (freeHaskellFunPtr unmapPtr `finally` freeHaskellFunPtr mapPtr)
        let signals=[("map",castFunPtr mapPtr),("unmap",castFunPtr unmapPtr),("close-request",castFunPtr closePtr)]
        acquired <- newIORef [] `onException` mapM_ (freeHaskellFunPtr . snd) signals
        let disconnect (handler,_) = do
              connected <- signalConnected window handler
              when (connected /= 0) (disconnectSignal window handler)
            rollback = (readIORef acquired >>= mapM_ disconnect)
              `finally` mapM_ (freeHaskellFunPtr . snd) signals
        connections <- (mapM (\(name,callback) -> withCString name $ \signal -> do
            handler <- connectSignal window signal callback nullPtr nullFunPtr 0
            require (handler /= 0) "signal connection failed"
            modifyIORef' acquired ((handler,callback):)
            pure (handler,callback)) signals) `onException` rollback
        pure connections)
        (\connections -> mask_ $ mapM_ (\(handler,callback) -> do
          connected <- signalConnected window handler
          when (connected /= 0) (disconnectSignal window handler)
          freeHaskellFunPtr callback) connections) $ \_ -> do
          windowPresent window
          let command=TE.encodeUtf8 ("CLOSE "<>configurationNonce config<>"\n")
              check = do
                requirePhysicalDefaultContextOwner owner
                now <- monotonic
                require (now < inherited) "original opener deadline expired"
                issue <- readIORef errorSlot
                maybe (pure ()) (ioError . userError) issue
              pump = check >> void (contextIteration nullPtr 0) >> check
              awaitMap = do
                pump
                ready <- readIORef mapped
                if ready then receipt config "mapped" else threadDelay 1000 >> awaitMap
              awaitCommand buffer = do
                pump
                ready <- hReady stdin
                if not ready then threadDelay 1000 >> awaitCommand buffer else do
                  chunk <- B.hGetSome stdin (B.length command+1-B.length buffer)
                  require (not (B.null chunk)) "opener command EOF"
                  let next=buffer<>chunk
                  require (next `B.isPrefixOf` command) "opener command refused"
                  if next==command then do
                    duplicate <- hReady stdin
                    require (not duplicate) "extra opener command refused"
                    writeIORef closing True
                    windowClose window
                  else awaitCommand next
              awaitClose = do
                pump
                done <- readIORef closed
                if done then do
                  actual <- windowMapped window
                  require (actual == 0) "unmap did not retire native window"
                  receipt config "closed"
                else threadDelay 1000 >> awaitClose
          awaitMap
          awaitCommand B.empty
          awaitClose) `finally` dispose
