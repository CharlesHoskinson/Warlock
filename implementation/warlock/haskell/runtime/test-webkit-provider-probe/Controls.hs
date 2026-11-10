module Main (main) where

import Control.Monad (unless)
import ProviderProbeContract (Observation(..), qualify)

-- Independent literal expectations for this exact AArch64 LP64 tuple.
-- No FFI or header module is imported by these controls.
reference :: Observation
reference = Observation (2,54,2) (2,54,2) (24,8,0) (24,8,0) (4,4,8,8) (4,4,8,8) True

cases :: [(String, Observation, Either String ())]
cases =
  [ ("fixed-aarch64-tuple", reference, Right ())
  , ("old-runtime-micro", reference { runtimeVersion = (2,54,1) }, Left "runtime-version")
  , ("foreign-runtime-major", reference { runtimeVersion = (3,54,2) }, Left "runtime-version")
  , ("old-header-micro", reference { headerVersion = (2,54,1) }, Left "header-version")
  , ("wrong-header-layout", reference { headerLayout = (16,8,0) }, Left "header-layout")
  , ("wrong-header-alignment", reference { headerLayout = (24,4,0) }, Left "header-layout")
  , ("wrong-enum-offset", reference { headerLayout = (24,8,4) }, Left "header-layout")
  , ("existing-home-abi-differs", reference { existingLayout = (32,8,0) }, Left "existing-layout")
  , ("wrong-int-width", reference { headerWidths = (8,4,8,8) }, Left "header-widths")
  , ("wrong-uint-width", reference { haskellWidths = (4,8,8,8) }, Left "haskell-widths")
  , ("wrong-long-width", reference { headerWidths = (4,4,4,8) }, Left "header-widths")
  , ("wrong-size-width", reference { haskellWidths = (4,4,8,4) }, Left "haskell-widths")
  , ("foreign-architecture", reference { headerAarch64 = False }, Left "architecture")
  ]

main :: IO ()
main = do
  mapM_ (\(name, observed, expected) ->
    unless (qualify observed == expected) (ioError (userError name))) cases
  putStrLn "webkit-provider-probe-contract-controls: 13 complete"
