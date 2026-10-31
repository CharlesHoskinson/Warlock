{-# LANGUAGE OverloadedStrings #-}
-- Test fixture only: uses the real validated resolver route, no raw FD issuer.
module VerifiedFixture (validatedFixtureLease) where
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Numeric (showHex)
import System.FilePath ((</>))
import System.Posix.Files (deviceID,fileID,getFileStatus)
import Warlock.Platform.Executable
import Warlock.Platform.Resolver

validatedFixtureLease :: FilePath -> FilePath -> IO HeldExecutable
validatedFixtureLease rootDir name = do
 rootStat <- getFileStatus rootDir
 fileStat <- getFileStatus (rootDir </> name)
 bytes <- B.readFile (rootDir </> name)
 let ident st = Identity (toInteger (deviceID st)) (toInteger (fileID st))
     pins = [Pin (C.pack ('/':name)) (ident fileStat) Regular]
     hex n = let s = showHex n "" in if length s == 1 then '0':s else s
     digest = C.pack (concatMap hex (B.unpack (SHA.hash bytes)))
 result <- withRoot (C.pack rootDir) (ident rootStat) $ \root -> do
  lease <- newExecutableLease
  validated <- acquireExecutableLease lease root pins (C.pack name) [] (toInteger (B.length bytes)) digest UiImage
  case validated of
   Left e -> ioError (userError (show e))
   Right () -> do
    issued <- issueReadyExecutable lease
    case issued of Nothing -> ioError (userError "validated fixture issuance failed"); Just (held,_,_) -> pure held
 case result of Left e -> ioError (userError (show e)); Right held -> pure held
