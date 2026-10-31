module Main (main) where
import Control.Concurrent (threadDelay)
import Control.Monad (forever)
import System.Exit (ExitCode(..))
import System.Environment (getArgs)
import System.IO (hFlush, stdout)
import System.Posix.Process (exitImmediately)
import System.Posix.Signals (Handler(Catch), installHandler, sigTERM)

main :: IO ()
main = do
 _ <- installHandler sigTERM (Catch (exitImmediately ExitSuccess)) Nothing
 args <- getArgs
 case args of
  [marker] -> writeFile marker "ready"
  _ -> exitImmediately (ExitFailure 2)
 putStrLn "READY"
 hFlush stdout
 forever (threadDelay 1000000)
