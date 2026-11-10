{-# LANGUAGE ForeignFunctionInterface #-}
module Main (main) where

import Control.Monad (unless)
import Foreign.C.Types (CInt(..), CUInt(..), CULong(..), CSize(..))
import Foreign.Storable (sizeOf)
import ProviderProbeContract (Observation(..), qualify)
import ProviderProbeHeaders (compiledVersion, compiledLayout, compiledWidths, compiledAarch64)
import qualified Warlock.Ui.WebKitABI as Existing
import System.Environment (getArgs)
import System.Exit (exitFailure)

-- The only authored calls into GTK/WebKit/GLib in this executable.
-- No GTK initialization, object construction, page load, display or helper call.
foreign import ccall unsafe "webkit_get_major_version" majorVersion :: IO CUInt
foreign import ccall unsafe "webkit_get_minor_version" minorVersion :: IO CUInt
foreign import ccall unsafe "webkit_get_micro_version" microVersion :: IO CUInt

triple :: (Int,Int,Int) -> String
triple (a,b,c) = show [a,b,c]

quadruple :: (Int,Int,Int,Int) -> String
quadruple (a,b,c,d) = show [a,b,c,d]

render :: Observation -> Either String () -> String
render observed result =
  "{\"schema\":1,\"kind\":\"fixed-webkit-version-header-abi\"," ++
  "\"runtimeVersion\":" ++ triple (runtimeVersion observed) ++
  ",\"headerVersion\":" ++ triple (headerVersion observed) ++
  ",\"headerLayout\":" ++ triple (headerLayout observed) ++
  ",\"existingLayout\":" ++ triple (existingLayout observed) ++
  ",\"headerWidths\":" ++ quadruple (headerWidths observed) ++
  ",\"haskellWidths\":" ++ quadruple (haskellWidths observed) ++
  ",\"headerAarch64\":" ++ (if headerAarch64 observed then "true" else "false") ++
  ",\"passed\":" ++ (either (const "false") (const "true") result) ++
  ",\"error\":" ++ either show (const "null") result ++
  ",\"providerQualified\":false,\"cleanupQualified\":false,\"inputQualified\":false," ++
  "\"nativeAcceptance\":false,\"originalAcceptance\":false}"

main :: IO ()
main = do
  arguments <- getArgs
  unless (null arguments) (ioError (userError "probe takes no arguments"))
  major <- majorVersion
  minor <- minorVersion
  micro <- microVersion
  let observed = Observation
        (fromIntegral major, fromIntegral minor, fromIntegral micro)
        compiledVersion compiledLayout
        (Existing.gValueSize, Existing.gValueAlignment, Existing.enumValueOffset)
        compiledWidths
        (sizeOf (0 :: CInt), sizeOf (0 :: CUInt), sizeOf (0 :: CULong), sizeOf (0 :: CSize))
        compiledAarch64
      result = qualify observed
  putStrLn (render observed result)
  either (const exitFailure) pure result
