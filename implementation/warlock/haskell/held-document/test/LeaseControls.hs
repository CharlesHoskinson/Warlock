{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Exception (AsyncException(..),finally,throwIO,try)
import Control.Monad (forM_,unless,when)
import qualified Data.ByteString.Char8 as B
import Data.IORef (newIORef,readIORef,writeIORef)
import System.Directory (doesFileExist,removeFile,renameFile)
import System.Environment (getArgs)
import System.FilePath ((</>))
import System.Posix.Files (deviceID,fileID,getFileStatus)
import qualified Warlock.Platform.Executable as Executable
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
  -- All currently public role constructors. This is metadata on the exact
  -- real resolver-selected held object, not thread/peer/native authority.
  forM_ [Executable.UiImage] $ \role -> do
   good <- Executable.newExecutableLease
   e <- Executable.acquireExecutableLease good root pins (B.pack name) [] size digest role
   st <- Executable.executableLeaseState good
   assert (e == Right () && st == Executable.ReadyLease) "validated issuance refused"
   issued <- Executable.issueReadyExecutable good
   case issued of
    Nothing -> ioError (userError "issue failed")
    Just (held,_,issuedRole) -> do
     assert (issuedRole == role) "issued role changed"
     liveRole <- Executable.observeHeldRole held
     assert (liveRole == Right role) "live held role changed"
     again <- Executable.issueReadyExecutable good
     assert (case again of Nothing -> True; _ -> False) "second issue"
     borrowed <- Executable.borrowHeld held
     case borrowed of
      Left x -> ioError (userError (show x))
      Right (_,release) -> do
       (do
         borrowedRole <- Executable.observeHeldRole held
         assert (borrowedRole == Right role) "borrowed live held role changed"
         busy <- Executable.retireHeld held
         assert (busy == Left Executable.LeaseBusy) "borrow did not retain"
         busyRole <- Executable.observeHeldRole held
         assert (busyRole == Right role) "busy retirement changed live held role"
         release; release
        ) `finally` release
       releasedRole <- Executable.observeHeldRole held
       assert (releasedRole == Right role) "released borrow changed live held role"
       retired <- Executable.retireExecutableLease good
       assert (retired == Right ()) "retirement via retained moved owner"
       closedRole <- Executable.observeHeldRole held
       assert (closedRole == Left Executable.LeaseClosed) "retired held role remained observable"
       lateBorrow <- Executable.borrowHeld held
       assert (case lateBorrow of Left Executable.LeaseClosed -> True; _ -> False) "retired held borrow admitted"
       later <- Executable.retireHeld held
       assert (later == Left Executable.LeaseClosed) "duplicate close"
 case result of Left e -> ioError (userError (show e)); Right () -> pure ()
