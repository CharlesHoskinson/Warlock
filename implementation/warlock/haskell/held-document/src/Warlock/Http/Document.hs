{-# LANGUAGE ForeignFunctionInterface #-}
module Warlock.Http.Document (prepareHtml) where
import Control.Exception (bracket)
import Control.Monad (unless)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.Char (isHexDigit)
import Foreign
import Foreign.C
import Warlock.Platform.Resolver (Root, Pin, resolveSnapshot)
type Object = Ptr ()
foreign import ccall unsafe "g_compute_checksum_for_data" checksumText :: CInt -> Ptr CUChar -> CSize -> IO CString
foreign import ccall unsafe "g_checksum_new" checksumNew :: CInt -> IO Object
foreign import ccall unsafe "g_checksum_update" checksumUpdate :: Object -> Ptr CUChar -> CLong -> IO ()
foreign import ccall unsafe "g_checksum_get_digest" checksumDigest :: Object -> Ptr CUChar -> Ptr CSize -> IO ()
foreign import ccall unsafe "g_checksum_free" checksumFree :: Object -> IO ()
foreign import ccall unsafe "g_base64_encode" base64Encode :: Ptr CUChar -> CSize -> IO CString
foreign import ccall unsafe "g_free" gFree :: Ptr a -> IO ()
require :: Bool -> String -> IO ()
require yes reason = unless yes (ioError (userError reason))
nonNull :: String -> IO (Ptr a) -> IO (Ptr a)
nonNull label action = do
  p <- action
  require (p /= nullPtr) (label ++ " returned null")
  pure p

maxHtmlBytes :: Int
maxHtmlBytes = 8 * 1024 * 1024

sha256 :: B.ByteString -> IO String
sha256 bytes = B.useAsCStringLen bytes $ \(pointer, count) ->
  bracket (nonNull "SHA256" (checksumText 2 (castPtr pointer) (fromIntegral count))) gFree peekCString

inlineHash :: B.ByteString -> IO String
inlineHash bytes = bracket (nonNull "checksum context" (checksumNew 2)) checksumFree $ \context ->
  B.useAsCStringLen bytes $ \(pointer, count) -> do
    checksumUpdate context (castPtr pointer) (fromIntegral count)
    allocaBytes 32 $ \digest -> alloca $ \size -> do
      poke size 32
      checksumDigest context digest size
      actual <- peek size
      require (actual == 32) "Unexpected SHA256 digest length"
      bracket (nonNull "base64 digest" (base64Encode digest 32)) gFree peekCString

-- Deliberately accept only the single bare-script/single bare-style compiler HTML shape.
-- An unfamiliar compiler output is a prerequisite failure, not permissive fallback.
extractOne :: String -> B.ByteString -> IO B.ByteString
extractOne tag bytes = do
  let opening = C.pack ("<" ++ tag ++ ">")
      closing = C.pack ("</" ++ tag ++ ">")
      (_, found) = B.breakSubstring opening bytes
  require (not (B.null found)) ("Missing exact " ++ tag ++ " opening")
  let content = B.drop (B.length opening) found
      (inside, end) = B.breakSubstring closing content
  require (not (B.null end)) ("Missing " ++ tag ++ " close")
  let after = B.drop (B.length closing) end
  require (not (opening `B.isInfixOf` after) && not (closing `B.isInfixOf` after)) ("Multiple " ++ tag ++ " blocks")
  pure inside

-- Exact wrapper observed from pinned Elm 0.19.2 standalone output. Unknown
-- document shapes are refused; the caller must still establish artifact provenance.
validateCompilerShape :: B.ByteString -> B.ByteString -> B.ByteString -> IO ()
validateCompilerShape bytes script style = do
  let prefix = C.pack "<!DOCTYPE HTML>\n<html>\n<head>\n  <meta charset=\"UTF-8\">\n  <title>"
      titleClose = C.pack "</title>\n  <style>"
  remainder <- maybe (ioError (userError "Unsupported compiler document shape")) pure (B.stripPrefix prefix bytes)
  let (title, _) = B.breakSubstring titleClose remainder
      titleChar c = (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_' || c == '.'
  require (not (B.null title) && B.length title <= 128 && C.all titleChar title) "Unsupported compiler document title"
  let expected = B.concat [prefix, title, titleClose, style,
        C.pack "</style>\n</head>\n\n<body>\n\n<pre id=\"elm\"></pre>\n\n<script>",
        script, C.pack "</script>\n\n</body>\n</html>"]
  require (bytes == expected) "Unsupported compiler document shape"

-- Root and pins must come from the caller's independently reviewed manifest.
-- All source descriptors are closed before resolveSnapshot returns its bytes.
prepareHtml :: Root -> [Pin] -> B.ByteString -> Integer -> String -> IO (B.ByteString, B.ByteString, B.ByteString)
prepareHtml root pins path declaredSize expected = do
  require (declaredSize > 0 && declaredSize <= toInteger maxHtmlBytes) "HTML declared size invalid"
  require (length expected == 64 && all isHexDigit expected && all (`notElem` ['A'..'F']) expected) "Expected SHA256 must be lowercase hex"
  observed <- resolveSnapshot root pins path [] declaredSize (toInteger maxHtmlBytes) (C.pack expected)
  bytes <- either (ioError . userError . ("HTML snapshot refused: " ++) . show) (pure . snd) observed
  require (not (B.null bytes) && B.length bytes <= maxHtmlBytes && not (B.elem 0 bytes)) "HTML empty, oversized or contains NUL"
  actual <- sha256 bytes
  require (actual == expected) "Reviewed HTML hash mismatch"
  scriptBytes <- extractOne "script" bytes
  styleBytes <- extractOne "style" bytes
  validateCompilerShape bytes scriptBytes styleBytes
  script <- inlineHash scriptBytes
  style <- inlineHash styleBytes
  pure (bytes, C.pack script, C.pack style)

