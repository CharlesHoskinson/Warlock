{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Monad (unless)
import GHC.Clock (getMonotonicTimeNSec)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import System.Directory (createDirectory,removeFile)
import System.Environment (getArgs)
import System.FilePath ((</>))
import System.Posix.Files (deviceID,fileID,getSymbolicLinkStatus,setFileMode)
import Warlock.Backend (loadBackendConfig,newNotificationIssuer,provisionNotificationIssuer,reserveNotificationGeneration,retireNotificationIssuer,notificationGenerationText)
check :: String -> Bool -> IO ()
check s b = unless b (ioError (userError s))
left :: Either a b -> Bool
left (Left _) = True
left _ = False
writePrivate :: FilePath -> B.ByteString -> IO ()
writePrivate p b = B.writeFile p b >> setFileMode p 0o600
main :: IO ()
main = do
 args <- getArgs
 root <- case args of [r] -> pure r; _ -> ioError (userError "fixed fixture root required")
 let pins=root </> "pins"; config=root </> "startup.json"; slot=pins </> "notification-epoch"; lock=pins </> "notification-epoch.lock"; witness=pins </> "notification-deployment"
 createDirectory pins
 setFileMode pins 0o700
 st <- getSymbolicLinkStatus pins
 started <- getMonotonicTimeNSec
 let absoluteDeadline = started + 30000000000
 let body=B.concat ["{\"schema\":1,\"binding\":{\"lifetime\":\"1\",\"session\":\"1\",\"frontend\":\"1\"},\"deadlineMonotonicNs\":\"",C.pack (show absoluteDeadline),"\",\"ui\":{\"path\":\"/fixture\",\"device\":\"1\",\"inode\":\"1\",\"size\":\"1\",\"sha256\":\"",B.replicate 64 48,"\",\"arguments\":[],\"ancestors\":[]},\"catalogRoots\":[],\"pinsRoot\":{\"path\":",C.pack (show pins),",\"device\":\"",C.pack (show (deviceID st)),"\",\"inode\":\"",C.pack (show (fileID st)),"\"},\"locale\":\"C\"}"]
 writePrivate config body
 cfg <- loadBackendConfig config >>= either (ioError . userError . show) pure
 missingOwner <- newNotificationIssuer cfg
 missing <- reserveNotificationGeneration missingOwner
 check "missing lock or witness refuses" (left missing)
 _ <- retireNotificationIssuer missingOwner
 installer <- newNotificationIssuer cfg
 provisioned <- provisionNotificationIssuer installer
 check "explicit provision" (either (const False) (const True) provisioned)
 done <- retireNotificationIssuer installer
 check "installer retired" done
 w <- B.readFile witness
 check "permanent witness bytes" (w=="warlock-notification-deployment-v1\n")
 r0 <- B.readFile slot
 check "initial epoch bytes" (r0=="warlock-notification-epoch-v1\n0\n")
 secondInstall <- newNotificationIssuer cfg
 again <- provisionNotificationIssuer secondInstall
 check "EEXIST never resets" (left again)
 _ <- retireNotificationIssuer secondInstall
 a <- newNotificationIssuer cfg
 one <- reserveNotificationGeneration a
 check "reserve one" (either (const False) (const True) one)
 check "returned generation literal 1" (case one of Right x -> notificationGenerationText x=="1"; _ -> False)
 duplicateHandle <- newNotificationIssuer cfg
 duplicateReserve <- reserveNotificationGeneration duplicateHandle
 check "second live handle refused" (left duplicateReserve)
 _ <- retireNotificationIssuer duplicateHandle
 b1 <- B.readFile slot
 check "literal one" (b1=="warlock-notification-epoch-v1\n1\n")
 check "retire first handle" =<< retireNotificationIssuer a
 b <- newNotificationIssuer cfg
 two <- reserveNotificationGeneration b
 check "new handle distinct generation" (case (one,two) of (Right x,Right y) -> x/=y; _ -> False)
 check "returned generation literal 2" (case two of Right x -> notificationGenerationText x=="2"; _ -> False)
 check "retire second handle" =<< retireNotificationIssuer b
 removeFile lock
 c <- newNotificationIssuer cfg
 noLock <- reserveNotificationGeneration c
 check "normal startup does not recreate lock" (left noLock)
 blocked <- reserveNotificationGeneration c
 check "failed owner refuses replay" (left blocked)
 _ <- retireNotificationIssuer c
 installer2 <- newNotificationIssuer cfg
 reset <- provisionNotificationIssuer installer2
 check "witness blocks resetting absent lock" (left reset)
 _ <- retireNotificationIssuer installer2
 writePrivate lock ""
 removeFile slot
 d <- newNotificationIssuer cfg
 noEpoch <- reserveNotificationGeneration d
 check "missing epoch refuses" (left noEpoch)
 _ <- retireNotificationIssuer d
 writePrivate slot "warlock-notification-epoch-v1\n02\n"
 e <- newNotificationIssuer cfg
 corrupt <- reserveNotificationGeneration e
 check "corrupt refuses" (left corrupt)
 _ <- retireNotificationIssuer e
 writePrivate slot "warlock-notification-epoch-v1\n18446744073709551615\n"
 f <- newNotificationIssuer cfg
 exhausted <- reserveNotificationGeneration f
 check "exhaustion refuses" (left exhausted)
 _ <- retireNotificationIssuer f
 writePrivate slot "warlock-notification-epoch-v1\n2\n"
 g <- newNotificationIssuer cfg
 validAgain <- reserveNotificationGeneration g
 check "fresh handle valid after refused input" (either (const False) (const True) validAgain)
 b3 <- B.readFile slot
 check "literal three" (b3=="warlock-notification-epoch-v1\n3\n")
 _ <- retireNotificationIssuer g
 let marker = "\"deadlineMonotonicNs\":\""
     (prefix,selectedField) = B.breakSubstring marker body
     (_,valueEnd) = B.breakSubstring "\"" (B.drop (B.length marker) selectedField)
     expiredBody = prefix <> marker <> "1" <> valueEnd
     expiredConfig = root </> "expired-startup.json"
 check "fixture locates exact deadline field" (not (B.null selectedField) && not (B.null valueEnd))
 writePrivate expiredConfig expiredBody
 expiredCfg <- loadBackendConfig expiredConfig >>= either (ioError . userError . show) pure
 expiredIssuer <- newNotificationIssuer expiredCfg
 beforeExpired <- B.readFile slot
 refusedExpired <- reserveNotificationGeneration expiredIssuer
 check "expired absolute deadline refuses reservation" (left refusedExpired)
 check "expired reservation does not advance slot" . (==beforeExpired) =<< B.readFile slot
 _ <- retireNotificationIssuer expiredIssuer
 putStrLn "notification issuer fixture complete"
