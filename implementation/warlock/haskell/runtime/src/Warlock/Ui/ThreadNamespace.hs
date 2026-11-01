-- Linux rejects CLONE_THREAD when the calling thread has a different PID
-- namespace selected for children. Check before entering a threaded library.
-- Contract: unreadable or incompatible kernel identities fail closed.
module Warlock.Ui.ThreadNamespace (requireThreadCompatibleNamespace) where
import Control.Exception (IOException, try)
import System.Posix.Files (deviceID, fileID, getFileStatus)

requireThreadCompatibleNamespace :: IO ()
requireThreadCompatibleNamespace = do
  identities <- try $ do
    current <- getFileStatus "/proc/thread-self/ns/pid"
    children <- getFileStatus "/proc/thread-self/ns/pid_for_children"
    pure ((deviceID current, fileID current) == (deviceID children, fileID children))
  case identities :: Either IOException Bool of
    Right True -> pure ()
    _ -> ioError (userError "GTK thread PID namespace incompatible or unavailable")

