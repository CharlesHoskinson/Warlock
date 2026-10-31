{-# LANGUAGE OverloadedStrings #-}
-- Private controlled source fixture; trusted root selects and pins the child.
module Main (main) where
import Control.Concurrent.MVar (newEmptyMVar,putMVar,readMVar)
import Control.Monad (unless)
import Control.Exception (SomeException,try,throwIO)
import qualified Crypto.Hash.SHA256 as SHA
import Numeric (showHex)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.IORef (modifyIORef',newIORef,readIORef)
import System.Environment (getArgs)
import System.FilePath (takeDirectory)
import System.Posix.User (getRealUserID,getRealGroupID)
import System.Posix.Files (deviceID,fileID,getSymbolicLinkStatus,isDirectory,isRegularFile)
import Text.Read (readMaybe)
import Warlock.Bootstrap.Aggregate
import Warlock.Bootstrap.CurrentSessions (newCurrentSessions)
import Warlock.Capture.Process.Bootstrap (Containment(..),OwnerStatus(..),selectedCustody,selectedContainment,selectedOperation,deadlineAfter)
import Warlock.Platform.Resolver (Identity(..),Kind(..),Pin(..),withRoot)
import Warlock.Protocol.Codec (decodeClientChecked)
import Warlock.Protocol.Ingress (Direction(..),ingressBinding)
import Warlock.Protocol.CredentialIngress
import Warlock.Protocol.Ingress (Priority(Control))
import OwnedControls (newRegistry,runOwnedControls,checkCredentialTrace)

ack :: B.ByteString
ack = "{\"version\":1,\"kind\":\"hello\",\"body\":{\"binding\":{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"}}}"
check :: String -> Bool -> IO ()
check label good = unless good (ioError (userError label))
main :: IO ()
main = do
 args <- getArgs
 (child,dev,ino,size,digest) <- case args of
  [path,d,i,n,sha] -> case (readMaybe d,readMaybe i,readMaybe n) of
   (Just a,Just b,Just c) | not (null path) && head path == '/' && a>=0 && b>0 && c>0 && length sha==64 -> pure (path,a,b,c,C.pack sha)
   _ -> ioError (userError "invalid trusted child pins")
  _ -> ioError (userError "expected child path dev inode size sha256")
 prepare <- B.readFile "/home/charles/Warlock/implementation/warlock/haskell/protocol/test/fixtures/valid-prepare.bin"
 let digestHex = concatMap (\w -> let h = showHex w "" in if length h == 1 then '0':h else h) (B.unpack (SHA.hash prepare))
 check "actual pinned corpus hash" (digestHex == "0d3341e70d17fbe5967dc898efcc978ff05b9029e80d60aee971ca9cfb8f2ed1")
 expected <- either (ioError . userError . show) pure (decodeClientChecked prepare)
 binding <- either (ioError . userError . show) pure (ingressBinding "1" "2" "3")
 callbacks <- newIORef (0 :: Int)
 ingressSlot <- newEmptyMVar
 ingress <- newCredentialIngress binding FromElm (\checked -> do
   check "checked message differs from actual canonical prepare" (checked == expected)
   modifyIORef' callbacks (+1)
   current <- readMVar ingressSlot
   queued <- enqueueCredentialIngress current Control ack
   check "fixture ACK queue" (queued == Right ())
   sent <- sendCredentialIngress current
   check "fixture ACK send" (sent == Right ())) (\_ -> ioError (userError "unexpected server handler"))
 putMVar ingressSlot ingress
 current <- newCurrentSessions
 owner <- newBootstrapOwner current
 pins <- sourcePins child dev ino
 rootStat <- getSymbolicLinkStatus "/"
 deadline <- deadlineAfter 5000000 >>= either (ioError . userError . show) pure
 registry <- newRegistry
 result <- withRoot "/" (Identity (toInteger (deviceID rootStat)) (toInteger (fileID rootStat))) $ \root -> try $ do
  bootstrapResult <- runBootstrap owner root pins (C.pack (drop 1 child)) [] size digest deadline [("DEL010_MODE","immediate"),("LANG","C")] ingress
  selectedPid <- bootstrapSelectedPid owner >>= maybe (ioError (userError "missing selected child PID")) pure
  uid <- toInteger <$> getRealUserID
  gid <- toInteger <$> getRealGroupID
  trace <- bootstrapCredentialTrace owner
  checkCredentialTrace "approved" selectedPid uid gid True trace
  observed <- bootstrapAuthObservation owner
  count <- readIORef callbacks
  retired <- retireBootstrap owner
  check "one real checked callback" (count == 1 && observed == Just (FrameObserved CredentialDelivered))
  check "bootstrap normal selected child and independent retirement" (case bootstrapResult of
   Executed selected -> selectedCustody selected == Available && selectedContainment selected == BeforeSignalLeaderExited && either (const False) (const True) (selectedOperation selected) && retired
   _ -> False)
  controlsDeadline <- deadlineAfter 5000000 >>= either (ioError . userError . show) pure
  runOwnedControls registry root pins (C.pack (drop 1 child)) [] size digest controlsDeadline prepare
 case result of
  Left problem -> ioError (userError (show problem))
  Right outcome -> do
   either (throwIO :: SomeException -> IO ()) pure outcome
   putStrLn "selected child, same-UID refusal and replacement controls completed"

sourcePins :: FilePath -> Integer -> Integer -> IO [Pin]
sourcePins child dev ino = do
 let parents = reverse (takeWhile (/= "/") (iterate takeDirectory (takeDirectory child)))
 dirs <- mapM pinDirectory parents
 st <- getSymbolicLinkStatus child
 check "selected executable dev/inode" (isRegularFile st && toInteger (deviceID st) == dev && toInteger (fileID st) == ino)
 pure (dirs ++ [Pin (C.pack child) (Identity dev ino) Regular])
 where
  pinDirectory path = do
   st <- getSymbolicLinkStatus path
   check "selected ancestor directory" (isDirectory st)
   pure (Pin (C.pack path) (Identity (toInteger (deviceID st)) (toInteger (fileID st))) Directory)
