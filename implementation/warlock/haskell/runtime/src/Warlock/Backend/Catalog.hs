{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Immutable catalog source data. Publication is a completed local reply write,
-- never remote receipt, executable admission, or native launch authority.
module Warlock.Backend.Catalog
 (Catalog,newCatalog,readCatalog,retireCatalog,retireCatalogIfSettled
 ,CatalogPublication,prepareCatalogPublication,publishCatalog,resolveDesktop
 ,ResolvedDesktop,resolvedLifetime,resolvedGeneration,resolvedIdentity
 ,resolvedRoot,resolvedPath,resolvedBytes,resolvedExec,resolvedName,resolvedIcon
 ,resolvedType,resolvedTerminal,resolvedHidden,resolvedNoDisplay) where
import Control.Concurrent.MVar
import Control.Exception (SomeException,SomeAsyncException,fromException,throwIO,try,mask)
import Control.Monad (foldM,unless)
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.IORef
import Data.List (sort,nub)
import qualified Data.Map.Strict as Map
import qualified Data.Set as Set
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Data.Unique (Unique,newUnique)
import System.Posix.Types (Fd)
import Warlock.Backend.Store
import Warlock.Protocol.Desktop (CatalogEntry,CatalogSnapshot,catalogEntry,catalogSnapshot,pinSnapshot)
import Warlock.Protocol.Identity (Counter,addCounter,parseCounter)

data Catalog = Catalog [DirectoryPin] Text Counter StoreOwner (MVar CatalogState)
data CatalogState = CatalogState
 { stateObserved :: Maybe (B.ByteString,Counter)
 , statePublished :: Maybe SnapshotData
 , statePending :: Maybe Unique
 , stateClosed :: Bool }
data SnapshotData = SnapshotData
 { snapSignature :: B.ByteString,snapGeneration :: Counter
 , snapSnapshot :: CatalogSnapshot,snapKnown :: Set.Set Text
 , snapSources :: Map.Map Text EntrySource }
data EntrySource = EntrySource
 { sourceIdentity :: Text,sourceRoot :: DirectoryPin,sourcePath :: B.ByteString
 , sourceBytes :: B.ByteString,sourceExec :: B.ByteString,sourceName :: Text
 , sourceIcon :: Text,sourceType :: Text,sourceTerminal :: Text
 , sourceHidden :: Bool,sourceNoDisplay :: Bool }
data CatalogPublication = CatalogPublication Catalog Unique (IORef Bool) SnapshotData
data ResolvedDesktop = ResolvedDesktop Counter Counter EntrySource

resolvedLifetime :: ResolvedDesktop -> Counter
resolvedLifetime (ResolvedDesktop value _ _) = value
resolvedGeneration :: ResolvedDesktop -> Counter
resolvedGeneration (ResolvedDesktop _ value _) = value
resolvedIdentity :: ResolvedDesktop -> Text
resolvedIdentity (ResolvedDesktop _ _ value) = sourceIdentity value
resolvedRoot :: ResolvedDesktop -> DirectoryPin
resolvedRoot (ResolvedDesktop _ _ value) = sourceRoot value
resolvedPath :: ResolvedDesktop -> B.ByteString
resolvedPath (ResolvedDesktop _ _ value) = sourcePath value
resolvedBytes :: ResolvedDesktop -> B.ByteString
resolvedBytes (ResolvedDesktop _ _ value) = sourceBytes value
resolvedExec :: ResolvedDesktop -> B.ByteString
resolvedExec (ResolvedDesktop _ _ value) = sourceExec value
resolvedName :: ResolvedDesktop -> Text
resolvedName (ResolvedDesktop _ _ value) = sourceName value
resolvedIcon :: ResolvedDesktop -> Text
resolvedIcon (ResolvedDesktop _ _ value) = sourceIcon value
resolvedType :: ResolvedDesktop -> Text
resolvedType (ResolvedDesktop _ _ value) = sourceType value
resolvedTerminal :: ResolvedDesktop -> Text
resolvedTerminal (ResolvedDesktop _ _ value) = sourceTerminal value
resolvedHidden :: ResolvedDesktop -> Bool
resolvedHidden (ResolvedDesktop _ _ value) = sourceHidden value
resolvedNoDisplay :: ResolvedDesktop -> Bool
resolvedNoDisplay (ResolvedDesktop _ _ value) = sourceNoDisplay value

newCatalog :: [DirectoryPin] -> Text -> Counter -> IO Catalog
newCatalog roots locale lifetime = do
 require (length roots<=32 && T.length locale<=128 && not (T.any (< ' ') locale)) "invalid trusted catalog configuration"
 Catalog roots locale lifetime <$> newStoreOwner <*> newMVar (CatalogState Nothing Nothing Nothing False)

invalidate :: Catalog -> IO ()
invalidate (Catalog _ _ _ _ state) = modifyMVar_ state $ \s ->
 pure (s {stateClosed=True,statePublished=Nothing,statePending=Nothing})
retireCatalog :: Catalog -> IO Bool
retireCatalog catalog@(Catalog _ _ _ owner _) = invalidate catalog >> retireStoreOwner owner
retireCatalogIfSettled :: Catalog -> IO Bool
retireCatalogIfSettled catalog@(Catalog _ _ _ owner _) = invalidate catalog >> retireStoreOwnerIfSettled owner
require :: Bool -> String -> IO ()
require good message = unless good (ioError (userError message))

-- A read observes and reserves a monotonically increasing data revision only.
-- It never authorizes resolution of an unpublished revision.
readCatalog :: Catalog -> IO (Either Text (CatalogSnapshot,Set.Set Text))
readCatalog catalog@(Catalog _ _ _ owner _) = attempt $ runOwned owner $ do
 value <- observe catalog
 pure (snapSnapshot value,snapKnown value)

prepareCatalogPublication :: Catalog -> IO (Either Text (CatalogSnapshot,Set.Set Text,CatalogPublication))
prepareCatalogPublication catalog@(Catalog _ _ _ owner state) = attempt $ runOwned owner $ do
 -- Beginning a replacement reply revokes prior resolution data even if the
 -- scan/encoding/write later fails or the caller never uses this token.
 modifyMVar_ state $ \current -> do
  require (not (stateClosed current)) "catalog retired"
  pure (current {statePublished=Nothing,statePending=Nothing})
 value <- observe catalog
 identity <- newUnique
 used <- newIORef False
 modifyMVar_ state $ \s -> do
  require (not (stateClosed s)) "catalog retired"
  pure (s {statePending=Just identity})
 pure (snapSnapshot value,snapKnown value,CatalogPublication catalog identity used value)

-- Claim and invalidate before invoking the real sender. Failed/uncertain writes
-- cannot keep an old publication alive or replay this once-only token.
-- StoreOwner prevents reentrant reads/publications; they refuse busy, not wait.
publishCatalog :: CatalogPublication -> IO () -> IO (Either Text ())
publishCatalog (CatalogPublication (Catalog _ _ _ owner state) identity used value) send =
 attempt $ runOwned owner $ mask $ \restore -> do
  already <- atomicModifyIORef' used (\old -> (True,old))
  require (not already) "catalog publication already attempted"
  modifyMVar_ state $ \s -> do
   require (not (stateClosed s) && statePending s==Just identity &&
    stateObserved s==Just (snapSignature value,snapGeneration value)) "catalog publication superseded"
   pure (s {statePending=Nothing,statePublished=Nothing})
  restore send
  modifyMVar_ state $ \s -> do
   require (not (stateClosed s) && stateObserved s==Just (snapSignature value,snapGeneration value)) "catalog publication retired"
   pure (s {statePublished=Just value})

-- No counter is allocated and no cache/publication state changes on resolution,
-- including a stale-source refusal. Previously returned bytes remain only data.
resolveDesktop :: Catalog -> Counter -> Counter -> Text -> IO (Either Text ResolvedDesktop)
resolveDesktop catalog@(Catalog _ _ lifetime owner state) wantedLifetime wantedGeneration identity =
 attempt $ runOwned owner $ do
  require (wantedLifetime==lifetime) "catalog lifetime mismatch"
  published <- withMVar state $ \s -> do
   require (not (stateClosed s)) "catalog retired"
   maybe (ioError (userError "catalog not published")) pure (statePublished s)
  require (snapGeneration published==wantedGeneration) "catalog generation mismatch"
  (signature,_) <- scanCurrent catalog
  require (signature==snapSignature published) "catalog source changed"
  value <- maybe (ioError (userError "catalog entry unavailable")) pure (Map.lookup identity (snapSources published))
  withMVar state $ \s -> do
   require (not (stateClosed s)) "catalog retired during resolution"
   case statePublished s of
    Just current -> require (snapSignature current==snapSignature published && snapGeneration current==wantedGeneration) "catalog publication changed"
    Nothing -> ioError (userError "catalog publication unavailable")
  pure (ResolvedDesktop lifetime wantedGeneration value)

observe :: Catalog -> IO SnapshotData
observe catalog@(Catalog _ _ lifetime _ state) = do
 (signature,visible) <- scanCurrent catalog
 modifyMVar state $ \s -> do
  require (not (stateClosed s)) "catalog retired"
  generation <- case stateObserved s of
   Nothing -> either (ioError . userError . show) pure (parseCounter False "1")
   Just (old,current) -> if old==signature then pure current else either (ioError . userError . show) pure (addCounter current 1)
  snapshot <- either (ioError . userError . T.unpack) pure (catalogSnapshot lifetime generation [entry | (_,entry,_) <- visible])
  let value=SnapshotData signature generation snapshot (Set.fromList [identity | (identity,_,_) <- visible]) (Map.fromList [(identity,source) | (identity,_,source) <- visible])
      unchanged=stateObserved s==Just (signature,generation)
  pure (s {stateObserved=Just (signature,generation),statePending=Nothing,
   statePublished=if unchanged then statePublished s else Nothing},value)

scanCurrent :: Catalog -> IO (B.ByteString,[(Text,CatalogEntry,EntrySource)])
scanCurrent (Catalog roots locale _ owner _) = do
 nodes <- newIORef (0 :: Int)
 byteCount <- newIORef (0 :: Int)
 groups <- mapM (\root -> withPinnedDirectory owner False root (scan owner nodes byteCount 0 B.empty)) roots
 let signature=SHA.hash (B.concat [C.pack (show index)<>C.pack ":"<>C.pack (show (B.length name))<>C.pack ":"<>name<>C.pack (show (B.length bytes))<>C.pack ":"<>bytes | (index,rows) <- zip [0 :: Int ..] groups, (name,bytes) <- rows])
     files=[(root,path,bytes) | (root,group) <- zip roots groups,(path,bytes) <- group]
 entries <- foldM (insertEntry locale) Map.empty files
 let visible=[(identity,entry,source) | (identity,Just (entry,source)) <- Map.toAscList entries]
 require (length visible<=2048) "catalog entry capacity"
 pure (signature,visible)

scan :: StoreOwner -> IORef Int -> IORef Int -> Int -> B.ByteString -> Fd -> IO [(B.ByteString,B.ByteString)]
scan owner nodes byteCount depth relative directory = do
 require (depth<=16) "catalog directory depth"
 before <- directoryStamp directory
 names <- sort <$> listNames owner directory
 values <- fmap concat $ mapM (\name -> do
  count <- atomicModifyIORef' nodes (\n -> (n+1,n+1))
  require (count<=16384) "catalog inventory capacity"
  folder <- entryDirectory directory name
  let path=if B.null relative then name else relative<>"/"<>name
  if folder then withChildDirectory owner directory name (scan owner nodes byteCount (depth+1) path)
  else if ".desktop" `B.isSuffixOf` name then do
   contents <- readRegular owner False directory name 262144 >>= maybe (ioError (userError "catalog entry disappeared")) pure
   total <- atomicModifyIORef' byteCount (\n -> (n+B.length contents,n+B.length contents))
   require (total<=16777216) "catalog source byte capacity"
   pure [(path,contents)]
  else pure []) names
 after <- directoryStamp directory
 require (before==after) "catalog directory changed during scan"
 pure values

insertEntry :: Text -> Map.Map Text (Maybe (CatalogEntry,EntrySource)) -> (DirectoryPin,B.ByteString,B.ByteString) -> IO (Map.Map Text (Maybe (CatalogEntry,EntrySource)))
insertEntry locale entries (root,path,bytes) = do
 decodedPath <- either (const (ioError (userError "catalog filename UTF8"))) pure (TE.decodeUtf8' path)
 let identity=T.replace "/" "-" (T.dropEnd 8 decodedPath)
 one <- either (ioError . userError . show) pure (parseCounter False "1")
 _ <- either (ioError . userError . T.unpack) pure (pinSnapshot one [identity])
 if Map.member identity entries then pure entries else do
  source <- either (const (ioError (userError "catalog source UTF8"))) pure (TE.decodeUtf8' bytes)
  require (not (T.any (=='\0') source)) "catalog source NUL"
  fields <- either (ioError . userError . T.unpack) pure (desktopFields source)
  let get name=Map.findWithDefault "" name fields
      hidden=T.toLower (get "Hidden")=="true"
      noDisplay=T.toLower (get "NoDisplay")=="true"
  if hidden || noDisplay then pure (Map.insert identity Nothing entries)
  else if get "Type"/="Application" || T.null (get "Exec") then pure entries
  else do
   let name=localized locale "Name" identity fields
       icon=Map.findWithDefault "application-x-executable" "Icon" fields
   value <- either (ioError . userError . T.unpack) pure
    (catalogEntry identity name icon (get "StartupWMClass") (localized locale "GenericName" "" fields) (filter (not . T.null) (T.splitOn ";" (localized locale "Keywords" "" fields))))
   let immutable=EntrySource identity root path bytes (TE.encodeUtf8 (get "Exec")) name icon (get "Type") (get "Terminal") hidden noDisplay
   pure (Map.insert identity (Just (value,immutable)) entries)

desktopFields :: Text -> Either Text (Map.Map Text Text)
desktopFields source = do
 (_,fields,seen) <- foldM line (False,Map.empty,False) (T.lines source)
 if seen then Right fields else Left "missing Desktop Entry section"
 where
  line (active,fields,seen) raw =
   let value=T.strip raw
   in if T.null value || T.isPrefixOf "#" value || T.isPrefixOf ";" value then Right (active,fields,seen)
      else if T.isPrefixOf "[" value && T.isSuffixOf "]" value then
       let next=value=="[Desktop Entry]" in Right (next,fields,seen || next)
      else if not active then Right (active,fields,seen)
      else let (key,remainder)=T.breakOn "=" value in
       if T.null (T.strip key) || T.null remainder then Left "malformed Desktop Entry field"
       else Right (active,Map.insert (T.strip key) (T.strip (T.drop 1 remainder)) fields,seen)

localized :: Text -> Text -> Text -> Map.Map Text Text -> Text
localized locale key fallback fields =
 let (prefix,modifierPart)=T.breakOn "@" locale
     base=T.takeWhile (/='.') prefix
     language=T.takeWhile (/='_') base
     modifier=T.drop 1 modifierPart
     candidates=if T.null modifierPart then [base,language] else [base<>"@"<>modifier,base,language<>"@"<>modifier,language]
     choose []=Map.findWithDefault fallback key fields
     choose (candidate:rest)=case Map.lookup (key<>"["<>candidate<>"]") fields of Just value -> value; Nothing -> choose rest
 in choose (nub candidates)

attempt :: IO a -> IO (Either Text a)
attempt action = do
 result <- try action
 case result of
  Left (problem :: SomeException) -> case fromException problem :: Maybe SomeAsyncException of
   Just _ -> throwIO problem
   Nothing -> pure (Left "catalog unavailable")
  Right value -> pure (Right value)
