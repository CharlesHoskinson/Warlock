{-# LANGUAGE OverloadedStrings #-}
module LifetimeOwnerControls (contenderControls,replacementControls) where
import Control.Monad (unless)
import qualified Data.ByteString as B
import System.Directory (renameFile)
import System.FilePath ((</>))
import System.Posix.Files (setFileMode)
import System.Posix.IO (OpenMode(ReadOnly),openFd,defaultFileFlags,closeFd)
import qualified Warlock.Native.Cancellation.PairStore as P
import qualified Warlock.Native.Cancellation.LifetimeOwner as L
import Warlock.Protocol.Identity (Binding,parseCounter)
check :: String -> Bool -> IO ()
check label ok = unless ok (ioError (userError label))
right :: Show e => Either e a -> IO a
right = either (ioError . userError . show) pure

-- The existing host already published and released its transient writer lock.
-- Each contender below opens a separate namespace and host-owner description.
contenderControls :: P.PairStore -> Binding -> FilePath -> IO ()
contenderControls store bound path = do
 -- A second host owner uses a genuinely independent namespace/lock open.
 zeroOwner <- right (parseCounter True "0")
 ownerContender <- P.newPairStore zeroOwner bound
 ownerContenderFd <- openFd path ReadOnly defaultFileFlags
 ownerContenderAccepted <- P.offerNamespace ownerContender ownerContenderFd
 unless ownerContenderAccepted (closeFd ownerContenderFd >> ioError (userError "ownerContender namespace not adopted"))
 ownershipBusy <- P.initializePairStore ownerContender
 check "host ownership stays exclusive after writer unlock" (ownershipBusy==Left (P.OwnerFailure L.Busy))
 ownerContenderStatus <- P.pairStatus ownerContender
 check "unacquired ownerContender remains retryable" (P.pairPhase ownerContenderStatus==P.Uninitialized)
 P.closeStorage store >>= right
 P.initializePairStore ownerContender >>= right
 P.closeStorage ownerContender >>= right

replacementControls :: P.PairStore -> FilePath -> IO ()
replacementControls replacedStore replacedPath = do
 let ownerName=replacedPath </> "host-owner.lock"
 renameFile ownerName (replacedPath </> "retained-host-owner.lock")
 B.writeFile ownerName B.empty
 setFileMode ownerName 0o600
 staleOwner <- P.claimPreparedWork replacedStore
 check "replaced lifetime owner cannot claim queued work" (case staleOwner of Left (P.OwnerFailure L.IdentityChanged) -> True; _ -> False)
 replacedStatus <- P.pairStatus replacedStore
 check "owner replacement quarantines and retains queued diagnostic" (P.pairPhase replacedStatus==P.Quarantined && map snd (P.transactions replacedStatus)==[P.Queued])
 P.closeStorage replacedStore >>= right
 replacement <- B.readFile ownerName
 check "cleanup does not remove unowned replacement lock" (B.null replacement)
