{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Exception (AsyncException(ThreadKilled), IOException, bracket, throwIO, try)
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.IORef (newIORef, readIORef, writeIORef)
import Numeric (showHex)
import System.Directory (createDirectory, getTemporaryDirectory, removeFile, removePathForcibly, renameFile)
import System.Exit (exitFailure)
import System.FilePath ((</>))
import System.IO (hClose, openTempFile)
import qualified System.Posix.Files
import System.Posix.Files (createNamedPipe, createSymbolicLink, deviceID, fileID, getFileStatus, getFdStatus)
import System.Posix.IO (OpenMode(WriteOnly), OpenFileFlags(append), closeFd, defaultFileFlags, fdWrite, openFd)
import Warlock.Http.Document (prepareHtml)
import Warlock.Platform.Descriptor (DescriptorFailure(..))
import Warlock.Platform.Resolver.Internal

check :: String -> Bool -> IO ()
check label ok = if ok then putStrLn (label ++ ": PASS") else putStrLn (label ++ ": FAIL") >> exitFailure
ident :: FilePath -> IO Identity
ident path = do st <- getFileStatus path; pure (Identity (toInteger (deviceID st)) (toInteger (fileID st)))
hex :: B.ByteString -> C.ByteString
hex = C.pack . concatMap (\n -> let x=showHex n "" in if length x == 1 then '0':x else x) . B.unpack . SHA.hash
mkRoot :: IO FilePath
mkRoot = do dir <- getTemporaryDirectory; (path,handle) <- openTempFile dir "held-document-"; hClose handle; removeFile path; createDirectory path; pure path
html :: B.ByteString
html = "<!DOCTYPE HTML>\n<html>\n<head>\n  <meta charset=\"UTF-8\">\n  <title>Main</title>\n  <style>y</style>\n</head>\n\n<body>\n\n<pre id=\"elm\"></pre>\n\n<script>x</script>\n\n</body>\n</html>"
emptyHooks :: Hooks
emptyHooks = Hooks (pure ()) (pure ()) (const (pure ())) (const (pure ())) (const (pure ()))
main :: IO ()
main = bracket mkRoot removePathForcibly $ \root -> do
 let path = root </> "main.html"; size = toInteger (B.length html); digest = hex html
 B.writeFile path html
 let tiny = root </> "tiny"
 B.writeFile tiny "abc"
 rootId <- ident root
 fileId <- ident path
 tinyId <- ident tiny
 let pins = [Pin "/main.html" fileId Regular,Pin "/tiny" tinyId Regular]
 result <- withRoot (C.pack root) rootId $ \r -> do
  (body,script,style) <- prepareHtml r pins "main.html" size (C.unpack digest)
  check "document exact immutable bytes" (body == html)
  check "script digest" (script == "LXEWQrcmsEQBYnyp+6wy9chTD7GQPMTbAiWHF5IaSIE=")
  check "style digest" (style == "ofzkNjhU/4iM/0uOeHXWAMJoI5BBKoz3mzfQsRFIsPo=")
  wrong <- resolveSnapshot r pins "main.html" [] size (8*1024*1024) (C.replicate 64 '0')
  check "wrong hash no bytes" (case wrong of Left _ -> True; _ -> False)
  swap <- resolveSnapshotWithHooks r pins "main.html" [] size (8*1024*1024) digest (emptyHooks {afterProbe=renameFile path (path++".old") >> createNamedPipe path 0o600})
  check "FIFO after probe fails without reopening FIFO" (case swap of Left _ -> True; _ -> False)
  removeFile path; renameFile (path++".old") path
  witness <- newIORef False
  grown <- resolveSnapshotWithHooks r pins "main.html" [] size (8*1024*1024) digest (emptyHooks {afterConsumer = \_ -> bracket (openFd path WriteOnly defaultFileFlags {append=True}) closeFd (\fd -> fdWrite fd "d" >>= writeIORef witness . (==1))})
  wrote <- readIORef witness
  check "positive append witness and size mismatch" (wrote && case grown of Left _ -> True; _ -> False)
  B.writeFile path html
  tinyWitness <- newIORef 0
  short <- resolveSnapshotWithHooks r pins "tiny" [] 3 4 (hex "abcd") (emptyHooks {afterConsumer = \_ -> bracket (openFd tiny WriteOnly defaultFileFlags {append=True}) closeFd (\fd -> fdWrite fd "d" >>= writeIORef tinyWitness)})
  four <- B.readFile tiny
  exactWrite <- readIORef tinyWitness
  check "3 to 4 positive write witness and refusal" (exactWrite == 1 && four=="abcd" && case short of Left (FileFailure DeclaredSizeMismatch) -> True; _ -> False)
  closed <- resolveSnapshotWithHooks r pins "main.html" [] size (8*1024*1024) digest (emptyHooks {beforeClose=closeFd})
  check "close error prevents successful bytes" (case closed of Left _ -> True; _ -> False)
  synchronous <- resolveSnapshotWithHooks r pins "main.html" [] size (8*1024*1024) digest (emptyHooks {afterConsumer = \_ -> ioError (userError "injected read")})
  check "synchronous exception yields no bytes" (case synchronous of Left _ -> True; _ -> False)
  fdRef <- newIORef Nothing
  injected <- try (resolveSnapshotWithHooks r pins "main.html" [] size (8*1024*1024) digest (emptyHooks {afterConsumer = \fd -> writeIORef fdRef (Just fd) >> throwIO ThreadKilled})) :: IO (Either AsyncException (Either ResolveError (Resolution,B.ByteString)))
  check "async exception yields no success" (case injected of Left ThreadKilled -> True; _ -> False)
  ownedFd <- readIORef fdRef
  descriptorClosed <- case ownedFd of
   Nothing -> pure False
   Just fd -> do observed <- try (getFdStatus fd) :: IO (Either IOException System.Posix.Files.FileStatus); pure (case observed of Left _ -> True; _ -> False)
  check "async exception closes owned descriptor" descriptorClosed
  renameFile path (path++".old"); B.writeFile path html
  replaced <- resolveSnapshot r pins "main.html" [] size (8*1024*1024) digest
  check "same bytes replacement inode refused" (case replaced of Left _ -> True; _ -> False)
  removeFile path; createSymbolicLink "main.html.old" path
  link <- resolveSnapshot r pins "main.html" [] size (8*1024*1024) digest
  check "symlink replacement refused" (case link of Left _ -> True; _ -> False)
 case result of Left e -> print e >> exitFailure; Right () -> pure ()
