{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Fixed schema1 identity store. A Saved reply requires completed real IO.
module Warlock.Backend.PinStore
 (PinStore,newPinStore,readPins,savePins,retirePinStore,retirePinStoreIfSettled) where
import Control.Exception (SomeException,SomeAsyncException,fromException,throwIO,try)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.IORef (newIORef,readIORef)
import qualified Data.Set as Set
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import System.Posix.Types (Fd)
import Warlock.Backend.Store
import Warlock.Protocol.Desktop
import Warlock.Protocol.Identity (addCounter,parseCounter)
import Warlock.Protocol.StrictJson

data PinStore = PinStore DirectoryPin StoreOwner
newPinStore :: DirectoryPin -> IO PinStore
newPinStore pin = PinStore pin <$> newStoreOwner
retirePinStore :: PinStore -> IO Bool
retirePinStore (PinStore _ owner) = retireStoreOwner owner
retirePinStoreIfSettled :: PinStore -> IO Bool
retirePinStoreIfSettled (PinStore _ owner) = retireStoreOwnerIfSettled owner

decodeStored :: B.ByteString -> Either Text PinSnapshot
decodeStored bytes = do
 limits <- either (Left . T.pack . show) Right (bounds 16384 16)
 raw <- either (Left . T.pack . show) Right (decodeStrict limits bytes)
 fields <- either (Left . T.pack . show) Right (exactObject ["schema","revision","identities"] raw)
 if lookup "schema" fields/=Just (JNumber "1") then Left "unsupported pin storage schema" else pure ()
 -- Retain the shared identity/counter/UTF16/UTF8 validation authority.
 let keep=B.concat ["{\"revision\":",value "revision" fields,",\"identities\":",value "identities" fields,"}"]
 decodePinSnapshot keep
 where
  value key fields = case lookup key fields of
   Just (JString text) -> quote text
   Just (JArray entries) -> "["<>B.intercalate "," [case entry of JString text -> quote text; _ -> "null" | entry <- entries]<>"]"
   _ -> "null"
  quote text = TE.encodeUtf8 ("\""<>T.concatMap escape text<>"\"")
  escape '"'="\\\""
  escape '\\'="\\\\"
  escape char=T.singleton char -- Shared decoder rejects all control characters.

storedBytes :: PinSnapshot -> B.ByteString
storedBytes snapshot = "{\"schema\":1,"<>B.drop 1 (encodePinSnapshot snapshot)

readAt :: StoreOwner -> Fd -> IO PinSnapshot
readAt owner directory = do
 bytes <- readRegular owner True directory (C.pack "taskbar.json") 16384
 case bytes of
  Nothing -> do
   revision <- either (ioError . userError . show) pure (parseCounter False "1")
   either (ioError . userError . T.unpack) pure (pinSnapshot revision [])
  Just raw -> either (ioError . userError . T.unpack) pure (decodeStored raw)

readPins :: PinStore -> IO (Either Text PinSnapshot)
readPins (PinStore pin owner) = attempt $ runOwned owner $
 withPinnedDirectory owner True pin $ \directory -> withPinLock owner directory (readAt owner directory)

savePins :: PinStore -> Set.Set Text -> PinSnapshot -> IO (PinStatus,Maybe PinSnapshot)
savePins (PinStore pin owner) allowed proposal = do
 published <- newIORef False
 outcome <- attempt $ runOwned owner $ withPinnedDirectory owner True pin $ \directory -> withPinLock owner directory $ do
  old <- readAt owner directory
  let known=allowed `Set.union` Set.fromList (pinIdentities old)
      admissible=all (`Set.member` known) (pinIdentities proposal)
  if not admissible || pinRevision old/=pinRevision proposal || pinIdentities old==pinIdentities proposal then pure (PinRefused,Just old) else
   case addCounter (pinRevision old) 1 of
    Left _ -> pure (PinRefused,Just old)
    Right revision -> do
     saved <- either (ioError . userError . T.unpack) pure (pinSnapshot revision (pinIdentities proposal))
     replacePins owner directory published (storedBytes saved)
     pure (PinSaved,Just saved)
 case outcome of
  Right result -> pure result
  Left _ -> do
   uncertain <- readIORef published
   pure (if uncertain then (PinUnknown,Nothing) else (PinRefused,Nothing))

attempt :: IO a -> IO (Either Text a)
attempt action = do
 result <- try action
 case result of
  Left (problem :: SomeException) -> case fromException problem :: Maybe SomeAsyncException of
   Just _ -> throwIO problem
   Nothing -> pure (Left "pin storage unavailable")
  Right value -> pure (Right value)
