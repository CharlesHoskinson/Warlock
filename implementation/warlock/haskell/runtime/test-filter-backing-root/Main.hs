{-# LANGUAGE OverloadedStrings #-}
module Main (main) where

import Control.Exception (IOException, try)
import Control.Monad (unless)
import qualified Data.ByteString as B
import Data.Bits ((.&.))
import qualified Data.Text as T
import System.Directory (createDirectory, doesPathExist)
import System.Environment (getArgs)
import System.FilePath ((</>))
import System.Posix.Files
  (createLink, createSymbolicLink, deviceID, fileID, fileMode, fileOwner,
   getSymbolicLinkStatus, isDirectory, setFileMode)
import System.Posix.User (getEffectiveUserID)
import Warlock.Capture.Process.Bootstrap (deadlineAfter)
import qualified Warlock.Ui.EngineProtocol as Protocol
import Warlock.Ui.FilterBackingRoot

check :: String -> Bool -> IO ()
check name value = unless value (ioError (userError name))

main :: IO ()
main = do
  args <- getArgs
  check "fixed noargs fixture" (null args)
  deadline <- deadlineAfter 5000000 >>= either (ioError . userError . show) pure
  uid <- toInteger <$> getEffectiveUserID
  root <- newFilterBackingRoot deadline
  binding <- filterBackingBinding root
  let (encoded,dev,ino,owner) = Protocol.backingRootFields binding
      path = T.unpack encoded
      prefix = "/tmp/warlock-ui-backing-"
      suffix = drop (length prefix) path
  check "fixed unpredictable root" (take (length prefix) path == prefix
    && length suffix == 64 && all (`elem` ("0123456789abcdef" :: String)) suffix)
  status <- getSymbolicLinkStatus path
  check "actual private directory identity" (isDirectory status
    && fileMode status .&. 0o7777 == 0o700 && toInteger (fileOwner status) == uid
    && toInteger (deviceID status) == dev && toInteger (fileID status) == ino && owner == uid)
  inspectFilterBacking root >>= check "fresh actual descriptor/root valid"
  mapM_ (\role -> do
    createDirectory (path </> role)
    setFileMode (path </> role) 0o700
    B.writeFile (path </> role </> "cache") "literal-cache"
    setFileMode (path </> role </> "cache") 0o600) ["controller","bar","popup"]
  inspectFilterBacking root >>= check "three real roles/cache files valid"
  discardUnstartedBacking root
  exists <- doesPathExist path
  check "exact unstarted owned tree removed" (not exists)
  discardUnstartedBacking root
  stale <- inspectFilterBacking root
  check "retired owner cannot validate reused descriptor" (not stale)
  other <- newFilterBackingRoot deadline
  (otherPath,_,_,_) <- Protocol.backingRootFields <$> filterBackingBinding other
  check "independent random allocation" (otherPath /= encoded)
  discardUnstartedBacking other

  -- Negative roots remain explicitly uncertain. The protected fixture's /tmp
  -- namespace owns their lifetime; this is not a normal-engine cleanup claim.
  symlinkRoot <- newFilterBackingRoot deadline
  (symlinkPath,_,_,_) <- Protocol.backingRootFields <$> filterBackingBinding symlinkRoot
  createSymbolicLink "/tmp" (T.unpack symlinkPath </> "controller")
  linked <- inspectFilterBacking symlinkRoot
  check "symlink role refused" (not linked)
  denied <- try (discardUnstartedBacking symlinkRoot) :: IO (Either IOException ())
  check "symlink never deleted by cleanup" (case denied of Left _ -> True; Right () -> False)
  linkRemains <- doesPathExist (T.unpack symlinkPath </> "controller")
  check "outside symlink target untouched" linkRemains

  hardRoot <- newFilterBackingRoot deadline
  (hardPath,_,_,_) <- Protocol.backingRootFields <$> filterBackingBinding hardRoot
  let directory = T.unpack hardPath </> "controller"
  createDirectory directory
  setFileMode directory 0o700
  B.writeFile (directory </> "one") "do-not-unlink"
  setFileMode (directory </> "one") 0o600
  createLink (directory </> "one") (directory </> "two")
  multi <- inspectFilterBacking hardRoot
  check "multiple-link regular file refused" (not multi)
  hardDenied <- try (discardUnstartedBacking hardRoot) :: IO (Either IOException ())
  check "hardlink cleanup refusal retained" (case hardDenied of Left _ -> True; Right () -> False)
  contents <- B.readFile (directory </> "one")
  check "refused tree unchanged before deletion" (contents == "do-not-unlink")
  putStrLn "filter-backing-root-controls: complete"
