{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Trusted startup file, never supplied by an HTTP request.
module Warlock.Ui.Config
 (UiConfig,uiBinding,uiDeadline,PreparedDocument(..),loadUiConfig,prepareDocuments) where
import Control.Exception (SomeException,SomeAsyncException,fromException,mask,throwIO,try)
import Control.Monad (unless)
import qualified Data.ByteString as B
import qualified Data.Text as T
import Data.Text (Text)
import qualified Data.Text.Encoding as TE
import System.Posix.Files (getSymbolicLinkStatus,deviceID,fileID)
import Text.Read (readMaybe)
import Warlock.Backend.Store (newStoreOwner,readStartupFile,retireStoreOwner)
import Warlock.Capture.Process.Bootstrap (AdmissionDeadline,deadlineFromAbsoluteNs)
import Warlock.Http.Document (prepareHtml)
import Warlock.Platform.Resolver (Identity(..),Kind(..),Pin(..),withRoot)
import Warlock.Protocol.Identity (Binding,Counter,binding,parseCounter)
import qualified Warlock.Protocol.StrictJson as J
import Warlock.Ui.Policy (Role(..))

data ParentPin = ParentPin FilePath Integer Integer
data Asset = Asset Role FilePath Integer Integer Integer String [ParentPin]
data UiConfig = UiConfig Binding AdmissionDeadline [Asset]
data PreparedDocument = PreparedDocument {documentRole :: Role,documentBytes :: B.ByteString,documentScriptHash :: B.ByteString,documentStyleHash :: B.ByteString} deriving (Eq,Show)
uiBinding :: UiConfig -> Binding
uiBinding (UiConfig value _ _) = value
uiDeadline :: UiConfig -> AdmissionDeadline
uiDeadline (UiConfig _ value _) = value

loadUiConfig :: FilePath -> IO (Either Text UiConfig)
loadUiConfig configPath = mask $ \restore -> do
 owner <- newStoreOwner
 observed <- try (restore (readStartupFile owner configPath))
 retired <- try (retireStoreOwner owner) :: IO (Either SomeException Bool)
 let asyncs=[problem | Left problem <- [retired],Just _ <- [fromException problem :: Maybe SomeAsyncException]]
 case observed of
  Left (problem :: SomeException) -> case fromException problem :: Maybe SomeAsyncException of
   Just _ -> throwIO problem
   Nothing -> case asyncs of first:_ -> throwIO first; [] -> pure (Left "UI startup configuration unavailable")
  Right raw -> case asyncs of
   first:_ -> throwIO first
   [] -> if not (either (const False) id retired) then pure (Left "UI configuration custody uncertain") else
    case parse raw of
     Left reason -> pure (Left reason)
     Right (bound,end,assets) -> do
      deadline <- deadlineFromAbsoluteNs end
      pure $ either (Left . T.pack . show) (\value -> Right (UiConfig bound value assets)) deadline
 where
  parse raw = do
   limits <- err (J.bounds 131072 16)
   value <- err (J.decodeStrict limits raw)
   fields <- obj ["schema","binding","deadlineMonotonicNs","documents"] value
   require (lookup "schema" fields==Just (J.JNumber "1")) "UI startup schema"
   boundFields <- key "binding" fields >>= obj ["lifetime","session","frontend"]
   life <- key "lifetime" boundFields >>= positive
   session <- key "session" boundFields >>= positive
   frontend <- key "frontend" boundFields >>= positive
   bound <- err (binding life session frontend)
   end <- key "deadlineMonotonicNs" fields >>= string
   docs <- key "documents" fields >>= obj ["controller","bar","popup"]
   assets <- mapM (\(name,role) -> key name docs >>= asset role) [("controller",Controller),("bar",Bar),("popup",Popup)]
   pure (bound,T.unpack end,assets)
  asset role value = do
   fields <- obj ["path","device","inode","size","sha256","ancestors"] value
   pathValue <- key "path" fields >>= parsePath
   dev <- key "device" fields >>= number True
   ino <- key "inode" fields >>= number False
   size <- key "size" fields >>= number False
   require (size<=8*1024*1024) "UI document size"
   digest <- key "sha256" fields >>= string
   require (T.length digest==64 && T.all (\c -> c>='0' && c<='9' || c>='a' && c<='f') digest) "UI document digest"
   parents <- key "ancestors" fields >>= array >>= mapM directory
   require (length parents<=64) "UI document ancestors"
   pure (Asset role pathValue dev ino size (T.unpack digest) parents)
  directory value = do
   fields <- obj ["path","device","inode"] value
   ParentPin <$> (key "path" fields >>= parsePath) <*> (key "device" fields >>= number True) <*> (key "inode" fields >>= number False)
  parsePath value = do
   text <- string value
   require (T.isPrefixOf "/" text && T.length text<=4096 && not (T.any (\c -> c<' ' || c=='\127') text) && all (\part -> part/="." && part/="..") (T.splitOn "/" text)) "UI trusted document path"
   pure (T.unpack text)
  number zero value = do
   text <- string value
   _ <- err (parseCounter zero text)
   maybe (Left "UI integer") Right (readMaybe (T.unpack text))

err :: Show a => Either a b -> Either Text b
err = either (Left . T.pack . show) Right
require :: Bool -> Text -> Either Text ()
require good reason = unless good (Left reason)
obj :: [Text] -> J.Json -> Either Text [(Text,J.Json)]
obj names = err . J.exactObject names
key :: Text -> [(Text,J.Json)] -> Either Text J.Json
key name fields = maybe (Left "UI configuration field") Right (lookup name fields)
string :: J.Json -> Either Text Text
string (J.JString value) = Right value
string _ = Left "UI configuration string"
array :: J.Json -> Either Text [J.Json]
array (J.JArray values) = Right values
array _ = Left "UI configuration array"
positive :: J.Json -> Either Text Counter
positive value = string value >>= err . parseCounter False

prepareDocuments :: UiConfig -> IO [PreparedDocument]
prepareDocuments (UiConfig _ _ assets) = mapM prepare assets
 where
  prepare (Asset role path dev ino size digest parents) = do
   rootStat <- getSymbolicLinkStatus "/"
   let rootIdentity=Identity (toInteger (deviceID rootStat)) (toInteger (fileID rootStat))
       pins=[Pin (TE.encodeUtf8 (T.pack name)) (Identity device inode) Directory | ParentPin name device inode <- parents]
           ++[Pin (TE.encodeUtf8 (T.pack path)) (Identity dev ino) Regular]
   result <- withRoot "/" rootIdentity $ \root -> prepareHtml root pins (TE.encodeUtf8 (T.pack (drop 1 path))) size digest
   (bytes,script,style) <- either (ioError . userError . show) pure result
   pure (PreparedDocument role bytes script style)
