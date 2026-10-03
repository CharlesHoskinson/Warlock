port module Main exposing (main)
import Json.Encode as E
import Platform

type Identity = Identity String
type Receipt = Committed | Refused | Cancelled | Unknown
type Operation = Idle | AwaitingRestore Identity | Reconciling Identity | FocusReady Identity
type Msg = Restore Identity | RestoreReceipt Identity Receipt | Observation Identity Bool | Cancel
type Effect = SendRestore Identity | SendFocus Identity | ReadNativeTruth Identity
type alias Model = { operation : Operation }

update : Msg -> Model -> ( Model, List Effect )
update msg model =
    case ( msg, model.operation ) of
        ( Restore identity, Idle ) ->
            ( { operation = AwaitingRestore identity }, [ SendRestore identity ] )
        ( RestoreReceipt identity receipt, AwaitingRestore current ) ->
            if identity /= current then
                ( model, [] )
            else
                case receipt of
                    Committed -> ( { operation = FocusReady current }, [ SendFocus current ] )
                    Unknown -> ( { operation = Reconciling current }, [ ReadNativeTruth current ] )
                    Refused -> ( { operation = Idle }, [] )
                    Cancelled -> ( { operation = Idle }, [] )
        ( Observation identity eligible, Reconciling current ) ->
            if identity /= current then ( model, [] )
            else if eligible then ( { operation = FocusReady current }, [ SendFocus current ] )
            else ( { operation = Idle }, [] )
        ( Cancel, AwaitingRestore _ ) ->
            -- Frontend suppression only: native cancellation requires its receipt.
            ( { operation = Idle }, [] )
        _ -> ( model, [] )

port results : E.Value -> Cmd msg
check : String -> Bool -> E.Value
check name passed = E.object [ ( "name", E.string name ), ( "passed", E.bool passed ) ]
main : Program () () Never
main =
    Platform.worker
        { init = \_ ->
            let
                a = Identity "9007199254740993"
                b = Identity "9007199254740994"
                ( pending, restoreEffects ) = update (Restore a) { operation = Idle }
                ( committed, focusEffects ) = update (RestoreReceipt a Committed) pending
                ( stale, staleEffects ) = update (RestoreReceipt b Committed) pending
                ( uncertain, uncertainEffects ) = update (RestoreReceipt a Unknown) pending
                ( denied, deniedEffects ) = update (RestoreReceipt a Refused) pending
                ( cancelled, _ ) = update Cancel pending
                ( afterCancel, afterCancelEffects ) = update (RestoreReceipt a Committed) cancelled
                ( observed, observationEffects ) = update (Observation a True) uncertain
            in
            ( (), results (E.list identity
                [ check "restore-before-focus" (pending.operation == AwaitingRestore a && restoreEffects == [ SendRestore a ])
                , check "matching-commit-releases-focus" (committed.operation == FocusReady a && focusEffects == [ SendFocus a ])
                , check "lossless-stale-identity-refused" (stale == pending && List.isEmpty staleEffects)
                , check "unknown-observes-without-replay" (uncertain.operation == Reconciling a && uncertainEffects == [ ReadNativeTruth a ])
                , check "refused-does-not-focus" (denied.operation == Idle && List.isEmpty deniedEffects)
                , check "late-after-cancel-does-not-focus" (afterCancel.operation == Idle && List.isEmpty afterCancelEffects)
                , check "fresh-observation-releases-focus" (observed.operation == FocusReady a && observationEffects == [ SendFocus a ])
                , check "pure-replay" (update (RestoreReceipt a Unknown) pending == update (RestoreReceipt a Unknown) pending)
                ]))
        , update = \impossible _ -> never impossible
        , subscriptions = \_ -> Sub.none
        }
