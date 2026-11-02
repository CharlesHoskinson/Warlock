module Main (main) where
import Control.Concurrent (threadDelay)
import Control.Monad (forever)
import System.Exit (ExitCode(..))
import System.Environment (getArgs)
import System.IO (hFlush, stdout)
import System.Posix.Files (fileExist)
import System.Posix.Process (exitImmediately)
import System.Posix.Signals (Handler(Catch), installHandler, sigTERM)

waitUntilRemoved :: FilePath -> Int -> IO ()
waitUntilRemoved _ 0 = pure ()
waitUntilRemoved path remaining = do
 exists <- fileExist path
 if not exists then pure ()
 else threadDelay 10000 >> waitUntilRemoved path (remaining - 1)

main :: IO ()
main = do
 _ <- installHandler sigTERM (Catch (exitImmediately ExitSuccess)) Nothing
 args <- getArgs
 case args of
  [marker] -> do
   writeFile marker "ready"
   putStrLn "READY"
   hFlush stdout
   forever (threadDelay 1000000)
  [marker, "exit-soon"] -> do
   writeFile marker "ready"
   putStrLn "READY"
   hFlush stdout
   threadDelay 80000
   exitImmediately (ExitFailure 7)
  [marker, "exit-when-removed"] -> do
   writeFile marker "ready"
   putStrLn "READY"
   hFlush stdout
   waitUntilRemoved marker 500
   exitImmediately ExitSuccess
  _ -> exitImmediately (ExitFailure 2)
