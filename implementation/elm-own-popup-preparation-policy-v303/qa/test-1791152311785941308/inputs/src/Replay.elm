port module Replay exposing (main)
import Binding
import Json.Decode as D
import Json.Encode as E
import OwnPopupPreparation as P
import Platform
import UInt64
port report : E.Value -> Cmd msg
counter value = D.decodeString UInt64.decoder ("\"" ++ value ++ "\"") |> Result.withDefault UInt64.zero
binding = D.decodeString Binding.decoder "{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"}" |> (\r -> case r of
    Ok value -> value
    Err _ -> Debug.todo "binding")
host = {pid=100,started=counter "30",surface=42,view=counter "1",generation=counter "2",topology=counter "3",publication=counter "22",lease=counter "4",menu=counter "5"}
original = {binding=binding,incarnation=counter "8",output=counter "7",workArea=counter "9",legacyRevision=counter "3",geometryRevision=counter "100",structure="same immutable normalized family/constraints/placement",action=P.Maximize,eligible=True}
blocked = {original|eligible=False,legacyRevision=counter "4",geometryRevision=counter "101"}
native = {host=host,binding=binding,exclusiveOwnGrab=True,sessionLocked=False,exclusiveLayer=False,dragging=False,modal=False}
proof = P.authenticate host native original blocked |> (\r -> case r of
    Just value -> value
    Nothing -> Debug.todo "proof")
selected = P.select 0 6000 proof P.initial
closed = P.closed 1 (counter "1") host True (counter "51") (counter "52") (Tuple.first selected)
fresh = {original|legacyRevision=counter "4",geometryRevision=counter "102"}
legacy = P.reply 2 (counter "1") False (counter "51") fresh (Tuple.first closed)
geometry = P.reply 3 (counter "1") True (counter "52") fresh (Tuple.first legacy)
isNone decision = case decision of
 P.None -> True
 _ -> False
isDispatch decision = case decision of
 P.DispatchFresh _ value -> value.legacyRevision==counter "4" && value.geometryRevision==counter "102"
 _ -> False
noSlot model = P.prepared model==Nothing
cases =
 [ ("own popup retains only planning capability",P.retain host native original blocked)
 , ("external grab does not retain",not (P.retain host {native|exclusiveOwnGrab=False} original blocked))
 , ("wrong host surface refused",P.authenticate {host|surface=43} native original blocked==Nothing)
 , ("wrong lease refused",P.authenticate {host|lease=counter "6"} native original blocked==Nothing)
 , ("wrong native binding refused",P.authenticate host {native|binding=D.decodeString Binding.decoder "{\"lifetime\":\"1\",\"session\":\"9\",\"frontend\":\"3\"}" |> Result.withDefault binding} original blocked==Nothing)
 , ("session lock refused",P.authenticate host {native|sessionLocked=True} original blocked==Nothing)
 , ("exclusive layer refused",P.authenticate host {native|exclusiveLayer=True} original blocked==Nothing)
 , ("drag refused",P.authenticate host {native|dragging=True} original blocked==Nothing)
 , ("modal refused",P.authenticate host {native|modal=True} original blocked==Nothing)
 , ("changed target refused",P.authenticate host native original {blocked|incarnation=counter "9"}==Nothing)
 , ("changed output refused",P.authenticate host native original {blocked|output=counter "8"}==Nothing)
 , ("changed workarea refused",P.authenticate host native original {blocked|workArea=counter "10"}==Nothing)
 , ("changed structural limits refused",P.authenticate host native original {blocked|structure="changed"}==Nothing)
 , ("changed action refused",P.authenticate host native original {blocked|action=P.RestoreGeometry}==Nothing)
 , ("preexisting ineligible refused",P.authenticate host native {original|eligible=False} blocked==Nothing)
 , ("selection only closes exact popup",case Tuple.second selected of
     P.ClosePopup token owned -> token==counter "1" && owned==host
     _ -> False)
 , ("duplicate selection never reserves",Tuple.first (P.select 1 6000 proof (Tuple.first selected))==Tuple.first selected)
 , ("reply before close fence cannot dispatch",isNone (Tuple.second (P.reply 1 (counter "1") False (counter "51") fresh (Tuple.first selected))))
 , ("no fence cancels without dispatch",noSlot (Tuple.first (P.closed 1 (counter "1") host False (counter "51") (counter "52") (Tuple.first selected))))
 , ("wrong close lease cancels",noSlot (Tuple.first (P.closed 1 (counter "1") {host|lease=counter "6"} True (counter "51") (counter "52") (Tuple.first selected))))
 , ("equal read IDs cancel",noSlot (Tuple.first (P.closed 1 (counter "1") host True (counter "51") (counter "51") (Tuple.first selected))))
 , ("close allocates observations only",case Tuple.second closed of
     P.Observe _ l g -> l==counter "51" && g==counter "52"
     _ -> False)
 , ("wrong read ID ignored",isNone (Tuple.second (P.reply 2 (counter "1") False (counter "99") fresh (Tuple.first closed))))
 , ("wrong token ignored",Tuple.first (P.reply 2 (counter "99") False (counter "51") fresh (Tuple.first closed))==Tuple.first closed)
 , ("one response never dispatches",isNone (Tuple.second legacy))
 , ("own popup still blocks effect eligibility",noSlot (Tuple.first (P.reply 2 (counter "1") False (counter "51") {fresh|eligible=False} (Tuple.first closed))))
 , ("changed workarea after fence cancels",noSlot (Tuple.first (P.reply 2 (counter "1") False (counter "51") {fresh|workArea=counter "10"} (Tuple.first closed))))
 , ("legacy revision regression cancels",noSlot (Tuple.first (P.reply 2 (counter "1") False (counter "51") {fresh|legacyRevision=counter "2"} (Tuple.first closed))))
 , ("geometry revision regression cancels",noSlot (Tuple.first (P.reply 2 (counter "1") True (counter "52") {fresh|geometryRevision=counter "99"} (Tuple.first closed))))
 , ("legacy and geometry revisions stay separate namespaces",isDispatch (Tuple.second geometry))
 , ("both fresh replies dispatch exactly once",isDispatch (Tuple.second geometry) && noSlot (Tuple.first geometry))
 , ("late duplicate cannot dispatch",isNone (Tuple.second (P.reply 4 (counter "1") True (counter "52") fresh (Tuple.first geometry))))
 , ("fresh inverse order dispatches once",let g=P.reply 2 (counter "1") True (counter "52") fresh (Tuple.first closed) in isDispatch (Tuple.second (P.reply 3 (counter "1") False (counter "51") fresh (Tuple.first g))))
 , ("deadline exact boundary cancels",noSlot (Tuple.first (P.reply 6000 (counter "1") True (counter "52") fresh (Tuple.first legacy))))
 , ("stale expiry cannot cancel",Tuple.first (P.expire 6000 (counter "99") (Tuple.first closed))==Tuple.first closed)
 , ("original timer cancels",noSlot (Tuple.first (P.expire 6000 (counter "1") (Tuple.first closed))))
 , ("consumed proof cannot reenter after dispatch",noSlot (Tuple.first (P.select 4 6000 proof (Tuple.first geometry))))
 , ("cancelled proof cannot reenter",let c=P.cancel (counter "1") (Tuple.first selected) in noSlot (Tuple.first (P.select 4 6000 proof (Tuple.first c))))
 , ("cancel before reply never replays",let c=P.cancel (counter "1") (Tuple.first legacy) in isNone (Tuple.second (P.reply 3 (counter "1") True (counter "52") fresh (Tuple.first c))))
 ]
main = Platform.worker {init=\_ -> ((),report (E.list (\(name,value)->E.object [("name",E.string name),("passed",E.bool value)]) cases)),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}
