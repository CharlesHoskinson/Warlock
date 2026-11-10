{-# LANGUAGE OverloadedStrings #-}
-- Protected private /run/user fixture; no compositor/Wayland protocol contacted.
module Main (main) where
import Control.Exception (bracket, finally)
import Control.Monad (forM, forM_, unless)
import qualified Network.Socket as S
import System.Directory (createDirectory, doesPathExist, removeDirectoryRecursive)
import System.Posix.Files (createSymbolicLink, removeLink, setFileMode, getSymbolicLinkStatus, fileOwner, fileMode, deviceID, fileID, isSocket)
import System.Posix.User (getRealUserID)
import System.Posix.Process (forkProcess, getProcessStatus, ProcessStatus(..), exitImmediately)
import System.Exit (ExitCode(..))
import Warlock.Ui.Display (resolveDisplayEnvironment, captureDisplayTransport, displayEnvironmentPairs, captureDisplayEnvironment)
import System.Environment (lookupEnv)
import qualified System.Environment.Blank as EnvironmentBlank
import Warlock.Ui.PrivateNetwork (enterPrivateNetwork)

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
   captured <- captureDisplayTransport (Just runtime) (Just name) >>= either
     (ioError . userError . show) pure
   child <- forkProcess $ do
    enterPrivateNetwork
    let retained = displayEnvironmentPairs captured
    exitImmediately (if retained == [("XDG_RUNTIME_DIR",runtime),("WAYLAND_DISPLAY",name)]
      then ExitSuccess else ExitFailure 1)
   status <- getProcessStatus True False child
   putStrLn ("display_namespace_child_status=" ++ show status)
   check "validated display settings survive actual private user/network namespace entry"
     (status == Just (Exited ExitSuccess))
   setFileMode runtime 0o755
   refused "shared runtime mode refused" (Just runtime) (Just name)
   check "captured settings are immutable; a fresh capture still applies strict checks"
     (displayEnvironmentPairs captured == [("XDG_RUNTIME_DIR",runtime),("WAYLAND_DISPLAY",name)])
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

  let privateParent = runtime ++ "/warlock-display-controls"
      privateRuntime = privateParent ++ "/session"
      privateName = "wayland-private"
  createDirectory privateParent
  setFileMode privateParent 0o700
  createDirectory privateRuntime
  setFileMode privateRuntime 0o700
  bracket (S.socket S.AF_UNIX S.Stream S.defaultProtocol) S.close $ \socket -> do
   S.bind socket (S.SockAddrUnix (privateRuntime ++ "/" ++ privateName))
   accepted <- resolveDisplayEnvironment (Just privateRuntime) (Just privateName)
   check "owned0700 canonical runtime descendant with relative endpoint accepted"
     (accepted == Right [("XDG_RUNTIME_DIR",privateRuntime),("WAYLAND_DISPLAY",privateName)])
   forM_ [privateRuntime ++ "/",privateParent ++ "//session",privateParent ++ "/./session",
          privateParent ++ "/../warlock-display-controls/session",runtime ++ "/../" ++ show uid,
          runtime ++ "/" ++ replicate 65 'x',runtime ++ concat (replicate 9 "/deep")] $ \bad ->
    refused "noncanonical or unbounded descendant refused" (Just bad) (Just privateName)
   refused "absolute display remains refused for owned descendant" (Just privateRuntime) (Just (privateRuntime ++ "/" ++ privateName))
   setFileMode privateParent 0o755
   refused "shared intermediate runtime ancestor refused" (Just privateRuntime) (Just privateName)
   setFileMode privateParent 0o700
   setFileMode privateRuntime 0o755
   refused "shared descendant runtime refused" (Just privateRuntime) (Just privateName)
   setFileMode privateRuntime 0o700
   createSymbolicLink "session" (privateParent ++ "/linked")
   refused "symlink intermediate descendant refused" (Just (privateParent ++ "/linked")) (Just privateName)
   removeLink (privateParent ++ "/linked")
   writeFile (privateParent ++ "/regular") "not a directory"
   refused "regular intermediate ancestor refused" (Just (privateParent ++ "/regular/child")) (Just privateName)

 ownedAccessibilityTransportControls

-- Optional AT transport crosses the existing public environment capture route.
-- These are real private pathname sockets, with no connection or bus service.
-- The protected runner must give this suite its existing isolated /run/user.
withSelectedEnvironment :: [(String,Maybe String)] -> IO a -> IO a
withSelectedEnvironment selected action = bracket
 (mapM (\(name,_) -> do value <- lookupEnv name; pure (name,value)) selected)
 (mapM_ put)
 (\_ -> mapM_ put selected >> action)
 where
 put (name,value) = do
  case value of
   Nothing -> EnvironmentBlank.unsetEnv name
   Just freshValue -> EnvironmentBlank.setEnv name freshValue True
  actual <- lookupEnv name
  check "selected fixture environment round-trip" (actual == value)

ownedAccessibilityTransportControls :: IO ()
ownedAccessibilityTransportControls = do
 uid <- getRealUserID
 let root = "/run/user/" ++ show uid
     runtime = root ++ "/warlock-at-transport-controls"
     name = "wayland-at-controls"
     path = runtime ++ "/a11y-bus"
     address = "unix:path=" ++ path
     ordinary = [("XDG_RUNTIME_DIR",runtime),("WAYLAND_DISPLAY",name)]
     observed selected = withSelectedEnvironment
       [("XDG_RUNTIME_DIR",Just runtime),("WAYLAND_DISPLAY",Just name)
       ,("AT_SPI_BUS_ADDRESS",selected)
       ,("DBUS_SESSION_BUS_ADDRESS",Just "unix:path=/unselected-ambient-bus")]
       (fmap (fmap displayEnvironmentPairs) captureDisplayEnvironment)
     verdict label action = do
       good <- action
       putStrLn ("owned-at:" ++ label ++ if good then "=PASS" else "=FAIL")
       pure good
     refused label value = verdict label (fmap (either (const True) (const False)) (observed (Just value)))
 exists <- doesPathExist root
 check "AT fixture isolated runtime absent" (not exists)
 createDirectory root
 setFileMode root 0o700
 flip finally (removeDirectoryRecursive root) $ do
  createDirectory runtime
  setFileMode runtime 0o700
  bracket (S.socket S.AF_UNIX S.Stream S.defaultProtocol) S.close $ \displaySocket -> do
   S.bind displaySocket (S.SockAddrUnix (runtime ++ "/" ++ name))
   absent <- verdict "absent-keeps-legacy-display-and-ignores-ambient-session" (fmap (== Right ordinary) (observed Nothing))
   missing <- refused "missing-selected-socket-refused" address
   bracket (S.socket S.AF_UNIX S.Stream S.defaultProtocol) S.close $ \atSocket -> do
    S.bind atSocket (S.SockAddrUnix path)
    present <- verdict "owned-at-address-survives-public-capture" (fmap (== Right (ordinary ++ [("AT_SPI_BUS_ADDRESS",address)])) (observed (Just address)))
    current <- verdict "capture-selects-no-session-or-system-bus" $ do
     value <- observed (Just address)
     pure (case value of
       Right pairs -> lookup "AT_SPI_BUS_ADDRESS" pairs == Just address
        && lookup "DBUS_SESSION_BUS_ADDRESS" pairs == Nothing
        && lookup "DBUS_SYSTEM_BUS_ADDRESS" pairs == Nothing
       Left _ -> False)
    hostile <- sequence
     [refused "empty-selection-refused" ""
     ,refused "abstract-address-refused" "unix:abstract=warlock-at"
     ,refused "tcp-address-refused" "tcp:host=127.0.0.1,port=12345"
     ,refused "multiple-addresses-refused" (address ++ ";unix:path=/tmp/bus")
     ,refused "guid-or-parameter-suffix-refused" (address ++ ",guid=" ++ replicate 32 '0')
     ,refused "relative-path-refused" "unix:path=a11y-bus"
     ,refused "ambient-user-bus-refused" ("unix:path=" ++ root ++ "/bus")
     ,refused "wrong-private-leaf-refused" ("unix:path=" ++ runtime ++ "/bus")
     ,refused "foreign-runtime-refused" "unix:path=/run/user/0/private/a11y-bus"
     ,refused "traversal-refused" ("unix:path=" ++ runtime ++ "/../a11y-bus")
     ,refused "overlong-refused" (address ++ replicate 4096 'x')]
    seeds <- forM [0..31 :: Int] $ \seed -> do
     let label = "literal-seed-" ++ show seed
         suffix = show (seed * 1103515245 + 12345)
     case seed `mod` 4 of
      0 -> verdict label (fmap (== Right (ordinary ++ [("AT_SPI_BUS_ADDRESS",address)])) (observed (Just address)))
      1 -> verdict label (fmap (== Right ordinary) (observed Nothing))
      2 -> refused label (address ++ ";unix:abstract=" ++ suffix)
      _ -> refused label ("unix:path=" ++ runtime ++ "/other-" ++ suffix)
    setFileMode runtime 0o755
    shared <- refused "shared-runtime-refused" address
    setFileMode runtime 0o700
    removeLink path
    createSymbolicLink name path
    linked <- refused "symlink-at-socket-refused" address
    removeLink path
    writeFile path "not a socket"
    regular <- refused "regular-at-endpoint-refused" address
    removeLink path
    unless (and ([absent,missing,present,current,shared,linked,regular] ++ hostile ++ seeds))
      (ioError (userError "owned AT transport capture controls failed"))
