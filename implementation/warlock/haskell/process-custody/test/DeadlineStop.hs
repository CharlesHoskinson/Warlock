{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Concurrent (forkIO, newEmptyMVar, putMVar, takeMVar, threadDelay)
import Control.Monad (unless)
import Data.IORef (newIORef, readIORef, writeIORef)
import System.Directory (doesFileExist, getTemporaryDirectory, removeFile)
import System.Environment (getArgs)
import System.IO (IOMode(ReadMode), hClose, openFile, openTempFile)
import Warlock.Capture.Process.Internal

check :: String -> Bool -> IO ()
check label value = unless value (ioError (userError label))

newMarker :: IO FilePath
newMarker = do
 dir <- getTemporaryDirectory
 (path, handle) <- openTempFile dir "owned-term-ready"
 hClose handle
 removeFile path
 pure path

awaitMarker :: FilePath -> Int -> IO ()
awaitMarker _ 0 = ioError (userError "child readiness missing")
awaitMarker path n = do
 ready <- doesFileExist path
 unless ready (threadDelay 10000 >> awaitMarker path (n - 1))

main :: IO ()
main = do
 let sample = 100000000000
     parse = deadlineFromAbsoluteNsAt sample
 check "inclusive exact 30 seconds" (case parse "130000000000" of Right d -> deadlineAbsoluteNs d == "130000000000"; _ -> False)
 check "one nanosecond beyond refused" (parse "130000000001" == Left BadArguments)
 check "equal current expired" (parse "100000000000" == Left TimedOut)
 check "minimal future retained" (case parse "100000000001" of Right d -> deadlineAbsoluteNs d == "100000000001"; _ -> False)
 check "maximum word not a wildcard" (parse "18446744073709551615" == Left BadArguments)
 check "syntax and integer overflow" (all ((== Left BadArguments) . parse) ["", "0", "-1", "+1", "01", " 1", "1 ", "1x", "18446744073709551616"])
 original <- deadlineAfter 5000000 >>= either (ioError . userError . show) pure
 imported <- deadlineFromAbsoluteNs (deadlineAbsoluteNs original)
 check "live original D not renewed" (imported == Right original)
 args <- getArgs
 case args of
  [child] -> do
   escaped <- newIORef Nothing
   owner <- newOwner
   marker <- newMarker
   deadline <- deadlineAfter 5000000 >>= either (ioError . userError . show) pure
   input <- openFile "/dev/null" ReadMode
   outcome <- runSelectedDetailed owner (selectedFixture child [marker] input) 4096 deadline $ \session -> do
    writeIORef escaped (Just session)
    awaitMarker marker 200
    first <- requestGracefulStop session
    second <- requestGracefulStop session
    check "one TERM request" (first == Right () && second == Left StopAlreadyAttempted)
    awaitLeader session
   check "owned child exited successfully" (case selectedOperation outcome of Right captured -> output captured == "READY\n"; _ -> False)
   state <- status owner
   check "owner settled" (state == Available)
   removeFile marker
   old <- readIORef escaped
   case old of
    Nothing -> ioError (userError "session missing")
    Just session -> do
     stale <- requestGracefulStop session
     check "escaped session cannot signal" (stale == Left SessionClosed)
   failureOwner <- newOwner
   failureMarker <- newMarker
   failureDeadline <- deadlineAfter 5000000 >>= either (ioError . userError . show) pure
   failureInput <- openFile "/dev/null" ReadMode
   failure <- runSelectedFixtureHook failureOwner (selectedFixture child [failureMarker] failureInput) 4096 failureDeadline (\session -> do
    awaitMarker failureMarker 200
    one <- requestGracefulStop session
    two <- requestGracefulStop session
    check "uncertain request is never retried" (one == Left SpawnOrIO && two == Left StopAlreadyAttempted)
    pure (Left SpawnOrIO)) (\stage -> if stage == "graceful-before-signal" then ioError (userError "injected pre-signal fault") else pure ())
   check "injected stop failure not success" (case failure of Left _ -> True; Right _ -> False)
   removeFile failureMarker
   closingMarker <- newMarker
   entered <- newEmptyMVar
   release <- newEmptyMVar
   requestResult <- newEmptyMVar
   closingOwner <- newOwner
   closingDeadline <- deadlineAfter 5000000 >>= either (ioError . userError . show) pure
   closingInput <- openFile "/dev/null" ReadMode
   _ <- runSelectedFixtureHook closingOwner (selectedFixture child [closingMarker] closingInput) 4096 closingDeadline (\session -> do
    awaitMarker closingMarker 200
    _ <- forkIO (requestGracefulStop session >>= putMVar requestResult)
    takeMVar entered
    _ <- forkIO (threadDelay 100000 >> putMVar release ())
    pure (Right ())) (\stage -> if stage == "graceful-before-signal" then putMVar entered () >> takeMVar release else pure ())
   closingResult <- takeMVar requestResult
   check "inflight signal cannot report success after scope closes" (closingResult == Left SessionClosed)
   closingState <- status closingOwner
   check "owner settles after inflight scope drain" (closingState == Available)
   removeFile closingMarker
  _ -> ioError (userError "expected child executable path")
