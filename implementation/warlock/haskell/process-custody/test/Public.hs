{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import System.Exit (exitFailure)
import Warlock.Capture.Process
main :: IO ()
main = do
 owner <- newOwner
 state <- status owner
 deadline <- deadlineAfter 1000000
 invalid <- runTool owner (Pactree "relative") ["pkg"] 1000 1000000
 case (state,deadline,invalid) of
  (Available,Right _,Left BadArguments) -> pure ()
  _ -> exitFailure
