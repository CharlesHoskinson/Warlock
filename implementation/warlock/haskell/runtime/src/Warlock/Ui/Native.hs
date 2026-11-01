{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- The approved UI owner alone owns fd0. Browser content never obtains this FD.
module Warlock.Ui.Native
 (Native,adoptNative,nativePeerPid,sendCommit,receiveGateway,retireNative) where
import Control.Concurrent.MVar
import Control.Exception (SomeException,SomeAsyncException,fromException,mask_,onException,throwIO,try)
import Control.Monad (unless)
import qualified Data.ByteString as B
import Data.Text (Text)
import qualified Data.Text as T
import qualified Network.Socket as S
import qualified Network.Socket.ByteString as N
import System.Posix.IO (FdOption(CloseOnExec,NonBlockingRead),setFdOption)
import System.Posix.Types (Fd(..))
import System.Timeout (timeout)
import Warlock.Capture.Process.Bootstrap (AdmissionDeadline,remainingMicros)
import Warlock.Protocol.Codec (decodeClientCheckedWith,desktopProfile,checkedDesktopCommit)
import qualified Warlock.Protocol.Desktop as D
import qualified Warlock.Protocol.Framing as F
import Warlock.Protocol.Identity (Binding)

data CloseState = Open | Closed | Uncertain deriving Eq
data Native = Native S.Socket Int Binding AdmissionDeadline (MVar CloseState) (MVar ())
nativePeerPid :: Native -> Int
nativePeerPid (Native _ pid _ _ _ _) = pid

adoptNative :: Binding -> AdmissionDeadline -> IO Native
adoptNative binding deadline = mask_ $ do
 -- This runs before GTK can create any engine subprocess.
 setFdOption (Fd 0) CloseOnExec True
 socket <- S.mkSocket 0
 (do
  -- mkSocket adopts an external descriptor without changing its status flags.
  -- The owner is deliberately nonthreaded; a blocking recv would stop every
  -- listener, engine callback and deadline while waiting for its first frame.
  setFdOption (Fd 0) NonBlockingRead True
  peer <- S.getPeerName socket
  unless (case peer of S.SockAddrUnix _ -> True; _ -> False) (ioError (userError "native endpoint is not a Unix peer"))
  credentials <- S.getPeerCredential socket
  pid <- case credentials of (Just value,Just _,Just _) | value>0 -> pure (fromIntegral value); _ -> ioError (userError "native peer credentials missing")
  Native socket pid binding deadline <$> newMVar Open <*> newMVar ()) `onException` S.close socket

bounded :: AdmissionDeadline -> IO a -> IO a
bounded deadline action = do
 left <- remainingMicros deadline
 unless (left>0) (ioError (userError "original UI deadline expired"))
 result <- timeout left action
 maybe (ioError (userError "original UI deadline expired")) pure result

sendCommit :: Native -> B.ByteString -> IO (Either Text D.DesktopCommit)
sendCommit (Native socket _ binding deadline closed writer) raw =
 case decodeClientCheckedWith desktopProfile raw >>= maybe (Left "not a desktop commit") Right . checkedDesktopCommit of
  Left refusal -> pure (Left refusal)
  Right checked ->
   if not (all ((==binding) . D.requestBinding) (D.commitRequests checked)) then pure (Left "foreign commit binding") else
    case F.desktopCommitPrefix raw of
     Left refusal -> pure (Left (T.pack (show refusal)))
     Right framed -> withMVar writer $ \_ -> do
      ended <- readMVar closed
      if ended/=Open then pure (Left "native endpoint retired") else bounded deadline (N.sendAll socket framed) >> pure (Right checked)

receiveGateway :: Native -> IO B.ByteString
receiveGateway (Native socket _ binding deadline closed _) = bounded deadline $ do
 ended <- readMVar closed
 unless (ended==Open) (ioError (userError "native endpoint retired"))
 prefix <- exact 4
 count <- either (ioError . userError . show) pure (F.desktopGatewayHeaderLength prefix)
 raw <- exact count
 reply <- either (ioError . userError . T.unpack) pure (D.decodeDesktopGateway raw)
 unless (D.replyBinding reply==binding) (ioError (userError "foreign native gateway binding"))
 pure raw
 where
  exact count = loop count []
  loop 0 parts = pure (B.concat (reverse parts))
  loop count parts = do
   part <- N.recv socket (min 65536 count)
   unless (not (B.null part)) (ioError (userError "native gateway EOF"))
   loop (count-B.length part) (part:parts)

retireNative :: Native -> IO Bool
retireNative (Native socket _ _ _ closed _) = mask_ $ do
 outcome <- modifyMVar closed $ \state -> case state of
  Closed -> pure (Closed,Right True)
  Uncertain -> pure (Uncertain,Right False)
  Open -> do
   result <- try (S.close socket) :: IO (Either SomeException ())
   pure $ case result of Right () -> (Closed,Right True); Left err -> (Uncertain,Left err)
 case outcome of
  Right clean -> pure clean
  Left err -> case fromException err :: Maybe SomeAsyncException of
   Just _ -> throwIO err
   Nothing -> pure False
