module ProviderProbeContract (Observation(..), qualify) where

data Observation = Observation
  { runtimeVersion :: (Int,Int,Int)
  , headerVersion :: (Int,Int,Int)
  , headerLayout :: (Int,Int,Int)
  , existingLayout :: (Int,Int,Int)
  , headerWidths :: (Int,Int,Int,Int)
  , haskellWidths :: (Int,Int,Int,Int)
  , headerAarch64 :: Bool
  } deriving (Eq,Show)

-- Fixed qualification question; caller/configuration cannot widen the tuple.
qualify :: Observation -> Either String ()
qualify observed
  | runtimeVersion observed /= (2,54,2) = Left "runtime-version"
  | headerVersion observed /= (2,54,2) = Left "header-version"
  | headerLayout observed /= (24,8,0) = Left "header-layout"
  | existingLayout observed /= (24,8,0) = Left "existing-layout"
  | headerWidths observed /= (4,4,8,8) = Left "header-widths"
  | haskellWidths observed /= (4,4,8,8) = Left "haskell-widths"
  | not (headerAarch64 observed) = Left "architecture"
  | otherwise = Right ()
