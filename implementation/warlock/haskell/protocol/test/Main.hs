{-# LANGUAGE OverloadedStrings #-}
module Main (main) where
import Control.Concurrent (forkIO, newEmptyMVar,putMVar,takeMVar,readMVar)
import Control.Exception (SomeException,AsyncException(ThreadKilled),throwTo,try)
import Control.Monad (replicateM_,replicateM,forM_,void)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as C
import Data.IORef (newIORef,modifyIORef',readIORef,writeIORef)
import qualified Data.Text as T
import qualified Warlock.Protocol.Boundary.Internal as G
import qualified Warlock.Protocol.Codec as Codec
import Warlock.Protocol.Identity (binding,parseCounter,Binding)
import Paths_warlock_protocol (getDataFileName)
check :: String -> Bool -> IO ()
check label ok = if ok then putStrLn ("PASS " ++ label) else ioError (userError label)
owner :: String -> Either String Binding
owner session = do
 a <- either (Left . show) Right (parseCounter False "1")
 b <- either (Left . show) Right (parseCounter False (T.pack session))
 c <- either (Left . show) Right (parseCounter False "3")
 either (Left . show) Right (binding a b c)
fixture :: FilePath -> IO B.ByteString
fixture name = getDataFileName ("test/fixtures/" ++ name) >>= B.readFile
main :: IO ()
main = do
 current <- either (ioError . userError) pure (owner "2")
 calls <- newIORef (0 :: Int)
 gate <- G.newGate current (\_ -> modifyIORef' calls (+1))
 good <- fixture "valid-negotiate.bin"
 hello <- fixture "valid-hello.bin"
 prepare <- fixture "valid-prepare.bin"
 one <- G.dispatch gate G.FromElm good
 two <- G.dispatch gate G.FromNative hello
 three <- G.dispatch gate G.FromElm prepare
 check "client and server valid controls reach real handler" (one == Right () && two == Right () && three == Right ())
 readIORef calls >>= check "positive handler exactly three times" . (==3)
 routed <- newIORef Nothing
 routing <- G.newGate current (writeIORef routed . Just . G.foldEnvelope Codec.encodeClientChecked Codec.encodeServerChecked)
 let v2Hello = "{\"version\":2,\"kind\":\"hello\",\"body\":{\"binding\":{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"}}}"
 v2Result <- G.dispatch routing G.FromNative v2Hello
 v2Routed <- readIORef routed
 check "v2 server positive reaches typed data routing" (v2Result == Right () && case v2Routed of Just (Right bytes) -> "\"version\":2" `B.isInfixOf` bytes; _ -> False)
 check "nonnumeric version is malformed schema" (G.decodeFor current G.FromElm "{\"version\":false,\"kind\":\"negotiate\",\"body\":{}}" == Left G.BadSchema)
 files <- mapM fixture ["invalid-duplicate-key.bin","invalid-extra-field.bin","invalid-version-unknown.bin","invalid-context-lifetime.bin","invalid-kind-unknown.bin","invalid-version-boolean.bin"]
 let badInputs = files ++ [B.pack [255], C.pack "{", B.replicate 65537 32, B.replicate 17 91 <> B.replicate 17 93, B.pack [0], C.pack "{\"version\":3,\"kind\":\"negotiate\",\"body\":{}}"]
 outcomes <- mapM (G.dispatch gate G.FromElm) badInputs
 check "all malformed client inputs refused" (all isLeft outcomes)
 malformedServer <- G.dispatch gate G.FromNative (C.pack "{\"version\":1,\"version\":1,\"kind\":\"hello\",\"body\":{}}")
 check "native duplicate key refused" (malformedServer == Left G.DuplicateField)
 invalidServer <- G.dispatch gate G.FromNative (C.pack "{\"version\":9,\"kind\":\"hello\",\"body\":{}}")
 check "native unsupported refused" (invalidServer == Left G.UnsupportedVersion)
 foreignGate <- either (ioError . userError) pure (owner "1") >>= \b -> G.newGate b (\_ -> modifyIORef' calls (+1))
 stale <- G.dispatch foreignGate G.FromElm good
 check "foreign current binding refused" (stale == Left G.ForeignBinding)
 history <- fixture "history-valid-positional-key.bin"
 hist <- G.dispatch gate G.FromNative history
 check "real SHA checked history accepted" (hist == Right ())
 lookupRequest <- fixture "lookup-v2-request-live.bin"
 lookupReply <- fixture "lookup-v2-result-absent.bin"
 wrongKey <- fixture "lookup-v2-wrong-key.bin"
 lookupOne <- G.dispatch foreignGate G.FromElm lookupRequest
 lookupTwo <- G.dispatch foreignGate G.FromNative lookupReply
 lookupBad <- G.dispatch foreignGate G.FromNative wrongKey
 check "v2 real SHA lookup client/server and wrong digest" (lookupOne == Right () && lookupTwo == Right () && lookupBad == Left G.BadDigest)
 readIORef calls >>= check "only six valid dispatches" . (==6)
 reasons <- G.rejectionReasons gate
 check "rejection reasons retained and typed" (length reasons == length badInputs + 2 && G.UnsupportedVersion `elem` reasons && G.BadUtf8 `elem` reasons && G.DuplicateField `elem` reasons)
 replicateM_ 10000 (G.dispatch gate G.FromElm "{" >> pure ())
 G.rejectionReasons gate >>= check "bounded reason history" . ((==128) . length)
 closed <- G.retire gate
 after <- G.dispatch gate G.FromElm good
 check "retired gate refuses future valid input" (closed == G.Retired && after == Left G.GateRetired)
 entered <- newEmptyMVar; finish <- newEmptyMVar; done <- newEmptyMVar
 concurrent <- G.newGate current (\_ -> putMVar entered () >> takeMVar finish)
 _ <- forkIO (G.dispatch concurrent G.FromElm good >>= putMVar done)
 takeMVar entered
 during <- G.retire concurrent
 blocked <- G.dispatch concurrent G.FromElm good
 check "admitted callback remains owned while retirement blocks new calls" (during == G.Draining 1 && blocked == Left G.GateRetired)
 putMVar finish (); final <- takeMVar done; settled <- G.gateStatus concurrent
 check "retirement waits for callback accounting" (final == Right () && settled == G.Retired)
 enteredAsync <- newEmptyMVar; blockAsync <- newEmptyMVar; finishedAsync <- newEmptyMVar
 interrupted <- G.newGate current (\_ -> putMVar enteredAsync () >> takeMVar blockAsync)
 thread <- forkIO $ do
  outcome <- try (G.dispatch interrupted G.FromElm good) :: IO (Either SomeException (Either G.Reason ()))
  putMVar finishedAsync outcome
 takeMVar enteredAsync
 asyncRetire <- G.retire interrupted
 throwTo thread ThreadKilled
 asyncResult <- takeMVar finishedAsync
 asyncStatus <- G.gateStatus interrupted
 asyncReasons <- G.rejectionReasons interrupted
 check "ThreadKilled rethrown after retirement accounting" (asyncRetire == G.Draining 1 && isException asyncResult && asyncStatus == G.Retired && asyncReasons == [G.HandlerFailed])
 failing <- G.newGate current (\_ -> ioError (userError "private failure"))
 raised <- try (G.dispatch failing G.FromElm good) :: IO (Either SomeException (Either G.Reason ()))
 status <- G.retire failing; logs <- G.rejectionReasons failing
 check "handler failure recorded and rethrown after accounting" (isException raised && status == G.Retired && logs == [G.HandlerFailed])
 -- Exercise the actual configured cap, not a smaller model-only threshold.
 started <- newEmptyMVar
 release <- newEmptyMVar
 capacity <- G.newGate current (\_ -> putMVar started () >> readMVar release)
 completions <- replicateM 64 newEmptyMVar
 forM_ completions $ \cell -> void $ forkIO $ do
  result <- try (G.dispatch capacity G.FromElm good) :: IO (Either SomeException (Either G.Reason ()))
  putMVar cell result
 replicateM_ 64 (takeMVar started)
 full <- G.gateStatus capacity
 overflow <- G.dispatch capacity G.FromElm good
 draining <- G.retire capacity
 denied <- G.dispatch capacity G.FromElm good
 check "all64 slots owned and new work refused during drain" (full == G.Live 64 && overflow == Left G.GateBusy && draining == G.Draining 64 && denied == Left G.GateRetired)
 putMVar release ()
 completed <- mapM takeMVar completions
 empty <- G.gateStatus capacity
 check "all64 callbacks settle before retirement" (all successful completed && empty == G.Retired)
 where
  isLeft (Left _) = True
  isLeft _ = False
  isException (Left _) = True
  isException _ = False
  successful (Right (Right ())) = True
  successful _ = False
