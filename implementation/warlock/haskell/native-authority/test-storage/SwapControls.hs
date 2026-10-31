{-# LANGUAGE OverloadedStrings #-}
-- Actual production hook after held-file sync, before name-based rename.
-- The target must not certify a different inode as the retained terminal.
module SwapControls (verifyNameSwap) where
import Control.Monad (unless)
import Data.Either (isLeft)
import qualified Data.ByteString as B
import System.Directory (createDirectory,renameFile)
import System.FilePath ((</>))
import System.Posix.Files (setFileMode)
import System.Posix.IO (OpenMode(ReadOnly),closeFd,defaultFileFlags,openFd)
import Warlock.Native.Cancellation.Internal (TerminalTicket,persistTerminalTicket)
import qualified Warlock.Native.Cancellation.Storage as S

verifyNameSwap :: FilePath -> TerminalTicket -> IO ()
verifyNameSwap root ticket = do
 let dir = root </> "name-swap"
     staging = dir </> ".warlock-cancel-terminal.tmp"
     displaced = dir </> "displaced-held-file"
 createDirectory dir
 setFileMode dir 0o700
 storage <- S.newStorageWithHookForTest (\stage -> if stage == S.Renaming then do
   renameFile staging displaced
   B.writeFile staging "different terminal bytes"
   setFileMode staging 0o600
  else pure ())
 fd <- openFd dir ReadOnly defaultFileFlags
 accepted <- S.offerDirectory storage fd
 unless accepted (closeFd fd >> ioError (userError "directory offer refused"))
 result <- persistTerminalTicket storage ticket
 _ <- S.retireStorage storage
 unless (isLeft result) (ioError (userError "replaced staging identity produced receipt"))
