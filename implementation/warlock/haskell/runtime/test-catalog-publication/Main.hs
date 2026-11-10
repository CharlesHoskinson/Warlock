{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Exception (throwIO)
import Control.Monad (unless)
import qualified Data.ByteString as B
import Data.IORef
import qualified Data.Set as Set
import qualified Warlock.Backend.Catalog as C
import Warlock.Backend (DirectoryPin(..))
import Warlock.Protocol.Identity (parseCounter)
import System.Directory (createDirectory)
import System.Environment (getArgs)
import System.FilePath ((</>))
import System.Posix.Files (getFileStatus,deviceID,fileID,setFileMode)

must :: Show e => Either e a -> IO a
must (Right x)=pure x
must (Left _) = ioError (userError "expected success")
check :: String -> Bool -> IO ()
check name good=unless good (ioError (userError name))
refused :: Either e a -> Bool
refused (Left _)=True
refused _=False
main :: IO ()
main = do
 [root] <- getArgs
 let dir=root </> "publication"; file=dir </> "sample.desktop"
 createDirectory dir
 setFileMode dir 0o700
 status <- getFileStatus dir
 let pin=DirectoryPin dir (fromIntegral (deviceID status)) (fromIntegral (fileID status))
     first="[Desktop Entry]\nType=Application\nName=Sample\nExec=app \"two words\"\nTerminal=true\n"
     second="[Desktop Entry]\nType=Application\nName=Changed\nExec=app second\n"
 one <- must (parseCounter False "1")
 two <- must (parseCounter False "2")
 wide <- must (parseCounter False "9007199254740993")
 B.writeFile file first
 catalog <- C.newCatalog [pin] "C" wide
 _ <- C.readCatalog catalog >>= must
 C.resolveDesktop catalog wide one "sample" >>= check "read-alone-not-published" . refused
 (_,_,failed) <- C.prepareCatalogPublication catalog >>= must
 C.publishCatalog failed (throwIO (userError "literal-send-failure")) >>= check "failed-send-not-published" . refused
 C.resolveDesktop catalog wide one "sample" >>= check "failure-no-resolution" . refused
 sends <- newIORef (0::Int)
 C.publishCatalog failed (modifyIORef' sends (+1)) >>= check "failed-token-not-replayed" . refused
 readIORef sends >>= check "replay-no-send" . (==0)
 (_,known,ready) <- C.prepareCatalogPublication catalog >>= must
 check "fixed-known-entry" (known==Set.singleton "sample")
 C.publishCatalog ready (modifyIORef' sends (+1)) >>= must
 actual <- C.resolveDesktop catalog wide one "sample" >>= must
 check "exact-root" (C.resolvedRoot actual==pin)
 check "exact-relative-source" (C.resolvedPath actual=="sample.desktop")
 check "exact-source-bytes" (C.resolvedBytes actual==first)
 check "raw-exec-preserved" (C.resolvedExec actual=="app \"two words\"")
 check "terminal-is-data" (C.resolvedTerminal actual=="true")
 C.resolveDesktop catalog one one "sample" >>= check "foreign-lifetime" . refused
 C.resolveDesktop catalog wide two "sample" >>= check "foreign-generation" . refused
 _ <- C.resolveDesktop catalog wide one "sample" >>= must
 B.writeFile file second
 C.resolveDesktop catalog wide one "sample" >>= check "changed-source-refused" . refused
 C.resolveDesktop catalog wide two "sample" >>= check "guess-next-not-published" . refused
 _ <- C.readCatalog catalog >>= must
 C.resolveDesktop catalog wide two "sample" >>= check "read-next-not-published" . refused
 (_,_,next) <- C.prepareCatalogPublication catalog >>= must
 C.publishCatalog next (pure ()) >>= must
 changed <- C.resolveDesktop catalog wide two "sample" >>= must
 check "valid-after-refusals" (C.resolvedBytes changed==second)
 (_,_,stopped) <- C.prepareCatalogPublication catalog >>= must
 retiredInside <- newIORef True
 C.publishCatalog stopped (C.retireCatalog catalog >>= writeIORef retiredInside) >>= check "retire-race-not-published" . refused
 readIORef retiredInside >>= check "busy-retirement-unconfirmed" . not
 C.resolveDesktop catalog wide two "sample" >>= check "retired-resolution-refused" . refused
 C.prepareCatalogPublication catalog >>= check "retired-prepare-refused" . refused
 C.retireCatalog catalog >>= check "settled-retire" 
 putStrLn "catalog-publication-controls: complete"
