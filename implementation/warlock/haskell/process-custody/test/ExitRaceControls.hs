{-# LANGUAGE OverloadedStrings #-}
-- Root-only real-process regression for exit between liveness and metadata.
-- No fake ProcessHandle, numeric-PID signal, new StopD or native authority.
module Main (main) where

import Control.Concurrent (threadDelay)
import Control.Exception (SomeException,mask_,try)
import Control.Monad (forM,unless,when)
import qualified Data.ByteString as B
import Data.IORef (IORef,atomicModifyIORef',modifyIORef',newIORef,readIORef,writeIORef)
import Data.List (intercalate)
import Foreign.StablePtr (StablePtr,newStablePtr)
import System.Directory (doesFileExist,getTemporaryDirectory,removeFile)
import System.Environment (getArgs)
import System.IO (BufferMode(NoBuffering),Handle,IOMode(ReadMode),hClose,hSetBuffering,openFile,openTempFile,stdout,withBinaryFile)
import Warlock.Capture.Process.Internal
 ( AdmissionDeadline,Captured(..),OwnerStatus(..),SessionObservation(..)
 , deadlineAbsoluteNs,leaderExited,observeChild,remainingMicros )
import Warlock.Capture.Process.Persistent.Internal
 ( PersistentOwner,PersistentStatus(..),PidfdCustody(..),SessionExit(..)
 , StopDeadlineObservation(..),newPersistentOwner,observeLiveStartup
 , persistentPidfdCustody,persistentStatus,persistentUnderlyingStatus
 , startBudgetAfter,startBudgetDeadline,stopBudgetMicros,tryPersistentStopDeadline
 , persistentFixture,withPersistentOwnerHook )

data Probe = Probe
 { observationHooks :: Int
 , killHooks :: Int
 , aliveAtObservationHook :: Bool
 , markerExitStimulusSent :: Bool
 , naturalExitBeforeMetadata :: Bool
 , latchedStopAbsolute :: Maybe String
 , stopDeadlineStableInHook :: Bool
 , remainingBeforeStimulus :: Maybe Int
 , remainingAfterNaturalExit :: Maybe Int
 , liveEntered :: Bool
 }

emptyProbe :: Probe
emptyProbe = Probe 0 0 False False False Nothing False Nothing Nothing False

-- Allocate this root and its unreleased RTS StablePtr BEFORE marker/input or
-- child acquisition. Its IORefs retain every external test handle and owner
-- across normal returns AND exceptions. Process exit is no cleanup receipt.
data CaseRoot = CaseRoot String PersistentOwner (IORef [Handle])
 (IORef (Maybe FilePath)) (IORef (Maybe SessionObservation)) (IORef Probe)
type Registry = IORef [(CaseRoot,StablePtr CaseRoot)]

registerCase :: Registry -> String -> IO CaseRoot
registerCase registry name = mask_ $ do
 owner <- newPersistentOwner
 handles <- newIORef []
 marker <- newIORef Nothing
 observation <- newIORef Nothing
 probe <- newIORef emptyProbe
 let root = CaseRoot name owner handles marker observation probe
 stable <- newStablePtr root
 atomicModifyIORef' registry (\roots -> ((root,stable):roots,()))
 pure root

fixtureInputs :: CaseRoot -> IO (FilePath,Handle)
fixtureInputs (CaseRoot _ _ handles marker _ _) = mask_ $ do
 temporary <- getTemporaryDirectory
 (path,markerHandle) <- openTempFile temporary "persistent-exit-race-"
 modifyIORef' handles (markerHandle:)
 writeIORef marker (Just path)
 hClose markerHandle
 removeFile path
 input <- openFile "/dev/null" ReadMode
 modifyIORef' handles (input:)
 pure (path,input)

require :: String -> Bool -> IO ()
require label good = unless good (ioError (userError label))

-- Every poll uses the SAME supplied absolute deadline. No fresh grace,
-- timeout budget, reap or process signal occurs in either polling helper.
awaitReady :: AdmissionDeadline -> FilePath -> IO ()
awaitReady deadline marker = do
 left <- remainingMicros deadline
 require "original startup deadline expired before marker readiness" (left>0)
 exists <- doesFileExist marker
 ready <- if exists then withBinaryFile marker ReadMode (\handle -> (=="ready") <$> B.hGet handle 6) else pure False
 unless ready (threadDelay (min 1000 left) >> awaitReady deadline marker)

awaitNaturalExit :: AdmissionDeadline -> SessionObservation -> IO ()
awaitNaturalExit deadline observed = do
 left <- remainingMicros deadline
 require "original latched stop deadline expired awaiting natural exit" (left>0)
 dead <- leaderExited (observedPid observed)
 unless dead (threadDelay (min 1000 left) >> awaitNaturalExit deadline observed)

latchedDeadline :: PersistentOwner -> IO AdmissionDeadline
latchedDeadline owner = do
 value <- tryPersistentStopDeadline owner
 case value of
  StopDeadlineLatched deadline -> pure deadline
  _ -> ioError (userError ("stop deadline was not already latched: " ++ show value))

runCase :: Registry -> FilePath -> Bool -> IO Bool
runCase registry child forceRace = do
 let name = if forceRace then "natural-exit-between-liveness-and-metadata" else "ordinary-verified-live-child"
 root@(CaseRoot _ owner handles markerCell observedCell probeCell) <- registerCase registry name
 setup <- try (fixtureInputs root) :: IO (Either SomeException (FilePath,Handle))
 attempted <- case setup of
  Left problem -> pure (Left problem)
  Right (marker,input) -> try $ do
   start <- startBudgetAfter 5000000 >>= either (ioError . userError . show) pure
   stop <- either (ioError . userError . show) pure (stopBudgetMicros 2000000)
   let startupD = startBudgetDeadline start
       arguments = if forceRace then [marker,"exit-when-removed"] else [marker]
       verifyReady observed = do
        awaitReady startupD marker
        fresh <- observeChild startupD (observedPid observed)
        require "actual selected child SessionObservation must remain exact"
         (fresh==Right observed && observedPid observed>0 && not (B.null (observedStart observed)) && observedExecutable observed==child)
        writeIORef observedCell (Just observed)
        pure (Right ())
       liveBody live = do
        expected <- readIORef observedCell
        actual <- observeLiveStartup live
        require "actual live session uses the verified same child" ((Just <$> actual)==Right expected)
        modifyIORef' probeCell (\probe -> probe {liveEntered=True})
       hook stage
        | stage=="persistent-before-leader-kill" = modifyIORef' probeCell (\probe -> probe {killHooks=killHooks probe+1})
        | stage=="persistent-before-leader-observation" = do
          modifyIORef' probeCell (\probe -> probe {observationHooks=observationHooks probe+1})
          expected <- readIORef observedCell >>= maybe (ioError (userError "verified child observation missing")) pure
          deadline <- latchedDeadline owner
          left <- remainingMicros deadline
          require "same stop deadline has budget before observation hook" (left>0)
          alreadyDead <- leaderExited (observedPid expected)
          require "controlled child must still be live before exit stimulus" (not alreadyDead)
          modifyIORef' probeCell (\probe -> probe {aliveAtObservationHook=True,latchedStopAbsolute=Just (deadlineAbsoluteNs deadline),remainingBeforeStimulus=Just left})
          when forceRace $ do
           -- Removing this owned marker is ONLY a child self-exit stimulus.
           -- It proves neither reap nor pidfd/pipe/provider retirement.
           removeFile marker
           modifyIORef' probeCell (\probe -> probe {markerExitStimulusSent=True})
           awaitNaturalExit deadline expected
           remaining <- remainingMicros deadline
           require "actual natural exit observed before original StopD" (remaining>0)
           modifyIORef' probeCell (\probe -> probe {naturalExitBeforeMetadata=True,remainingAfterNaturalExit=Just remaining})
          after <- tryPersistentStopDeadline owner
          require "observation hook must not renew the original stop deadline" (after==StopDeadlineLatched deadline)
          modifyIORef' probeCell (\probe -> probe {stopDeadlineStableInHook=True})
        | otherwise = pure ()
   withPersistentOwnerHook owner (persistentFixture child arguments input) 4096 start stop verifyReady liveBody hook
 phase <- persistentStatus owner
 raw <- persistentUnderlyingStatus owner
 custody <- persistentPidfdCustody owner
 stopObservation <- tryPersistentStopDeadline owner
 observed <- readIORef observedCell
 probe <- readIORef probeCell
 retainedHandles <- readIORef handles
 marker <- readIORef markerCell
 let leaderReaped = case attempted of
      Right (Right ((),LeaderReaped captured)) -> output captured=="READY\n"
      _ -> False
     stopUnchanged = case stopObservation of
      StopDeadlineLatched deadline -> latchedStopAbsolute probe==Just (deadlineAbsoluteNs deadline)
      _ -> False
     expectedKillCount = if forceRace then 0 else 1
     checks =
      [ ("actual-session-and-readiness-verified",observed/=Nothing && liveEntered probe)
      , ("new-before-observation-hook-reached-exactly-once",observationHooks probe==1 && aliveAtObservationHook probe)
      , ("original-latched-stop-deadline-unchanged",stopDeadlineStableInHook probe && stopUnchanged)
      , ("exact-before-kill-hook-count",killHooks probe==expectedKillCount)
      , ("controlled-natural-exit-before-metadata",not forceRace || (markerExitStimulusSent probe && naturalExitBeforeMetadata probe))
      , ("actual-owned-LeaderReaped",leaderReaped)
      , ("actual-PersistentRetired",phase==PersistentRetired)
      , ("actual-underlying-Available",raw==Available)
      , ("actual-PidfdClosed",custody==PidfdClosed)
      ]
     passed = all snd checks
 putStrLn (object
  [ ("schema","1"),("case",quote name),("forcedNaturalExitRace",boolean forceRace)
  , ("passed",boolean passed),("result",quote (show attempted))
  , ("sessionObservation",quote (show observed)),("persistentStatus",quote (show phase))
  , ("underlyingStatus",quote (show raw)),("pidfdCustody",quote (show custody))
  , ("stopDeadlineObservation",quote (show stopObservation))
  , ("beforeObservationHookCount",show (observationHooks probe)),("beforeKillHookCount",show (killHooks probe))
  , ("childAliveBeforeStimulus",boolean (aliveAtObservationHook probe))
  , ("markerRemovedOnlyAsExitStimulus",boolean (markerExitStimulusSent probe))
  , ("actualNaturalExitBeforeMetadata",boolean (naturalExitBeforeMetadata probe))
  , ("remainingStopMicrosBeforeStimulus",maybe "null" show (remainingBeforeStimulus probe))
  , ("remainingStopMicrosAfterNaturalExit",maybe "null" show (remainingAfterNaturalExit probe))
  , ("checks",object [(label,boolean good) | (label,good) <- checks])
  , ("stronglyRetainedExternalFixtureHandleCount",show (length retainedHandles))
  , ("marker",maybe "null" quote marker),("externalFixtureHandleCleanupClaim","false")
  , ("scope",quote "Real owned leader lifecycle only; marker removal and leaderExited are not reap or physical cleanup receipts")
  , ("providerCleanupQualified","false"),("nativeAccepted","false"),("originalRequirementAccepted","false")
  ])
 -- Only remove an ordinary leftover marker AFTER all actual owned retirement
 -- observations succeeded. Quarantined owners/handles remain strongly rooted.
 when passed $ case marker of
  Nothing -> pure ()
  Just path -> do
   exists <- doesFileExist path
   when exists (removeFile path)
 pure passed

main :: IO ()
main = do
 hSetBuffering stdout NoBuffering
 arguments <- getArgs
 child <- case arguments of
  [path@('/':_)] -> pure path
  _ -> ioError (userError "expected absolute pinned graceful-stop-child executable path")
 registry <- newIORef ([] :: [(CaseRoot,StablePtr CaseRoot)])
 outcomes <- forM [False,True] $ \forceRace -> do
  result <- try (runCase registry child forceRace) :: IO (Either SomeException Bool)
  case result of
   Right passed -> pure passed
   Left problem -> putStrLn (object [("caseException",quote (show problem)),("forcedNaturalExitRace",boolean forceRace),("passed","false")]) >> pure False
 roots <- readIORef registry
 states <- forM roots $ \(CaseRoot name owner handles marker _ _,_) -> do
  phase <- persistentStatus owner
  retained <- readIORef handles
  path <- readIORef marker
  pure (object [("case",quote name),("phase",quote (show phase)),("retainedFixtureHandles",show (length retained)),("marker",maybe "null" quote path)])
 let passed = outcomes==[True,True] && length roots==2
 putStrLn (object [("schema","1"),("suite",quote "persistent-exit-race-controls"),("passed",boolean passed),("cases","2"),("strongRegistryRoots",show (length roots)),("registry", "["++intercalate "," states++"]"),("stablePtrsReleased","false"),("providerCleanupQualified","false"),("nativeAccepted","false")])
 require "persistent exit race regression failed; raw real-process observations retained above" passed

boolean :: Bool -> String
boolean value = if value then "true" else "false"

object :: [(String,String)] -> String
object fields = "{" ++ intercalate "," [quote key ++ ":" ++ value | (key,value) <- fields] ++ "}"

quote :: String -> String
quote value = "\"" ++ concatMap escape value ++ "\""
 where
  escape '"' = "\\\""
  escape '\\' = "\\\\"
  escape char
   | char<' ' = "\\u00" ++ [hexDigit (fromEnum char `div` 16),hexDigit (fromEnum char `mod` 16)]
   | otherwise = [char]
  hexDigit nibble = case drop nibble "0123456789abcdef" of digit:_ -> digit; [] -> '0'
