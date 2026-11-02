module Main (main) where

import Warlock.Backend.Store (acquisitionFailureControls)
import System.IO (BufferMode(NoBuffering),hSetBuffering,stdout)

main :: IO ()
main = do
  hSetBuffering stdout NoBuffering
  acquisitionFailureControls
