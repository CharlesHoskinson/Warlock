{-# LANGUAGE OverloadedStrings #-}
-- A regular FD supplied by a future reviewed resolver, not path authentication.
module Warlock.Platform.Descriptor (DescriptorFailure(..), observeRegular, observeRegularExact, observeAcquiredExact, readAcquiredExact) where
import qualified Crypto.Hash.SHA256 as SHA256
import Control.Exception (IOException, bracket, finally, mask, onException, try)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Numeric (showHex)
import System.IO (Handle, hClose)
import System.Posix.Files (deviceID, fileID, fileSize, getFdStatus, isRegularFile, modificationTimeHiRes, statusChangeTimeHiRes)
import System.Posix.IO (closeFd, fdToHandle)
import System.Posix.Types (Fd)

data DescriptorFailure = IoFailure | NotRegular | TooLarge | IdentityChanged | DeclaredSizeMismatch | DigestMismatch deriving (Eq, Show)

-- Consumes the descriptor: ownership transfers to this function. It checks held
-- file identity before and after a bounded read and reports close errors. This
-- DOES NOT prove the caller opened the declared path, that no writer changed and
-- restored content between checks, or loader/runtime binding to this descriptor.
observeRegular :: Fd -> Integer -> B.ByteString -> IO (Either DescriptorFailure ())
observeRegular fd maxBytes expected = fmap (fmap (const ())) (observeSized fd Nothing maxBytes expected)

-- Consumes the FD and checks declared size inside the same owned snapshot as SHA.
observeRegularExact :: Fd -> Integer -> Integer -> B.ByteString -> IO (Either DescriptorFailure ())
observeRegularExact fd expectedSize maxBytes expected = fmap (fmap (const ())) (observeSized fd (Just expectedSize) maxBytes expected)

observeSized :: Fd -> Maybe Integer -> Integer -> B.ByteString -> IO (Either DescriptorFailure B.ByteString)
observeSized fd expectedSize maxBytes expected = do
 result <- try (bracket (fdToHandle fd `onException` closeFd fd) hClose (readOwned fd expectedSize maxBytes expected)) :: IO (Either IOException (Either DescriptorFailure B.ByteString))
 pure (either (const (Left IoFailure)) id result)

readOwned :: Fd -> Maybe Integer -> Integer -> B.ByteString -> Handle -> IO (Either DescriptorFailure B.ByteString)
readOwned fd expectedSize maxBytes expected handle = do
 before <- getFdStatus fd
 if not (isRegularFile before) then pure (Left NotRegular)
 else if maxBytes < 0 || maxBytes > 67108864 || toInteger (fileSize before) > maxBytes then pure (Left TooLarge)
 else if maybe False (/= toInteger (fileSize before)) expectedSize then pure (Left DeclaredSizeMismatch)
 else do
  bytes <- readBounded handle maxBytes [] 0
  after <- getFdStatus fd
  let same = deviceID before == deviceID after && fileID before == fileID after && fileSize before == fileSize after && modificationTimeHiRes before == modificationTimeHiRes after && statusChangeTimeHiRes before == statusChangeTimeHiRes after
  pure $ case bytes of
   Left failure -> Left failure
   Right content | not same || toInteger (B.length content) /= toInteger (fileSize after) -> Left IdentityChanged
                 | hexDigest (SHA256.hash content) /= expected -> Left DigestMismatch
                 | otherwise -> Right content

readBounded :: Handle -> Integer -> [B.ByteString] -> Integer -> IO (Either DescriptorFailure B.ByteString)
readBounded handle limit chunks count = do
 chunk <- B.hGetSome handle 65536
 let total = count + toInteger (B.length chunk)
 if total > limit then pure (Left TooLarge)
 else if B.null chunk then pure (Right (B.concat (reverse chunks)))
 else readBounded handle limit (chunk:chunks) total

hexDigest :: B.ByteString -> B.ByteString
hexDigest = C.pack . concatMap byteHex . B.unpack
 where byteHex n = let digits = showHex n "" in if length digits == 1 then '0':digits else digits

-- Acquires the duplicate and installs its consuming handle owner without an
-- unmasked gap. The hook runs only after ownership is installed; production
-- passes a no-op. Read and test hook run with the caller's masking state.
observeAcquiredExact :: IO Fd -> (Fd -> IO ()) -> (Fd -> IO ()) -> Integer -> Integer -> B.ByteString -> IO (Either DescriptorFailure ())
observeAcquiredExact acquire beforeInstall hook expectedSize maxBytes expected =
 fmap (fmap (const ())) (readAcquiredExact acquire beforeInstall hook (const (pure ())) expectedSize maxBytes expected)

-- Internal hook is a test seam, never exposed by the public resolver facade.
-- A success value is returned only after hClose succeeds; async exceptions propagate.
readAcquiredExact :: IO Fd -> (Fd -> IO ()) -> (Fd -> IO ()) -> (Fd -> IO ()) -> Integer -> Integer -> B.ByteString -> IO (Either DescriptorFailure B.ByteString)
readAcquiredExact acquire beforeInstall hook beforeClose expectedSize maxBytes expected = do
 result <- try (mask $ \restore -> do
  fd <- acquire
  beforeInstall fd `onException` closeFd fd
  handle <- fdToHandle fd `onException` closeFd fd
  restore (do hook fd; content <- readOwned fd (Just expectedSize) maxBytes expected handle; beforeClose fd; pure content) `finally` hClose handle) :: IO (Either IOException (Either DescriptorFailure B.ByteString))
 pure (either (const (Left IoFailure)) id result)
