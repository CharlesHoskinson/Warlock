{-# LANGUAGE OverloadedStrings #-}
-- Protected private /run/user fixture; no compositor/Wayland protocol contacted.
module Main (main) where
import Control.Exception (bracket, finally)
import Control.Monad (forM_, unless)
import qualified Network.Socket as S
import System.Directory (createDirectory, doesPathExist, removeDirectoryRecursive)
import System.Posix.Files (createSymbolicLink, removeLink, setFileMode, getSymbolicLinkStatus, fileOwner, fileMode, deviceID, fileID, isSocket)
import System.Posix.User (getRealUserID)
import Warlock.Ui.Display (resolveDisplayEnvironment)

check :: String -> Bool -> IO ()
check name good = do
 putStrLn (name ++ if good then "=PASS" else "=FAIL")
 unless good (ioError (userError name))

main :: IO ()
main = S.withSocketsDo $ do
 uid <- getRealUserID
 let runtime = "/run/user/" ++ show uid
     name = "wayland-warlock-display-control"
     path = runtime ++ "/" ++ name
     refused label dir display = resolveDisplayEnvironment dir display >>= check label . either (const True) (const False)
 empty <- resolveDisplayEnvironment Nothing Nothing
 check "no-display preserves hermetic non-GUI child" (empty == Right [])
 refused "runtime alone refused" (Just runtime) Nothing
 refused "display alone refused" Nothing (Just name)
 refused "foreign runtime refused" (Just "/run/user/0") (Just name)
 forM_ [0..255 :: Int] $ \seed -> do
  let tag = show (seed * 1103515245 + 12345)
      hostile = ["../wayland-" ++ tag, "/wayland-" ++ tag, "other-" ++ tag,
                 "wayland-../" ++ tag, "wayland-" ++ tag ++ "\0", "wayland-" ++ tag ++ "\n",
                 "wayland-" ++ replicate (57 + seed) 'x', "wayland-" ++ tag ++ "/socket"] !! (seed `mod` 8)
  refused ("hostile-name-seed-" ++ show seed) (Just runtime) (Just hostile)
 exists <- doesPathExist runtime
 check "isolated runtime fixture absent before creation" (not exists)
 createDirectory runtime
 setFileMode runtime 0o700
 flip finally (removeDirectoryRecursive runtime) $ do
  refused "missing socket refused" (Just runtime) (Just name)
  bracket (S.socket S.AF_UNIX S.Stream S.defaultProtocol) S.close $ \socket -> do
   S.bind socket (S.SockAddrUnix path)
   forM_ ["/", "/run", "/run/user",runtime,path] $ \observedPath -> do
    metadata <- getSymbolicLinkStatus observedPath
    putStrLn ("display_fixture_metadata=" ++ show (observedPath,fileOwner metadata,fileMode metadata,deviceID metadata,fileID metadata,isSocket metadata))
   accepted <- resolveDisplayEnvironment (Just runtime) (Just name)
   check "actual owned private Unix socket accepted" (accepted == Right [("XDG_RUNTIME_DIR",runtime),("WAYLAND_DISPLAY",name)])
   setFileMode runtime 0o755
   refused "shared runtime mode refused" (Just runtime) (Just name)
   setFileMode runtime 0o700
   createSymbolicLink name (runtime ++ "/wayland-link")
   refused "symlink endpoint refused" (Just runtime) (Just "wayland-link")
   removeLink (runtime ++ "/wayland-link")
   writeFile (runtime ++ "/wayland-file") "not a socket"
   refused "regular endpoint refused" (Just runtime) (Just "wayland-file")
  let boundary = "wayland-" ++ replicate 56 'a'
  bracket (S.socket S.AF_UNIX S.Stream S.defaultProtocol) S.close $ \socket -> do
   S.bind socket (S.SockAddrUnix (runtime ++ "/" ++ boundary))
   accepted <- resolveDisplayEnvironment (Just runtime) (Just boundary)
   check "64-character owned socket accepted" (either (const False) (const True) accepted)
   refused "65-character socket name refused" (Just runtime) (Just (boundary ++ "a"))
