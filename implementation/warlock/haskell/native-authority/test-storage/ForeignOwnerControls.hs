-- Root-only optional controls requiring an independently provisioned foreign
-- actual UID. They fail if the real OS fixture does not meet that premise.
module ForeignOwnerControls (foreignDirectory,foreignStagingFile) where
import Control.Monad (unless)
import Data.Either (isLeft)
import System.Directory (createDirectory)
import System.FilePath ((</>))
import System.Posix.Files (fileOwner,getFdStatus,getFileStatus,setFileMode,setOwnerAndGroup)
import System.Posix.IO (OpenMode(ReadOnly),closeFd,defaultFileFlags,openFd)
import System.Posix.Types (Fd,GroupID,UserID)
import System.Posix.User (getEffectiveUserID)
import Warlock.Native.Cancellation.Internal (TerminalTicket,persistTerminalTicket)
import qualified Warlock.Native.Cancellation.Storage as S

foreignDirectory :: Fd -> TerminalTicket -> IO ()
foreignDirectory fd ticket = do
 uid <- getEffectiveUserID
 stat <- getFdStatus fd
 unless (fileOwner stat /= uid) (closeFd fd >> ioError (userError "foreign directory fixture has same uid"))
 storage <- S.newStorage
 offered <- S.offerDirectory storage fd
 unless offered (closeFd fd >> ioError (userError "foreign directory offer refused"))
 result <- persistTerminalTicket storage ticket
 _ <- S.retireStorage storage
 unless (isLeft result) (ioError (userError "foreign directory accepted"))

-- The separately owned root harness must arrange real authority to change
-- only this temporary fixture's uid. No in-memory fake uid is accepted.
foreignStagingFile :: FilePath -> UserID -> GroupID -> TerminalTicket -> IO ()
foreignStagingFile root otherUid otherGid ticket = do
 uid <- getEffectiveUserID
 unless (otherUid /= uid) (ioError (userError "foreign file fixture has same uid"))
 let dir = root </> "foreign-file-owner"
     file = dir </> ".warlock-cancel-terminal.tmp"
 createDirectory dir
 setFileMode dir 0o700
 storage <- S.newStorageWithHookForTest (\stage -> if stage == S.Writing then do
   setOwnerAndGroup file otherUid otherGid
   actual <- getFileStatus file
   unless (fileOwner actual == otherUid) (ioError (userError "foreign uid not installed"))
  else pure ())
 fd <- openFd dir ReadOnly defaultFileFlags
 accepted <- S.offerDirectory storage fd
 unless accepted (closeFd fd >> ioError (userError "directory offer refused"))
 result <- persistTerminalTicket storage ticket
 _ <- S.retireStorage storage
 unless (isLeft result) (ioError (userError "foreign staging owner accepted"))
