{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Exception (AsyncException(..),finally,throwIO,try)
import Control.Monad (unless,when)
import qualified Data.ByteString.Char8 as B
import Data.IORef (newIORef,readIORef,writeIORef)
import System.Directory (doesFileExist,removeFile,renameFile)
import System.Environment (getArgs)
import System.FilePath ((</>))
import System.Posix.Files (deviceID,fileID,getFileStatus)
import Warlock.Platform.Executable.Internal
import Warlock.Platform.Resolver.Internal (Identity(..),Kind(..),Pin(..),ResolveError,withRoot,noHooks)

assert :: Bool -> String -> IO ()
assert ok message = unless ok (ioError (userError message))
main :: IO ()
main = do
 args <- getArgs
 case args of
  [directory,name,sizeText,digest] -> case reads sizeText of
   [(size,"")] -> run directory name size (B.pack digest)
   _ -> ioError (userError "invalid size")
  _ -> ioError (userError "expected disposable root, name, size, sha256")
run :: FilePath -> FilePath -> Integer -> B.ByteString -> IO ()
run directory name size digest = do
 rootStatus <- getFileStatus directory
 itemStatus <- getFileStatus (directory </> name)
 let ident st = Identity (toInteger (deviceID st)) (toInteger (fileID st))
     pins = [Pin (B.pack ('/':name)) (ident itemStatus) Regular]
     checkDenied candidate = do st <- executableLeaseState candidate; assert (st /= ReadyLease) "unexpected Ready"
 result <- withRoot (B.pack directory) (ident rootStatus) $ \root -> do
  badDigest <- newExecutableLease
  a <- acquireExecutableLease badDigest root pins (B.pack name) [] size (B.replicate 64 '0') UiImage
  assert (either (const True) (const False) a) "wrong hash admitted"; checkDenied badDigest
  badSize <- newExecutableLease
  b <- acquireExecutableLease badSize root pins (B.pack name) [] (size+1) digest UiImage
  assert (either (const True) (const False) b) "wrong size admitted"; checkDenied badSize
  badIdentity <- newExecutableLease
  let wrongPins = [Pin (B.pack ('/':name)) (Identity 0 0) Regular]
  c <- acquireExecutableLease badIdentity root wrongPins (B.pack name) [] size digest UiImage
  assert (either (const True) (const False) c) "wrong identity admitted"; checkDenied badIdentity
  changed <- newIORef False
  let original = directory </> name; saved = original ++ ".fixture-saved"
      substitute = renameFile original saved >> writeIORef changed True >> B.writeFile original "replacement"
      restore = do
       wasChanged <- readIORef changed
       when wasChanged $ do
        exists <- doesFileExist original
        when exists (removeFile original)
        renameFile saved original
  pending <- newExecutableLease
  d <- acquireExecutableLeaseWithHooks pending root pins (B.pack name) [] size digest UiImage noHooks substitute `finally` restore
  pendingState <- executableLeaseState pending
  assert (either (const True) (const False) d && pendingState == ClosedLease) "post-consumer substitution or pending close"
  cancelled <- newExecutableLease
  interrupted <- try (acquireExecutableLeaseWithHooks cancelled root pins (B.pack name) [] size digest UiImage noHooks (throwIO ThreadKilled)) :: IO (Either AsyncException (Either ResolveError ()))
  cancelledState <- executableLeaseState cancelled
  assert (case interrupted of Left ThreadKilled -> cancelledState == ClosedLease; _ -> False) "pending async custody"
  good <- newExecutableLease
  e <- acquireExecutableLease good root pins (B.pack name) [] size digest UiImage
  st <- executableLeaseState good
  assert (e == Right () && st == ReadyLease) "validated issuance refused"
  issued <- issueReadyExecutable good
  case issued of
   Nothing -> ioError (userError "issue failed")
   Just (held,_,_) -> do
    again <- issueReadyExecutable good
    assert (case again of Nothing -> True; _ -> False) "second issue"
    borrowed <- borrowHeld held
    case borrowed of
     Left x -> ioError (userError (show x))
     Right (_,release) -> do
      busy <- retireHeld held
      assert (busy == Left LeaseBusy) "borrow did not retain"
      release; release
      retired <- retireExecutableLease good
      assert (retired == Right ()) "retirement via retained moved owner"
      later <- retireHeld held
      assert (later == Left LeaseClosed) "duplicate close"
 case result of Left e -> ioError (userError (show e)); Right () -> pure ()
