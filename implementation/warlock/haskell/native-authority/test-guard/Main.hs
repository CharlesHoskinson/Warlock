{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Exception (AsyncException(ThreadKilled),SomeException,fromException,throwIO,try)
import Control.Monad (unless)
import Data.IORef (newIORef,modifyIORef',readIORef)
import qualified Data.Text as T
import System.Directory (createDirectory,renameFile)
import System.Environment (getArgs)
import System.FilePath ((</>))
import System.Posix.Files (setFileMode,getFdStatus,deviceID,fileID)
import System.Posix.IO (OpenMode(ReadOnly),openFd,defaultFileFlags,closeFd)
import qualified Warlock.Native.Cancellation.HostGuard as G
import Warlock.Protocol.Identity (parseCounter)

check :: String -> Bool -> IO ()
check label ok = unless ok (ioError (userError label))
right :: Show e => Either e a -> IO a
right = either (ioError . userError . show) pure
guardFor :: FilePath -> IO G.HostGuard
guardFor path = do
 zero <- right (parseCounter True "0")
 guard <- G.newHostGuard zero
 fd <- openFd path ReadOnly defaultFileFlags
 accepted <- G.offerNamespace guard fd
 unless accepted (closeFd fd >> ioError (userError "namespace offer refused"))
 pure guard
main :: IO ()
main = do
 args <- getArgs
 root <- case args of [p] -> pure p; _ -> ioError (userError "owned fixture root required")
 let path = root </> "host-guard"
 createDirectory path
 setFileMode path 0o700
 a <- guardFor path
 b <- guardFor path
 calls <- newIORef (0 :: Int)
 result <- G.withHostGuard a $ \lease -> do
  modifyIORef' calls (+1)
  namespace <- G.withNamespace lease $ \fd -> do
   status <- getFdStatus fd
   pure (toInteger (deviceID status),toInteger (fileID status))
  check "borrow actual namespace identity" (namespace == Right (G.guardNamespaceIdentity lease))
  nested <- G.withHostGuard a (\_ -> pure ())
  check "same-object nested guard is busy" (nested == Left G.Busy)
  contended <- G.withHostGuard b (\_ -> modifyIORef' calls (+100))
  check "different open description sees actual kernel lock" (contended == Left G.Busy)
  retire <- G.retireHostGuard a
  check "active lease excludes retirement" (retire == Left G.Busy)
  pure (G.guardGeneration lease)
 _ <- right result
 observed <- readIORef calls
 check "only owning callback ran" (observed == 1)
 after <- G.withHostGuard b (\_ -> pure True)
 check "kernel lock released after callback" (after == Right True)
 interrupted <- try (G.withHostGuard a (\_ -> throwIO ThreadKilled)) :: IO (Either SomeException (Either G.GuardError ()))
 check "original async propagated" (case interrupted of
  Left err -> case fromException err of Just ThreadKilled -> True; _ -> False
  Right _ -> False)
 status <- G.guardStatus a
 check "failed operation quarantined with handles retained" (G.guardPhase status == G.Quarantined && G.namespaceState status == G.Retained && G.lockHandleState status == G.Retained && not (G.lockHeld status))
 failures <- G.guardFailures a
 check "original exception retained" (any (\(origin,err) -> origin == G.OperationFailure && (case fromException err of Just ThreadKilled -> True; _ -> False)) failures)
 released <- G.withHostGuard b (\_ -> pure True)
 check "async operation still unlocks actual kernel guard" (released == Right True)
 denied <- G.withHostGuard a (\_ -> pure ())
 check "quarantined owner cannot resume writes" (denied == Left G.Unavailable)
 c <- guardFor path
 _ <- G.withHostGuard c (\_ -> pure ()) >>= right
 renameFile (path </> "host-writer.lock") (path </> "old-host-writer.lock")
 writeFile (path </> "host-writer.lock") ""
 setFileMode (path </> "host-writer.lock") 0o600
 wrong <- G.withHostGuard c (\_ -> modifyIORef' calls (+100))
 check "replaced lock name refuses exact callback" (wrong == Left G.IdentityChanged)
 count <- readIORef calls
 check "replacement callback never ran" (count == 1)
 forGuards [a,b,c]
 putStrLn (T.unpack "host guard component controls complete")
 where
  forGuards [] = pure ()
  forGuards (guard:rest) = do
   status <- G.retireHostGuard guard >>= right
   check "independent descriptors closed" (G.namespaceState status == G.ConfirmedClosed && G.lockHandleState status == G.ConfirmedClosed && G.guardPhase status == G.Retired)
   again <- G.retireHostGuard guard >>= right
   check "retirement idempotent" (again == status)
   forGuards rest
