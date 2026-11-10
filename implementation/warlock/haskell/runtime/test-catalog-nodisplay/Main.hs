{-# LANGUAGE OverloadedStrings #-}
module Main (main) where

import Control.Exception (bracket)
import Control.Monad (unless)
import qualified Data.ByteString as B
import qualified Data.Set as Set
import qualified Data.Text.Encoding as TE
import System.Directory (createDirectory, listDirectory)
import System.Environment (getArgs)
import System.FilePath ((</>), isAbsolute)
import System.Posix.Files
  ( deviceID, fileID, getSymbolicLinkStatus, setFileMode )
import Warlock.Backend (DirectoryPin(..))
import qualified Warlock.Backend.Catalog as Catalog
import qualified Warlock.Protocol.Desktop as D
import Warlock.Protocol.Identity (parseCounter)

must :: Show e => Either e a -> IO a
must = either (ioError . userError . show) pure

check :: String -> Bool -> IO ()
check label ok = unless ok (ioError (userError ("failed: " ++ label)))

main :: IO ()
main = do
  args <- getArgs
  root <- case args of
    [path] | isAbsolute path -> pure path
    _ -> ioError (userError "expected absolute empty private fixture root")

  contents <- listDirectory root
  check "empty-root" (null contents)

  let high = root </> "high"
      low = root </> "low"
      file dir = dir </> "same.desktop"
      write dir bytes =
        B.writeFile (file dir) bytes >> setFileMode (file dir) 0o600
      visible = TE.encodeUtf8
        "[Desktop Entry]\nType=Application\nName=Café\nExec=/bin/echo \"two words\" --literal=\\\\value\n"
      changed = TE.encodeUtf8
        "[Desktop Entry]\nType=Application\nName=Café\nExec=/bin/echo \"other words\" --literal=\\\\value\n"
      suppressed = TE.encodeUtf8
        "[Desktop Entry]\nType=Application\nName=Café\nExec=/bin/echo \"two words\"\nNoDisplay=true\n"
      fallback = TE.encodeUtf8
        "[Desktop Entry]\nType=Application\nName=Lower\nExec=/bin/true\n"
      pin dir = do
        st <- getSymbolicLinkStatus dir
        pure (DirectoryPin dir (toInteger (deviceID st)) (toInteger (fileID st)))
      retire owner = Catalog.retireCatalog owner >>= check "owner-retired"

  createDirectory high
  createDirectory low
  setFileMode high 0o700
  setFileMode low 0o700
  write high visible
  write low fallback
  highPin <- pin high
  lowPin <- pin low

  one <- must (parseCounter False "1")
  two <- must (parseCounter False "2")
  three <- must (parseCounter False "3")
  four <- must (parseCounter False "4")
  entry <- must
    (D.catalogEntry "same" "Café" "application-x-executable" "" "" [])
  first <- must (D.catalogSnapshot one one [entry])
  omitted <- must (D.catalogSnapshot one two [])
  restored <- must (D.catalogSnapshot one three [entry])
  revised <- must (D.catalogSnapshot one four [entry])

  bracket (Catalog.newCatalog [highPin, lowPin] "C" one) retire $ \owner -> do
    initial <- Catalog.readCatalog owner >>= must
    check "visible-high-generation-1" (initial == (first, Set.singleton "same"))

    write high (B.pack [255])
    invalid <- Catalog.readCatalog owner
    check "invalid-utf8-refused" (case invalid of
      Left _ -> True
      Right _ -> False)

    write high visible
    recovered <- Catalog.readCatalog owner >>= must
    check "identical-valid-after-refusal-keeps-generation-1"
      (recovered == (first, Set.singleton "same"))

    write high suppressed
    hidden <- Catalog.readCatalog owner >>= must
    check "nodisplay-masks-lower-generation-2" (hidden == (omitted, Set.empty))
    B.readFile (file high) >>= check "nodisplay-source-bytes-unchanged" . (== suppressed)

    write high visible
    visibleAgain <- Catalog.readCatalog owner >>= must
    check "visible-again-generation-3"
      (visibleAgain == (restored, Set.singleton "same"))

    write high changed
    execChanged <- Catalog.readCatalog owner >>= must
    check "raw-exec-change-generation-4"
      (execChanged == (revised, Set.singleton "same"))
    B.readFile (file high) >>= check "escaped-exec-source-bytes-unchanged" . (== changed)

  putStrLn "catalog-nodisplay-controls: complete"
