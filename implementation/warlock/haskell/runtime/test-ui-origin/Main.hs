{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Independent public-library QA. No engine, GUI admission or CSP execution is
-- inferred from HTTP headers. Root alone executes this selected test image.
module Main (main) where

import Control.Exception (IOException,SomeException,bracket,finally,try)
import Control.Concurrent (forkFinally,newEmptyMVar,putMVar,takeMVar,threadDelay,tryReadMVar)
import Control.Monad (forM,forM_,unless,when)
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.Either (isLeft)
import Data.IORef (IORef,modifyIORef',newIORef,readIORef,writeIORef)
import Data.List (stripPrefix)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import GHC.Clock (getMonotonicTimeNSec)
import qualified Network.Socket as S
import qualified Network.Socket.ByteString as N
import Numeric (showHex)
import System.Directory (createDirectory,doesFileExist,listDirectory)
import System.Environment (getArgs,getEnv,getExecutablePath)
import System.Exit (ExitCode(..),exitFailure)
import System.FilePath ((</>),isAbsolute,takeDirectory)
import System.Posix.Files (deviceID,fileID,getSymbolicLinkStatus,isRegularFile,setFileMode)
import System.Posix.IO (FdOption(CloseOnExec,NonBlockingRead),dupTo,queryFdOption,setFdOption)
import System.Posix.Process (ProcessStatus(..),exitImmediately,forkProcess,getProcessID,getProcessStatus)
import System.Posix.Signals (sigKILL,signalProcess)
import System.Posix.Types (Fd(..))
import System.Process (readProcessWithExitCode)
import System.Timeout (timeout)
import Text.Read (readMaybe)
import Warlock.Capture.Process.Bootstrap (deadlineAfter)
import qualified Warlock.Protocol.Desktop as Desktop
import qualified Warlock.Protocol.Framing as Framing
import qualified Warlock.Protocol.Identity as Identity
import qualified Warlock.Ui.Native as Native
import Warlock.Backend
import Warlock.Bootstrap (BootstrapResult(..))
import qualified Warlock.Protocol.StrictJson as J
import qualified Warlock.Ui.Config as Config
import qualified Warlock.Ui.Http as Http
import qualified Warlock.Ui.Owner as Owner
import qualified Warlock.Ui.Policy as Policy
import Warlock.Ui.PrivateNetwork (enterPrivateNetwork, withPeerNetwork)

must :: Show e => Either e a -> IO a
must = either (ioError . userError . show) pure
check :: IORef Int -> String -> Bool -> IO ()
check budget label good = modifyIORef' budget (+1) >> unless good (ioError (userError label))
jsonBytes :: J.Json -> B.ByteString
jsonBytes = TE.encodeUtf8 . J.renderJson
object :: [(T.Text,J.Json)] -> J.Json
object = J.JObject
text :: String -> J.Json
text = J.JString . T.pack
at :: T.Text -> J.Json -> J.Json
at key (J.JObject fields) = maybe J.JNull id (lookup key fields)
at _ _ = J.JNull
replaceJson :: T.Text -> J.Json -> J.Json -> J.Json
replaceJson key value (J.JObject fields) = J.JObject ((key,value):filter ((/=key) . fst) fields)
replaceJson _ _ value = value
parseJson :: B.ByteString -> IO J.Json
parseJson bytes = must (J.bounds (16*1024*1024) 32) >>= \bounds -> must (J.decodeStrict bounds bytes)
sha :: B.ByteString -> String
sha = concatMap (\octet -> let digits=showHex octet "" in replicate (2-length digits) '0'++digits) . B.unpack . SHA.hash
writePrivate :: FilePath -> B.ByteString -> IO ()
writePrivate file bytes = B.writeFile file bytes >> setFileMode file 0o600
fresh :: FilePath -> IO FilePath
fresh file = createDirectory file >> setFileMode file 0o700 >> pure file
directoryFact :: FilePath -> IO J.Json
directoryFact path = do
 status <- getSymbolicLinkStatus path
 pure (object [("path",text path),("device",text (show (deviceID status))),("inode",text (show (fileID status)))])
imageFact :: FilePath -> IO J.Json
imageFact path = do
 status <- getSymbolicLinkStatus path
 unless (isAbsolute path && isRegularFile status) (ioError (userError "QA image must be an absolute regular nonsymlink file"))
 bytes <- B.readFile path
 pure (object [("path",text path),("device",text (show (deviceID status))),("inode",text (show (fileID status))),("size",text (show (B.length bytes))),("sha256",text (sha bytes))])
ancestors :: FilePath -> IO [J.Json]
ancestors path = mapM directoryFact (reverse (takeWhile (/="/") (iterate takeDirectory (takeDirectory path))))
stringField :: T.Text -> J.Json -> IO String
stringField key value = case at key value of J.JString result -> pure (T.unpack result); _ -> ioError (userError ("missing string "++T.unpack key))

lcg :: Int -> [Integer]
lcg count = take count (tail (iterate (\n -> (1664525*n+1013904223) `mod` 4294967296) (20261101 :: Integer)))
roleCases :: [(Policy.Role,B.ByteString,Policy.Route)]
roleCases = [(Policy.Controller,"/commit",Policy.Commit),(Policy.Bar,"/actions",Policy.Actions),(Policy.Popup,"/actions",Policy.Actions)]
posted :: Policy.Origin -> B.ByteString -> [(B.ByteString,B.ByteString)]
posted origin body = [("Host",Policy.hostBytes origin),("Origin",Policy.originBytes origin),("X-Warlock-Api","1"),("Content-Type","application/json"),("Content-Length",C.pack (show (B.length body)))]
replaceHeader :: B.ByteString -> B.ByteString -> [(B.ByteString,B.ByteString)] -> [(B.ByteString,B.ByteString)]
replaceHeader key value headers = (key,value):filter ((/=key) . fst) headers

policyCorpus :: IORef Int -> FilePath -> IO ()
policyCorpus budget directory = do
 rows <- forM (zip [0 :: Int ..] (lcg 256)) $ \(index,state) -> do
  origin <- must (Policy.makeOrigin (42000+fromInteger (state `mod` 20000)))
  let (role,target,route)=roleCases!!(index `mod` 3)
      body=jsonBytes (object [("seed",J.JNumber (T.pack (show state)))])
      headers=posted origin body
      label="policy LCG20261101 case "++show index++" state "++show state
      invalid=case index `mod` 16 of
       0 -> ("POST",target,replaceHeader "Host" "localhost:1" headers,body)
       1 -> ("POST",target,filter ((/="Host") . fst) headers,body)
       2 -> ("POST",target,replaceHeader "Origin" "http://127.0.0.1:1" headers,body)
       3 -> ("POST",target,replaceHeader "Origin" "null" headers,body)
       4 -> ("POST",target,("hOsT",Policy.hostBytes origin):headers,body)
       5 -> ("POST",target,("Transfer-Encoding","chunked"):headers,body)
       6 -> ("POST",target,replaceHeader "Content-Length" ("0"<>C.pack (show (B.length body))) headers,body)
       7 -> ("POST",target,replaceHeader "Content-Type" "text/plain" headers,body)
       8 -> ("POST",target,filter ((/="X-Warlock-Api") . fst) headers,body)
       9 -> ("POST",target<>"/../events",headers,body)
       10 -> ("POST",if role==Policy.Controller then "/actions" else "/commit",headers,body)
       11 -> ("PUT",target,headers,body)
       12 -> ("POST",target,replaceHeader "Content-Length" "0" headers,body)
       13 -> ("POST",target,("bad header","x"):headers,body)
       14 -> ("POST","/%2e%2e/"<>target,headers,body)
       _ -> ("POST",target,replaceHeader "Host" (Policy.hostBytes origin<>" ") headers,body)
      (method,badTarget,badHeaders,badBody)=invalid
  check budget (label++" valid same-role transport positive") (Policy.admitRequest origin role "POST" target headers body==Right route)
  check budget (label++" generated independent refusal class "++show (index `mod` 16)) (isLeft (Policy.admitRequest origin role method badTarget badHeaders badBody))
  check budget (label++" blind GET cannot consume events") (isLeft (Policy.admitRequest origin role "GET" "/events" [("Host",Policy.hostBytes origin)] B.empty))
  check budget (label++" API GET positive preserves role") (Policy.admitRequest origin role "GET" "/events" [("Host",Policy.hostBytes origin),("X-Warlock-Api","1")] B.empty==Right Policy.Events)
  check budget (label++" CORS preflight never admitted") (isLeft (Policy.admitRequest origin role "OPTIONS" target [("Host",Policy.hostBytes origin),("Origin","http://attacker.invalid")] B.empty))
  check budget (label++" exact document navigation positive") (Policy.navigationAllowed origin (Policy.documentUri origin))
  forM_ [Policy.documentUri origin<>"?x=1",Policy.documentUri origin<>"#x","https://attacker.invalid/index.html","file:///etc/passwd","data:text/html,x","javascript:alert(1)","blob:http://127.0.0.1/x",Policy.originBytes origin<>"/other"] $ \uri -> do
   check budget (label++" unapproved navigation URI "++C.unpack uri) (not (Policy.navigationAllowed origin uri))
   check budget (label++" unapproved resource URI "++C.unpack uri) (not (Policy.resourceAllowed origin role uri))
  let hashA=C.replicate 43 'A'<>"=";hashB=C.replicate 42 'A'<>"E="
  csp <- must (Policy.contentSecurityPolicy origin hashA hashB)
  check budget (label++" syntactic CSP pins only exact scripts/styles/origin") (B.isInfixOf ("script-src 'sha256-"<>hashA<>"'") csp && B.isInfixOf ("style-src 'sha256-"<>hashB<>"'") csp && B.isInfixOf ("connect-src "<>Policy.originBytes origin) csp && not (B.isInfixOf "unsafe-" csp))
  check budget (label++" malformed hash cannot inject CSP") (isLeft (Policy.contentSecurityPolicy origin (hashA<>";unsafe-eval") hashB))
  rules <- parseJson (Policy.resourceFilter origin role)
  check budget (label++" actual blocking filter JSON has initial deny rule") (case rules of J.JArray (first:_) -> at "type" (at "action" first)==text "block"; _ -> False)
  pure (object [("index",J.JNumber (T.pack (show index))),("state",text (show state)),("role",text (show role)),("method",J.JString (TE.decodeUtf8 method)),("target",J.JString (TE.decodeUtf8 badTarget)),("headers",J.JArray [J.JArray [J.JString (TE.decodeUtf8 key),J.JString (TE.decodeUtf8 value)] | (key,value)<-badHeaders]),("body",J.JString (TE.decodeUtf8 badBody)),("expected",text "refused")])
 writePrivate (directory </> "policy-corpus.json") (jsonBytes (J.JArray rows))

wireRequest :: B.ByteString -> B.ByteString -> [(B.ByteString,B.ByteString)] -> B.ByteString -> B.ByteString
wireRequest method target headers body = method<>" "<>target<>" HTTP/1.1\r\n"<>B.concat [key<>": "<>value<>"\r\n" | (key,value)<-headers]<>"\r\n"<>body
httpCorpus :: IORef Int -> FilePath -> IO ()
httpCorpus budget directory = do
 let good=wireRequest "GET" "/index.html" [("Host","127.0.0.1:42000")] B.empty
     bad=[("duplicate-case-header",wireRequest "GET" "/index.html" [("Host","x"),("hOsT","y")] B.empty)
         ,("transfer-encoding",wireRequest "GET" "/index.html" [("Host","x"),("Transfer-Encoding","chunked")] B.empty)
         ,("noncanonical-length",wireRequest "POST" "/commit" [("Host","x"),("Content-Length","01")] "x")
         ,("truncated-body",wireRequest "POST" "/commit" [("Content-Length","2")] "x")
         ,("trailing-byte",good<>"x"),("pipelined-message",good<>good)
         ,("bare-LF","GET /index.html HTTP/1.1\nHost: x\n\n")
         ,("obsolete-fold","GET /index.html HTTP/1.1\r\nHost: x\r\n continuation\r\n\r\n")
         ,("nul-header",wireRequest "GET" "/index.html" [("Host",B.pack [0])] B.empty)
         ,("header-capacity",wireRequest "GET" "/index.html" [("Host",B.replicate 16384 120)] B.empty)]
 decoded <- must (Http.decodeRequest good)
 check budget "actual HTTP parser normal complete request" (Http.requestMethod decoded=="GET" && Http.requestTarget decoded=="/index.html" && Http.requestBody decoded==B.empty)
 forM_ bad $ \(label,wire) -> check budget ("actual HTTP parser rejects "++label) (isLeft (Http.decodeRequest wire))
 forM_ [8192,131072 :: Int] $ \size -> do
  let body=B.replicate size 120;wire=wireRequest "POST" "/commit" [("Content-Length",C.pack (show size))] body
  parsed <- must (Http.decodeRequest wire)
  check budget ("parser preserves exact body boundary "++show size) (Http.requestBody parsed==body)
 writePrivate (directory </> "http-negative-corpus.json") (jsonBytes (J.JArray [object [("case",text label),("wireSHA256",text (sha wire)),("wireHex",text (concatMap (\octet -> let digits=showHex octet "" in replicate (2-length digits) '0'++digits) (B.unpack wire)))] | (label,wire)<-bad]))

data Response = Response Int [(B.ByteString,B.ByteString)] B.ByteString deriving Show
getPort :: Policy.Origin -> IO S.PortNumber
getPort origin = do
 let portText=C.unpack (B.drop 1 (C.dropWhile (/=':') (Policy.hostBytes origin)))
 value <- maybe (ioError (userError "trusted numeric origin port")) pure (readMaybe portText :: Maybe Int)
 pure (fromIntegral value)
request :: Policy.Origin -> B.ByteString -> B.ByteString -> [(B.ByteString,B.ByteString)] -> B.ByteString -> IO Response
request origin method target headers body = do
 result <- timeout 2000000 $ bracket (S.socket S.AF_INET S.Stream S.defaultProtocol) S.close $ \socket -> do
  port <- getPort origin
  S.connect socket (S.SockAddrInet port (S.tupleToHostAddress (127,0,0,1)))
  N.sendAll socket (wireRequest method target headers body)
  raw <- collect socket [] 0
  let (headerBytes,suffix)=B.breakSubstring "\r\n\r\n" raw
  unless (not (B.null suffix)) (ioError (userError "HTTP response header absent"))
  let linesValue=C.lines headerBytes
  status <- case linesValue of
   first:_ -> case C.words first of _:code:_ -> maybe (ioError (userError "HTTP status")) pure (readMaybe (C.unpack code)); _ -> ioError (userError "HTTP status shape")
   _ -> ioError (userError "HTTP response empty")
  let fields=[(C.map lower key,C.dropWhile (==' ') (C.filter (/='\r') (B.drop 1 value))) | line<-drop 1 linesValue,let (key,value)=B.break (==58) line]
      responseBody=B.drop 4 suffix
  unless (lookup "content-length" fields==Just (C.pack (show (B.length responseBody)))) (ioError (userError "actual response length mismatch"))
  pure (Response status fields responseBody)
 maybe (ioError (userError "bounded QA HTTP request timed out")) pure result
 where
  lower :: Char -> Char
  lower c=if c>='A' && c<='Z' then toEnum (fromEnum c+32) else c
  collect :: S.Socket -> [B.ByteString] -> Int -> IO B.ByteString
  collect socket chunks count = do
   part <- N.recv socket 4096
   if B.null part then pure (B.concat (reverse chunks)) else do
    unless (count+B.length part<=9*1024*1024) (ioError (userError "bounded HTTP QA response"))
    collect socket (part:chunks) (count+B.length part)

bindingJson :: J.Json
bindingJson = object [("lifetime",text "9007199254740993"),("session",text "9007199254740995"),("frontend",text "9007199254740997")]
scopeJson :: J.Json
scopeJson = object [("id",text "1"),("generation",text "1")]
projection :: Maybe J.Json -> J.Json
projection selected = object [("viewProtocol",J.JNumber "1"),("kind",text "view-frame"),("revision",text "1"),("views",J.JArray (maybe [] (:[]) selected)),("focusOwner",J.JNull),("popupOwner",J.JNull),("frame",object [("surfaceProtocol",J.JNumber "2"),("publication",text "1"),("lease",text "0"),("mode",text "closed"),("status",text "controlled QA transport projection"),("bar",J.JArray [focusControl True "focus-valid"]),("popup",J.JArray [])]),("announcer",J.JNull),("announcement",J.JNull)]
focusControl :: Bool -> String -> J.Json
focusControl enabled domId = object [("id",text ("qa:"++domId)),("domId",text domId),("label",text "QA control"),("ariaLabel",text "QA control"),("detail",text ""),("enabled",J.JBool enabled),("focusOnly",J.JBool False)]
commit :: [J.Json] -> B.ByteString
commit requests = jsonBytes (object [("viewProtocol",J.JNumber "1"),("kind",text "view-commit"),("projection",projection Nothing),("requests",J.JArray requests),("focus",J.JArray [])])
catalogRequest :: J.Json
catalogRequest = object [("protocolVersion",J.JNumber "3"),("kind",text "catalog-request"),("binding",bindingJson),("requestId",text "7")]

exerciseOwner :: IORef Int -> IORef [J.Json] -> [Config.PreparedDocument] -> Owner.UiEndpoints -> (Owner.TrustedOwnerEvent -> IO (Either T.Text ())) -> IO Owner.EngineResult
exerciseOwner budget observations documents endpoints emit = do
 let controller=Owner.controllerOrigin endpoints
     bar=Owner.barOrigin endpoints
     popup=Owner.popupOrigin endpoints
     getters origin=[("Host",Policy.hostBytes origin),("X-Warlock-Api","1")]
     record label response@(Response code _ body)=modifyIORef' observations (object [("case",text label),("status",J.JNumber (T.pack (show code))),("bodySHA256",text (sha body))]:) >> pure response
     api origin method target body = request origin method target (if method=="POST" then posted origin body else getters origin) body >>= record (C.unpack method++" "++C.unpack target)
 initialProjection <- Owner.uiLastProjection endpoints
 check budget "no committed projection before first send" (initialProjection == Nothing)
 check budget "three actual listener origins distinct" (length (unique (map Policy.originBytes [controller,bar,popup]))==3)
 forM_ [(Policy.Controller,controller),(Policy.Bar,bar),(Policy.Popup,popup)] $ \(role,origin) -> do
  Response code headers body <- request origin "GET" "/index.html" [("Host",Policy.hostBytes origin)] B.empty >>= record (show role++" packaged document")
  document <- case filter ((==role) . Config.documentRole) documents of [value] -> pure value; _ -> ioError (userError "prepared role document")
  csp <- must (Policy.contentSecurityPolicy origin (Config.documentScriptHash document) (Config.documentStyleHash document))
  check budget (show role++" serves exact actual held compilerHTML and CSP") (code==200 && body==Config.documentBytes document && lookup "content-security-policy" headers==Just csp && lookup "x-content-type-options" headers==Just "nosniff")
 forM_ (zip [0 :: Int ..] (lcg 32)) $ \(index,state) -> do
  let body="{}";base=posted bar body
      (method,target,headers)=case index `mod` 8 of
       0 -> ("POST","/actions",replaceHeader "Origin" (Policy.originBytes controller) base)
       1 -> ("POST","/commit",base)
       2 -> ("POST","/actions",filter ((/="X-Warlock-Api") . fst) base)
       3 -> ("POST","/actions",replaceHeader "Host" ("attacker-"<>C.pack (show state)) base)
       4 -> ("GET","/events",[("Host",Policy.hostBytes bar)])
       5 -> ("OPTIONS","/actions",[("Host",Policy.hostBytes bar),("Origin",Policy.originBytes controller)])
       6 -> ("GET","/%2e%2e/index.html",[("Host",Policy.hostBytes bar)])
       _ -> ("POST","/actions",("hOsT",Policy.hostBytes bar):base)
      actualBody=if method=="POST" then body else B.empty
  modifyIORef' observations (object [("case",text ("generated listener input "++show index)),("seed",text (show state)),("origin",J.JString (TE.decodeUtf8 (Policy.originBytes bar))),("method",J.JString (TE.decodeUtf8 method)),("target",J.JString (TE.decodeUtf8 target)),("headers",J.JArray [J.JArray [J.JString (TE.decodeUtf8 key),J.JString (TE.decodeUtf8 value)] | (key,value)<-headers]),("wireSHA256",text (sha (wireRequest method target headers actualBody))),("expected",text "refused")]:)
  Response code _ _ <- request bar method target headers actualBody >>= record ("actual generated denial "++show index++" seed "++show state)
  check budget ("actual listener rejects generated role/header/path class "++show index) (code>=400 && code<500)
 -- A renderer cannot install a native tag even with valid same-role headers.
 forM_ ["native-event","view-topology","view-disposition","view-dismiss","view-escape","view-reflow","focus"] $ \kind -> do
  Response code _ _ <- api bar "POST" "/actions" (jsonBytes (object [("bridgeProtocol",J.JNumber "1"),("kind",text kind),("payload",object [])]))
  check budget ("renderer cannot forge source "++kind) (code==400)
 Response emptyCode _ _ <- api controller "GET" "/events" B.empty
 check budget "rejected renderers leave native/controller queue empty" (emptyCode==204)
 -- Complete controlled transport projection, not a native resource grant.
 let focused=replaceJson "focus" (J.JArray [text "focus-valid"]) (either (error . show) id (J.bounds 131072 16 >>= \limits -> J.decodeStrict limits (commit [])))
 Response presentationCode _ _ <- api controller "POST" "/commit" (jsonBytes focused)
 check budget "actual controller presentation commit forwarded without GUI ACK" (presentationCode==204)
 committedProjection <- Owner.uiLastProjection endpoints
 check budget "only successfully forwarded projection is exposed" (committedProjection == Just (at "projection" focused))
 forM_ ["presentation","announcements","focus"] $ \kind -> do
  Response code _ bytes <- api bar "GET" "/events" B.empty
  packet <- parseJson bytes
  check budget ("actual bar event order "++kind) (code==200 && at "kind" packet==text kind)
  if kind=="focus" then check budget "actual focus target inherits exact current projection scope" (at "payload" packet==object [("focusProtocol",J.JNumber "1"),("kind",text "focus"),("surface",text "bar"),("publication",text "1"),("lease",text "0"),("domId",text "focus-valid")]) else pure ()
 let baseProjection=projection Nothing
     baseFrame=at "frame" baseProjection
     withControls barRows popupRows=replaceJson "popup" (J.JArray popupRows) (replaceJson "bar" (J.JArray barRows) baseFrame)
     withFrame frameValue=replaceJson "projection" (replaceJson "frame" frameValue baseProjection) focused
     focusNegatives=[("absent",replaceJson "focus" (J.JArray [text "unapproved-target"]) focused)
       ,("disabled",withFrame (withControls [focusControl False "focus-valid"] []))
       ,("ambiguous-roles",withFrame (withControls [focusControl True "focus-valid"] [focusControl True "focus-valid"]))]
 forM_ focusNegatives $ \(label,value) -> do
  Response code _ _ <- api controller "POST" "/commit" (jsonBytes value)
  check budget ("owner rejects "++label++" focus before whole native frame") (code==400)
 forM_ (zip [0 :: Int ..] (lcg 8)) $ \(index,state) -> do
  let bad=object [("protocolVersion",J.JNumber "3"),("kind",text ("unknown-"++show state)),("binding",bindingJson),("requestId",text "8")]
  Response code _ _ <- api controller "POST" "/commit" (commit [catalogRequest,bad])
  check budget ("actual complete controller valid-first invalid-suffix refuses case "++show index) (code==400)
 afterRejected <- Owner.uiLastProjection endpoints
 check budget "rejected commits preserve last successfully sent projection" (afterRejected == committedProjection)
 Response catalogCode _ _ <- api controller "POST" "/commit" (commit [catalogRequest])
 check budget "actual controller whole catalog commit forwarded once" (catalogCode==204)
 let poll remaining = do
      response@(Response code _ _) <- api controller "GET" "/events" B.empty
      if code==200 || remaining<=0 then pure response else threadDelay 2000 >> poll (remaining-1)
 Response gatewayCode _ gatewayBytes <- poll (32 :: Int)
 gateway <- parseJson gatewayBytes
 check budget "actual authenticated backend gateway reaches only controller" (gatewayCode==200 && at "kind" gateway==text "native-event" && at "kind" (at "payload" gateway)==text "application-catalog" && at "binding" (at "payload" gateway)==bindingJson && at "requestId" (at "payload" gateway)==text "7")
 -- This explicitly controlled native callback is a QA precondition, not actual
 -- compositor/window evidence or a production-startup fabricated topology.
 let topology=object [("viewProtocol",J.JNumber "1"),("kind",text "view-topology"),("revision",text "1"),("views",J.JArray [scopeJson])]
 modifyIORef' observations (object [("case",text "explicit controlled owner callback fixture"),("payload",topology),("nativeAcceptance",J.JBool False)]:)
 emit (Owner.OwnerTopology topology) >>= must
 clearedProjection <- Owner.uiLastProjection endpoints
 check budget "new topology retires previous projection scope" (clearedProjection == Nothing)
 Response blindCode _ _ <- request controller "GET" "/events" [("Host",Policy.hostBytes controller)] B.empty >>= record "blind GET before topology dequeue"
 check budget "blind controller GET cannot consume owned event" (blindCode==403)
 Response topologyCode _ topologyBytes <- api controller "GET" "/events" B.empty
 topologyGateway <- parseJson topologyBytes
 check budget "approved GET retains exact controlled topology event" (topologyCode==200 && at "kind" topologyGateway==text "view-topology" && at "payload" topologyGateway==topology)
 -- The real current-scope commit is sent through the same HTTP/native route.
 let scopedProjection = projection (Just scopeJson)
     scopedCommit = replaceJson "projection" scopedProjection focused
     eventPayload target token = object [("scope",target),("lease",text token)]
     escapePayload target publication token = object [("scope",target),("publication",text publication),("lease",text token)]
 Response scopedCode _ _ <- api controller "POST" "/commit" (jsonBytes scopedCommit)
 check budget "current scope projection forwarded" (scopedCode == 204)
 forM_ [("view-dismiss", Owner.OwnerDismiss (eventPayload scopeJson "0")),
        ("view-reflow", Owner.OwnerReflow (eventPayload scopeJson "0")),
        ("view-escape", Owner.OwnerEscape (escapePayload scopeJson "1" "0"))] $ \(kind,event) -> do
  accepted <- emit event
  Response eventCode _ eventBytes <- api controller "GET" "/events" B.empty
  packet <- parseJson eventBytes
  check budget ("current " ++ kind ++ " enqueued once") (accepted == Right () && eventCode == 200 && at "kind" packet == text kind)
 let newerFrame = replaceJson "lease" (text "1") (replaceJson "publication" (text "2") (at "frame" scopedProjection))
     newerCommit = replaceJson "projection" (replaceJson "frame" newerFrame scopedProjection) focused
 Response newerCode _ _ <- api controller "POST" "/commit" (jsonBytes newerCommit)
 check budget "new current projection forwarded" (newerCode == 204)
 let wrongScope = object [("id",text "2"),("generation",text "1")]
 forM_ [("old dismiss lease", Owner.OwnerDismiss (eventPayload scopeJson "0")),
        ("old reflow lease", Owner.OwnerReflow (eventPayload scopeJson "0")),
        ("old escape lease", Owner.OwnerEscape (escapePayload scopeJson "1" "0")),
        ("old escape publication", Owner.OwnerEscape (escapePayload scopeJson "1" "1")),
        ("foreign scope", Owner.OwnerEscape (escapePayload wrongScope "2" "1"))] $ \(label,event) -> do
  rejected <- emit event
  Response eventCode _ _ <- api controller "GET" "/events" B.empty
  check budget ("stale " ++ label ++ " refused without event") (rejected == Left "stale native UI projection" && eventCode == 204)
 let newEscape = Owner.OwnerEscape (escapePayload scopeJson "2" "1")
 freshEscapeResult <- emit newEscape
 Response freshCode _ freshBytes <- api controller "GET" "/events" B.empty
 freshPacket <- parseJson freshBytes
 check budget "current escape succeeds after stale refusals" (freshEscapeResult == Right () && freshCode == 200 && at "kind" freshPacket == text "view-escape")
 let renderer=object [("surfaceProtocol",J.JNumber "2"),("kind",text "surface-action"),("surface",text "bar"),("publication",text "1"),("lease",text "0"),("id",text "bar:applications")]
 Response actionCode _ _ <- api bar "POST" "/actions" (jsonBytes renderer)
 check budget "approved scoped renderer action is transport receipt only" (actionCode==204)
 Response foreignSurfaceCode _ _ <- api popup "POST" "/actions" (jsonBytes renderer)
 check budget "renderer cannot claim another surface role" (foreignSurfaceCode==400)
 Response wrongRoleCode _ _ <- request controller "GET" "/events" [("Host",Policy.hostBytes controller),("X-Warlock-Api","1"),("Origin",Policy.originBytes popup)] B.empty >>= record "cross-role event GET"
 check budget "cross-role API GET cannot consume action" (wrongRoleCode==403)
 Response actionEventCode _ actionBytes <- api controller "GET" "/events" B.empty
 actionGateway <- parseJson actionBytes
 check budget "listener owns renderer provenance and scope" (actionEventCode==200 && at "kind" actionGateway==text "view-action" && at "scope" (at "payload" actionGateway)==scopeJson && at "action" (at "payload" actionGateway)==renderer)
 pure (Owner.EngineResult True True)
 where unique = foldr (\value rest -> if value `elem` rest then rest else value:rest) []

data ChildMode = Ordinary | NoNetwork | QueueBound | RetireThrows deriving (Eq,Show)
child :: ChildMode -> FilePath -> FilePath -> IO ()
child mode configPath observationsPath = do
 budget <- newIORef 0
 observations <- newIORef []
 outcome <- try $ withPeerNetwork $ \witness -> do
  unless (mode==NoNetwork) enterPrivateNetwork
  config <- Config.loadUiConfig configPath >>= must
  documents <- if mode `elem` [Ordinary,RetireThrows] then Config.prepareDocuments config else pure []
  let queueControl endpoints emit = do
       let origin=Owner.controllerOrigin endpoints;wire=commit [catalogRequest]
       Response code _ _ <- request origin "POST" "/commit" (posted origin wire) wire
       check budget "queue-bound case forwards exactly one positive full frame first" (code==204)
       -- A local HTTP204 proves sending, not backend consumption. Wait for
       -- the actual authenticated reply before racing the queue boundary.
       let poll remaining = do
            response@(Response status _ _) <- request origin "GET" "/events" [("Host",Policy.hostBytes origin),("X-Warlock-Api","1")] B.empty
            if status==200 || remaining<=0 then pure response else threadDelay 2000 >> poll (remaining-1)
       Response gatewayCode _ gatewayBytes <- poll (32 :: Int)
       gateway <- parseJson gatewayBytes
       check budget "queue-bound precondition consumes the matching authenticated catalog reply"
         (gatewayCode==200 && at "kind" gateway==text "native-event" && at "kind" (at "payload" gateway)==text "application-catalog" && at "binding" (at "payload" gateway)==bindingJson && at "requestId" (at "payload" gateway)==text "7")
       forM_ [1..16 :: Int] $ \revision -> do
        let payload=object [("viewProtocol",J.JNumber "1"),("kind",text "view-topology"),("revision",text (show revision)),("views",J.JArray [scopeJson])]
        admitted <- emit (Owner.OwnerTopology payload)
        check budget ("owned queue admits exact boundary event "++show revision) (admitted==Right ())
       let overflow=object [("viewProtocol",J.JNumber "1"),("kind",text "view-topology"),("revision",text "17"),("views",J.JArray [scopeJson])]
       refused <- emit (Owner.OwnerTopology overflow)
       check budget "owned seventeenth event refuses instead of evicting" (isLeft refused)
       retired <- emit (Owner.OwnerTopology overflow)
       check budget "poisoned callback cannot regain event admission" (isLeft retired)
       modifyIORef' observations (object [("case",text "explicit controlled16-event boundary fixture"),("nativeAcceptance",J.JBool False)]:)
       pure (Owner.EngineResult True True)
      callback = case mode of
       Ordinary -> exerciseOwner budget observations documents
       RetireThrows -> \endpoints emit -> do
        result <- exerciseOwner budget observations documents endpoints emit
        -- A local HTTP204 is not backend consumption. Keep the peer live
        -- until a final read-only fence response proves all prior frames were
        -- consumed, then trigger the retirement failure being tested.
        current <- Owner.uiLastProjection endpoints >>= maybe
          (ioError (userError "retirement fence projection absent")) pure
        let origin=Owner.controllerOrigin endpoints
            fenceRequest=replaceJson "requestId" (text "97") catalogRequest
            wire=jsonBytes (object [("viewProtocol",J.JNumber "1"),("kind",text "view-commit"),
              ("projection",current),("requests",J.JArray [fenceRequest]),("focus",J.JArray [])])
        Response sent _ _ <- request origin "POST" "/commit" (posted origin wire) wire
        check budget "retirement fixture sends one final read-only fence" (sent==204)
        let pollFence remaining = do
             Response code _ bytes <- request origin "GET" "/events"
               [("Host",Policy.hostBytes origin),("X-Warlock-Api","1")] B.empty
             matched <- if code/=200 then pure False else do
              packet <- parseJson bytes
              pure (at "kind" packet==text "native-event"
                && at "kind" (at "payload" packet)==text "application-catalog"
                && at "binding" (at "payload" packet)==bindingJson
                && at "requestId" (at "payload" packet)==text "97")
             if matched then pure True else if remaining<=0 then pure False
               else threadDelay 2000 >> pollFence (remaining-1)
        consumed <- pollFence (64 :: Int)
        check budget "retirement exception follows actual authenticated backend consumption" consumed
        pure result
       NoNetwork -> \_ _ -> ioError (userError "UI callback reached without private network")
       QueueBound -> queueControl
  prepareCount <- newIORef (0 :: Int)
  retireCount <- newIORef (0 :: Int)
  result <- if mode `elem` [Ordinary,RetireThrows] then Owner.runUiOwnerPrepared witness config (\endpoints emit -> do
    modifyIORef' prepareCount (+1)
    stopped <- Owner.uiShouldStop endpoints
    projected <- Owner.uiLastProjection endpoints
    check budget "prepared owner retains three immutable distinct origins before engine execution"
      (Owner.controllerOrigin endpoints/=Owner.barOrigin endpoints && Owner.barOrigin endpoints/=Owner.popupOrigin endpoints && Owner.controllerOrigin endpoints/=Owner.popupOrigin endpoints)
    check budget "prepared owner begins live without a fabricated projection" (not stopped && projected==Nothing)
    pure (callback endpoints emit,do
      modifyIORef' retireCount (+1)
      when (mode==RetireThrows) (ioError (userError "controlled engine retirement failure"))))
    else Owner.runUiOwner witness config callback
  when (mode `elem` [Ordinary,RetireThrows]) $ do
    prepared <- readIORef prepareCount
    retired <- readIORef retireCount
    check budget "prepared engine is acquired and retired exactly once" (prepared==1 && retired==1)
  check budget "actual UI owner independently confirms cleanup disposition"
    (Owner.uiCleanup result==(mode/=RetireThrows) && Owner.uiPeerPid result/=Nothing)
  case mode of
   Ordinary -> do
    check budget "actual UI owner positive completes" (Owner.uiPassed result)
    check budget "only four complete controller frames and one renderer action admitted" (Owner.uiCommitCount result==4 && Owner.uiActionCount result==1)
   RetireThrows -> do
    check budget "retirement failure overrides prior engine success and cleanup receipt"
      (not (Owner.uiPassed result) && not (Owner.uiCleanup result) && not (Owner.uiEngineCleanup result) && Owner.uiFailure result/=Nothing)
    check budget "retirement failure preserves actual admitted frame counts"
      (Owner.uiCommitCount result==5 && Owner.uiActionCount result==1)
   NoNetwork -> check budget "same-backend network refuses before listeners or callbacks" (not (Owner.uiPassed result) && null (Owner.uiOrigins result) && Owner.uiRequestCount result==0 && Owner.uiCommitCount result==0 && Owner.uiActionCount result==0)
   QueueBound -> check budget "event queue bound fails closed without another native frame" (not (Owner.uiPassed result) && Owner.uiCommitCount result==1 && Owner.uiActionCount result==0)
  forM_ (Owner.uiOrigins result) $ \(_,raw) -> do
   let portText=C.unpack (B.drop 1 (C.dropWhile (/=':') (B.drop 7 raw)))
   port <- maybe (ioError (userError "retired origin port")) (must . Policy.makeOrigin) (readMaybe portText)
   refused <- try (request port "GET" "/index.html" [("Host",Policy.hostBytes port)] B.empty) :: IO (Either IOException Response)
   check budget "retired listener cannot be reached in same private network" (isLeft refused)
  count <- readIORef budget
  rows <- reverse <$> readIORef observations
  pure (object [("passed",J.JBool True),("mode",text (show mode)),("checks",J.JNumber (T.pack (show count))),("owner",either (const J.JNull) id (J.bounds 131072 32 >>= \limits -> J.decodeStrict limits (Owner.uiResultJson result))),("observations",J.JArray rows),("engineExecuted",J.JBool False),("nativeAcceptance",J.JBool False)])
 case outcome of
  Right value -> writePrivate observationsPath (jsonBytes value)
  Left (problem :: SomeException) -> do
   count <- readIORef budget
   rows <- reverse <$> readIORef observations
   writePrivate observationsPath (jsonBytes (object [("passed",J.JBool False),("error",text (show problem)),("checksReached",J.JNumber (T.pack (show count))),("observations",J.JArray rows),("engineExecuted",J.JBool False),("nativeAcceptance",J.JBool False)]))
   exitFailure

-- Exercise the actual adopted fd0 with an intentionally blocking endpoint.
-- The reader runs in a distinct process: a broken unsafe recv cannot freeze
-- the independent parent watchdog or be mistaken for successful cleanup.
adoptionBlockingRegression :: IORef Int -> FilePath -> IO ()
adoptionBlockingRegression budget storage = do
 let marker = storage </> "native-reader-progress"
 owner <- getProcessID
 counter <- must (Identity.parseCounter False "1")
 bound <- must (Identity.binding counter counter counter)
 reply <- must (Desktop.applicationAttached bound >>= Desktop.encodeDesktopGateway)
 framed <- must (Framing.desktopGatewayPrefix reply)
 (peer,endpoint) <- S.socketPair S.AF_UNIX S.Stream S.defaultProtocol
 S.withFdSocket endpoint $ \raw -> do
  when (raw == 0) (ioError (userError "expected separately owned socket endpoint"))
  setFdOption (Fd raw) NonBlockingRead False
  blocked <- queryFdOption (Fd raw) NonBlockingRead
  unless (not blocked) (ioError (userError "fixture endpoint must start blocking"))
 started <- getMonotonicTimeNSec
 let end = toInteger started + 5000000000
     remaining = do now <- getMonotonicTimeNSec; pure (toInteger now < end)
 pid <- forkProcess $ do
  S.close peer
  outcome <- try $ do
   S.withFdSocket endpoint $ \raw -> do
    _ <- dupTo (Fd raw) (Fd 0)
    pure ()
   S.close endpoint
   initial <- queryFdOption (Fd 0) NonBlockingRead
   unless (not initial) (ioError (userError "inherited fd0 unexpectedly nonblocking"))
   deadline <- deadlineAfter 5000000 >>= must
   native <- Native.adoptNative bound deadline
   closedOnExec <- queryFdOption (Fd 0) CloseOnExec
   unless (closedOnExec && Native.nativePeerPid native == fromIntegral owner)
     (ioError (userError "adoption lost close-on-exec or peer credentials"))
   done <- newEmptyMVar
   _ <- forkFinally (Native.receiveGateway native) (putMVar done)
   -- The peer deliberately sends no bytes until this timer and pending check.
   threadDelay 10000
   early <- tryReadMVar done
   unless (case early of Nothing -> True; Just _ -> False)
     (ioError (userError "empty peer unexpectedly completed receive"))
   nonblocking <- queryFdOption (Fd 0) NonBlockingRead
   unless nonblocking (ioError (userError "adopted endpoint remains blocking"))
   writePrivate marker "scheduler-progress"
   received <- takeMVar done >>= either (ioError . userError . show) pure
   unless (received == reply) (ioError (userError "gateway frame changed"))
   eof <- try (Native.receiveGateway native) :: IO (Either IOException B.ByteString)
   unless (isLeft eof) (ioError (userError "gateway EOF unexpectedly admitted"))
   clean <- Native.retireNative native
   unless clean (ioError (userError "adopted endpoint retirement failed"))
  case outcome of
   Right () -> exitImmediately ExitSuccess
   Left (problem :: SomeException) -> C.putStrLn (C.pack ("blocking adoption child: " ++ show problem)) >> exitImmediately (ExitFailure 1)
 S.close endpoint
 reaped <- newIORef False
 let cleanup = do
      done <- readIORef reaped
      unless done $ do
       status <- getProcessStatus False False pid
       case status of
        Just _ -> writeIORef reaped True
        Nothing -> do
         signalProcess sigKILL pid
         _ <- getProcessStatus True False pid
         writeIORef reaped True
      S.close peer
     awaitMarker = do
      exists <- doesFileExist marker
      if exists then pure True else do
       live <- remaining
       if live then threadDelay 10000 >> awaitMarker else pure False
     awaitExit = do
      status <- getProcessStatus False False pid
      case status of
       Just value -> writeIORef reaped True >> pure (Just value)
       Nothing -> do
        live <- remaining
        if live then threadDelay 10000 >> awaitExit else pure Nothing
 (do
   ready <- awaitMarker
   check budget "blocking inherited socket permits nonthreaded reader and timer progress" ready
   -- The gateway is delayed until the child has independently proved progress.
   N.sendAll peer framed
   S.shutdown peer S.ShutdownSend
   status <- awaitExit
   check budget "blocking-adoption child receives exact gateway and retires normally" (status == Just (Exited ExitSuccess))
  ) `finally` cleanup

parent :: FilePath -> IO ()
parent storage = do
 names <- listDirectory storage
 unless (null names) (ioError (userError "fresh private QA storage required"))
 budget <- newIORef 0
 adoptionBlockingRegression budget storage
 policyCorpus budget storage
 httpCorpus budget storage
 manifestPath <- getEnv "WARLOCK_UI_ORIGIN_MANIFEST"
 manifestBytes <- B.readFile manifestPath
 manifest <- parseJson manifestBytes
 _ <- must (J.exactObject ["backend","documents"] manifest)
 backendPath <- stringField "path" (at "backend" manifest)
 backendImage <- imageFact backendPath
 _ <- must (J.exactObject ["path","device","inode","size","sha256"] (at "backend" manifest))
 check budget "independent production backend image pin" (all (\key -> at key backendImage==at key (at "backend" manifest)) ["path","device","inode","size","sha256"])
 self <- getExecutablePath
 selfImage <- imageFact self
 parents <- ancestors self
 applications <- fresh (storage </> "applications")
 pins <- fresh (storage </> "pins")
 writePrivate (applications </> "safe.desktop") "[Desktop Entry]\nType=Application\nName=Safe\nExec=/bin/true\n"
 applicationsFact <- directoryFact applications
 pinsFact <- directoryFact pins
 forM_ [("public-library",False,Ordinary),("production-cli",True,Ordinary),("same-network-refused",False,NoNetwork),("event-queue-bound",False,QueueBound),("prepared-retirement-failure",False,RetireThrows)] $ \(label,useCLI,mode) -> do
  directory <- fresh (storage </> label)
  let uiPath=directory </> "ui.json";backendConfigPath=directory </> "backend.json";observationsPath=directory </> "observations.json"
  now <- getMonotonicTimeNSec
  let deadline=text (show (toInteger now+5000000000))
      uiConfig=object [("schema",J.JNumber "1"),("binding",bindingJson),("deadlineMonotonicNs",deadline),("documents",at "documents" manifest)]
      imageFields=case selfImage of J.JObject fields -> fields; _ -> []
      childFlag=case mode of Ordinary -> "--child"; NoNetwork -> "--child-no-network"; QueueBound -> "--child-queue-bound"; RetireThrows -> "--child-retire-throws"
      selected=object (imageFields++[("arguments",J.JArray [text childFlag,text uiPath,text observationsPath]),("ancestors",J.JArray parents)])
      backendConfig=object [("schema",J.JNumber "1"),("binding",bindingJson),("deadlineMonotonicNs",deadline),("ui",selected),("catalogRoots",J.JArray [applicationsFact]),("pinsRoot",pinsFact),("locale",text "C")]
  writePrivate uiPath (jsonBytes uiConfig)
  writePrivate backendConfigPath (jsonBytes backendConfig)
  if useCLI then do
   (code,out,err) <- readProcessWithExitCode backendPath [backendConfigPath] ""
   writePrivate (directory </> "backend.stdout") (C.pack out)
   writePrivate (directory </> "backend.stderr") (C.pack err)
   actual <- parseJson (C.pack out)
   check budget "actual production CLI uses unchanged authenticated UI session" (code==ExitSuccess && at "passed" actual==J.JBool True && at "cleanup" actual==J.JBool True && at "callbacks" actual==J.JNumber "4" && at "operations" actual==J.JNumber "1")
  else do
   config <- loadBackendConfig backendConfigPath >>= must
   result <- runBackend config
   writePrivate (directory </> "backend-result.json") (backendResultJson result)
   when (not (backendPassed result)) $ do
    C.putStrLn (backendResultJson result)
    let detail = case backendBootstrap result of
         Left problem -> "backend error=" ++ T.unpack problem
         Right Refused -> "bootstrap refused"
         Right PendingCustody -> "bootstrap pending custody"
         Right (Executed selectedResult) ->
          -- Only the typed error constructor is printed. Captured output is
          -- deliberately suppressed; the fixture's observation file is separate.
          case stripPrefix "SelectedOutcome {selectedOperation = Left " (show selectedResult) of
           Just rest -> "selected operation error=" ++ takeWhile (/=',') rest
           Nothing -> "selected operation details suppressed"
    putStrLn ("ui_origin_failure_diagnostic=" ++ detail)
    exists <- doesFileExist observationsPath
    putStrLn ("ui_origin_observation_file_exists=" ++ show exists)
    when exists $ do
     value <- B.readFile observationsPath >>= parseJson
     C.putStrLn (jsonBytes (object [("passed",at "passed" value),("error",at "error" value),("checksReached",at "checksReached" value)]))
   let expectedFrames=case mode of Ordinary -> 4; NoNetwork -> 0; QueueBound -> 1; RetireThrows -> 5
       expectedOperations=case mode of NoNetwork -> 0; RetireThrows -> 2; _ -> 1
   check budget (label++" actual library frame/IO boundary and independent cleanup") (backendCleanup result && backendCallbackCount result==expectedFrames && backendOperationCount result==expectedOperations && backendSelectedPid result/=Nothing && backendPassed result==(mode/=NoNetwork))
  observedBytes <- B.readFile observationsPath
  observed <- parseJson observedBytes
  check budget (label++" selected same-PID UI child completes expected controls") (at "passed" observed==J.JBool True && at "engineExecuted" observed==J.JBool False && at "mode" observed==text (show mode))
 afterSelf <- imageFact self
 afterBackend <- imageFact backendPath
 afterManifest <- B.readFile manifestPath
 check budget "all pinned QA/backend/manifest inputs unchanged" (afterSelf==selfImage && afterBackend==backendImage && afterManifest==manifestBytes)
 total <- readIORef budget
 putStrLn ("{\"schema\":1,\"suite\":\"ui-origin-controls\",\"passed\":true,\"checks\":"++show total++",\"seed\":20261101,\"generatedPolicyCases\":256,\"generatedListenerCases\":32,\"generatedControllerBodyCases\":8,\"engineExecuted\":false,\"originalAcceptance\":false,\"nativeAcceptance\":false}")

main :: IO ()
main = S.withSocketsDo $ do
 args <- getArgs
 case args of
  ["--child",configPath,observationsPath] -> child Ordinary configPath observationsPath
  ["--child-no-network",configPath,observationsPath] -> child NoNetwork configPath observationsPath
  ["--child-queue-bound",configPath,observationsPath] -> child QueueBound configPath observationsPath
  ["--child-retire-throws",configPath,observationsPath] -> child RetireThrows configPath observationsPath
  [storage] -> parent storage
  _ -> ioError (userError "expected EMPTY_QA_ROOT or --child UI_CONFIG OBSERVATIONS")
