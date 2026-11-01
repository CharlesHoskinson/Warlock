{-# LANGUAGE OverloadedStrings #-}
-- Trusted QA client. Sends complete Main commits unchanged, never extracts RPCs.
module Main (main) where

import Control.Exception (IOException, catch)
import Control.Concurrent (threadDelay)
import Control.Monad (forM, unless)
import qualified Data.ByteString as B
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Foreign.C.Error (Errno(..), eCONNRESET)
import GHC.IO.Exception (ioe_errno)
import System.Environment (getArgs)
import System.IO (BufferMode(NoBuffering), Handle, hClose, hSetBinaryMode, hSetBuffering)
import System.Posix.IO (OpenMode(WriteOnly), closeFd, creat, defaultFileFlags, exclusive, fdToHandle, openFd)
import System.Posix.Types (Fd(..))
import Warlock.Protocol.Codec (decodeServerCheckedWith, desktopProfile)
import qualified Warlock.Protocol.Framing as F
import qualified Warlock.Protocol.StrictJson as J

data Step = Step B.ByteString Int Bool
require :: Bool -> String -> IO ()
require yes label = unless yes (ioError (userError label))
must :: Show e => Either e a -> IO a
must = either (ioError . userError . show) pure
field :: T.Text -> [(T.Text,J.Json)] -> IO J.Json
field name values = maybe (ioError (userError "script field missing")) pure (lookup name values)
script :: B.ByteString -> IO [Step]
script bytes = do
  limits <- must (J.bounds (8*1024*1024) 16)
  root <- must (J.decodeStrict limits bytes)
  top <- must (J.exactObject ["schema","frames"] root)
  version <- field "schema" top
  require (version == J.JNumber "1") "script schema"
  frames <- field "frames" top
  case frames of
    J.JArray rows | length rows <= 32 -> forM rows $ \row -> do
      pairs <- must (J.exactObject ["wire","replies","refused"] row)
      w <- field "wire" pairs
      n <- field "replies" pairs
      r <- field "refused" pairs
      case (w,n,r) of
        (J.JString raw,J.JNumber count,J.JBool expectRefusal) ->
          case reads (T.unpack count) of
            [(expected,"")] | expected >= 0 && expected <= 16 && B.length (TE.encodeUtf8 raw) <= 2*1024*1024 -> pure (Step (TE.encodeUtf8 raw) expected expectRefusal)
            _ -> ioError (userError "script reply budget")
        _ -> ioError (userError "script typed fields")
    _ -> ioError (userError "script frame budget")

readFrame :: Handle -> IO B.ByteString
readFrame h = do
  header <- B.hGet h 4
  n <- must (F.desktopGatewayHeaderLength header)
  body <- B.hGet h n
  require (B.length body == n) "short real backend response"
  _ <- must (decodeServerCheckedWith desktopProfile body)
  pure body
refusal :: Handle -> IO ()
refusal h = (do
  header <- B.hGet h 4
  require (B.null header) "refused frame produced a reply") `catch` onlyReset
  where
    onlyReset :: IOException -> IO ()
    onlyReset err = case ioe_errno err of
      Just code | Errno code == eCONNRESET -> pure ()
      _ -> ioError err
-- Deliberate malformed/over-limit corpus must actually reach the production
-- receiver; a safe client-side encoder must not filter the negative controls.
wireFrame :: B.ByteString -> B.ByteString
wireFrame bytes = let n=B.length bytes
  in B.pack [fromIntegral (n `div` 16777216),fromIntegral (n `div` 65536),fromIntegral (n `div` 256),fromIntegral n] <> bytes

main :: IO ()
main = do
  args <- getArgs
  (input,output) <- case args of
    [a,b] | take 1 a == "/" && take 1 b == "/" -> pure (a,b)
    _ -> ioError (userError "expected trusted absolute SCRIPT OUTPUT paths")
  steps <- B.readFile input >>= script
  h <- fdToHandle (Fd 0)
  hSetBinaryMode h True
  hSetBuffering h NoBuffering
  replies <- fmap concat $ forM steps $ \(Step wire count expectRefusal) -> do
    let framed=wireFrame wire; (first,rest)=B.splitAt 3 framed
    B.hPut h first
    B.hPut h rest
    results <- mapM (const (readFrame h)) [1..count]
    if expectRefusal then refusal h else pure ()
    -- No invented ACK exists for presentation-only commits. Keep the selected
    -- producer alive briefly; the independent caller checks the real callback
    -- receipt instead of treating this liveness interval as an acknowledgement.
    if count==0 && not expectRefusal then threadDelay 100000 else pure ()
    pure results
  fd <- openFd output WriteOnly defaultFileFlags {creat=Just 0o600,exclusive=True}
  result <- fdToHandle fd `catch` (\err -> closeFd fd >> ioError (err :: IOException))
  B.hPut result (TE.encodeUtf8 (J.renderJson (J.JArray (map (J.JString . TE.decodeUtf8) replies))))
  hClose result
  hClose h
