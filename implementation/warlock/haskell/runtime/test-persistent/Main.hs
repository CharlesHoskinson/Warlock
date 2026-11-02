{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Public-library integration only: no src directory or admission-test CPP.
-- A callback is subsequent-policy entry, never proof of a native mutation.
module Main (main) where

import Control.Exception (IOException,SomeException,bracket,bracketOnError,try)
import Control.Monad (forM,unless)
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.Char (isHexDigit,ord)
import Data.IORef (modifyIORef',newIORef,readIORef)
import Data.List (intercalate,nub,stripPrefix)
import Numeric (showHex)
import System.Environment (getArgs)
import System.FilePath (takeDirectory,(</>))
import System.IO (IOMode(ReadMode),hClose,withBinaryFile)
import System.Posix.Directory (openDirStream,readDirStream,closeDirStream)
import System.Posix.IO (OpenMode(ReadOnly),closeFd,defaultFileFlags,fdToHandle,openFd)
import System.Posix.Process (getProcessID)
import System.Posix.Files (deviceID,fileID,fileSize,fileMode,fileOwner,getFdStatus,getSymbolicLinkStatus,isDirectory,isRegularFile,linkCount,readSymbolicLink)
import System.Posix.User (getRealUserID,getEffectiveUserID,getRealGroupID,getEffectiveGroupID)
import Text.Read (readMaybe)
import Warlock.Bootstrap
import Warlock.Capture.Process.Bootstrap (Captured(..),Containment(..),OwnerStatus(..),ToolError(BadArguments),selectedCustody,selectedContainment,selectedOperation,deadlineAfter)
import Warlock.Platform.Resolver (Root,Identity(..),Kind(..),Pin(..),withRoot)
import Warlock.Protocol.Codec (decodeClientChecked,encodeClientChecked)
import Warlock.Protocol.CredentialIngress
import Warlock.Protocol.Ingress (Direction(..),Priority(..),Reason(..),ChannelError(StreamEOF),Phase(..),EndpointState(..),phase,endpoint,ingressBinding)

data Case = Case String String Integer Bool

quote :: String -> String
quote value = '"':concatMap escape value ++ "\""
 where
  escape '"' = "\\\""
  escape '\\' = "\\\\"
  escape char | ord char < 32 = let digits=showHex (ord char) "" in "\\u" ++ replicate (4-length digits) '0' ++ digits
              | otherwise = [char]
object :: [(String,String)] -> String
object fields = "{" ++ intercalate "," [quote name ++ ":" ++ value | (name,value) <- fields] ++ "}"
array :: [String] -> String
array values = "[" ++ intercalate "," values ++ "]"
boolean :: Bool -> String
boolean good = if good then "true" else "false"
sha :: B.ByteString -> String
sha = concatMap (\byte -> let digits=showHex byte "" in replicate (2-length digits) '0' ++ digits) . B.unpack . SHA.hash
check :: String -> Bool -> IO ()
check label good = unless good (ioError (userError label))

-- Independent, explicit client oracle. Full-width request/generation strings
-- are compared as checked values; no runtime observation supplies expectations.
request :: Integer -> Int -> B.ByteString
request seed index = C.pack (object [("version","1"),("kind",quote "prepare"),("body",object
 [("binding",object [("lifetime",quote "1"),("session",quote "2"),("frontend",quote "3")])
 ,("intent",object [("request",quote (show identity)),("generation",quote (show (identity+1000000))),("incarnation",quote "9007199254740993"),("operation",quote "restore"),("context",object [("lifetime",quote "1"),("epoch",quote "3"),("output",quote "4"),("revision",quote "5")])])
 ,("selectionId",quote (replicate (32-length token) '0' ++ token))])])
 where
  identity = 9007199254742000 + seed*10 + toInteger index
  token = showHex (seed*17+toInteger index) ""

indices :: Integer -> [Int]
indices seed = let allIndices=[0..2+fromInteger (seed `mod` 3)]
 in if odd seed then reverse allIndices else drop 1 allIndices ++ take 1 allIndices

ack :: B.ByteString
ack = "{\"version\":1,\"kind\":\"hello\",\"body\":{\"binding\":{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"}}}"

credentialJson :: CredentialObservation -> String
credentialJson (CredentialObservation stage pid uid gid) = object [("stage",quote (show stage)),("pid",show pid),("uid",show uid),("gid",show gid)]

-- Complete admitted frames have fragments then one final admission attempt.
-- A rejected later frame may leave a fragment-only suffix. Its authentication
-- must still be checked independently against actual kernel process facts.
groups :: [CredentialObservation] -> ([[CredentialObservation]],[CredentialObservation])
groups [] = ([],[])
groups rows =
 let (fragments,rest)=span (\(CredentialObservation stage _ _ _) -> stage==FragmentObserved) rows
 in case rest of
     admission@(CredentialObservation AdmissionObserved _ _ _):tailRows ->
      let (complete,trailing)=groups tailRows in ((fragments++[admission]):complete,trailing)
     _ -> ([],rows)

writerFacts :: B.ByteString -> Maybe (Integer,Integer,Integer)
writerFacts bytes = case [words line | line <- lines (C.unpack bytes), take 15 line == "fixture_writer "] of
 [[_,pid,uid,gid]] -> (,,) <$> (stripPrefix "pid=" pid >>= readMaybe) <*> (stripPrefix "uid=" uid >>= readMaybe) <*> (stripPrefix "gid=" gid >>= readMaybe)
 _ -> Nothing

-- QA metadata only. These fixed proc reads neither authenticate a sender nor
-- grant an effect. Probe failure is incomplete evidence, not a fabricated map.
contextLine :: String -> IO String
contextLine phaseName = do
 pid <- getProcessID
 uid <- getRealUserID
 euid <- getEffectiveUserID
 gid <- getRealGroupID
 egid <- getEffectiveGroupID
 uidMap <- boundedProc "/proc/self/uid_map" 4096
 gidMap <- boundedProc "/proc/self/gid_map" 4096
 userNs <- readSymbolicLink "/proc/self/ns/user"
 pidNs <- readSymbolicLink "/proc/self/ns/pid"
 unless (length userNs<=64 && length pidNs<=64) (ioError (userError "context namespace bound"))
 status <- boundedProc "/proc/self/status" 65536
 eff <- capability "CapEff:" status
 prm <- capability "CapPrm:" status
 pure ("fixture_context " ++ show ["1",phaseName,show pid,show uid,show euid,show gid,show egid,C.unpack uidMap,C.unpack gidMap,userNs,pidNs,eff,prm])
 where
  boundedProc path bound = withBinaryFile path ReadMode $ \handle -> do
   bytes <- B.hGet handle (bound+1)
   unless (B.length bytes<=bound) (ioError (userError "context proc bound"))
   pure bytes
  capability name status = case [C.unpack value | line <- C.lines status, [field,value] <- [C.words line],field==C.pack name] of
   [value] | length value==16 && all isHexDigit value -> pure value
   _ -> ioError (userError "context capability field")

type ContextRow = [(String,String)]
type ContextPlan = (FilePath,(Integer,Integer))

contextKeys :: [String]
contextKeys = ["phase","pid","uid","euid","gid","egid","uidMap","gidMap","userNamespace","pidNamespace","capEff","capPrm"]

parseContext :: String -> Maybe ContextRow
parseContext line = do
 raw <- stripPrefix "fixture_context " line
 fields <- readMaybe raw :: Maybe [String]
 case fields of
  ["1",phaseName,pid,uid,euid,gid,egid,uidMap,gidMap,userNs,pidNs,eff,prm]
   | phaseName `elem` ["receiver","before-setuid","after-setuid"]
   , all natural [pid,uid,euid,gid,egid], pid/="0"
   , validMap uidMap && validMap gidMap
   , validNs "user:[" userNs && validNs "pid:[" pidNs
   , all (\value -> length value==16 && all isHexDigit value) [eff,prm] ->
    Just (zip contextKeys [phaseName,pid,uid,euid,gid,egid,uidMap,gidMap,userNs,pidNs,eff,prm])
  _ -> Nothing
 where
  natural value = not (null value) && length value<=20 && all (\c -> c>='0' && c<='9') value && maybe False ((==value) . show) (readMaybe value :: Maybe Integer)
  validMap value = length value<=4096 && not (null (lines value)) && all (\row -> case words row of
   [inside,outside,count] -> all natural [inside,outside,count] && (readMaybe count :: Maybe Integer)>Just 0
   _ -> False) (lines value)
  validNs prefixValue value = length value<=64 && case stripPrefix prefixValue value of
   Just suffix -> case reverse suffix of ']':digits -> natural (reverse digits); _ -> False
   Nothing -> False

contextJson :: ContextRow -> String
contextJson fields = object [(key,if key `elem` ["pid","uid","euid","gid","egid"] then value else quote value) | (key,value) <- fields]

privateDirectory :: FilePath -> IO (Integer,Integer)
privateDirectory directory = do
 uid <- getRealUserID
 status <- getSymbolicLinkStatus directory
 unless (not (null directory) && head directory=='/' && isDirectory status && fileOwner status==uid && fileMode status `mod` 512==0o700) (ioError (userError "private context directory required"))
 pure (toInteger (deviceID status),toInteger (fileID status))

prepareContext :: Maybe FilePath -> IO (Maybe ContextPlan)
prepareContext Nothing = pure Nothing
prepareContext (Just directory) = do
 stamp <- privateDirectory directory
 entries <- bracket (openDirStream directory) closeDirStream (\stream -> sequence [readDirStream stream,readDirStream stream,readDirStream stream])
 unless (all (`elem` [".","..",""]) entries) (ioError (userError "fresh private context directory required"))
 pure (Just (directory </> "sender-context.receipt",stamp))

readContextReceipt :: ContextPlan -> IO B.ByteString
readContextReceipt (path,stamp) = do
 beforeDir <- privateDirectory (takeDirectory path)
 unless (beforeDir==stamp) (ioError (userError "context directory identity changed"))
 uid <- getRealUserID
 before <- getSymbolicLinkStatus path
 let fileStamp status=(deviceID status,fileID status,fileSize status,fileMode status,fileOwner status,linkCount status)
 unless (isRegularFile before && fileOwner before==uid && fileMode before `mod` 512==0o600 && linkCount before==1 && fileSize before>0 && fileSize before<=40000) (ioError (userError "private context receipt required"))
 bytes <- bracket (bracketOnError (openFd path ReadOnly defaultFileFlags) closeFd (\fd -> do
   actual <- getFdStatus fd
   unless (fileStamp actual==fileStamp before) (ioError (userError "context receipt identity changed"))
   fdToHandle fd)) hClose (\handle -> B.hGet handle 40001)
 after <- getSymbolicLinkStatus path
 afterDir <- privateDirectory (takeDirectory path)
 unless (fileStamp after==fileStamp before && afterDir==stamp && toInteger (B.length bytes)==toInteger (fileSize before)) (ioError (userError "context receipt changed"))
 pure bytes

contextEvidence :: Either IOException (Maybe ContextPlan) -> Either IOException String -> Either IOException String -> Maybe Integer -> Integer -> Integer -> Maybe Integer -> [CredentialObservation] -> Bool -> IO String
contextEvidence plan receiverBefore receiverAfter selectedPid uid gid targetUid refusedTrace normal = do
 receipt <- case plan of Right (Just selected) -> try (readContextReceipt selected); _ -> pure (Left (userError "context receipt not requested or unavailable"))
 let receiver = either (const Nothing) parseContext receiverBefore
     receiverStable = case (receiverBefore,receiverAfter) of (Right before,Right after) -> before==after; _ -> False
     senders = either (const Nothing) (\bytes -> case lines (C.unpack bytes) of [before,after] -> (,) <$> parseContext before <*> parseContext after; _ -> Nothing) receipt
     value key fields=lookup key fields
     identity row=sequence [value key row >>= readMaybe | key <- ["pid","uid","euid","gid","egid"]] :: Maybe [Integer]
     exactIdentity = case (senders,selectedPid,targetUid) of
      (Just (before,after),Just pid,Just target) -> identity before==Just [pid,uid,uid,gid,gid] && identity after==Just [pid,target,target,gid,gid] && value "phase" before==Just "before-setuid" && value "phase" after==Just "after-setuid" && not (null refusedTrace) && all (\(CredentialObservation stage p u g) -> stage==FragmentObserved && (p,u,g)==(pid,target,gid)) refusedTrace
      _ -> False
     mapsAgree = case (receiver,senders) of
      (Just host,Just (before,after)) -> all (\key -> value key host==value key before && value key before==value key after) ["uidMap","gidMap","userNamespace","pidNamespace"] && value "phase" host==Just "receiver" && (identity host >>= \ids -> case ids of [_,u,e,g,eg] -> Just [u,e,g,eg]; _ -> Nothing)==Just [uid,uid,gid,gid]
      _ -> False
     complete = normal && receiverStable && exactIdentity && mapsAgree
     rowJson = maybe "null" contextJson
 pure (object [("schema","1"),("contextEvidenceComplete",boolean complete),("receiverStable",boolean receiverStable),("senderIdsMatchKernelTrace",boolean exactIdentity),("sameMeasuredNamespaceAndMaps",boolean mapsAgree),("receiver",rowJson receiver),("senderBefore",maybe "null" (contextJson . fst) senders),("senderAfter",maybe "null" (contextJson . snd) senders),("receiptSHA256",either (const "null") (quote . sha) receipt),("receiptPath",case plan of Right (Just (path,_)) -> quote path; _ -> "null"),("status",quote (if complete then "complete" else "incomplete: missing, failed or mismatched actual context observation")),("authenticationVerdictIndependent","true"),("authority",quote "QA process self-observation only; recvmsg credentials and production admission trace remain authoritative")])

runCase :: Root -> [Pin] -> FilePath -> Integer -> B.ByteString -> Maybe Integer -> Maybe FilePath -> Case -> IO Bool
runCase root pins child size digest crossUid contextDirectory (Case name fixtureMode seed positive) = do
 current <- newCurrentSessions
 owner <- newBootstrapOwner current
 callbackRows <- newIORef ([] :: [(B.ByteString,[CredentialObservation])])
 failures <- newIORef ([] :: [String])
 retireDuring <- newIORef ([] :: [Bool])
 let require label good = unless good (modifyIORef' failures (++[label]))
     emptySession = fixtureMode=="persistent-empty-exit"
     expectedIndices = if emptySession then [] else if positive then indices seed else if fixtureMode=="persistent-buffered-retire" then take 1 (indices seed) else [0]
     rawExpected = map (request seed) expectedIndices
 expected <- mapM (either (ioError . userError . show) pure . decodeClientChecked) rawExpected
 binding <- either (ioError . userError . show) pure (ingressBinding "1" "2" "3")
 ingressSlot <- newIORef Nothing
 ingress <- newCredentialIngress binding FromElm (\checked -> do
  previous <- readIORef callbackRows
  trace <- bootstrapCredentialTrace owner
  actual <- either (ioError . userError . show) pure (encodeClientChecked checked)
  let index=length previous
  require "callback exact independently expected checked message/order" (take 1 (drop index expected)==[checked])
  require "each callback follows its own actual final admission attempt" (not (null trace) && case last trace of CredentialObservation AdmissionObserved _ _ _ -> length [() | CredentialObservation AdmissionObserved _ _ _ <- trace]==index+1; _ -> False)
  modifyIORef' callbackRows (++[(actual,trace)])
  -- ACK1 is sent only after actual registration retirement has returned. The
  -- after-retire client waits for that ACK before issuing its second request.
  if fixtureMode `elem` ["persistent-buffered-retire","persistent-after-retire"] && index==0 then retireBootstrap owner >>= \settled -> modifyIORef' retireDuring (++[settled]) else pure ()
  selected <- readIORef ingressSlot >>= maybe (ioError (userError "callback ingress unavailable")) pure
  queued <- enqueueCredentialIngress selected Control ack
  require "ACK enqueue succeeds" (queued==Right ())
  sent <- sendCredentialIngress selected
  require "ACK send succeeds" (sent==Right ())) (\_ -> modifyIORef' failures (++["unexpected server callback"]))
 writeIngress ingressSlot ingress
 deadline <- deadlineAfter 5000000 >>= either (ioError . userError . show) pure
 let isCross=fixtureMode=="persistent-cross-user-same-pid"
 contextPlan <- if isCross then try (prepareContext contextDirectory) else pure (Right Nothing)
 receiverBefore <- if isCross then try (contextLine "receiver") else pure (Right "")
 let contextEnvironment=case contextPlan of Right (Just (path,_)) -> [("DEL010_CONTEXT_PATH",path)]; _ -> []
     environment=[("DEL010_MODE",fixtureMode),("DEL010_SEED",show seed),("LANG","C")] ++ maybe [] (\uid -> [("DEL010_WRITER_UID",show uid)]) crossUid ++ contextEnvironment
 attempt <- try (runBootstrap owner root pins (C.pack (drop 1 child)) [] size digest deadline environment ingress) :: IO (Either SomeException BootstrapResult)
 trace <- bootstrapCredentialTrace owner
 selectedPid <- bootstrapSelectedPid owner
 observed <- bootstrapAuthObservation owner
 callbacks <- readIORef callbackRows
 retired <- try (retireBootstrap owner) :: IO (Either SomeException Bool)
 (ingressState,readerState) <- credentialIngressStatus ingress
 retained <- retainedCredentialIngressFrames ingress
 during <- readIORef retireDuring
 uid <- toInteger <$> getRealUserID
 gid <- toInteger <$> getRealGroupID
 receiverAfter <- if isCross then try (contextLine "receiver") else pure (Right "")
 let (complete,trailing)=groups trace
     captured=case attempt of Right (Executed outcome) -> either (const Nothing) Just (selectedOperation outcome); _ -> Nothing
     actualOutput=maybe B.empty output captured
     actualDiagnostics=maybe B.empty diagnostics captured
     normal=case attempt of
      Right (Executed outcome) -> selectedCustody outcome==Available && selectedContainment outcome==BeforeSignalLeaderExited
       && (if positive then maybe False (const True) captured else selectedOperation outcome==Left BadArguments)
      _ -> False
     identities=[(pid,user,group) | CredentialObservation _ pid user group <- trace]
     selectedIdentities=maybe [] (\pid -> [(pid,uid,gid)]) selectedPid
     forked=fixtureMode=="persistent-unrelated-fork"
     admittedGroups=take (length callbacks) complete
     allowedIdentities=and [maybe False (==pid) selectedPid && user==uid && group==gid | groupRows <- admittedGroups,CredentialObservation _ pid user group <- groupRows]
     finalIs expectedResult = observed==Just (FrameObserved expectedResult)
 require "exact callback count, including zero callbacks for refused suffix" (length callbacks==length expected)
 require "distinct seeded full-width requests really traverse production loop" (not positive || (length callbacks>=3 && length (nub (map fst callbacks))==length callbacks))
 require "actual credential trace complete and below diagnostic truncation bound" (if emptySession then null trace else not (null trace) && length trace<64)
 require "every delivered frame has authenticated fragments before final admission" (length admittedGroups==length callbacks && all (\rows -> length rows>=3 && all (\(CredentialObservation stage _ _ _) -> stage==FragmentObserved) (init rows)) admittedGroups && allowedIdentities)
 require "selected child PID independently observed" (selectedPid/=Nothing)
 require "normal owned selected leader exit and exact success/refusal operation result" normal
 require "independent bootstrap resource retirement succeeds" (either (const False) id retired)
 require "owned ingress endpoint and credential reader retired independently" (phase ingressState==OwnerRetired && endpoint ingressState==Just EndpointConfirmed && readerState==ReaderReady)
 require "no retained ACK replay or outbound mutation" (null retained)
 if positive then do
  require "all and only expected frame admission groups retained" (length complete==length expected && null trailing && all (`elem` selectedIdentities) identities)
  require "clean EOF preserves last meaningful admitted observation" (finalIs CredentialDelivered)
 else case fixtureMode of
  "persistent-empty-exit" -> do
   require "initial exact StreamEOF is refused without any delivered frame" (finalIs (CredentialFrameRejected (CredentialTransport StreamEOF)) && null callbacks && null complete && null trailing && null trace)
   require "empty child exit does not invoke callback retirement hook" (null during)
  "persistent-buffered-retire" -> do
   require "retirement while running does not falsely certify physical cleanup" (during==[False])
   require "buffered old frame is refused after actual registration retirement" (case observed of Just (FrameObserved (CredentialFrameRejected (CredentialPeer ScopeClosed))) -> True; Just (FrameObserved (CredentialFrameRejected (CredentialPeer ForeignSession))) -> True; _ -> False)
   require "refused buffered frame never obtains final admission" (length complete==1 && not (null trailing) && all (`elem` selectedIdentities) identities)
  "persistent-after-retire" -> do
   require "post-expiry send follows registration retirement before ACK1" (during==[False])
   require "request sent after expiry is refused by actual session authorization" (case observed of Just (FrameObserved (CredentialFrameRejected (CredentialPeer ScopeClosed))) -> True; Just (FrameObserved (CredentialFrameRejected (CredentialPeer ForeignSession))) -> True; _ -> False)
   require "actual same-user selected sender has no final admission after expiry" (length complete==1 && not (null trailing) && all (`elem` selectedIdentities) identities && all (\(CredentialObservation stage _ _ _) -> stage==FragmentObserved) trailing)
  "persistent-malformed" -> require "malformed frame is an exact schema refusal without next callback" (finalIs (CredentialRejected BadSchema) && length complete==2 && null trailing && all (`elem` selectedIdentities) identities)
  "persistent-foreign-binding" -> require "other wire session refused before policy callback" (finalIs (CredentialRejected ForeignBinding) && length complete==2 && null trailing && all (`elem` selectedIdentities) identities)
  "persistent-cross-user-same-pid" -> do
   require "same selected PID with real different kernel UID refused before final admission" (finalIs (CredentialFrameRejected (CredentialPeer ForeignUser)) && length complete==1 && not (null trailing))
   require "every real refused kernel fragment has exact selected PID and distinct required UID" (crossUid/=Nothing && all (\(CredentialObservation stage pid user group) -> stage==FragmentObserved && Just pid==selectedPid && Just user==crossUid && user/=uid && group==gid) trailing)
   case writerFacts actualOutput of
    Nothing -> pure () -- Refused public operation intentionally discards capture.
    Just facts -> require "optional writer stdout corroborates actual kernel identity" (all (\(CredentialObservation _ p u g) -> (p,u,g)==facts) trailing)
  _ | forked -> do
   require "actual unrelated kernel sender refused before final admission" (finalIs (CredentialFrameRejected (CredentialPeer ForeignProcess)) && length complete==1 && not (null trailing))
   let refusedFacts=[(pid,user,group) | CredentialObservation _ pid user group <- trailing]
   require "real unrelated sender has one stable distinct kernel PID and expected user/group" (length (nub refusedFacts)==1 && all (\(pid,user,group) -> pid>0 && Just pid/=selectedPid && user==uid && group==gid) refusedFacts && all (\(CredentialObservation stage _ _ _) -> stage==FragmentObserved) trailing)
   case writerFacts actualOutput of
    Nothing -> pure () -- Kernel recvmsg, not discarded stdout, is authoritative.
    Just facts -> require "optional fork stdout corroborates actual kernel identity" (all (==facts) refusedFacts)
  _ -> require "known negative fixture mode" False
 contextFields <-
  if isCross
   then do
    evidence <- contextEvidence contextPlan receiverBefore receiverAfter selectedPid uid gid crossUid trailing normal
    pure [("credentialContextEvidence",evidence)]
   else pure []
 errors <- readIORef failures
 let passed=null errors
 putStrLn (object ([("schema","1"),("requirement",quote "ELM-DEL-010"),("case",quote name),("mode",quote fixtureMode),("seed",show seed),("passed",boolean passed),("nativeEffectClaim","false"),("subsequentPolicyEntryCount",show (length callbacks)),("expectedRawFrames",array (map (quote . C.unpack) rawExpected)),("expectedFrameHashes",array (map (quote . sha) rawExpected)),("callbacks",array [object [("wire",quote (C.unpack bytes)),("credentialCheckpoint",array (map credentialJson checkpoint))] | (bytes,checkpoint) <- callbacks]),("credentials",array (map credentialJson trace)),("selectedPid",maybe "null" show selectedPid),("receiverUid",show uid),("receiverGid",show gid),("authObservation",quote (show observed)),("bootstrapResult",quote (show attempt)),("stdout",quote (C.unpack actualOutput)),("stderr",quote (C.unpack actualDiagnostics)),("retirement",quote (show retired)),("retirementDuringCallback",array (map boolean during)),("ingressState",quote (show ingressState)),("readerState",quote (show readerState)),("failures",array (map quote errors))] ++ contextFields))
 pure passed
 where
  writeIngress slot value = modifyIORef' slot (const (Just value))

main :: IO ()
main = do
 args <- getArgs
 (child,dev,ino,size,digest,mode,crossUid,contextDirectory) <- case args of
  [path,d,i,n,shaText,"common"] -> parsePins path d i n shaText "common" Nothing Nothing
  [path,d,i,n,shaText,"full",uidText] -> case readMaybe uidText of
   Just uid | uid==1 -> parsePins path d i n shaText "full" (Just uid) Nothing
   _ -> ioError (userError "full mode requires actual delegated writer UID1")
  [path,d,i,n,shaText,"full",uidText,directory] -> case readMaybe uidText of
   Just uid | uid==1 && not (null directory) && head directory=='/' -> parsePins path d i n shaText "full" (Just uid) (Just directory)
   _ -> ioError (userError "full context mode requires UID1 and trusted absolute private directory")
  _ -> ioError (userError "expected CHILD DEV INODE SIZE SHA common | CHILD DEV INODE SIZE SHA full 1 [PRIVATE_CONTEXT_DIRECTORY]")
 pins <- sourcePins child dev ino
 bytes <- B.readFile child
 check "independently supplied selected executable size/hash" (toInteger (B.length bytes)==size && C.pack (sha bytes)==digest)
 uidMap <- B.readFile "/proc/self/uid_map"
 gidMap <- B.readFile "/proc/self/gid_map"
 receiver <- toInteger <$> getRealUserID
 check "full mode receiver is mapped service UID0" (mode/="full" || receiver==0)
 putStrLn (object [("schema","1"),("kind",quote "persistent-auth-environment"),("mode",quote mode),("scope",quote "Public Haskell bootstrap library with actual kernel credentials; subsequent policy entry only, no native effects"),("selectedExecutable",quote child),("sha256",quote (sha bytes)),("size",show size),("device",show dev),("inode",show ino),("uidMap",quote (C.unpack uidMap)),("gidMap",quote (C.unpack gidMap)),("crossUserRequired",boolean (mode=="full")),("crossUserEvidence",if mode=="full" then quote "requires real UID1 writer trace in its case" else quote "unavailable in common mode; no full original acceptance")])
 let seeded=[Case ("seed-"++show seed) "persistent-seeded" seed True | seed <- [20261031..20261038]]
     negatives=[Case "empty-first-EOF" "persistent-empty-exit" 20261031 False,Case "buffered-retirement" "persistent-buffered-retire" 20261031 False,Case "after-retirement-send" "persistent-after-retire" 20261031 False,Case "malformed" "persistent-malformed" 20261031 False,Case "foreign-binding" "persistent-foreign-binding" 20261031 False,Case "unrelated-same-user" "persistent-unrelated-fork" 20261031 False]
     crossCases=if mode=="full" then [Case "actual-cross-user" "persistent-cross-user-same-pid" 20261031 False] else []
 rootStat <- getSymbolicLinkStatus "/"
 result <- withRoot "/" (Identity (toInteger (deviceID rootStat)) (toInteger (fileID rootStat))) $ \root -> forM (seeded++negatives++crossCases) $ \testCase -> do
  outcome <- try (runCase root pins child size digest crossUid contextDirectory testCase) :: IO (Either SomeException Bool)
  case outcome of
   Right passed -> pure passed
   Left problem -> do
    let Case name _ seed _=testCase
    putStrLn (object [("schema","1"),("case",quote name),("seed",show seed),("passed","false"),("fixtureException",quote (show problem))])
    pure False
 outcomes <- either (ioError . userError . show) pure result
 let passed=and outcomes && length outcomes==(if mode=="full" then 15 else 14)
 putStrLn (object [("schema","1"),("kind",quote "persistent-auth-verdict"),("mode",quote mode),("passed",boolean passed),("cases",show (length outcomes)),("crossUserIncluded",boolean (mode=="full")),("completeOriginalEvidence",boolean (passed && mode=="full")),("nativeExecutionAcceptance","false")])
 check "persistent bootstrap controls failed; raw structured traces above are retained" passed
 where
  parsePins path d i n shaText mode crossUid contextDirectory = case (readMaybe d,readMaybe i,readMaybe n) of
   (Just dev,Just ino,Just size) | not (null path) && head path=='/' && dev>=0 && ino>0 && size>0 && length shaText==64 -> pure (path,dev,ino,size,C.pack shaText,mode,crossUid,contextDirectory)
   _ -> ioError (userError "invalid trusted selected child pins")

sourcePins :: FilePath -> Integer -> Integer -> IO [Pin]
sourcePins child dev ino = do
 let parents=reverse (takeWhile (/="/") (iterate takeDirectory (takeDirectory child)))
 dirs <- mapM pinDirectory parents
 st <- getSymbolicLinkStatus child
 check "selected executable identity and regular file" (isRegularFile st && toInteger (deviceID st)==dev && toInteger (fileID st)==ino && fileSize st>0)
 pure (dirs++[Pin (C.pack child) (Identity dev ino) Regular])
 where
  pinDirectory path = do
   st <- getSymbolicLinkStatus path
   check "selected executable ancestor is directory" (isDirectory st)
   pure (Pin (C.pack path) (Identity (toInteger (deviceID st)) (toInteger (fileID st))) Directory)
