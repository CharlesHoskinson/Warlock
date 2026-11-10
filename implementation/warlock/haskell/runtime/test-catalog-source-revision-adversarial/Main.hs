{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Exception (bracket)
import Control.Monad (unless)
import qualified Data.ByteString as B
import qualified Data.Set as Set
import System.Directory (createDirectory, listDirectory, removeFile)
import System.Environment (getArgs)
import System.FilePath ((</>), isAbsolute)
import System.Posix.Files (deviceID, fileID, getSymbolicLinkStatus, setFileMode)
import Warlock.Backend (DirectoryPin(..))
import qualified Warlock.Backend.Catalog as Catalog
import qualified Warlock.Protocol.Desktop as D
import Warlock.Protocol.Identity (parseCounter)

must :: Show e => Either e a -> IO a
must = either (ioError . userError . show) pure
check :: String -> Bool -> IO ()
check label ok = unless ok (ioError (userError label))

main :: IO ()
main = do
  args <- getArgs
  root <- case args of
    [path] | isAbsolute path -> pure path
    _ -> ioError (userError "expected absolute empty owned fixture root")
  listDirectory root >>= check "empty root" . null
  let high = root </> "high"
      low = root </> "low"
      file dir = dir </> "same.desktop"
      bytes = "[Desktop Entry]\nType=Application\nName=Example\nExec=/bin/true\n"
      write dir contents = B.writeFile (file dir) contents >> setFileMode (file dir) 0o600
      pin dir = do
        st <- getSymbolicLinkStatus dir
        pure (DirectoryPin dir (toInteger (deviceID st)) (toInteger (fileID st)))
      retire owner = Catalog.retireCatalog owner >>= check "owner retirement"
  createDirectory high
  createDirectory low
  setFileMode high 0o700
  setFileMode low 0o700
  write high bytes
  write low bytes
  hp <- pin high
  lp <- pin low
  one <- must (parseCounter False "1")
  two <- must (parseCounter False "2")
  three <- must (parseCounter False "3")
  four <- must (parseCounter False "4")
  entry <- must (D.catalogEntry "same" "Example" "application-x-executable" "" "" [])
  s1 <- must (D.catalogSnapshot one one [entry])
  s2 <- must (D.catalogSnapshot one two [entry])
  s3 <- must (D.catalogSnapshot one three [entry])
  s4 <- must (D.catalogSnapshot one four [entry])
  let ids = Set.singleton "same"
  bracket (Catalog.newCatalog [hp,lp] "C" one) retire $ \owner -> do
    initial <- Catalog.readCatalog owner >>= must
    check "initial high winner" (initial == (s1,ids))
    write low (B.pack [255])
    shadow <- Catalog.readCatalog owner >>= must
    check "malformed shadow remains invisible" (shadow == (s2,ids))
    removeFile (file high)
    invalid <- Catalog.readCatalog owner
    check "exposed malformed refused" (case invalid of Left _ -> True; Right _ -> False)
    write low bytes
    recovered <- Catalog.readCatalog owner >>= must
    check "valid after refusal" (recovered == (s3,ids))
    stable <- Catalog.readCatalog owner >>= must
    check "unchanged generation" (stable == (s3,ids))
    removeFile (file low)
    write high bytes
    moved <- Catalog.readCatalog owner >>= must
    check "same bytes different root advances revision" (moved == (s4,ids))
  putStrLn "catalog-source-revision-adversarial: complete"
