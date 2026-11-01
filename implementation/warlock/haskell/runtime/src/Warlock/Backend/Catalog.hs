{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- Read-only native-selected .desktop metadata. Exec is never dispatched.
module Warlock.Backend.Catalog (Catalog,newCatalog,readCatalog,retireCatalog) where
import Control.Concurrent.MVar
import Control.Exception (SomeException,SomeAsyncException,fromException,throwIO,try)
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
import System.Posix.Types (Fd)
import Warlock.Backend.Store
import Warlock.Protocol.Desktop (CatalogEntry,CatalogSnapshot,catalogEntry,catalogSnapshot,pinSnapshot)
import Warlock.Protocol.Identity (Counter,addCounter,parseCounter)

data Catalog = Catalog [DirectoryPin] Text Counter StoreOwner (MVar (Maybe (B.ByteString,Counter)))
newCatalog :: [DirectoryPin] -> Text -> Counter -> IO Catalog
newCatalog roots locale lifetime = do
 require (length roots<=32 && T.length locale<=128 && not (T.any (< ' ') locale)) "invalid trusted catalog configuration"
 Catalog roots locale lifetime <$> newStoreOwner <*> newMVar Nothing
retireCatalog :: Catalog -> IO Bool
retireCatalog (Catalog _ _ _ owner _) = retireStoreOwner owner
require :: Bool -> String -> IO ()
require good message = unless good (ioError (userError message))

readCatalog :: Catalog -> IO (Either Text (CatalogSnapshot,Set.Set Text))
readCatalog (Catalog roots locale lifetime owner state) = attempt $ runOwned owner $ do
 nodes <- newIORef (0 :: Int)
 byteCount <- newIORef (0 :: Int)
 groups <- mapM (\root -> withPinnedDirectory owner False root (scan owner nodes byteCount 0 B.empty)) roots
 let files=concat groups
     signature=SHA.hash (B.concat [C.pack (show (B.length name))<>C.pack ":"<>name<>C.pack (show (B.length bytes))<>C.pack ":"<>bytes | (name,bytes) <- files])
 entries <- foldM (insertEntry locale) Map.empty files
 let visible=[(identity,value) | (identity,Just value) <- Map.toAscList entries]
 require (length visible<=2048) "catalog entry capacity"
 modifyMVar state $ \previous -> do
  generation <- case previous of
   Nothing -> either (ioError . userError . show) pure (parseCounter False "1")
   Just (old,current) -> if old==signature then pure current else either (ioError . userError . show) pure (addCounter current 1)
  snapshot <- either (ioError . userError . T.unpack) pure (catalogSnapshot lifetime generation (map snd visible))
  pure (Just (signature,generation),(snapshot,Set.fromList (map fst visible)))

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

insertEntry :: Text -> Map.Map Text (Maybe CatalogEntry) -> (B.ByteString,B.ByteString) -> IO (Map.Map Text (Maybe CatalogEntry))
insertEntry locale entries (path,bytes) = do
 decodedPath <- either (const (ioError (userError "catalog filename UTF8"))) pure (TE.decodeUtf8' path)
 let identity=T.replace "/" "-" (T.dropEnd 8 decodedPath)
 one <- either (ioError . userError . show) pure (parseCounter False "1")
 _ <- either (ioError . userError . T.unpack) pure (pinSnapshot one [identity])
 if Map.member identity entries then pure entries else do
  source <- either (const (ioError (userError "catalog source UTF8"))) pure (TE.decodeUtf8' bytes)
  require (not (T.any (=='\0') source)) "catalog source NUL"
  fields <- either (ioError . userError . T.unpack) pure (desktopFields source)
  let get name=Map.findWithDefault "" name fields
  if T.toLower (get "Hidden")=="true" then pure (Map.insert identity Nothing entries)
  else if get "Type"/="Application" || T.null (get "Exec") then pure entries
  else do
   value <- either (ioError . userError . T.unpack) pure
    (catalogEntry identity (localized locale "Name" identity fields) (Map.findWithDefault "application-x-executable" "Icon" fields) (get "StartupWMClass") (localized locale "GenericName" "" fields) (filter (not . T.null) (T.splitOn ";" (localized locale "Keywords" "" fields))))
   pure (Map.insert identity (Just value) entries)

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
