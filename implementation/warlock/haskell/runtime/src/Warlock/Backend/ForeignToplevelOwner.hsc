{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE ScopedTypeVariables #-}
-- A private, observation-only Wayland connection. Selection is startup data;
-- neither construction nor a snapshot grants compositor operation authority.
module Warlock.Backend.ForeignToplevelOwner
 ( EndpointSelection(..), AncestorPin(..), ProcessPin(..), ExecutablePin(..)
 , ForeignToplevelOwner, ObservationResult(..), Retirement(..)
 , withForeignToplevelOwner, readToplevelSnapshot
 ) where
#define _GNU_SOURCE 1
#include <wayland-client-core.h>
#include <wayland-client-protocol.h>
#include <wayland-util.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/types.h>
#include <poll.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
import Control.Concurrent (ThreadId,myThreadId,runInBoundThread)
import Control.Concurrent.MVar
import Control.Exception (SomeException,mask,mask_,try,bracket,finally,onException)
import Control.Monad (forM_,unless,when)
import qualified Data.ByteString as B
import qualified Data.ByteString.Char8 as BC
import Data.IORef
import qualified Data.Map.Strict as Map
import Data.Text (Text)
import qualified Data.Text.Encoding as TE
import Foreign
import Foreign.C
import System.FilePath (takeDirectory,takeFileName,(</>))
import System.IO (openBinaryFile,IOMode(ReadMode),hClose)
import qualified System.Posix.Files as Files
import System.Posix.Types (Fd(..))
import Text.Read (readMaybe)
import Warlock.Backend.Store (DirectoryPin(..))
import Warlock.Capture.Process.Bootstrap (AdmissionDeadline,remainingMicros)
import Warlock.Platform.Resolver (Identity(..),Pin,Link,Resolution(..),withRoot,resolveSnapshot)
import Warlock.Protocol.Identity (Counter)
import qualified Warlock.Protocol.ForeignToplevel as FT

type Proxy = Ptr ()
type Dispatcher = Ptr () -> Proxy -> CUInt -> Ptr () -> Ptr () -> IO CInt
foreign import ccall "wrapper" makeDispatcher :: Dispatcher -> IO (FunPtr Dispatcher)
foreign import ccall unsafe "gettid" kernelTid :: IO CInt
foreign import ccall unsafe "getpid" kernelPid :: IO CInt
foreign import ccall unsafe "socket" socketC :: CInt -> CInt -> CInt -> IO CInt
foreign import ccall unsafe "connect" connectC :: CInt -> Ptr () -> CUInt -> IO CInt
foreign import ccall unsafe "getsockopt" getsockoptC :: CInt -> CInt -> CInt -> Ptr () -> Ptr CUInt -> IO CInt
foreign import ccall unsafe "open" openC :: CString -> CInt -> IO CInt
foreign import ccall unsafe "openat" openatC :: CInt -> CString -> CInt -> IO CInt
foreign import ccall unsafe "close" closeC :: CInt -> IO CInt
foreign import ccall safe "poll" pollC :: Ptr () -> CULong -> CInt -> IO CInt
foreign import ccall unsafe "strnlen" strnlenC :: CString -> CSize -> IO CSize
foreign import ccall unsafe "wl_display_connect_to_fd" connectDisplay :: CInt -> IO Proxy
foreign import ccall unsafe "wl_display_disconnect" disconnectDisplay :: Proxy -> IO ()
foreign import ccall unsafe "wl_display_create_queue" createQueue :: Proxy -> IO (Ptr ())
foreign import ccall unsafe "wl_event_queue_destroy" destroyQueue :: Ptr () -> IO ()
foreign import ccall unsafe "wl_display_set_max_buffer_size" setBufferLimit :: Proxy -> CSize -> IO ()
foreign import ccall unsafe "wl_proxy_marshal_array_flags" marshal :: Proxy -> CUInt -> Ptr () -> CUInt -> CUInt -> Ptr () -> IO Proxy
foreign import ccall unsafe "wl_proxy_add_dispatcher" addDispatcher :: Proxy -> FunPtr Dispatcher -> Ptr () -> Ptr () -> IO CInt
foreign import ccall unsafe "wl_proxy_set_queue" setQueue :: Proxy -> Ptr () -> IO ()
foreign import ccall unsafe "wl_proxy_get_id" proxyId :: Proxy -> IO Word32
foreign import ccall unsafe "wl_proxy_destroy" destroyProxy :: Proxy -> IO ()
-- This call can invoke the Haskell dispatcher. It MUST be callback-safe.
foreign import ccall safe "wl_display_dispatch_queue_pending_single" pendingSingle :: Proxy -> Ptr () -> IO CInt
foreign import ccall unsafe "wl_display_prepare_read_queue" prepareRead :: Proxy -> Ptr () -> IO CInt
foreign import ccall unsafe "wl_display_cancel_read" cancelRead :: Proxy -> IO ()
foreign import ccall unsafe "wl_display_read_events" readEvents :: Proxy -> IO CInt
foreign import ccall unsafe "wl_display_flush" flushDisplay :: Proxy -> IO CInt
foreign import ccall "&wl_registry_interface" registryInterface :: Ptr ()
foreign import ccall "&wl_callback_interface" callbackInterface :: Ptr ()
foreign import ccall "&wl_output_interface" outputInterface :: Ptr ()
foreign import ccall "&wl_seat_interface" seatInterface :: Ptr ()
foreign import ccall "&wl_surface_interface" surfaceInterface :: Ptr ()

-- Every path component, including /, is explicit and held with NOFOLLOW.
data AncestorPin = AncestorPin DirectoryPin Integer Integer deriving (Eq,Show)
-- PID, birth ticks, parent PID, UID, GID. The list is the selected process first,
-- followed by its explicitly selected ancestors; it is not an ambient scan.
data ProcessPin = ProcessPin Integer Integer Integer Integer Integer deriving (Eq,Show)
data ExecutablePin = ExecutablePin Identity [Pin] B.ByteString [Link] Integer B.ByteString
data EndpointSelection = EndpointSelection
 { endpointBootId :: B.ByteString
 , endpointDirectory :: [AncestorPin]
 , endpointName :: String
 , endpointSocketIdentity :: Identity
 , endpointSocketUid :: Integer
 , endpointSocketMode :: Integer
 , endpointProcesses :: [ProcessPin]
 , endpointExecutable :: ExecutablePin
 , endpointGeneration :: Counter
 }

data Role = Registry | Manager Word32 | Output Word32 FT.Output
          | Toplevel FT.Handle | Barrier (IORef Bool) | Unclassified
data ForeignToplevelOwner = Owner
 { ownerSelection :: EndpointSelection, ownerDeadline :: AdmissionDeadline
 , ownerThread :: ThreadId, ownerPhysical :: (CInt,CInt)
 , ownerGate :: MVar (), ownerStopped :: IORef Bool
 , ownerFault :: IORef Bool, ownerCallbacks :: IORef Int, ownerDispatching :: IORef Bool
 , ownerState :: IORef FT.Owner, ownerEvents :: IORef Int, ownerIssued :: IORef Int
 , ownerProxies :: IORef (Map.Map Proxy Role), ownerFds :: IORef [CInt]
 , ownerSocket :: IORef (Maybe CInt), ownerDisplay :: IORef Proxy
 , ownerQueue :: IORef (Ptr ()), ownerPrepared :: IORef Bool
 , ownerMemory :: IORef [Ptr ()], ownerDispatcher :: IORef (Maybe (FunPtr Dispatcher))
 , ownerStable :: IORef (Maybe (StablePtr ForeignToplevelOwner))
 , ownerInterfaces :: IORef (Ptr (),Ptr ()), ownerParent :: IORef CInt
 }
data Retirement = Retired | Retained ForeignToplevelOwner
data ObservationResult a = ObservationResult (Either SomeException a) Retirement

require :: Bool -> String -> IO ()
require good reason = unless good (ioError (userError reason))
fromPure :: Show e => Either e a -> IO a
fromPure = either (ioError . userError . show) pure

live :: ForeignToplevelOwner -> IO ()
live owner = do
 tid <- kernelTid
 pid <- kernelPid
 left <- remainingMicros (ownerDeadline owner)
 stopped <- readIORef (ownerStopped owner)
 failed <- readIORef (ownerFault owner)
 require ((pid,tid)==ownerPhysical owner && left>0 && not stopped && not failed) "foreign observation owner/deadline refused"

-- An exception never creates a clean receipt. No finalizer attempts uncertain
-- destruction. The StablePtr deliberately keeps an unknown owner reachable.
withForeignToplevelOwner :: EndpointSelection -> AdmissionDeadline
 -> (ForeignToplevelOwner -> IO a) -> IO (ObservationResult a)
withForeignToplevelOwner selection deadline action = runInBoundThread $ mask $ \restore -> do
 state <- fromPure (FT.newOwner (endpointGeneration selection))
 thread <- myThreadId
 physical <- (,) <$> kernelPid <*> kernelTid
 owner <- Owner selection deadline thread physical <$> newMVar () <*> newIORef False
  <*> newIORef False <*> newIORef 0 <*> newIORef False <*> newIORef state <*> newIORef 0 <*> newIORef 0
  <*> newIORef Map.empty <*> newIORef [] <*> newIORef Nothing <*> newIORef nullPtr
  <*> newIORef nullPtr <*> newIORef False <*> newIORef [] <*> newIORef Nothing
  <*> newIORef Nothing <*> newIORef (nullPtr,nullPtr) <*> newIORef (-1)
 stable <- newStablePtr owner
 writeIORef (ownerStable owner) (Just stable)
 result <- try $ do
  initialize owner
  restore (action owner)
 -- Demarshalling may create NEW_ID proxies before queue insertion fails.
 -- Such an escaped failure cannot be repaired by observing an empty queue.
 case result of
  Left _ -> do
   display <- readIORef (ownerDisplay owner)
   when (display/=nullPtr) (writeIORef (ownerFault owner) True)
  Right _ -> pure ()
 retirement <- retire owner
 pure (ObservationResult result retirement)

-- Only this bound thread may drive callbacks; reentrant use is rejected.
readToplevelSnapshot :: ForeignToplevelOwner -> IO FT.Snapshot
readToplevelSnapshot owner = (mask_ $ do
 currentThread <- myThreadId
 require (currentThread==ownerThread owner) "foreign observation called from another Haskell thread"
 live owner
 acquired <- tryTakeMVar (ownerGate owner)
 require (acquired==Just ()) "foreign observation busy"
 (do verifyPeer owner
     barrier owner
     verifyPeer owner
     state <- readIORef (ownerState owner)
     answer <- fromPure (FT.snapshot state)
     live owner
     pure answer) `finally` putMVar (ownerGate owner) ()
 ) `onException` mask_ (do
  -- A caller may catch the public read failure and return normally. Preserve
  -- the fault here: demarshalling may already own an untracked NEW_ID.
  display <- readIORef (ownerDisplay owner)
  when (display/=nullPtr) (atomicWriteIORef (ownerFault owner) True)
 )

trackedMemory :: ForeignToplevelOwner -> Int -> IO (Ptr ())
trackedMemory owner bytes = do
 live owner
 ptr <- callocBytes bytes
 modifyIORef' (ownerMemory owner) (ptr:)
 pure ptr
literal :: ForeignToplevelOwner -> String -> IO CString
literal owner value = do
 ptr <- trackedMemory owner (length value+1)
 withCString value $ \source -> copyBytes ptr (castPtr source) (length value+1)
 pure (castPtr ptr)

messages :: ForeignToplevelOwner -> [(String,String,[Ptr ()])] -> IO (Ptr ())
messages owner entries = do
 table <- trackedMemory owner (length entries * #{size struct wl_message})
 forM_ (zip [0 :: Int ..] entries) $ \(index,(name,signature,types)) -> do
  namePtr <- literal owner name
  signaturePtr <- literal owner signature
  typesPtr <- trackedMemory owner (max 1 (length types) * sizeOf (nullPtr :: Ptr ()))
  pokeArray (castPtr typesPtr) types
  let row=table `plusPtr` (index * #{size struct wl_message})
  #{poke struct wl_message,name} row namePtr
  #{poke struct wl_message,signature} row signaturePtr
  #{poke struct wl_message,types} row typesPtr
 pure table

interface :: ForeignToplevelOwner -> Ptr () -> String -> Int
 -> [(String,String,[Ptr ()])] -> [(String,String,[Ptr ()])] -> IO ()
interface owner ptr name version methods events = do
 namePtr <- literal owner name
 methodPtr <- messages owner methods
 eventPtr <- messages owner events
 #{poke struct wl_interface,name} ptr namePtr
 #{poke struct wl_interface,version} ptr (fromIntegral version :: CInt)
 #{poke struct wl_interface,method_count} ptr (fromIntegral (length methods) :: CInt)
 #{poke struct wl_interface,methods} ptr methodPtr
 #{poke struct wl_interface,event_count} ptr (fromIntegral (length events) :: CInt)
 #{poke struct wl_interface,events} ptr eventPtr

makeInterfaces :: ForeignToplevelOwner -> IO ()
makeInterfaces owner = do
 manager <- trackedMemory owner #{size struct wl_interface}
 handle <- trackedMemory owner #{size struct wl_interface}
 interface owner manager "zwlr_foreign_toplevel_manager_v1" 3
  [("stop","",[])] [("toplevel","n",[handle]),("finished","",[])]
 interface owner handle "zwlr_foreign_toplevel_handle_v1" 3
  [("set_maximized","",[]),("unset_maximized","",[]),("set_minimized","",[])
  ,("unset_minimized","",[]),("activate","o",[seatInterface]),("close","",[])
  ,("set_rectangle","oiiii",[surfaceInterface,nullPtr,nullPtr,nullPtr,nullPtr])
  ,("destroy","",[]),("set_fullscreen","2?o",[outputInterface]),("unset_fullscreen","2",[])]
  [("title","s",[nullPtr]),("app_id","s",[nullPtr]),("output_enter","o",[outputInterface])
  ,("output_leave","o",[outputInterface]),("state","a",[nullPtr]),("done","",[])
  ,("closed","",[]),("parent","3?o",[handle])]
 writeIORef (ownerInterfaces owner) (manager,handle)

identityOf :: Files.FileStatus -> Identity
identityOf status = Identity (toInteger (Files.deviceID status)) (toInteger (Files.fileID status))
modeOf :: Files.FileStatus -> Integer
modeOf status = toInteger (Files.fileMode status .&. 0o7777)
directoryFlags :: CInt
directoryFlags = #{const O_RDONLY} .|. #{const O_DIRECTORY} .|. #{const O_NOFOLLOW} .|. #{const O_CLOEXEC}

openDirectories :: ForeignToplevelOwner -> IO CInt
openDirectories owner = do
 let pins=endpointDirectory (ownerSelection owner)
 require (not (null pins) && length pins<=64) "foreign endpoint ancestor bound"
 walk Nothing "/" pins
 where
  walk _ _ [] = ioError (userError "foreign endpoint missing parent")
  walk parent expected (AncestorPin pin uid mode:rest) = do
   live owner
   require (directoryPath pin==expected && uid>=0 && mode>=0 && mode<=0o7777
     && mode .&. 0o022==0) "foreign endpoint unsafe ancestor selection"
   fd <- case parent of
    Nothing -> withCString "/" (\name -> throwErrnoIfMinus1 "foreign root" (openC name directoryFlags))
    Just prior -> withCString (takeFileName expected) (\name -> throwErrnoIfMinus1 "foreign ancestor" (openatC prior name directoryFlags))
   modifyIORef' (ownerFds owner) (fd:)
   status <- Files.getFdStatus (Fd fd)
   require (Files.isDirectory status && identityOf status==Identity (directoryDevice pin) (directoryInode pin)
     && toInteger (Files.fileOwner status)==uid && modeOf status==mode) "foreign ancestor changed"
   case rest of
    [] -> pure fd
    AncestorPin next _ _: _ -> do
     require (takeDirectory (directoryPath next)==expected && takeFileName (directoryPath next) `notElem` ["",".",".."])
       "foreign ancestor chain differs"
     walk (Just fd) (directoryPath next) rest

socketPath :: ForeignToplevelOwner -> IO FilePath
socketPath owner = do
 parent <- readIORef (ownerParent owner)
 let name=endpointName (ownerSelection owner)
 require (parent>=0 && not (null name) && length name<=64 && all (\c -> c/='/' && c/='\0' && fromEnum c>=33 && fromEnum c<127) name
   && name/="." && name/="..") "foreign socket name refused"
 pure ("/proc/self/fd/"++show parent </> name)

verifySocket :: ForeignToplevelOwner -> IO ()
verifySocket owner = do
 live owner
 path <- socketPath owner
 status <- Files.getSymbolicLinkStatus path
 let selection=ownerSelection owner
 require (Files.isSocket status && identityOf status==endpointSocketIdentity selection
   && toInteger (Files.fileOwner status)==endpointSocketUid selection && modeOf status==endpointSocketMode selection)
   "foreign socket identity changed"
 -- Held components must still have the selected names, not just old inodes.
 forM_ (endpointDirectory selection) $ \(AncestorPin pin uid mode) -> do
  live owner
  current <- Files.getSymbolicLinkStatus (directoryPath pin)
  require (Files.isDirectory current && identityOf current==Identity (directoryDevice pin) (directoryInode pin)
    && toInteger (Files.fileOwner current)==uid && modeOf current==mode) "foreign named ancestor changed"

boundedFile :: ForeignToplevelOwner -> FilePath -> Int -> IO B.ByteString
boundedFile owner path cap = do
 live owner
 -- Fixed /proc files only. Reading at most cap+1 prevents unbounded proc text.
 bracket (openBinaryFile path ReadMode) hClose $ \stream -> do
  bytes <- B.hGet stream (cap+1)
  require (B.length bytes<=cap) "foreign proc observation exceeds bound"
  live owner
  pure bytes

verifyProcesses :: ForeignToplevelOwner -> IO ()
verifyProcesses owner = do
 let pins=endpointProcesses (ownerSelection owner)
     boot=endpointBootId (ownerSelection owner)
 require (B.length boot==36 && B.all (\c -> c==45 || c>=48 && c<=57 || c>=97 && c<=102) boot) "foreign boot pin invalid"
 actualBoot <- boundedFile owner "/proc/sys/kernel/random/boot_id" 64
 require (actualBoot==boot<>"\n") "foreign boot changed"
 require (length pins>=2 && length pins<=32) "foreign selected process ancestry absent"
 forM_ (zip pins (map Just (drop 1 pins)++[Nothing])) $ \(ProcessPin pid birth parent uid gid,next) -> do
  require (pid>0 && birth>0 && parent>=0 && parent/=pid && uid>=0 && gid>=0) "foreign process pin invalid"
  case next of
   Just (ProcessPin ancestor _ _ _ _) -> require (parent==ancestor) "foreign selected ancestry not contiguous"
   Nothing -> pure ()
  let base="/proc/"++show pid
  before <- boundedFile owner (base++"/stat") 8192
  status <- Files.getFileStatus base
  after <- boundedFile owner (base++"/stat") 8192
  require (toInteger (Files.fileOwner status)==uid && toInteger (Files.fileGroup status)==gid)
    "foreign process credentials changed"
  require (processStamp before==Just (pid,parent,birth) && processStamp after==Just (pid,parent,birth))
    "foreign selected process birth/parent differs"

-- Compare identity fields, not changing CPU-time counters in /proc/stat.
processStamp :: B.ByteString -> Maybe (Integer,Integer,Integer)
processStamp bytes = do
 let closing=B.elemIndices 41 bytes
 if null closing then Nothing else do
  let fields=BC.words (B.drop (last closing+2) bytes)
      numberAt index=if length fields>index then readMaybe (BC.unpack (fields!!index)) else Nothing
  if null fields || head fields `elem` ["Z","X","x"] then Nothing else do
   pid <- readMaybe (BC.unpack (BC.takeWhile (/=' ') bytes))
   parent <- numberAt 1
   birth <- numberAt 19
   pure (pid,parent,birth)

verifyExecutable :: ForeignToplevelOwner -> IO ()
verifyExecutable owner = do
 live owner
 let selection=ownerSelection owner
     ExecutablePin rootIdentity pins path links size digest=endpointExecutable selection
 require (not (null (endpointProcesses selection))) "foreign selected process missing"
 let ProcessPin pid _ _ _ _=head (endpointProcesses selection)
 before <- Files.getFileStatus ("/proc/"++show pid++"/exe")
 outcome <- withRoot "/" rootIdentity $ \root -> resolveSnapshot root pins path links size 67108864 digest
 (resolution,_) <- fromPure outcome >>= fromPure
 after <- Files.getFileStatus ("/proc/"++show pid++"/exe")
 named <- Files.readSymbolicLink ("/proc/"++show pid++"/exe")
 require (Files.isRegularFile before && Files.isRegularFile after && identityOf before==resolvedIdentity resolution
   && identityOf after==identityOf before && toInteger (Files.fileSize after)==size
   && named==BC.unpack (resolvedPath resolution)) "foreign compositor executable differs"
 live owner

verifyPeer :: ForeignToplevelOwner -> IO ()
verifyPeer owner = do
 live owner
 verifySocket owner
 verifyProcesses owner
 verifyExecutable owner
 selected <- readIORef (ownerSocket owner)
 fd <- maybe (ioError (userError "foreign socket absent")) pure selected
 allocaBytes #{size struct ucred} $ \credentials -> alloca $ \size -> do
  poke size (fromIntegral (#{size struct ucred} :: Int) :: CUInt)
  _ <- throwErrnoIfMinus1 "foreign peer credentials" (getsockoptC fd #{const SOL_SOCKET} #{const SO_PEERCRED} credentials size)
  actualSize <- peek size
  pid <- #{peek struct ucred,pid} credentials :: IO CInt
  uid <- #{peek struct ucred,uid} credentials :: IO CUInt
  gid <- #{peek struct ucred,gid} credentials :: IO CUInt
  let ProcessPin expectedPid _ _ expectedUid expectedGid=head (endpointProcesses (ownerSelection owner))
  require (actualSize==fromIntegral (#{size struct ucred} :: Int) && toInteger pid==expectedPid
    && toInteger uid==expectedUid && toInteger gid==expectedGid && expectedUid==endpointSocketUid (ownerSelection owner)) "foreign authenticated peer differs"
 verifyProcesses owner
 live owner

waitFd :: ForeignToplevelOwner -> CInt -> CShort -> IO CShort
waitFd owner fd events = do
 live owner
 left <- remainingMicros (ownerDeadline owner)
 allocaBytes #{size struct pollfd} $ \row -> do
  fillBytes row 0 #{size struct pollfd}
  #{poke struct pollfd,fd} row fd
  #{poke struct pollfd,events} row events
  result <- pollC row 1 (fromIntegral (left `div` 1000))
  if result<0 then do
   problem <- getErrno
   if problem==eINTR then waitFd owner fd events else throwErrno "foreign poll"
  else do
   live owner
   flags <- #{peek struct pollfd,revents} row :: IO CShort
   require (result>0 && flags .&. (#{const POLLERR} .|. #{const POLLHUP} .|. #{const POLLNVAL})==0) "foreign poll timeout/peer closure"
   pure flags

connectEndpoint :: ForeignToplevelOwner -> IO ()
connectEndpoint owner = do
 parent <- openDirectories owner
 writeIORef (ownerParent owner) parent
 verifySocket owner
 verifyProcesses owner
 verifyExecutable owner
 fd <- throwErrnoIfMinus1 "foreign socket" (socketC #{const AF_UNIX} (#{const SOCK_STREAM} .|. #{const SOCK_NONBLOCK} .|. #{const SOCK_CLOEXEC}) 0)
 modifyIORef' (ownerFds owner) (fd:)
 writeIORef (ownerSocket owner) (Just fd)
 path <- socketPath owner
 withCString path $ \name -> allocaBytes #{size struct sockaddr_un} $ \address -> do
  require (length path < (#{size struct sockaddr_un} - #{offset struct sockaddr_un,sun_path})) "foreign held socket path too long"
  fillBytes address 0 #{size struct sockaddr_un}
  #{poke struct sockaddr_un,sun_family} address (#{const AF_UNIX} :: CUShort)
  copyBytes (address `plusPtr` #{offset struct sockaddr_un,sun_path}) (castPtr name) (length path+1)
  live owner
  result <- connectC fd address (fromIntegral (#{offset struct sockaddr_un,sun_path}+length path+1 :: Int))
  when (result<0) $ do
   problem <- getErrno
   require (problem==eINPROGRESS || problem==eAGAIN) "foreign socket connect refused"
   _ <- waitFd owner fd #{const POLLOUT}
   alloca $ \errorPtr -> alloca $ \size -> do
    poke size (fromIntegral (sizeOf (0 :: CInt)) :: CUInt)
    _ <- throwErrnoIfMinus1 "foreign connect status" (getsockoptC fd #{const SOL_SOCKET} #{const SO_ERROR} (castPtr errorPtr) size)
    problemCode <- peek errorPtr :: IO CInt
    require (problemCode==0) "foreign asynchronous connect failed"
 verifyPeer owner
 live owner
 -- The function consumes fd even on failure (Wayland 1.26.0 contract).
 modifyIORef' (ownerFds owner) (filter (/=fd))
 display <- connectDisplay fd
 writeIORef (ownerDisplay owner) display
 when (display==nullPtr) $ writeIORef (ownerSocket owner) Nothing
 require (display/=nullPtr) "foreign Wayland connection failed"
 setBufferLimit display 65536
 queue <- createQueue display
 writeIORef (ownerQueue owner) queue
 require (queue/=nullPtr) "foreign event queue unavailable"

initialize :: ForeignToplevelOwner -> IO ()
initialize owner = do
 live owner
 callback <- makeDispatcher dispatch
 writeIORef (ownerDispatcher owner) (Just callback)
 makeInterfaces owner
 connectEndpoint owner
 display <- readIORef (ownerDisplay owner)
 registry <- newProxy owner display 1 registryInterface 1 [PtrArgument nullPtr]
 installRole owner registry Registry
 -- First barrier enumerates globals. Callback bindings issued before the
 -- second barrier receive their initial per-handle events on the same queue.
 barrier owner
 proxies <- readIORef (ownerProxies owner)
 require (length [() | Manager _ <- Map.elems proxies]==1) "foreign manager version 3 unavailable/ambiguous"
 barrier owner
 verifyPeer owner

data Argument = UIntArgument Word32 | PtrArgument (Ptr ())
newProxy :: ForeignToplevelOwner -> Proxy -> Word32 -> Ptr () -> Word32 -> [Argument] -> IO Proxy
newProxy owner parent opcode iface version arguments = do
 live owner
 issued <- readIORef (ownerIssued owner)
 require (issued<4096 && length arguments<=8) "foreign proxy/request budget exhausted"
 writeIORef (ownerIssued owner) (issued+1)
 allocaBytes (max 1 (length arguments) * #{size union wl_argument}) $ \buffer -> do
  fillBytes buffer 0 (max 1 (length arguments) * #{size union wl_argument})
  forM_ (zip [0 :: Int ..] arguments) $ \(index,value) -> do
   let row=buffer `plusPtr` (index * #{size union wl_argument})
   case value of
    UIntArgument number -> #{poke union wl_argument,u} row number
    PtrArgument ptr -> #{poke union wl_argument,o} row ptr
  proxy <- marshal parent (fromIntegral opcode) iface (fromIntegral version) 0 buffer
  require (proxy/=nullPtr) "foreign proxy construction failed"
  modifyIORef' (ownerProxies owner) (Map.insert proxy Unclassified)
  queue <- readIORef (ownerQueue owner)
  setQueue proxy queue
  pure proxy

installRole :: ForeignToplevelOwner -> Proxy -> Role -> IO ()
installRole owner proxy role = do
 modifyIORef' (ownerProxies owner) (Map.insert proxy role)
 callback <- readIORef (ownerDispatcher owner) >>= maybe (ioError (userError "foreign dispatcher absent")) pure
 stable <- readIORef (ownerStable owner) >>= maybe (ioError (userError "foreign owner token absent")) pure
 result <- addDispatcher proxy callback (castStablePtrToPtr stable) nullPtr
 require (result==0) "foreign dispatcher installation failed"

dropProxy :: ForeignToplevelOwner -> Proxy -> IO ()
dropProxy owner proxy = do
 live owner
 known <- Map.member proxy <$> readIORef (ownerProxies owner)
 require known "foreign proxy retirement repeated"
 destroyProxy proxy
 modifyIORef' (ownerProxies owner) (Map.delete proxy)

apply :: ForeignToplevelOwner -> FT.Event -> IO ()
apply owner event = do
 current <- readIORef (ownerState owner)
 next <- fromPure (FT.applyEvent event current)
 writeIORef (ownerState owner) next

dispatch :: Dispatcher
dispatch token target opcode _ arguments = mask_ $ do
 owner <- deRefStablePtr (castPtrToStablePtr token)
 modifyIORef' (ownerCallbacks owner) (+1)
 result <- try (do
  live owner
  dispatching <- readIORef (ownerDispatching owner)
  active <- readIORef (ownerCallbacks owner)
  require (dispatching && active==1) "foreign callback outside serialized dispatch"
  count <- readIORef (ownerEvents owner)
  require (count<8192) "foreign callback budget exhausted"
  writeIORef (ownerEvents owner) (count+1)
  role <- Map.lookup target <$> readIORef (ownerProxies owner)
  maybe (ioError (userError "foreign callback target not owned"))
    (\selected -> eventFor owner target selected opcode arguments) role)
 modifyIORef' (ownerCallbacks owner) (subtract 1)
 case result of
  Left (_ :: SomeException) -> writeIORef (ownerFault owner) True >> pure (-1)
  Right () -> pure 0

arg :: Ptr () -> Int -> Ptr ()
arg base index = base `plusPtr` (index * #{size union wl_argument})
argUInt :: Ptr () -> Int -> IO Word32
argUInt base index = #{peek union wl_argument,u} (arg base index)
argPtr :: Ptr () -> Int -> IO (Ptr ())
argPtr base index = #{peek union wl_argument,o} (arg base index)
textPointer :: CString -> IO Text
textPointer ptr = do
 require (ptr/=nullPtr) "foreign string is null"
 size <- strnlenC ptr 1025
 require (size<=1024) "foreign string bound exceeded"
 bytes <- B.packCStringLen (ptr,fromIntegral size)
 fromPure (TE.decodeUtf8' bytes)
argText :: Ptr () -> Int -> IO Text
argText base index = argPtr base index >>= textPointer . castPtr

eventFor :: ForeignToplevelOwner -> Proxy -> Role -> CUInt -> Ptr () -> IO ()
eventFor owner target role opcode arguments = case role of
 Registry -> case opcode of
  0 -> do
   name <- argUInt arguments 0
   interfaceName <- argText arguments 1
   version <- argUInt arguments 2
   when (interfaceName=="zwlr_foreign_toplevel_manager_v1") $ do
    require (version>=3) "foreign manager version below 3"
    existing <- readIORef (ownerProxies owner)
    require (null [() | Manager _ <- Map.elems existing]) "foreign manager duplicated"
    (manager,_) <- readIORef (ownerInterfaces owner)
    proxy <- bindGlobal owner target name manager 3 "zwlr_foreign_toplevel_manager_v1"
    installRole owner proxy (Manager name)
   when (interfaceName=="wl_output") $ do
    require (version>=1) "foreign output invalid version"
    proxy <- bindGlobal owner target name outputInterface (min version 4) "wl_output"
    wire <- proxyId proxy
    current <- readIORef (ownerState owner)
    (next,output) <- fromPure (FT.addOutput wire current)
    writeIORef (ownerState owner) next
    installRole owner proxy (Output name output)
  1 -> do
   name <- argUInt arguments 0
   proxies <- readIORef (ownerProxies owner)
   forM_ (Map.toList proxies) $ \(proxy,selected) -> case selected of
    Output global output | global==name -> do
     current <- readIORef (ownerState owner)
     fromPure (FT.removeOutput output current) >>= writeIORef (ownerState owner)
     dropProxy owner proxy
    Manager global | global==name -> ioError (userError "foreign manager removed")
    _ -> pure ()
  _ -> ioError (userError "foreign registry opcode")
 Manager _ -> case opcode of
  0 -> do
   proxy <- argPtr arguments 0
   require (proxy/=nullPtr) "foreign toplevel is null"
   -- Track the received new_id before any validation or allocation can fail.
   modifyIORef' (ownerProxies owner) (Map.insert proxy Unclassified)
   queue <- readIORef (ownerQueue owner)
   setQueue proxy queue
   wire <- proxyId proxy
   current <- readIORef (ownerState owner)
   (next,handle) <- fromPure (FT.addToplevel wire current)
   writeIORef (ownerState owner) next
   installRole owner proxy (Toplevel handle)
  1 -> apply owner FT.ManagerFinished >> ioError (userError "foreign manager finished")
  _ -> ioError (userError "foreign manager opcode")
 Toplevel handle -> case opcode of
  0 -> argText arguments 0 >>= apply owner . FT.Title handle
  1 -> argText arguments 0 >>= apply owner . FT.AppId handle
  2 -> outputToken owner arguments >>= apply owner . FT.OutputEnter handle
  3 -> outputToken owner arguments >>= apply owner . FT.OutputLeave handle
  4 -> do
   array <- argPtr arguments 0
   require (array/=nullPtr) "foreign states null"
   bytes <- #{peek struct wl_array,size} array :: IO CSize
   values <- #{peek struct wl_array,data} array :: IO (Ptr Word32)
   require (bytes<=16 && bytes `mod` 4==0 && (bytes==0 || values/=nullPtr)) "foreign state array bound"
   states <- peekArray (fromIntegral bytes `div` 4) values
   apply owner (FT.States handle states)
  5 -> apply owner (FT.Done handle)
  6 -> apply owner (FT.Closed handle) >> dropProxy owner target
  7 -> do
   parent <- argPtr arguments 0
   token <- if parent==nullPtr then pure Nothing else do
    selected <- Map.lookup parent <$> readIORef (ownerProxies owner)
    case selected of
     Just (Toplevel parentHandle) -> pure (Just parentHandle)
     _ -> ioError (userError "foreign parent not current")
   apply owner (FT.Parent handle token)
  _ -> ioError (userError "foreign toplevel opcode")
 Output _ _ -> do
  -- Output identity is the registry lifetime. Geometry is not workspace,
  -- hidden status or effect authority. Still bound all variable-size payloads.
  require (opcode<=5) "foreign output opcode"
  when (opcode==0) $ do
   _ <- argText arguments 5
   _ <- argText arguments 6
   pure ()
  when (opcode==4 || opcode==5) $ do
   _ <- argText arguments 0
   pure ()
 Barrier done -> do
  require (opcode==0) "foreign sync opcode"
  writeIORef done True
  dropProxy owner target
 Unclassified -> ioError (userError "foreign unclassified callback")

outputToken :: ForeignToplevelOwner -> Ptr () -> IO FT.Output
outputToken owner arguments = do
 ptr <- argPtr arguments 0
 selected <- Map.lookup ptr <$> readIORef (ownerProxies owner)
 case selected of
  Just (Output _ token) -> pure token
  _ -> ioError (userError "foreign output not current")

bindGlobal :: ForeignToplevelOwner -> Proxy -> Word32 -> Ptr () -> Word32 -> String -> IO Proxy
bindGlobal owner registry name iface version wireName = withCString wireName $ \text ->
 newProxy owner registry 0 iface version [UIntArgument name,PtrArgument (castPtr text),UIntArgument version,PtrArgument nullPtr]

barrier :: ForeignToplevelOwner -> IO ()
barrier owner = do
 live owner
 display <- readIORef (ownerDisplay owner)
 done <- newIORef False
 callback <- newProxy owner display 0 callbackInterface 1 [PtrArgument nullPtr]
 installRole owner callback (Barrier done)
 let wait = do
      live owner
      completed <- readIORef done
      unless completed (pump owner >> wait)
 wait

-- Never reset the deadline. Every successful prepare_read is paired exactly
-- once with read_events or cancel_read, including interruption/error paths.
pump :: ForeignToplevelOwner -> IO ()
pump owner = mask_ $ do
 live owner
 display <- readIORef (ownerDisplay owner)
 queue <- readIORef (ownerQueue owner)
 writeIORef (ownerDispatching owner) True
 count <- pendingSingle display queue `finally` writeIORef (ownerDispatching owner) False
 require (count>=0 && count<=1) "foreign pending dispatch failed"
 live owner
 when (count==0) $ do
  prepared <- prepareRead display queue
  if prepared<0 then do
   problem <- getErrno
   require (problem==eAGAIN) "foreign prepare read failed"
  else do
   writeIORef (ownerPrepared owner) True
   (do
     live owner
     flushed <- flushDisplay display
     writable <- if flushed>=0 then pure False else do
      problem <- getErrno
      require (problem==eAGAIN) "foreign flush failed"
      pure True
     fd <- readIORef (ownerSocket owner) >>= maybe (ioError (userError "foreign fd missing")) pure
     ready <- waitFd owner fd (#{const POLLIN} .|. if writable then #{const POLLOUT} else 0)
     if ready .&. #{const POLLIN}/=0 then do
      live owner
      result <- readEvents display
      writeIORef (ownerPrepared owner) False
      require (result>=0) "foreign read failed"
     else do
      cancelRead display
      writeIORef (ownerPrepared owner) False
    ) `onException` do
     pending <- readIORef (ownerPrepared owner)
     when pending $ cancelRead display >> writeIORef (ownerPrepared owner) False

-- This is local retirement, not a protocol manager-finished inference. All
-- dispatches are synchronous on our thread; no shared/default display is used.
retire :: ForeignToplevelOwner -> IO Retirement
retire owner = mask_ $ do
 acquired <- tryTakeMVar (ownerGate owner)
 case acquired of
  Nothing -> pure (Retained owner)
  Just () -> do
   writeIORef (ownerStopped owner) True
   outcome <- try $ do
    let settle = do
         current <- myThreadId
         remaining <- remainingMicros (ownerDeadline owner)
         active <- readIORef (ownerCallbacks owner)
         dispatching <- readIORef (ownerDispatching owner)
         physical <- (,) <$> kernelPid <*> kernelTid
         require (current==ownerThread owner && physical==ownerPhysical owner && remaining>0 && active==0 && not dispatching) "foreign retirement unconfirmed"
    settle
    failed <- readIORef (ownerFault owner)
    require (not failed) "foreign retirement retains faulted callback/transport owner"
    display <- readIORef (ownerDisplay owner)
    queue <- readIORef (ownerQueue owner)
    prepared <- readIORef (ownerPrepared owner)
    when prepared $ do
     require (display/=nullPtr) "foreign read preparation without display"
     cancelRead display
     writeIORef (ownerPrepared owner) False
    if display==nullPtr then do
     tracked <- readIORef (ownerProxies owner)
     issued <- readIORef (ownerIssued owner)
     require (queue==nullPtr && Map.null tracked && issued==0) "foreign absent display has unresolved proxies"
    else do
     require (queue/=nullPtr) "foreign retirement has no private queue proof"
     settle
     -- create_proxies precedes dispatcher tracking. A pending NEW_ID can
     -- therefore own resources outside ownerProxies. Do not drain, read or
     -- dispatch here: only a successful empty-queue reservation is evidence.
     ready <- prepareRead display queue
     require (ready==0) "foreign retirement retains pending private queue"
     writeIORef (ownerPrepared owner) True
     cancelRead display
     writeIORef (ownerPrepared owner) False
     settle
    -- No read/dispatch follows this proof. This connection is exclusive to
    -- our physical thread, so socket arrivals cannot allocate further proxies.
    proxies <- Map.keys <$> readIORef (ownerProxies owner)
    forM_ proxies $ \proxy -> do
     settle
     destroyProxy proxy
     modifyIORef' (ownerProxies owner) (Map.delete proxy)
    when (queue/=nullPtr) $ do
     settle
     destroyQueue queue
     writeIORef (ownerQueue owner) nullPtr
    when (display/=nullPtr) $ do
     settle
     disconnectDisplay display
     writeIORef (ownerDisplay owner) nullPtr
     writeIORef (ownerSocket owner) Nothing
    fds <- readIORef (ownerFds owner)
    forM_ fds $ \fd -> do
     settle
     -- close is never retried: EINTR may already have consumed the descriptor.
     result <- closeC fd
     require (result==0) "foreign descriptor close uncertain"
     modifyIORef' (ownerFds owner) (filter (/=fd))
    settle
    callback <- readIORef (ownerDispatcher owner)
    forM_ callback $ \pointer -> settle >> freeHaskellFunPtr pointer
    writeIORef (ownerDispatcher owner) Nothing
    memory <- readIORef (ownerMemory owner)
    forM_ memory $ \pointer -> do
     settle
     free pointer
     modifyIORef' (ownerMemory owner) (filter (/=pointer))
    settle
    stable <- readIORef (ownerStable owner)
    writeIORef (ownerStable owner) Nothing
    forM_ stable freeStablePtr
   putMVar (ownerGate owner) ()
   case outcome of
    Right () -> pure Retired
    Left (_ :: SomeException) -> pure (Retained owner)
