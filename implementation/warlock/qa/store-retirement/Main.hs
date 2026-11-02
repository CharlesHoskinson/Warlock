module Main (main) where

import Control.Monad (unless)
import Data.Bits ((.&.))
import System.Directory (listDirectory)
import System.Environment (getArgs)
import System.FilePath (isAbsolute)
import System.Posix.Files
  (deviceID, fileID, fileMode, fileOwner, getSymbolicLinkStatus, isDirectory)
import System.Posix.User (getEffectiveUserID)
import Warlock.Backend.Store (DirectoryPin(..), storeRetirementControls)

-- Root-only isolated QA Store variant. The shipping library does not export
-- storeRetirementControls. Root supplies a fresh retained owned namespace.
main :: IO ()
main = do
  args <- getArgs
  root <- case args of
    [path] | isAbsolute path -> pure path
    _ -> ioError (userError "expected one fresh owned0700 absolute QA directory")
  status <- getSymbolicLinkStatus root
  uid <- getEffectiveUserID
  entries <- listDirectory root
  unless (isDirectory status && fileOwner status == uid && fileMode status .&. 0o7777 == 0o700 && null entries)
    (ioError (userError "QA directory must be fresh owned0700"))
  let pin=DirectoryPin root (toInteger (deviceID status)) (toInteger (fileID status))
  storeRetirementControls pin
  putStrLn "Store acquisition/publication and settled-only controls passed"
