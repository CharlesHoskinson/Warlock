{-# LANGUAGE ForeignFunctionInterface #-}
{-# LANGUAGE OverloadedStrings #-}
-- Private producer for the trusted host event loop. Installing a view claim
-- does not authenticate input, create a native grant or prove physical input.
module Warlock.Native.Cancellation.Selection
 ( SelectionRegistry, ViewClaim, Selection, SelectionError(..), SelectionPhase(..)
 , newSelectionRegistry, viewClaim, installCurrentView, retireCurrentView
 , captureSelection, spendSelection, selectionId, selectionBinding, selectionScope
 , selectionPublication, selectionLease, selectionControl, selectionIntent, selectionAccepted, selectionDeadline, selectionPhase ) where
#define _GNU_SOURCE 1
#include <sys/types.h>
#include <sys/random.h>
#include <time.h>
import Control.Concurrent (ThreadId,myThreadId)
import Control.Exception (SomeAsyncException,SomeException,fromException,mask,throwIO,try)
import qualified Data.ByteString as B
import Data.Int (Int64)
import Data.IORef (IORef,newIORef,readIORef,atomicModifyIORef')
import Data.List (find)
import qualified Data.Text as T
import qualified Data.Text.Encoding as TE
import Data.Word (Word8,Word64)
import Foreign.C.Error (throwErrnoIfMinus1Retry,throwErrnoIfMinus1_)
import Foreign.C.Types (CInt(..),CSize(..))
import Foreign.Marshal.Alloc (allocaBytes,allocaBytesAligned)
import Foreign.Marshal.Array (peekArray)
import Foreign.Ptr (Ptr,plusPtr)
import Foreign.Storable (peekByteOff)
import Numeric (showHex)
import Warlock.Protocol.Custody (Intent,Operation(Restore),intentBinding,intentOperation)
import Warlock.Protocol.Identity (Binding,Counter,addCounter,isZero,parseCounter)

foreign import ccall safe "clock_gettime" c_clockGettime :: CInt -> Ptr () -> IO CInt
foreign import ccall safe "getrandom" c_getrandom :: Ptr Word8 -> CSize -> CInt -> IO #{type ssize_t}

data SelectionError = WrongThread | InvalidClaim | NoCurrentView | Capacity | EntropyFailure | ClockFailure | Expired | ForeignSelection | AlreadySpent deriving (Eq,Show)
data ViewClaim = ViewClaim !Binding !Counter !Counter !Counter !Counter !T.Text !Intent deriving (Eq,Show)
data SelectionPhase = Captured | Spent deriving (Eq,Show)
data Selection = Selection !T.Text !ViewClaim !Counter !Counter !SelectionPhase deriving (Eq,Show)
data State = State !(Maybe ViewClaim) ![Selection]
data SelectionRegistry = SelectionRegistry !ThreadId !(IORef State)
selectionId :: Selection -> T.Text
selectionId (Selection ident _ _ _ _) = ident
selectionBinding :: Selection -> Binding
selectionBinding (Selection _ (ViewClaim bindingValue _ _ _ _ _ _) _ _ _) = bindingValue
selectionScope :: Selection -> (Counter,Counter)
selectionScope (Selection _ (ViewClaim _ ident generation _ _ _ _) _ _ _) = (ident,generation)
selectionPublication, selectionLease :: Selection -> Counter
selectionPublication (Selection _ (ViewClaim _ _ _ publication _ _ _) _ _ _) = publication
selectionLease (Selection _ (ViewClaim _ _ _ _ lease _ _) _ _ _) = lease
selectionControl :: Selection -> T.Text
selectionControl (Selection _ (ViewClaim _ _ _ _ _ control _) _ _ _) = control
selectionIntent :: Selection -> Intent
selectionIntent (Selection _ (ViewClaim _ _ _ _ _ _ expected) _ _ _) = expected
selectionAccepted, selectionDeadline :: Selection -> Counter
selectionAccepted (Selection _ _ accepted _ _) = accepted
selectionDeadline (Selection _ _ _ deadlineValue _) = deadlineValue
selectionPhase :: Selection -> SelectionPhase
selectionPhase (Selection _ _ _ _ phase) = phase

-- Only the owning trusted host may install a claim AFTER checking its actual
-- current view/control. This function does not turn caller data into evidence.
viewClaim :: Binding -> Counter -> Counter -> Counter -> Counter -> T.Text -> Intent -> Either SelectionError ViewClaim
viewClaim bindingValue ident generation publication lease control expectedIntent
 | intentBinding expectedIntent /= bindingValue || intentOperation expectedIntent /= Restore || any isZero [ident,generation,publication,lease] || T.null control || T.any (=='\0') control || B.length (TE.encodeUtf8 control) > 512 = Left InvalidClaim
 | otherwise = Right (ViewClaim bindingValue ident generation publication lease control expectedIntent)
newSelectionRegistry :: IO SelectionRegistry
newSelectionRegistry = SelectionRegistry <$> myThreadId <*> newIORef (State Nothing [])
checkThread :: SelectionRegistry -> IO (Either SelectionError ())
checkThread (SelectionRegistry thread _) = do now <- myThreadId; pure (if now == thread then Right () else Left WrongThread)
installCurrentView :: SelectionRegistry -> ViewClaim -> IO (Either SelectionError ())
installCurrentView owner@(SelectionRegistry _ state) claim = do
 checked <- checkThread owner
 case checked of
  Left err -> pure (Left err)
  Right () -> atomicModifyIORef' state $ \(State _ slots) ->
   let retain selected@(Selection _ selectedClaim _ _ _) = selectionPhase selected == Spent || selectedClaim == claim
   in (State (Just claim) (filter retain slots),Right ())
retireCurrentView :: SelectionRegistry -> IO (Either SelectionError ())
retireCurrentView owner@(SelectionRegistry _ state) = do
 checked <- checkThread owner
 case checked of
  Left err -> pure (Left err)
  Right () -> atomicModifyIORef' state $ \(State _ slots) ->
   (State Nothing (filter ((== Spent) . selectionPhase) slots),Right ())

clockCounter :: IO (Either SelectionError Counter)
clockCounter = do
 result <- try (allocaBytesAligned #{size struct timespec} #{alignment struct timespec} $ \buffer -> do
  throwErrnoIfMinus1_ "clock_gettime" (c_clockGettime #{const CLOCK_MONOTONIC} buffer)
  seconds <- #{peek struct timespec, tv_sec} buffer :: IO #{type time_t}
  nanos <- #{peek struct timespec, tv_nsec} buffer :: IO #{type long}
  let sec = toInteger seconds; fraction = toInteger nanos; value = sec * 1000000000 + fraction
  pure $ if sec < 0 || fraction < 0 || fraction >= 1000000000 || value <= 0 || value > toInteger (maxBound :: Word64)
   then Left ClockFailure else either (const (Left ClockFailure)) Right (parseCounter False (T.pack (show value)))) :: IO (Either SomeException (Either SelectionError Counter))
 case result of
  Right value -> pure value
  Left err -> case fromException err :: Maybe SomeAsyncException of Just _ -> throwIO err; Nothing -> pure (Left ClockFailure)
randomId :: IO T.Text
randomId = allocaBytes 16 $ \buffer -> do
 let loop offset
      | offset == 16 = pure ()
      | otherwise = do
         got <- throwErrnoIfMinus1Retry "getrandom selection" (c_getrandom (buffer `plusPtr` offset) (fromIntegral (16-offset)) #{const GRND_NONBLOCK})
         if got <= 0 || got > fromIntegral (16-offset) then ioError (userError "selection entropy") else loop (offset+fromIntegral got)
 loop (0 :: Int)
 bytes <- peekArray 16 buffer :: IO [Word8]
 let hex byte = let value = showHex byte "" in if length value == 1 then '0':value else value
 pure (T.pack (concatMap hex bytes))

-- Called synchronously by that host only after input/action/lease validation.
-- The original monotonic A and D are installed once, before queue or disk.
captureSelection :: SelectionRegistry -> ViewClaim -> IO (Either SelectionError Selection)
captureSelection owner@(SelectionRegistry _ state) expected = mask $ \restore -> do
 checked <- checkThread owner
 case checked of
  Left err -> pure (Left err)
  Right () -> do
   State current slots <- readIORef state
   if current /= Just expected then pure (Left NoCurrentView) else if length slots >= 16 then pure (Left Capacity) else do
    sampled <- restore clockCounter
    case sampled of
     Left err -> pure (Left err)
     Right accepted -> case addCounter accepted (2000000000 :: Word64) of
      Left _ -> pure (Left ClockFailure)
      Right end -> do
       entropy <- try (restore randomId) :: IO (Either SomeException T.Text)
       case entropy of
        Left err -> case fromException err :: Maybe SomeAsyncException of Just _ -> throwIO err; Nothing -> pure (Left EntropyFailure)
        Right ident -> do
         now <- restore clockCounter
         case now of
          Left err -> pure (Left err)
          Right observed | observed < accepted || observed >= end -> pure (Left Expired)
          Right _ -> atomicModifyIORef' state $ \old@(State currentView oldSlots) ->
           if currentView /= Just expected then (old,Left NoCurrentView)
           else if length oldSlots >= 16 || any ((==ident) . selectionId) oldSlots then (old,Left Capacity)
           else let selected = Selection ident expected accepted end Captured in (State currentView (selected:oldSlots),Right selected)

-- No spent token is returned to Captured after any subsequent I/O failure.
spendSelection :: SelectionRegistry -> T.Text -> Binding -> Intent -> IO (Either SelectionError Selection)
spendSelection owner@(SelectionRegistry _ state) ident expectedBinding action = mask $ \restore -> do
 checked <- checkThread owner
 case checked of
  Left err -> pure (Left err)
  Right () -> do
   sampled <- restore clockCounter
   case sampled of
    Left err -> pure (Left err)
    Right now -> atomicModifyIORef' state $ \old@(State current slots) -> case find ((==ident) . selectionId) slots of
     Nothing -> (old,Left ForeignSelection)
     Just selected@(Selection token claim@(ViewClaim _ _ _ _ _ _ expectedIntent) accepted end phase)
      | phase /= Captured -> (old,Left AlreadySpent)
      | current /= Just claim || selectionBinding selected /= expectedBinding || intentBinding action /= expectedBinding || intentOperation action /= Restore || action /= expectedIntent -> (old,Left ForeignSelection)
      | now < accepted || now >= end -> (old,Left Expired)
      | otherwise -> let spent = Selection token claim accepted end Spent
                         rest = filter ((/=token) . selectionId) slots
                     in (State current (spent:rest),Right spent)
