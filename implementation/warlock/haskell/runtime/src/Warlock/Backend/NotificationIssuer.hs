{-# LANGUAGE ScopedTypeVariables #-}
{-# LANGUAGE OverloadedStrings #-}
module Warlock.Backend.NotificationIssuer
 (NotificationGeneration,NotificationIssuer,IssuerFailure,issuerFailureCustody,IssuerInterrupted(..),newIssuer,provisionIssuer,reserveGeneration,retireIssuer,generationText) where
import Control.Concurrent.MVar
import Control.Exception (Exception(..),SomeException,SomeAsyncException,asyncExceptionFromException,asyncExceptionToException,fromException,mask,throwIO,try)
import Data.Text (Text)
import qualified Data.Text as T
import Data.Word (Word64)
import Warlock.Capture.Process.Bootstrap (AdmissionDeadline,ToolError,deadlineFromAbsoluteNs,remainingMicros)
import Warlock.Backend.Store

data NotificationGeneration = NotificationGeneration Word64 deriving Eq
generationText :: NotificationGeneration -> Text
generationText (NotificationGeneration value) = T.pack (show value)
data State = Idle | Holding StoreOwner NotificationLifetime | Poisoned StoreOwner [StoreOwner] | Closed
data NotificationIssuer = NotificationIssuer DirectoryPin (Either ToolError AdmissionDeadline) (MVar State)
instance Eq NotificationIssuer where
 NotificationIssuer _ _ a == NotificationIssuer _ _ b = a==b
instance Show NotificationIssuer where show _ = "<notification-issuer>"
data IssuerFailure = IssuerFailure Text NotificationIssuer
instance Show IssuerFailure where show _ = "notification issuer unavailable or uncertain"
issuerFailureCustody :: IssuerFailure -> NotificationIssuer
issuerFailureCustody (IssuerFailure _ issuer) = issuer
-- Async classification is retained and the original exception and issuer are accessible.
data IssuerInterrupted = IssuerInterrupted SomeException NotificationIssuer
instance Show IssuerInterrupted where show _ = "notification issuer interrupted; custody retained"
instance Exception IssuerInterrupted where
 toException = asyncExceptionToException
 fromException = asyncExceptionFromException

newIssuer :: DirectoryPin -> String -> IO NotificationIssuer
newIssuer pin absolute = do
 deadline <- deadlineFromAbsoluteNs absolute
 NotificationIssuer pin deadline <$> newMVar Idle
provisionIssuer :: NotificationIssuer -> IO (Either IssuerFailure ())
provisionIssuer issuer = use issuer True provisionNotificationSlot
reserveGeneration :: NotificationIssuer -> IO (Either IssuerFailure NotificationGeneration)
reserveGeneration issuer = fmap (fmap NotificationGeneration) (use issuer False reserveNotificationSlot)

use :: NotificationIssuer -> Bool -> (StoreOwner -> DirectoryPin -> IO a) -> IO (Either IssuerFailure a)
use issuer@(NotificationIssuer pin selected gate) provisioning operation = mask $ \restore -> do
 result <- modifyMVarMasked gate $ \state -> case state of
  Closed -> pure (Closed,Right (Left "notification issuer closed"))
  Poisoned life others -> pure (Poisoned life others,Right (Left "notification issuer poisoned"))
  _ -> do
   life <- case state of Holding owner _ -> pure owner; _ -> newStoreOwner
   transaction <- newStoreOwner
   checker <- newStoreOwner
   let originalLease = case state of Holding _ lease -> Just lease; _ -> Nothing
   attempted <- try (restore (do
     deadline <- either (ioError . userError . show) pure selected
     before <- remainingMicros deadline
     if before<=0 then ioError (userError "notification deadline expired") else pure ()
     lease0 <- case originalLease of
      Just lease -> pure (Just lease)
      Nothing | provisioning -> pure Nothing
      Nothing -> Just <$> acquireNotificationLifetime life pin
     case lease0 of Just lease -> checkNotificationLifetime checker pin lease; Nothing -> pure ()
     value <- operation transaction pin
     lease <- case lease0 of Just valueLease -> pure valueLease; Nothing -> acquireNotificationLifetime life pin
     after <- remainingMicros deadline
     if after<=0 then ioError (userError "notification deadline expired after operation") else pure (lease,value)))
   settled <- try (retireStoreOwnerIfSettled transaction)
   validated <- case (attempted,settled) of
    (Right (lease,_),Right True) -> try (restore (checkNotificationLifetime checker pin lease))
    _ -> pure (Right ())
   checked <- try (retireStoreOwnerIfSettled checker)
   final <- case (attempted,settled,validated,checked) of
    (Right _,Right True,Right (),Right True) -> try (case selected of Left _ -> pure False; Right d -> (>0) <$> remainingMicros d)
    _ -> pure (Right False)
   let failures = [e | Left e <- [fmap (const ()) attempted,fmap (const ()) settled,validated,fmap (const ()) checked,fmap (const ()) final]]
       asyncs = [e | e <- failures, Just _ <- [fromException e :: Maybe SomeAsyncException]]
   case (attempted,settled,validated,checked,final) of
    (Right (lease,value),Right True,Right (),Right True,Right True) -> pure (Holding life lease,Right (Right value))
    _ -> case asyncs of
     e:_ -> pure (Poisoned life [transaction,checker],Left e)
     [] -> pure (Poisoned life [transaction,checker],Right (Left "notification issuer unavailable or uncertain"))
 case result of
  Left problem -> throwIO (IssuerInterrupted problem issuer)
  Right (Left message) -> pure (Left (IssuerFailure message issuer))
  Right (Right value) -> pure (Right value)

retireIssuer :: NotificationIssuer -> IO Bool
retireIssuer (NotificationIssuer _ _ gate) = modifyMVarMasked gate $ \state -> case state of
 Closed -> pure (Closed,True)
 Idle -> pure (Closed,True)
 Holding life lease -> do
  done <- retireStoreOwner life
  if done then pure (Closed,True) else pure (Holding life lease,False)
 Poisoned life others -> do
  settled <- mapM retireStoreOwnerIfSettled others
  if not (and settled) then pure (Poisoned life others,False) else do
   done <- retireStoreOwner life
   if done then pure (Closed,True) else pure (Poisoned life others,False)
