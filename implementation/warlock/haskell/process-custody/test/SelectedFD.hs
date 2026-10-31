{-# LANGUAGE OverloadedStrings #-}
-- Root-only source fixture. It uses the actual selected child and shared Owner.
module Main (main) where
import Control.Concurrent (threadDelay)
import Control.Exception (bracket)
import Control.Monad (unless)
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Numeric (showHex)
import qualified Network.Socket as Socket
import qualified Warlock.Capture.Process.Owner as OwnerCore
import System.Directory (getTemporaryDirectory, removeFile)
import System.Environment (getArgs)
import System.Exit (exitFailure)
import System.IO (hFlush, hSeek, SeekMode(AbsoluteSeek), openBinaryTempFile)
import System.Posix.Files (deviceID, fileID, fileSize, getFdStatus)
import System.Posix.IO (closeFd, handleToFd, queryFdOption, setFdOption, FdOption(CloseOnExec))
import System.Posix.Types (Fd(..))
import Warlock.Capture.Process.Internal

check :: String -> Bool -> IO ()
check name condition = unless condition (putStrLn (name ++ ": FAIL") >> exitFailure) >> putStrLn (name ++ ": PASS")
hex :: B.ByteString -> String
hex = concatMap (\n -> let digits = showHex n "" in if length digits == 1 then '0':digits else digits) . B.unpack
withFileFd :: B.ByteString -> (Fd -> IO a) -> IO a
withFileFd bytes use = bracket acquire release (\(_,fd) -> use fd)
 where
  acquire = do
   tmp <- getTemporaryDirectory
   (path,handle) <- openBinaryTempFile tmp "selected-fd-control"
   B.hPut handle bytes
   hFlush handle
   hSeek handle AbsoluteSeek 0
   fd <- handleToFd handle
   setFdOption fd CloseOnExec True
   pure (path,fd)
  release (path,fd) = closeFd fd >> removeFile path

main :: IO ()
main = do
 args <- getArgs
 case args of
  [child] -> withFileFd "selected-alpha" $ \first -> withFileFd "selected-beta" $ \second -> withFileFd "forbidden-sentinel" $ \sentinel -> bracket (Socket.socket Socket.AF_UNIX Socket.Stream Socket.defaultProtocol) Socket.close $ \ambient -> Socket.withFdSocket ambient $ \socketFd -> do
   setFdOption (Fd socketFd) CloseOnExec False
   firstStatus <- getFdStatus first
   secondStatus <- getFdStatus second
   sentinelStatus <- getFdStatus sentinel
   -- The sentinel is a test-owned FD; its deliberate lack of CLOEXEC makes
   -- closefrom, not a parent flag, responsible for its absence in the child.
   setFdOption sentinel CloseOnExec False
   firstBefore <- queryFdOption first CloseOnExec
   secondBefore <- queryFdOption second CloseOnExec
   childHash <- C.pack . hex . SHA.hash <$> B.readFile child
   let row number st bytes = (number,toInteger (deviceID st),toInteger (fileID st),toInteger (fileSize st),hex (SHA.hash bytes))
       selected = [row (3 :: Int) firstStatus "selected-alpha",row 4 secondStatus "selected-beta"]
       forbidden = [(toInteger (deviceID sentinelStatus),toInteger (fileID sentinelStatus))]
       command mode = [show selected,show forbidden,"",mode]
   owner <- newOwner
   success <- runFixturePinnedFDsObserved owner child childHash (command "ok") [first,second] 65536 5000000
   firstAfter <- queryFdOption first CloseOnExec
   secondAfter <- queryFdOption second CloseOnExec
   successState <- status owner
   check "selected descriptors and sentinel" (case operation success of Right captured -> C.isInfixOf "selected child descriptor 3: PASS" (output captured) && C.isInfixOf "selected child descriptor 4: PASS" (output captured) && C.isInfixOf "unselected sentinel identities absent: PASS" (output captured) && C.isInfixOf "no inherited sockets: PASS" (output captured) && diagnostics captured == "selected-fd-child-stderr"; _ -> False)
   check "parent selected CLOEXEC unchanged" (firstBefore && secondBefore && firstAfter && secondAfter && successState == Available)
   failure <- runFixturePinnedFDsObserved owner child childHash (command "exit7") [first,second] 65536 5000000
   check "nonzero preserves diagnostic" (operation failure == Left (Unsuccessful 7) && case capturedOutput failure of Just captured -> diagnostics captured == "selected-fd-child-stderr"; Nothing -> False)
   duplicate <- runFixturePinnedFDsObserved owner child childHash (command "ok") [first,first] 65536 5000000
   check "duplicate source refused" (operation duplicate == Left BadArguments && capturedOutput duplicate == Nothing)
   tooMany <- runFixturePinnedFDsObserved owner child childHash (command "ok") (map Fd [3..131]) 65536 5000000
   check "129 sources refused without truncation" (operation tooMany == Left BadArguments && capturedOutput tooMany == Nothing)
   expired <- runFixturePinnedFDsObservedHook owner child childHash (command "ok") [first,second] 65536 10000 (\stage -> if stage == "before-spawn" then threadDelay 30000 else pure ())
   expiredState <- status owner
   check "expired D refuses spawn" (operation expired == Left TimedOut && expiredState == Available)
   faultOwner <- newOwner
   fault <- runFixturePinnedFDsObservedHook faultOwner child childHash (command "ok") [first,second] 65536 5000000 (\stage -> if stage == "fd-after-publish" then ioError (userError "controlled post-publication fault") else pure ())
   faultState <- status faultOwner
   check "post-publication failure quarantines" (operation fault == Left CleanupUncertain && case faultState of Quarantined _ -> True; _ -> False)
   retained <- OwnerCore.ownerPending faultOwner
   case retained of
    Nothing -> check "pending child and identities retained" False
    Just pending -> do
     (descriptors,pid,hasHandle) <- OwnerCore.pendingSnapshot pending
     native <- OwnerCore.pendingNativeSnapshot pending
     let identified entry = case entry of OwnerCore.PendingClosed _ (Just _) -> True; OwnerCore.PendingUncertain _ (Just _) -> True; OwnerCore.PendingHandle _ _ (Just _) -> True; _ -> False
         noOpen entry = case entry of OwnerCore.PendingOpen _ _ -> False; _ -> True
     check "pending child and identities retained" (case pid of Just childPid -> childPid > 0 && hasHandle && any identified descriptors && all noOpen descriptors && length native == 2 && all (== OwnerCore.NativeFreed) native; Nothing -> False)
  _ -> putStrLn "usage: whitelisted-controls /absolute/pinned-selected-child" >> exitFailure
