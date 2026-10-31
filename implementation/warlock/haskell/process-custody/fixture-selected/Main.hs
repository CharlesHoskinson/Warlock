{-# LANGUAGE OverloadedStrings #-}
-- CPU fixture only. Literal expected identities are test data, never authority.
module Main (main) where
import Control.Exception (IOException,try)
import Control.Monad (forM,forM_,unless)
import qualified Crypto.Hash.SHA256 as SHA
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.List (isPrefixOf)
import Numeric (showHex)
import System.Directory (listDirectory)
import System.Environment (getArgs)
import System.Exit (ExitCode(ExitFailure),exitWith)
import System.IO (hFlush,stdout,stderr)
import System.IO.Error (isDoesNotExistError)
import System.Posix.Files (FileStatus,getFileStatus,getFdStatus,fileID,deviceID,fileSize,readSymbolicLink)
import System.Posix.IO (queryFdOption,FdOption(CloseOnExec))
import System.Posix.Types (Fd(..))
import Text.Read (readMaybe)

type Selected = (Int,Integer,Integer,Integer,String)
type Forbidden = (Integer,Integer)
check :: String -> Bool -> IO ()
check label yes = unless yes (ioError (userError label)) >> putStrLn (label++": PASS")
hex :: B.ByteString -> String
hex = concatMap (\n -> let s=showHex n "" in if length s==1 then '0':s else s) . B.unpack
main :: IO ()
main = do
 args <- getArgs
 (rows,forbidden,wantInput,failExit) <- case args of
  [a,b,input,mode] -> case (readMaybe a :: Maybe [Selected],readMaybe b :: Maybe [Forbidden]) of
   (Just selected,Just absent) | not (null selected) && length selected<=256 && mode `elem` ["ok","exit7"] -> pure (selected,absent,input,mode=="exit7")
   _ -> ioError (userError "invalid fixture declarations")
  _ -> ioError (userError "selected rows, forbidden identities, stdin, mode")
 check "selected destinations contiguous" (map (\(fd,_,_,_,_) -> fd) rows==[3..length rows+2])
 forM_ rows $ \(number,dev,ino,size,digest) -> do
  let fd=Fd (fromIntegral number)
  before <- getFdStatus fd
  closeOnExec <- queryFdOption fd CloseOnExec
  bytes <- B.readFile ("/proc/self/fd/"++show number)
  after <- getFdStatus fd
  check ("selected child descriptor "++show number) (toInteger (deviceID before)==dev && toInteger (fileID before)==ino && toInteger (fileSize before)==size && toInteger (deviceID after)==dev && toInteger (fileID after)==ino && toInteger (B.length bytes)==size && hex (SHA.hash bytes)==digest && not closeOnExec)
 names <- listDirectory "/proc/self/fd"
 observed <- forM names $ \name -> do
  got <- try (getFileStatus ("/proc/self/fd/"++name)) :: IO (Either IOException FileStatus)
  case got of
   Right st -> pure (Just (toInteger (deviceID st),toInteger (fileID st)))
   Left err | isDoesNotExistError err -> pure Nothing
            | otherwise -> ioError err
 check "unselected sentinel identities absent" (all (\identity -> Just identity `notElem` observed) forbidden)
 sockets <- forM names $ \name -> do
  got <- try (readSymbolicLink ("/proc/self/fd/"++name)) :: IO (Either IOException FilePath)
  case got of
   Right target -> pure ("socket:[" `isPrefixOf` target)
   Left err | isDoesNotExistError err -> pure False
            | otherwise -> ioError err
 check "no inherited sockets" (not (or sockets))
 input <- C.getContents
 check "explicit standard input" (input==C.pack wantInput)
 C.hPutStr stderr "selected-fd-child-stderr"
 hFlush stdout
 hFlush stderr
 if failExit then exitWith (ExitFailure 7) else pure ()
