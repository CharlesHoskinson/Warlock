port module UiHttpReplay exposing (main)

{-| QA interpreter for the actual production transport and owning pure policy.
No request/result reducer, receipt authority or alternate policy is modeled here.
The JavaScript oracle controls XHR outcomes and checks actual generated commands.
-}

import DesktopPolicy as Policy
import Json.Decode as D
import Json.Encode as E
import NativePreviewProposalIngress as Ingress
import NativePreviewRealm as Realm
import Http
import OutputController as Outputs
import Platform
import Process
import Task
import UiHttp

port incoming : (D.Value -> msg) -> Sub msg
port outgoing : E.Value -> Cmd msg

type alias Flags = { renderer : Bool }
type alias Model = { http : UiHttp.Model, policy : Policy.Model, renderer : Bool }
type Msg = Control D.Value | Transport UiHttp.Msg | Deadline Policy.Msg

report : String -> Maybe UiHttp.Event -> Model -> Cmd Msg
report label event model =
    outgoing (E.object
        [ ("label",E.string label)
        , ("problem",UiHttp.problem model.http |> Maybe.map E.string |> Maybe.withDefault E.null)
        , ("pendingBatches",E.int (Outputs.pendingBatches model.policy.controller))
        , ("event",case event of
            Nothing -> E.null
            Just (UiHttp.Incoming raw) -> E.object [("kind",E.string "incoming"),("value",raw)]
            Just (UiHttp.Lost reason) -> E.object [("kind",E.string "lost"),("reason",E.string reason)]
            Just (UiHttp.TransportConsumedCompleted _) -> E.object [("kind",E.string "consumed")])
        ])

policyEffects : List Policy.Effect -> Model -> (Model,List (Cmd Msg))
policyEffects descriptions initialModel =
    let
        step description (state,queued) =
            case description of
                Policy.Publish wire ->
                    let (http,command,_)=UiHttp.enqueue wire state.http
                    in ({state | http=http},Cmd.map Transport command::queued)
                Policy.Delay duration message ->
                    (state,(Process.sleep duration |> Task.perform (\_ -> Deadline (Policy.Deadline message)))::queued)
        (result,commands)=List.foldl step (initialModel,[]) descriptions
    in (result,List.reverse commands)

policy : Policy.Msg -> Model -> (Model,List (Cmd Msg))
policy message model =
    let (next,descriptions)=Policy.update message model.policy
    in policyEffects descriptions {model | policy=next}

-- Exercise production pure transitions using tickets minted only by ingress.
contractProbe : D.Value -> Cmd Msg
contractProbe raw =
    let decoder = D.map5 (\grant identity command ticket alternate -> (grant,(identity,command),(ticket,alternate)))
            (D.field "grant" Realm.grantDecoder) (D.field "identity" D.string)
            (D.field "command" D.value) (D.field "ticket" D.value) (D.field "alternate" D.value)
        bool name value = (name,E.bool value)
        result name value = outgoing (E.object [("label",E.string "contract-probe"),(name,value)])
    in case D.decodeValue decoder raw of
        Err _ -> result "error" (E.string "invalid probe input")
        Ok (grant,(identity,command),(fact,alternate)) ->
            case Ingress.enqueue [{identity=identity,command=command}] (Ingress.empty grant) of
                Nothing -> result "error" (E.string "ingress capacity")
                Just ingress ->
                    case (Ingress.issuedWithConfirmation fact ingress,Ingress.issuedWithConfirmation alternate ingress) of
                        (Just (_,ticket),Just (_,other)) ->
                            let (initial,_) = UiHttp.popupEffects
                                (first,firstEffects,_) = UiHttp.enqueueEffects (E.int 0) initial
                                push n state = let (next,_,_) = UiHttp.enqueueEffects (E.int n) state in next
                                full = List.foldl push first (List.range 1 15)
                                (deferred,deferredEffects,deferredResult) = UiHttp.tryEnqueueConsumedEffects ticket full
                                (overflow,_,overflowEvent) = UiHttp.enqueueEffects (E.int 16) full
                                firstSend = List.filterMap (\effect -> case effect of
                                    UiHttp.SendRequest requestId kind _ -> Just (requestId,kind)
                                    _ -> Nothing) firstEffects |> List.head
                                checkFirst = case firstSend of
                                    Nothing -> E.object [("error",E.string "no initial tagged send")]
                                    Just (id,kind) ->
                                        let (wrong,wrongEffects,_) = UiHttp.updateEffects (UiHttp.PostedFor id UiHttp.PopupConsumed (Ok "")) full
                                            (wrongError,wrongErrorEffects,_) = UiHttp.updateEffects (UiHttp.PostedFor id UiHttp.PopupConsumed (Err Http.Timeout)) full
                                            (legacy,legacyEffects,_) = UiHttp.updateEffects (UiHttp.Posted (Ok "")) full
                                            (drained,nextEffects,_) = UiHttp.updateEffects (UiHttp.PostedFor id kind (Ok "")) full
                                            (queued,queuedEffects,queuedResult) = UiHttp.tryEnqueueConsumedEffects ticket drained
                                            (duplicate,duplicateEffects,duplicateResult) = UiHttp.tryEnqueueConsumedEffects ticket queued
                                            (stale,staleEffects,_) = UiHttp.updateEffects (UiHttp.PostedFor id kind (Ok "")) queued
                                            (conflicted,conflictEffects,conflictResult) = UiHttp.tryEnqueueConsumedEffects other queued
                                            drain model effects count ordered =
                                                case List.filterMap (\effect -> case effect of
                                                    UiHttp.SendRequest requestId requestKind body -> Just (requestId,requestKind,body)
                                                    _ -> Nothing) effects of
                                                    [(requestId,requestKind,body)] ->
                                                        if requestKind == UiHttp.PopupConsumed then
                                                            let (_,_,event) = UiHttp.updateEffects (UiHttp.PostedFor requestId requestKind (Ok "")) model
                                                                exact = E.encode 0 body == E.encode 0 (Ingress.encodeConsumed ticket)
                                                                completed = case event of
                                                                    Just (UiHttp.TransportConsumedCompleted original) -> Ingress.sameAcceptedTicket original ticket
                                                                    _ -> False
                                                            in E.object [("count",E.int count),("fifo",E.bool ordered),("exact",E.bool exact),("completed",E.bool completed)]
                                                        else if count >= 15 then E.object [("error",E.string "extra action")] else
                                                            let (next,effectsNext,_) = UiHttp.updateEffects (UiHttp.PostedFor requestId requestKind (Ok "")) model
                                                                expected = E.encode 0 body == E.encode 0 (E.int (count+1))
                                                            in drain next effectsNext (count+1) (ordered && requestKind == UiHttp.RendererAction && expected)
                                                    _ -> E.object [("error",E.string "missing or duplicate send")]
                                        in E.object
                                            [ bool "deferred" (deferredResult == UiHttp.Deferred && deferred == full && List.isEmpty deferredEffects)
                                            , bool "overflow17" (UiHttp.problem overflow /= Nothing && overflowEvent /= Nothing)
                                            , bool "wrongKindStutter" (wrong == full && List.isEmpty wrongEffects)
                                            , bool "wrongErrorStutter" (wrongError == full && List.isEmpty wrongErrorEffects)
                                            , bool "legacyStutter" (legacy == full && List.isEmpty legacyEffects)
                                            , bool "queuedAfterDrain" (queuedResult == UiHttp.Queued && List.isEmpty queuedEffects)
                                            , bool "alreadyQueuedStutter" (duplicateResult == UiHttp.AlreadyQueued && duplicate == queued && List.isEmpty duplicateEffects)
                                            , bool "staleStutter" (stale == queued && List.isEmpty staleEffects)
                                            , bool "alteredWireStopped" (conflictResult == UiHttp.Stopped && UiHttp.problem conflicted /= Nothing && not (List.any (\effect -> case effect of
                                                UiHttp.SendRequest _ _ _ -> True
                                                _ -> False) conflictEffects))
                                            , ("drain",drain queued nextEffects 0 True)
                                            ]
                            in result "checks" checkFirst
                        _ -> result "error" (E.string "ticket not accepted by real ingress")

update : Msg -> Model -> (Model,Cmd Msg)
update message model =
    case message of
        Control raw ->
            case D.decodeValue (D.field "kind" D.string) raw of
                Ok "contract-probe" -> (model,contractProbe raw)
                Ok "enqueue" ->
                    case D.decodeValue (D.field "value" D.value) raw of
                        Err _ -> (model,report "invalid-control" Nothing model)
                        Ok value ->
                            let (http,command,event)=UiHttp.enqueue value model.http
                                next={model | http=http}
                            in (next,Cmd.batch [Cmd.map Transport command,report "enqueue" event next])
                Ok "stop" ->
                    let (http,command,event)=UiHttp.stop "Explicit fixture stop" model.http
                        next={model | http=http}
                    in (next,Cmd.batch [Cmd.map Transport command,report "stop" event next])
                Ok "policy" ->
                    case D.decodeValue (D.field "value" D.value) raw of
                        Err _ -> (model,report "invalid-control" Nothing model)
                        Ok value ->
                            let (next,commands)=policy (Policy.Incoming value) model
                            in (next,Cmd.batch (report "policy" Nothing next::commands))
                _ -> (model,report "invalid-control" Nothing model)
        Deadline value ->
            let (next,commands)=policy value model
            in (next,Cmd.batch (report "deadline" Nothing next::commands))
        Transport value ->
            let (http,command,event)=UiHttp.update value model.http
                current={model | http=http}
                (next,commands)=case event of
                    Just (UiHttp.Incoming raw) ->
                        if model.renderer then (current,[]) else policy (Policy.Incoming raw) current
                    Just (UiHttp.Lost _) -> policy Policy.TransportLost current
                    Just (UiHttp.TransportConsumedCompleted _) -> (current,[])
                    Nothing -> (current,[])
            in (next,Cmd.batch (Cmd.map Transport command::report "transport" event next::commands))

main : Program Flags Model Msg
main = Platform.worker
    { init=\flags ->
        let (http,command)=if flags.renderer then UiHttp.renderer else UiHttp.controller
        in ({http=http,policy=Policy.initial,renderer=flags.renderer},Cmd.map Transport command)
    , update=update
    , subscriptions=\_ -> incoming Control
    }
