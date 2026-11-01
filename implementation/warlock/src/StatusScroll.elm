module StatusScroll exposing
    ( Model
    , Epoch
    , reservedDomPrefix
    , isReservedDomId
    , initial
    , fromFloor
    , epoch
    , epochString
    , formatDomId
    , domId
    , domIdForSnapshot
    , exhausted
    , currentStatus
    , observe
    , observeSnapshot
    )

{-| Local viewport scroll-reset state for the passive taskbar status region.

 Contracts and invariants:
 - Display status text is compared strictly for local viewport scroll reset; it
   carries zero native, attention, or announcement authority.
 - `reservedDomPrefix` (`"warlock-bar-status-scroll-"`) is structurally reserved
   for the bar status scrollport; `SurfaceRenderer.controlDomId` excludes every
   rendered control/input/caption/description DOM `id` from this prefix across
   all frames so queued or stale `Browser.Dom.setViewportOf` tasks can never
   alias a control element (no cross-frame ABA).
 - `Epoch` wraps a strictly positive `UInt64.Counter` (`1 .. 18446744073709551615`)
   with private constructors.
 - The first accepted presentation seeds the initial epoch without emitting an
   unnecessary reset task on fresh mount.
 - Repeating an identical display status across new publications, appearance
   updates, or control updates preserves the exact `Epoch` and DOM ID so user
   scroll offset and focus stay intact and any already-queued reset for that
   epoch still resolves its target element.
 - Changing accepted display status advances `Epoch` monotonically by `+1` and
   emits a local viewport reset targeting the new epoch's DOM ID; stale tasks
   targeting any retired epoch ID fail closed (`Browser.Dom.NotFound`).
 - Counter exhaustion (`UInt64.next == Nothing`) permanently withdraws the DOM ID
   (`Nothing`) and emits no reset task (fail-closed, zero ID reuse).
-}

import SurfaceSnapshot
import UInt64 exposing (Counter)


type Epoch
    = Epoch Counter


type State
    = Unseeded Counter
    | Active Epoch String
    | Exhausted String


type Model
    = Model State


reservedDomPrefix : String
reservedDomPrefix =
    "warlock-bar-status-scroll-"


isReservedDomId : String -> Bool
isReservedDomId candidate =
    String.startsWith reservedDomPrefix candidate


initial : Model
initial =
    fromFloor UInt64.zero


fromFloor : Counter -> Model
fromFloor floor =
    Model (Unseeded floor)


epoch : Model -> Maybe Epoch
epoch (Model state) =
    case state of
        Unseeded _ ->
            Nothing

        Active currentEpoch _ ->
            Just currentEpoch

        Exhausted _ ->
            Nothing


epochString : Epoch -> String
epochString (Epoch counter) =
    UInt64.string counter


formatDomId : Epoch -> String
formatDomId currentEpoch =
    reservedDomPrefix ++ epochString currentEpoch


domId : Model -> Maybe String
domId model =
    epoch model |> Maybe.map formatDomId


domIdForSnapshot : SurfaceSnapshot.Snapshot -> Model -> Maybe String
domIdForSnapshot _ model =
    domId model


exhausted : Model -> Bool
exhausted (Model state) =
    case state of
        Exhausted _ ->
            True

        _ ->
            False


currentStatus : Model -> Maybe String
currentStatus (Model state) =
    case state of
        Unseeded _ ->
            Nothing

        Active _ statusText ->
            Just statusText

        Exhausted statusText ->
            Just statusText


observe : String -> Model -> ( Model, Maybe ( Epoch, String ) )
observe nextStatus (Model state) =
    case state of
        Unseeded floor ->
            case UInt64.next floor of
                Just firstCounter ->
                    ( Model (Active (Epoch firstCounter) nextStatus), Nothing )

                Nothing ->
                    ( Model (Exhausted nextStatus), Nothing )

        Active ((Epoch counter) as currentEpoch) previousStatus ->
            if nextStatus == previousStatus then
                ( Model (Active currentEpoch previousStatus), Nothing )

            else
                case UInt64.next counter of
                    Just nextCounter ->
                        let
                            nextEpoch =
                                Epoch nextCounter
                        in
                        ( Model (Active nextEpoch nextStatus)
                        , Just ( nextEpoch, formatDomId nextEpoch )
                        )

                    Nothing ->
                        ( Model (Exhausted nextStatus), Nothing )

        Exhausted _ ->
            ( Model (Exhausted nextStatus), Nothing )


observeSnapshot : SurfaceSnapshot.Snapshot -> Model -> ( Model, Maybe ( Epoch, String ) )
observeSnapshot snapshot model =
    let
        snapDetails =
            SurfaceSnapshot.details snapshot
    in
    observe snapDetails.status model
