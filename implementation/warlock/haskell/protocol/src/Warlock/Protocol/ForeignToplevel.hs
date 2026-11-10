{-# LANGUAGE OverloadedStrings #-}
-- Pure zwlr_foreign_toplevel_manager_v1 version 3 callback state. Construction
-- does not authenticate a display, grant operations or prove callback retirement.
module Warlock.Protocol.ForeignToplevel
  ( Owner, Handle, Output, Event(..), State(..), Error(..), Snapshot, Toplevel
  , newOwner, addToplevel, addOutput, removeOutput, applyEvent, snapshot, toplevels
  , toplevelHandle, toplevelTitle, toplevelAppId, toplevelStates, toplevelOutputs, toplevelParent
  ) where

import Control.Monad (unless)
import Data.Char (ord)
import qualified Data.Map.Strict as Map
import qualified Data.Set as Set
import Data.Text (Text)
import qualified Data.Text as T
import Data.Word (Word32)
import Warlock.Protocol.Identity (Counter, addCounter, isZero, parseCounter)
import Warlock.Protocol.StrictJson (utf16Length)

-- Wire IDs are connection-local and reusable. The issuer must keep these opaque
-- tokens in each callback closure; lookup of a late callback by wire ID is unsafe.
data Handle = Handle !Counter !Word32 !Counter deriving (Eq, Ord, Show)
data Output = Output !Counter !Word32 !Counter deriving (Eq, Ord, Show)
data State = Maximized | Minimized | Activated | Fullscreen deriving (Eq, Ord, Show)
data Error = Retired | InvalidIdentity | StaleHandle | StaleOutput | Capacity
           | CounterExhausted | InvalidText | InvalidStates | InvalidOutputChange
           | Incomplete | StaleParent | ParentCycle deriving (Eq, Show)
data Event = Title Handle Text | AppId Handle Text | States Handle [Word32]
           | OutputEnter Handle Output | OutputLeave Handle Output
           | Parent Handle (Maybe Handle) | Done Handle | Closed Handle
           | ManagerFinished deriving (Eq, Show)

data Draft = Draft !(Maybe Text) !(Maybe Text) !(Maybe [State]) !(Set.Set Output) !(Maybe Handle)
  deriving (Eq, Show)
data Toplevel = Toplevel !Handle !Text !Text ![State] ![Output] !(Maybe Handle)
  deriving (Eq, Show)
data Entry = Entry !Handle !Draft !(Maybe Toplevel) deriving (Eq, Show)
data Owner = Owner !Counter !Counter !Bool !(Map.Map Word32 Entry) !(Map.Map Word32 Output)
  deriving (Eq, Show)
newtype Snapshot = Snapshot [Toplevel] deriving (Eq, Show)

newOwner :: Counter -> Either Error Owner
newOwner generation
  | isZero generation = Left InvalidIdentity
  | otherwise = case parseCounter True "0" of
      Left _ -> Left InvalidIdentity
      Right zero -> Right (Owner generation zero True Map.empty Map.empty)

serialAfter :: Counter -> Either Error Counter
serialAfter value = either (const (Left CounterExhausted)) Right (addCounter value 1)

addToplevel :: Word32 -> Owner -> Either Error (Owner,Handle)
addToplevel wire (Owner generation serial live entries outputs)
  | not live = Left Retired
  | wire==0 || Map.member wire entries = Left InvalidIdentity
  | Map.size entries>=256 = Left Capacity
  | otherwise = do
      next <- serialAfter serial
      let token=Handle generation wire next
          entry=Entry token (Draft Nothing Nothing Nothing Set.empty Nothing) Nothing
      Right (Owner generation next live (Map.insert wire entry entries) outputs,token)

addOutput :: Word32 -> Owner -> Either Error (Owner,Output)
addOutput wire (Owner generation serial live entries outputs)
  | not live = Left Retired
  | wire==0 || Map.member wire outputs = Left InvalidIdentity
  | Map.size outputs>=64 = Left Capacity
  | otherwise = do
      next <- serialAfter serial
      let token=Output generation wire next
      Right (Owner generation next live entries (Map.insert wire token outputs),token)

entryFor :: Handle -> Owner -> Either Error Entry
entryFor token@(Handle generation wire _) (Owner current _ live entries _)
  | not live = Left Retired
  | generation/=current = Left StaleHandle
  | otherwise = case Map.lookup wire entries of
      Just entry@(Entry held _ _) | held==token -> Right entry
      _ -> Left StaleHandle

outputCurrent :: Output -> Owner -> Bool
outputCurrent token@(Output generation wire _) (Owner current _ live _ outputs) =
  live && generation==current && Map.lookup wire outputs==Just token

-- Registry removal proves this output no longer exists. Remove its membership
-- from both pending and committed facts, rather than inventing a replacement.
removeOutput :: Output -> Owner -> Either Error Owner
removeOutput token@(Output _ wire _) owner@(Owner generation serial live entries outputs)
  | not live = Left Retired
  | not (outputCurrent token owner) = Left StaleOutput
  | otherwise = Right (Owner generation serial live (Map.map remove entries) (Map.delete wire outputs))
  where
    remove (Entry held (Draft title app states visible parent) committed) =
      Entry held (Draft title app states (Set.delete token visible) parent) (fmap withoutOutput committed)
    withoutOutput (Toplevel held title app states visible parent) =
      Toplevel held title app states (filter (/=token) visible) parent

textField :: Text -> Either Error Text
textField value
  | utf16Length (T.take 257 value)>256 || T.any (\c -> ord c<32 || (ord c>=0xD800 && ord c<=0xDFFF)) value = Left InvalidText
  | otherwise = Right value

stateArray :: [Word32] -> Either Error [State]
stateArray values
  | length (take 5 values)>4 || Set.size (Set.fromList values)/=length values = Left InvalidStates
  | otherwise = fmap Set.toAscList (Set.fromList <$> traverse decode values)
  where
    decode 0 = Right Maximized
    decode 1 = Right Minimized
    decode 2 = Right Activated
    decode 3 = Right Fullscreen
    decode _ = Left InvalidStates

applyEvent :: Event -> Owner -> Either Error Owner
applyEvent ManagerFinished (Owner generation serial live _ _)
  | not live = Left Retired
  | otherwise = Right (Owner generation serial False Map.empty Map.empty)
applyEvent event owner@(Owner generation serial live entries outputs) = do
  token <- eventHandle event
  Entry held draft committed <- entryFor token owner
  let replace nextDraft nextCommitted =
        case held of
          Handle _ wire _ -> Right (Owner generation serial live (Map.insert wire (Entry held nextDraft nextCommitted) entries) outputs)
  case (event,draft) of
    (Title _ value,Draft _ app states visible parent) -> do
      checked <- textField value
      replace (Draft (Just checked) app states visible parent) committed
    (AppId _ value,Draft title _ states visible parent) -> do
      checked <- textField value
      replace (Draft title (Just checked) states visible parent) committed
    (States _ values,Draft title app _ visible parent) -> do
      checked <- stateArray values
      replace (Draft title app (Just checked) visible parent) committed
    (OutputEnter _ output,Draft title app states visible parent) -> do
      unless (outputCurrent output owner) (Left StaleOutput)
      unless (not (Set.member output visible)) (Left InvalidOutputChange)
      replace (Draft title app states (Set.insert output visible) parent) committed
    (OutputLeave _ output,Draft title app states visible parent) -> do
      unless (outputCurrent output owner) (Left StaleOutput)
      unless (Set.member output visible) (Left InvalidOutputChange)
      replace (Draft title app states (Set.delete output visible) parent) committed
    (Parent _ parent,Draft title app states visible _) -> do
      case parent of
        Nothing -> Right ()
        Just selected -> do
          _ <- entryFor selected owner
          unless (selected/=held) (Left ParentCycle)
      replace (Draft title app states visible parent) committed
    (Done _,Draft (Just title) (Just app) (Just states) visible parent) ->
      replace draft (Just (Toplevel held title app states (Set.toAscList visible) parent))
    (Done _,_) -> Left Incomplete
    (Closed _,_) -> case held of
      Handle _ wire _ -> Right (Owner generation serial live (Map.delete wire entries) outputs)

-- ManagerFinished is normally handled before token lookup; remain total.
eventHandle :: Event -> Either Error Handle
eventHandle event = case event of
  Title token _ -> Right token
  AppId token _ -> Right token
  States token _ -> Right token
  OutputEnter token _ -> Right token
  OutputLeave token _ -> Right token
  Parent token _ -> Right token
  Done token -> Right token
  Closed token -> Right token
  ManagerFinished -> Left Retired

snapshot :: Owner -> Either Error Snapshot
snapshot (Owner _ _ False _ _) = Left Retired
snapshot owner@(Owner _ _ True entries _) = do
  let rows=[row | Entry _ _ (Just row) <- Map.elems entries]
      table=Map.fromList [(toplevelHandle row,row) | row<-rows]
      visit seen token
        | Set.member token seen = Left ParentCycle
        | otherwise = case Map.lookup token table of
            Nothing -> Left StaleParent
            Just row -> case toplevelParent row of
              Nothing -> Right ()
              Just parent -> visit (Set.insert token seen) parent
  mapM_ (\row -> do
    unless (all (`outputCurrent` owner) (toplevelOutputs row)) (Left StaleOutput)
    visit Set.empty (toplevelHandle row)) rows
  Right (Snapshot rows)

toplevels :: Snapshot -> [Toplevel]
toplevels (Snapshot rows) = rows

toplevelHandle :: Toplevel -> Handle
toplevelHandle (Toplevel token _ _ _ _ _) = token

toplevelTitle, toplevelAppId :: Toplevel -> Text
toplevelTitle (Toplevel _ value _ _ _ _) = value
toplevelAppId (Toplevel _ _ value _ _ _) = value

toplevelStates :: Toplevel -> [State]
toplevelStates (Toplevel _ _ _ value _ _) = value

toplevelOutputs :: Toplevel -> [Output]
toplevelOutputs (Toplevel _ _ _ _ value _) = value

toplevelParent :: Toplevel -> Maybe Handle
toplevelParent (Toplevel _ _ _ _ _ value) = value
