-- Root-only source fixture: execute against canonical built package units.
-- The child executable, expected digest and size are independently selected.
module Main (main) where
import Control.Exception (bracket)
import Control.Monad (unless)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import System.Environment (getArgs)
import System.FilePath ((</>), takeFileName)
import System.IO (Handle, hClose, hFlush, hPutStrLn)
import System.Posix.Files (deviceID, fileID, getFileStatus)
import System.Posix.IO (createPipe, fdToHandle)
import Text.Read (readMaybe)
import Warlock.Capture.Process.Bootstrap
import Warlock.Platform.Executable
  ( LeaseRole(..), newExecutableLease, acquireExecutableLease
  , issueReadyExecutable, retireExecutableLease )
import Warlock.Platform.Resolver (Identity(..), Kind(..), Pin(..), withRoot)

check :: Bool -> String -> IO ()
check ok message = unless ok (ioError (userError message))
main :: IO ()
main = do
 args <- getArgs
 case args of
  [directory,name,sizeText,digest] -> case readMaybe sizeText of
   Just size | size > 0 && takeFileName name == name -> run directory name size (C.pack digest)
   _ -> ioError (userError "invalid fixture size or basename")
  _ -> ioError (userError "expected root basename expected-size expected-sha256")
run :: FilePath -> FilePath -> Integer -> B.ByteString -> IO ()
run directory name size digest = do
 rootStatus <- getFileStatus directory
 imageStatus <- getFileStatus (directory </> name)
 let ident st = Identity (toInteger (deviceID st)) (toInteger (fileID st))
     pins = [Pin (C.pack ('/':name)) (ident imageStatus) Regular]
 result <- withRoot (C.pack directory) (ident rootStatus) $ \root -> do
  lease <- newExecutableLease
  acquired <- acquireExecutableLease lease root pins (C.pack name) [] size digest UiImage
  check (acquired == Right ()) "resolver refused selected child"
  issued <- issueReadyExecutable lease
  case issued of
   Nothing -> ioError (userError "selected lease not issued")
   Just (held,_,_) -> do
    exercise held
    retired <- retireExecutableLease lease
    check (retired == Right ()) "validated lease retirement"
 case result of
  Left err -> ioError (userError (show err))
  Right () -> pure ()

exercise :: HeldExecutable -> IO ()
exercise held = do
 (readEnd,writeEnd) <- createPipe
 reader <- fdToHandle readEnd
 writer <- fdToHandle writeEnd
 bracket (pure writer) hClose $ \controlWriter -> do
  ticket <- newTransferTicket reader
  plan <- either (ioError . userError . show) pure $
    selectedHeld held [] ticket [("LC_ALL","C"),("LANG","C"),("PATH","/usr/bin")]
  deadline <- deadlineAfter 5000000 >>= either (ioError . userError . show) pure
  owner <- newOwner
  result <- runSelectedDetailed owner plan 65536 deadline (conversation controlWriter)
  check (selectedCustody result == Available) "owner did not settle"
  check (case selectedOperation result of Right _ -> True; Left _ -> False) "selected child did not finish successfully"
  check (selectedContainment result /= SignalStateUnknown) "leader observation unavailable"
  disposition <- transferDisposition ticket
  case disposition of
   CallerOwned -> do
    closed <- closeCallerTransfer ticket
    check (closed == Right ()) "caller ticket cleanup failed"
   TransferClosed -> pure ()
   _ -> ioError (userError "ticket still owned or uncertain")

conversation :: Handle -> Session -> IO (Either ToolError ())
conversation writer session = do
 first <- observeSession session
 case first of
  Left err -> pure (Left err)
  Right observed -> do
   second <- observeSession session
   case second of
    Right same | same == observed && observedPid observed > 0 && not (B.null (observedStart observed)) -> do
     hPutStrLn writer "finish"
     hFlush writer
     awaitLeader session
    _ -> pure (Left SpawnOrIO)
