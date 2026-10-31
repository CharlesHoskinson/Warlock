{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Concurrent (threadDelay)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import System.Environment (getArgs)
import System.Exit (ExitCode(ExitFailure), exitFailure, exitWith)
import System.IO (stdout, stderr)
main :: IO ()
main = do
 args <- getArgs
 case args of
  ["--fixture","ok"] -> C.putStr "fixture-ok"
  ["--fixture","overflow"] -> B.hPut stdout (B.replicate 131072 65)
  ["--fixture","stderr-overflow"] -> B.hPut stderr (B.replicate 131072 66)
  ["--fixture","hang"] -> threadDelay 30000000
  ["--fixture","exit7"] -> exitWith (ExitFailure 7)
  ["--fixture","marker", path] -> C.writeFile path "spawned"
  _ -> exitFailure
