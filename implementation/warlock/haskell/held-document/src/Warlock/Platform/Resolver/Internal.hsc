{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE ScopedTypeVariables #-}
{-# LANGUAGE OverloadedStrings #-}
{-# OPTIONS_GHC -Wall #-}
#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/vfs.h>
#include <linux/magic.h>
-- Linux-specific private proposal. No path, capability, or runtime acceptance.
module Warlock.Platform.Resolver.Internal
 ( Root, Identity(..), Kind(..), Pin(..), Link(..), Resolution(..), ResolveError(..)
 , withRoot, withRootTestProc, resolve, resolveWithHook, Hooks(..), resolveWithHooks, resolveSnapshot, resolveSnapshotWithHooks ) where

import Control.Exception (Exception, IOException, bracket, bracketOnError, throwIO, try, uninterruptibleMask_)
import Control.Concurrent.MVar (MVar, newMVar, modifyMVar, withMVar)
import Control.Monad (unless, when)
import Data.Bits ((.|.))
import Data.Int (Int64)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import qualified Data.Map.Strict as M
import qualified Data.Set as S
import Foreign.C.Error (throwErrnoIfMinus1Retry, throwErrnoIfMinus1)
import Foreign.C.String (CString)
import Foreign.C.Types (CChar(..), CInt(..), CSize(..), CLong(..))
import Foreign.Marshal.Alloc (allocaBytes)
import Foreign.Ptr (Ptr)
import Foreign.Storable (peekByteOff)
import System.Posix.Files (deviceID, fileID, fileSize, getFdStatus, isDirectory, isRegularFile, isSymbolicLink)
import System.Posix.IO (closeFd)
import System.Posix.Types (Fd(..))
import Warlock.Platform.Descriptor (readAcquiredExact, DescriptorFailure)

foreign import ccall unsafe "open" c_open :: CString -> CInt -> IO CInt
foreign import ccall unsafe "openat" c_openat :: CInt -> CString -> CInt -> IO CInt
foreign import ccall unsafe "fcntl" c_fcntl :: CInt -> CInt -> CInt -> IO CInt
foreign import ccall unsafe "fstatfs" c_fstatfs :: CInt -> Ptr () -> IO CInt
foreign import ccall unsafe "readlinkat" c_readlinkat :: CInt -> CString -> Ptr CChar -> CSize -> IO #{type ssize_t}

pathFlags, directoryFlags, readFlags :: CInt
pathFlags = #{const O_PATH} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC}
directoryFlags = pathFlags .|. #{const O_DIRECTORY}
readFlags = #{const O_RDONLY} .|. #{const O_NONBLOCK} .|. #{const O_CLOEXEC}

newtype Root = Root (MVar (Maybe (Fd,Fd)))
-- These identities are a manifest snapshot, not an authentication credential.
data Identity = Identity Integer Integer deriving (Eq, Ord, Show)
data Kind = Directory | SymbolicLink B.ByteString | Regular deriving (Eq, Show)
data Pin = Pin { pinPath :: B.ByteString, pinIdentity :: Identity, pinKind :: Kind } deriving (Eq, Show)
data Link = Link B.ByteString B.ByteString deriving (Eq, Show)
data Resolution = Resolution { resolvedPath :: B.ByteString, resolvedIdentity :: Identity, observedLinks :: [Link] } deriving (Eq, Show)
data ResolveError = InvalidPath | Limit | MissingPin B.ByteString | DuplicatePin | IdentityMismatch B.ByteString | TypeMismatch B.ByteString | LinkMismatch B.ByteString | Cycle | UnexpectedLink | FileFailure DescriptorFailure | OsFailure deriving (Eq, Show)

data Abort = Abort ResolveError deriving Show
instance Exception Abort

abort :: ResolveError -> IO a
abort = throwIO . Abort
identity :: Fd -> IO Identity
identity fd = do status <- getFdStatus fd; pure (Identity (toInteger (deviceID status)) (toInteger (fileID status)))
fdNumber :: Fd -> CInt
fdNumber (Fd n) = n
openName :: Fd -> B.ByteString -> CInt -> IO Fd
openName fd name flags = B.useAsCString name $ \p -> Fd <$> throwErrnoIfMinus1Retry "openat" (c_openat (fdNumber fd) p flags)

-- The caller establishes that every ancestor of this bootstrap path belongs to
-- the trusted platform root. The final component is O_NOFOLLOW. Root never
-- escapes this lexical callback or becomes an exported raw descriptor.
withRoot :: B.ByteString -> Identity -> (Root -> IO a) -> IO (Either ResolveError a)
withRoot = withRootTestProc "/proc/self/fd"

-- Only a test harness should expose an alternate proc bootstrap. Production
-- entrypoint withRoot fixes the kernel path and never accepts caller text.
withRootTestProc :: B.ByteString -> B.ByteString -> Identity -> (Root -> IO a) -> IO (Either ResolveError a)
withRootTestProc procPath path expected action = guardErrors $
 bracket acquire retire (action . Root)
 where
  acquire = do
   when (B.null path || B.elem 0 path || B.length path > 4096) (abort InvalidPath)
   bracketOnError (B.useAsCString path $ \p -> Fd <$> throwErrnoIfMinus1Retry "open-root" (c_open p directoryFlags)) closeFd $ \root -> do
    found <- identity root
    unless (found == expected) (abort (IdentityMismatch "/"))
    bracketOnError (B.useAsCString procPath $ \p -> Fd <$> throwErrnoIfMinus1Retry "open-procfd" (c_open p directoryFlags)) closeFd $ \proc -> do
     stat <- getFdStatus proc
     unless (isDirectory stat) (abort (TypeMismatch "procfd"))
     allocaBytes #{size struct statfs} $ \buffer -> do
      _ <- throwErrnoIfMinus1Retry "fstatfs" (c_fstatfs (fdNumber proc) buffer)
      fsType <- peekByteOff buffer #{offset struct statfs, f_type} :: IO CLong
      unless (fsType == fromIntegral (#{const PROC_SUPER_MAGIC} :: Integer)) (abort (TypeMismatch "procfs"))
     newMVar (Just (root,proc))
  retire gate = do
   pair <- uninterruptibleMask_ $ modifyMVar gate (\state -> pure (Nothing,state))
   maybe (pure ()) closeBoth pair

closeBoth :: (Fd,Fd) -> IO ()
closeBoth (a,b) = do
 x <- try (closeFd a) :: IO (Either IOException ())
 y <- try (closeFd b) :: IO (Either IOException ())
 case (x,y) of
  (Right (),Right ()) -> pure ()
  _ -> ioError (userError "descriptor close failed")

clone :: Fd -> IO Fd
clone fd = Fd <$> throwErrnoIfMinus1Retry "fcntl-dupfd-cloexec" (c_fcntl (fdNumber fd) #{const F_DUPFD_CLOEXEC} 0)

lease :: MVar (Maybe (Fd,Fd)) -> IO (Fd,Fd)
lease gate = uninterruptibleMask_ $ withMVar gate $ \state -> case state of
 Nothing -> abort OsFailure
 Just (root,proc) -> bracketOnError (clone root) closeFd $ \r -> do
  p <- clone proc
  pure (r,p)

guardErrors :: forall a. IO a -> IO (Either ResolveError a)
guardErrors io = do
 outcome <- try (try io :: IO (Either IOException a))
 case outcome of
  Left (Abort reason) -> pure (Left reason)
  Right (Left _) -> pure (Left OsFailure)
  Right (Right value) -> pure (Right value)

-- User paths are canonical root-relative; link targets are relative and may
-- contain dot-dot only when the result stays inside the pinned root.
parts :: B.ByteString -> Either ResolveError [B.ByteString]
parts path
 | B.null path || B.length path > 4096 || B.elem 0 path || B.head path == 47 = Left InvalidPath
 | otherwise = let xs = C.split '/' path in if length xs > 128 || any bad xs then Left InvalidPath else Right xs
 where bad x = B.null x || x == "." || x == ".." || B.length x > 255
relativeTarget :: [B.ByteString] -> B.ByteString -> Either ResolveError [B.ByteString]
relativeTarget base target
 | B.null target || B.length target > 4096 || B.head target == 47 || B.elem 0 target = Left InvalidPath
 | otherwise = foldl step (Right base) (C.split '/' target)
 where
  step acc x = do
   xs <- acc
   if B.null x || x == "." then Right xs
   else if x == ".." then case reverse xs of [] -> Left InvalidPath; (_:rest) -> Right (reverse rest)
   else if B.length x > 255 || length xs >= 128 then Left Limit else Right (xs ++ [x])
label :: [B.ByteString] -> B.ByteString
label xs = "/" <> C.intercalate "/" xs
fromEither :: Either ResolveError a -> IO a
fromEither = either abort pure

readLinkHeld :: Fd -> IO B.ByteString
readLinkHeld fd = allocaBytes 4097 $ \buffer -> B.useAsCString "" $ \empty -> do
 n <- throwErrnoIfMinus1 "readlinkat-empty" (c_readlinkat (fdNumber fd) empty buffer 4097)
 if n >= 4097 then abort Limit else B.packCStringLen (buffer, fromIntegral n)

-- Re-open every name relative to its still-held parent: this catches observed
-- swaps at the two check points, not every adversarial same-UID race.
recheck :: [(Fd,B.ByteString,Identity)] -> IO ()
recheck checks = mapM_ verify checks
 where verify (parent,name,want) = bracket (openName parent name pathFlags) closeFd $ \fd -> do
        got <- identity fd
        unless (got == want) (abort (IdentityMismatch name))

data Hooks = Hooks { afterLease :: IO (), afterProbe :: IO (), beforeConsumer :: Fd -> IO (), afterConsumer :: Fd -> IO (), beforeClose :: Fd -> IO () }
noHooks :: Hooks
noHooks = Hooks (pure ()) (pure ()) (const (pure ())) (const (pure ())) (const (pure ()))
resolve :: Root -> [Pin] -> B.ByteString -> [Link] -> Integer -> Integer -> B.ByteString -> IO (Either ResolveError Resolution)
resolve root pins input expectedLinks expectedSize limit digest = resolveWithHooks root pins input expectedLinks expectedSize limit digest noHooks
resolveWithHook :: Root -> [Pin] -> B.ByteString -> [Link] -> Integer -> Integer -> B.ByteString -> IO () -> IO (Either ResolveError Resolution)
resolveWithHook root pins input expectedLinks expectedSize limit digest hook = resolveWithHooks root pins input expectedLinks expectedSize limit digest (noHooks {afterProbe=hook})
-- Hooks are test seams only and must not be exported in a production facade.
resolveWithHooks :: Root -> [Pin] -> B.ByteString -> [Link] -> Integer -> Integer -> B.ByteString -> Hooks -> IO (Either ResolveError Resolution)
resolveWithHooks root pins input expectedLinks expectedSize limit digest hooks = fmap (fmap fst) (resolveSnapshotWithHooks root pins input expectedLinks expectedSize limit digest hooks)

resolveSnapshot :: Root -> [Pin] -> B.ByteString -> [Link] -> Integer -> Integer -> B.ByteString -> IO (Either ResolveError (Resolution,B.ByteString))
resolveSnapshot root pins input expectedLinks expectedSize limit digest = resolveSnapshotWithHooks root pins input expectedLinks expectedSize limit digest noHooks

resolveSnapshotWithHooks :: Root -> [Pin] -> B.ByteString -> [Link] -> Integer -> Integer -> B.ByteString -> Hooks -> IO (Either ResolveError (Resolution,B.ByteString))
resolveSnapshotWithHooks (Root gate) pins input expectedLinks expectedSize limit digest hooks = guardErrors $
 bracket (lease gate) closeBoth $ \(root,proc) -> do
  afterLease hooks
  inputParts <- fromEither (parts input)
  when (length pins > 16384 || length expectedLinks > 40 || expectedSize < 0 || limit < 0 || expectedSize > limit || limit > 67108864) (abort Limit)
  mapM_ (\p -> do _ <- fromEither (parts (B.drop 1 (pinPath p))); unless (B.isPrefixOf "/" (pinPath p) && B.length (pinPath p) <= 4096) (abort InvalidPath)) pins
  mapM_ (\(Link name target) -> do _ <- fromEither (parts (B.drop 1 name)); unless (B.isPrefixOf "/" name && B.length name <= 4096 && B.length target <= 4096 && not (B.elem 0 target)) (abort InvalidPath)) expectedLinks
  mapM_ (\p -> case pinKind p of SymbolicLink target -> when (B.null target || B.length target > 4096 || B.elem 0 target) (abort InvalidPath); _ -> pure ()) pins
  let index = M.fromList [(pinPath p,p) | p <- pins]
  when (M.size index /= length pins) (abort DuplicatePin)
  walk index root proc S.empty [] [] [] root [] inputParts

 where
  walk index root proc seen links checks parents parent prefix remaining = case remaining of
   [] -> abort InvalidPath
   name:rest -> do
    let current = prefix ++ [name]; key = label current
    when (B.length key > 4096) (abort Limit)
    pin <- maybe (abort (MissingPin key)) pure (M.lookup key index)
    bracket (openName parent name pathFlags) closeFd $ \probe -> do
     status <- getFdStatus probe
     ident <- identity probe
     unless (ident == pinIdentity pin) (abort (IdentityMismatch key))
     let checks' = (parent,name,ident):checks
     if isSymbolicLink status then do
      target <- readLinkHeld probe
      case pinKind pin of SymbolicLink literal | literal == target -> pure (); _ -> abort (LinkMismatch key)
      when (S.member key seen || length links >= 40) (abort Cycle)
      let thisLink = Link key target; links' = links ++ [thisLink]
      when (length links' > length expectedLinks || take (length links') expectedLinks /= links') (abort UnexpectedLink)
      next <- fromEither (relativeTarget prefix target)
      when (length (next ++ rest) > 128) (abort Limit)
      walk index root proc (S.insert key seen) links' checks' (probe:parents) root [] (next ++ rest)
     else if null rest then do
      unless (isRegularFile status && pinKind pin == Regular) (abort (TypeMismatch key))
      unless (links == expectedLinks) (abort UnexpectedLink)
      afterProbe hooks
      let fdName = C.pack (show (fdNumber probe))
      bracket (openName proc fdName readFlags) closeFd $ \readFd -> do
       readStatus <- getFdStatus readFd
       readIdentity <- identity readFd
       unless (isRegularFile readStatus && readIdentity == ident && toInteger (fileSize readStatus) == expectedSize) (abort (IdentityMismatch key))
       recheck checks'
       result <- readAcquiredExact (clone readFd) (beforeConsumer hooks) (afterConsumer hooks) (beforeClose hooks) expectedSize limit digest
       content <- either (abort . FileFailure) pure result
       recheck checks'
       pure (Resolution key ident links,content)
     else do
      unless (isDirectory status && pinKind pin == Directory) (abort (TypeMismatch key))
      walk index root proc seen links checks' (probe:parents) probe current rest
