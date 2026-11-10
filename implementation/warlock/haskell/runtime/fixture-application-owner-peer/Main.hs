{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ForeignFunctionInterface #-}
module Main (main) where
import Control.Monad (unless)
import Data.IORef (newIORef,atomicModifyIORef')
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import qualified Data.Text.Encoding as TE
import Foreign.C.Error (throwErrnoIfMinus1_)
import Foreign.C.Types (CInt(..))
import System.IO (BufferMode(NoBuffering),hClose,hSetBinaryMode,hSetBuffering)
import System.Posix.IO (fdToHandle)
import System.Posix.Types (Fd(..))
import Warlock.Protocol.Codec (decodeServerCheckedWith,checkedDesktopReply,desktopProfile)
import qualified Warlock.Protocol.Desktop as D
import qualified Warlock.Protocol.Framing as F
import Warlock.Protocol.Identity (parseCounter)
foreign import ccall unsafe "shutdown" shutdownWrite :: CInt -> CInt -> IO CInt
must :: Show e => Either e a -> IO a
must = either (ioError . userError . show) pure
check :: String -> Bool -> IO ()
check name good = unless good (ioError (userError name))
owner :: B.ByteString
owner = "{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"}"
projection :: B.ByteString
projection = "{\"viewProtocol\":1,\"kind\":\"view-frame\",\"revision\":\"1\",\"views\":[],\"focusOwner\":null,\"popupOwner\":null,\"frame\":{\"surfaceProtocol\":2,\"publication\":\"1\",\"lease\":\"0\",\"mode\":\"closed\",\"status\":\"controlled owner fixture\",\"bar\":[],\"popup\":[]},\"announcer\":null,\"announcement\":null}"
commit :: B.ByteString -> B.ByteString
commit req = "{\"viewProtocol\":1,\"kind\":\"view-commit\",\"projection\":"<>projection<>",\"requests\":["<>req<>"],\"focus\":[]}"
launch :: B.ByteString -> B.ByteString -> B.ByteString -> B.ByteString
launch request generation entry = commit ("{\"protocolVersion\":3,\"kind\":\"application-launch\",\"binding\":"<>owner<>",\"intent\":{\"request\":\""<>request<>"\",\"lifetime\":\"1\",\"generation\":\""<>generation<>"\",\"entry\":\""<>entry<>"\"}}")
main :: IO ()
main = do
 h <- fdToHandle (Fd 0)
 hSetBinaryMode h True
 hSetBuffering h NoBuffering
 firstFrame <- newIORef True
 let receive = do
      header <- B.hGet h 4
      n <- must (F.desktopGatewayHeaderLength header)
      bytes <- B.hGet h n
      check "complete server frame" (B.length bytes==n)
      checked <- must (decodeServerCheckedWith desktopProfile bytes)
      maybe (ioError (userError "desktop reply required")) pure (checkedDesktopReply checked)
     exchange raw = do
      wire <- must (F.desktopGatewayPrefix raw)
      B.hPut h wire
      first <- atomicModifyIORef' firstFrame (\old -> (False,old))
      if first then do
       attachment <- receive
       check "actual producer advertises typed application availability" (D.applicationAvailability attachment==Just D.ApplicationLaunchAvailable)
      else pure ()
      receive
     outcome request generation entry expected = do
      reply <- exchange (launch request generation entry)
      counter <- must (parseCounter False (TE.decodeUtf8 request))
      case D.launchOutcome reply of
       Just (intent,observed) -> do
        check "reply request identity" (D.launchRequest intent==counter)
        check "literal launch outcome" (observed==expected)
       Nothing -> ioError (userError "launch outcome missing")
 _ <- exchange (commit ("{\"protocolVersion\":3,\"kind\":\"catalog-request\",\"binding\":"<>owner<>",\"requestId\":\"7\"}"))
 -- Actual invalid ELF resolves its pinned bytes, fails acquisition and closes.
 outcome "8" "1" "bad-recorder" (D.LaunchRefused D.NativeEntryUnavailable)
 -- That failed identity is consumed forever; cleanup must not reset frontier.
 outcome "8" "1" "ux003-recorder" (D.LaunchRefused D.RequestReuse)
 outcome "9" "1" "ux003-recorder" D.LaunchSubmitted
 outcome "10" "2" "ux003-recorder" (D.LaunchRefused D.NativeEntryUnavailable)
 outcome "11" "1" "ux003-recorder" D.LaunchSubmitted
 throwErrnoIfMinus1_ "shutdown" (shutdownWrite 0 1)
 hClose h
 C.putStrLn "application-owner-peer: complete"
