{-# LANGUAGE OverloadedStrings #-}
-- Root-only selected executable: fd 0 is the already activated owned socket.
module Main (main) where
import Control.Monad (unless)
import Control.Exception (IOException,catch,throwIO)
import Foreign.C.Error (Errno(..),eCONNRESET)
import GHC.IO.Exception (ioe_errno)
import qualified Data.ByteString as B
import System.Environment (lookupEnv)
import System.IO (Handle,BufferMode(NoBuffering),hSetBinaryMode,hSetBuffering)
import System.Posix.IO (fdToHandle)
import System.Posix.Types (Fd(..))
import Warlock.Protocol.Codec (decodeServerChecked)
import Warlock.Protocol.Framing (headerLength,prefix)

prepare :: B.ByteString
prepare = "{\"version\":1,\"kind\":\"prepare\",\"body\":{\"binding\":{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"},\"intent\":{\"request\":\"6\",\"generation\":\"7\",\"incarnation\":\"9007199254740993\",\"operation\":\"restore\",\"context\":{\"lifetime\":\"1\",\"epoch\":\"3\",\"output\":\"4\",\"revision\":\"5\"}},\"selectionId\":\"0123456789abcdef0123456789abcdef\"}}"

-- A complete checked server frame is an explicit root-fixture control/ACK.
-- A host-side refusal closes its endpoint; EOF here means only that closure,
-- never that a retained peer FD has independently reached EOF.
readControl :: Handle -> IO (Maybe B.ByteString)
readControl h = do
 header <- B.hGet h 4
 if B.null header then pure Nothing else do
  n <- either (ioError . userError . show) pure (headerLength header)
  body <- B.hGet h n
  unless (B.length body == n) (ioError (userError "short fixture control"))
  either (ioError . userError . show) (const (pure (Just body))) (decodeServerChecked body)

-- Refusal fixtures alone allow the exact kernel reset produced when the
-- receiver closes with an unread request body. Every other I/O error propagates.
readExpectedRefusal :: Handle -> IO (Maybe B.ByteString)
readExpectedRefusal h = readControl h `catch` resetOnly
 where
  resetOnly :: IOException -> IO (Maybe B.ByteString)
  resetOnly err = case ioe_errno err of
   Just number | Errno number == eCONNRESET -> pure Nothing
   _ -> throwIO err

main :: IO ()
main = do
 h <- fdToHandle (Fd 0)
 hSetBinaryMode h True
 hSetBuffering h NoBuffering
 mode <- lookupEnv "DEL010_MODE"
 start <- case mode of
  Just "immediate" -> pure (Just "positive")
  Just "controlled" -> readControl h
  Just "controlled-refusal" -> do
   reply <- readExpectedRefusal h
   case reply of
    Nothing -> pure Nothing
    Just _ -> ioError (userError "unexpected control in foreign-refusal fixture")
  _ -> ioError (userError "fixed fixture mode required")
 case start of
  Nothing -> pure ()
  Just command -> do
   frame <- either (ioError . userError . show) pure (prefix prepare)
   B.hPut h frame
   let expectedRefusal = "\"session\":\"3\"" `B.isInfixOf` command
   ack <- if expectedRefusal then readExpectedRefusal h else readControl h
   unless (maybe expectedRefusal (const True) ack) (ioError (userError "positive ACK missing"))
