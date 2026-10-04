module Menu exposing
    ( Action(..), AppId, Binding, DeclaredActionId, Effect(..), IntentId, Item
    , MenuId, MenuSnapshot, Model, Msg(..), Navigation(..), Outcome(..), OutputId
    , ProviderId, Snapshot, Status(..), Target(..), WindowId
    , appId, binding, declaredActionId, init, intentNumber, menuNumber, outputId
    , maxItems, maxLabel, maxOutstanding, maxRetired
    , providerId, snapshot, update, windowId
    )

{-| Pure context-menu lifecycle. Identifiers are authority-issued data, not
labels or executable commands. Construction is for an already validated adapter;
this module is not a transport decoder or a native authority implementation.

Dispatch carries the frozen binding for independent broker revalidation. A menu
never interprets a label as an action. Pending/uncertain dispatches survive menu
dismissal and block replay against the same binding until a definitive receipt.

This derivative bounds rows, labels, unresolved operations and retirement
tombstones. Labels use Elm String.length (UTF-16 units), without normalization or
grapheme counting. No unresolved operation or retirement is evicted. A new unique
retirement beyond the budget closes menus and permanently exhausts this instance;
exact correlated receipts still work. Duplicate retirements consume no capacity.
-}


maxItems : Int
maxItems =
    64


maxLabel : Int
maxLabel =
    256


maxOutstanding : Int
maxOutstanding =
    64


maxRetired : Int
maxRetired =
    128


type WindowId
    = WindowId String String


type AppId
    = AppId String


type ProviderId
    = ProviderId String


type OutputId
    = OutputId String


type DeclaredActionId
    = DeclaredActionId String


type MenuId
    = MenuId Int


type IntentId
    = IntentId Int


type Target
    = Window WindowId
    | Application AppId String
    | ProviderSelection ProviderId String (List String)
    | Background OutputId String


type Binding
    = Binding
        { authority : String
        , revision : String
        , output : OutputId
        , outputGeneration : String
        , target : Target
        }


windowId : String -> String -> WindowId
windowId =
    WindowId


appId : String -> AppId
appId =
    AppId


providerId : String -> ProviderId
providerId =
    ProviderId


outputId : String -> OutputId
outputId =
    OutputId


declaredActionId : String -> DeclaredActionId
declaredActionId =
    DeclaredActionId


binding : { authority : String, revision : String, output : OutputId, outputGeneration : String, target : Target } -> Binding
binding =
    Binding


type Action
    = Restore
    | Move
    | Size
    | Minimize
    | Maximize
    | Close
    | ExitFullscreen
    | AlwaysOnTop Bool
    | PinToTaskbar Bool
    | Launch DeclaredActionId
    | ProviderCommand DeclaredActionId


type alias Item =
    { label : String, enabled : Bool, action : Action }


type Navigation
    = Up
    | Down
    | Home
    | End


type Outcome
    = Committed
    | Refusal String
    | Cancellation
    | Uncertain


type Status
    = Ready
    | Pending IntentId
    | Refused String
    | Cancelled
    | Unknown IntentId


type alias MenuSnapshot =
    { id : MenuId
    , binding : Binding
    , items : List Item
    , selected : Maybe Int
    , status : Status
    }


type alias Snapshot =
    { menu : Maybe MenuSnapshot
    , lastOutcome : Maybe ( IntentId, Outcome )
    , outstanding : Int
    , invalidatedCount : Int
    , retiredOutputCount : Int
    , exhausted : Bool
    }


type alias Outstanding =
    { id : IntentId, binding : Binding, uncertain : Bool }


type Model
    = Model
        { menu : Maybe MenuSnapshot
        , nextMenu : Int
        , nextIntent : Int
        , outstanding : List Outstanding
        , lastOutcome : Maybe ( IntentId, Outcome )
        , invalidated : List Binding
        , retiredOutputs : List ( OutputId, String )
        , exhausted : Bool
        }


type Msg
    = Open Binding (List Item)
    | Select MenuId Binding Int
    | Navigate MenuId Navigation
    | Activate MenuId Binding Int
    | ReceiveFor IntentId Binding Outcome
    | Dismiss MenuId
    | Invalidate Binding
    | OutputRetired OutputId String


type Effect
    = Dispatch IntentId Binding Action


init : Model
init =
    Model
        { menu = Nothing
        , nextMenu = 1
        , nextIntent = 1
        , outstanding = []
        , lastOutcome = Nothing
        , invalidated = []
        , retiredOutputs = []
        , exhausted = False
        }


snapshot : Model -> Snapshot
snapshot (Model state) =
    { menu = state.menu
    , lastOutcome = state.lastOutcome
    , outstanding = List.length state.outstanding
    , invalidatedCount = List.length state.invalidated
    , retiredOutputCount = List.length state.retiredOutputs
    , exhausted = state.exhausted
    }


menuNumber : MenuId -> Int
menuNumber (MenuId number) =
    number


intentNumber : IntentId -> Int
intentNumber (IntentId number) =
    number


enabledIndices : List Item -> List Int
enabledIndices items =
    items
        |> List.indexedMap (\index item -> if item.enabled then Just index else Nothing)
        |> List.filterMap identity


itemAt : Int -> List Item -> Maybe Item
itemAt index items =
    if index < 0 then
        Nothing

    else
        List.head (List.drop index items)


navigate : Navigation -> MenuSnapshot -> MenuSnapshot
navigate direction menu =
    let
        enabled =
            enabledIndices menu.items

        first =
            List.head enabled

        last =
            List.head (List.reverse enabled)

        selected =
            case direction of
                Home ->
                    first

                End ->
                    last

                Down ->
                    case menu.selected of
                        Nothing -> first
                        Just index ->
                            List.head (List.filter ((<) index) enabled)
                                |> orElse first

                Up ->
                    case menu.selected of
                        Nothing -> last
                        Just index ->
                            List.head (List.reverse (List.filter ((>) index) enabled))
                                |> orElse last
    in
    { menu | selected = selected }


orElse : Maybe a -> Maybe a -> Maybe a
orElse fallback value =
    case value of
        Just _ -> value
        Nothing -> fallback


outputTuple : Binding -> ( OutputId, String )
outputTuple (Binding value) =
    ( value.output, value.outputGeneration )


sameTarget : Binding -> Binding -> Bool
sameTarget (Binding left) (Binding right) =
    left.target == right.target


awaits : IntentId -> Status -> Bool
awaits id status =
    case status of
        Pending pending -> pending == id
        Unknown unknown -> unknown == id
        _ -> False


validItems : List Item -> Bool
validItems items =
    let
        uniqueActions remaining seen =
            case remaining of
                [] -> True
                item :: rest ->
                    if List.member item.action seen then
                        False
                    else
                        uniqueActions rest (item.action :: seen)
    in
    List.length items <= maxItems
        && List.all (\item -> String.length item.label <= maxLabel && not (String.isEmpty (String.trim item.label))) items
        && uniqueActions items []


boundedOutcome : Outcome -> Outcome
boundedOutcome outcome =
    case outcome of
        Refusal reason ->
            let
                take remaining characters =
                    case characters of
                        [] -> ""
                        character :: rest ->
                            let value = String.fromChar character
                            in if String.length value > remaining then
                                ""
                            else
                                value ++ take (remaining - String.length value) rest
                -- Include one lookahead unit so a pair crossing unit 256 is
                -- complete before Elm converts it to Char. Only this bounded
                -- prefix is traversed; the first character that cannot fit
                -- terminates the result rather than skipping a codepoint.
                completePrefix =
                    String.left (maxLabel + 1) reason
                        |> String.toList
                        |> take maxLabel
            in
            Refusal completePrefix

        _ -> outcome


update : Msg -> Model -> ( Model, List Effect )
update message ((Model state) as model) =
    let
        unchanged =
            ( model, [] )

        valid target =
            not (List.member target state.invalidated)
                && not (List.member (outputTuple target) state.retiredOutputs)

        editMenu id transform =
            case state.menu of
                Just menu ->
                    if menu.id == id then
                        ( Model { state | menu = transform menu }, [] )
                    else
                        unchanged

                Nothing -> unchanged
    in
    case message of
        Open target items ->
            if state.exhausted || not (valid target) || not (validItems items) || state.nextMenu > 2147483647 then
                unchanged

            else
                let
                    status =
                        case List.head (List.filter (\entry -> sameTarget entry.binding target) state.outstanding) of
                            Nothing -> Ready
                            Just entry ->
                                if entry.uncertain then Unknown entry.id else Pending entry.id

                    menu =
                        { id = MenuId state.nextMenu
                        , binding = target
                        , items = items
                        , selected = List.head (enabledIndices items)
                        , status = status
                        }
                in
                ( Model { state | menu = Just menu, nextMenu = state.nextMenu + 1 }, [] )

        Select id target index ->
            editMenu id
                (\menu ->
                    if menu.binding == target && valid target then
                        case itemAt index menu.items of
                            Just item ->
                                if item.enabled then Just { menu | selected = Just index } else Just menu
                            Nothing -> Just menu
                    else
                        Just menu
                )

        Navigate id direction ->
            editMenu id (navigate direction >> Just)

        Activate id target index ->
            case state.menu of
                Nothing -> unchanged
                Just menu ->
                    if state.exhausted || menu.id /= id || menu.binding /= target || not (valid target) || state.nextIntent > 2147483647 then
                        unchanged

                    else if List.any (\entry -> sameTarget entry.binding target) state.outstanding then
                        unchanged

                    else
                        case itemAt index menu.items of
                            Just item ->
                                if item.enabled && List.length state.outstanding >= maxOutstanding then
                                    ( Model { state | menu = Just { menu | status = Refused "Outstanding operation limit reached; reconcile existing requests." } }, [] )

                                else if item.enabled then
                                    let
                                        intent = IntentId state.nextIntent
                                        entry = { id = intent, binding = target, uncertain = False }
                                    in
                                    ( Model
                                        { state
                                            | menu = Just { menu | selected = Just index, status = Pending intent }
                                            , nextIntent = state.nextIntent + 1
                                            , outstanding = entry :: state.outstanding
                                        }
                                    , [ Dispatch intent target item.action ]
                                    )
                                else unchanged

                            Nothing -> unchanged

        ReceiveFor intent receiptBinding receivedOutcome ->
            case List.head (List.filter (\entry -> entry.id == intent) state.outstanding) of
                Nothing -> unchanged
                Just entry ->
                    let
                        outcome = boundedOutcome receivedOutcome
                        outstanding =
                            if outcome == Uncertain then
                                List.map (\current -> if current.id == intent then { current | uncertain = True } else current) state.outstanding
                            else
                                List.filter (\current -> current.id /= intent) state.outstanding

                        menu =
                            state.menu
                                |> Maybe.andThen
                                    (\current ->
                                        if not (awaits intent current.status) then
                                            Just current
                                        else
                                            case outcome of
                                                Committed -> Nothing
                                                Refusal reason -> Just { current | status = Refused reason }
                                                Cancellation -> Just { current | status = Cancelled }
                                                Uncertain -> Just { current | status = Unknown intent }
                                    )
                    in
                    ( Model { state | outstanding = outstanding, menu = menu, lastOutcome = Just ( intent, outcome ) }, [] )

        Dismiss id ->
            editMenu id (\_ -> Nothing)

        Invalidate target ->
            if List.member target state.invalidated || state.exhausted then
                unchanged

            else if List.length state.invalidated + List.length state.retiredOutputs >= maxRetired then
                ( Model { state | exhausted = True, menu = Nothing }, [] )

            else
                let
                    invalidated = target :: state.invalidated
                    menu =
                        state.menu |> Maybe.andThen (\current -> if current.binding == target then Nothing else Just current)
                in
                ( Model { state | invalidated = invalidated, menu = menu }, [] )

        OutputRetired output generation ->
            let
                retired = ( output, generation )
            in
            if List.member retired state.retiredOutputs || state.exhausted then
                unchanged

            else if List.length state.invalidated + List.length state.retiredOutputs >= maxRetired then
                ( Model { state | exhausted = True, menu = Nothing }, [] )

            else
                let
                    retiredOutputs = retired :: state.retiredOutputs
                    menu =
                        state.menu |> Maybe.andThen (\current -> if outputTuple current.binding == retired then Nothing else Just current)
                in
                ( Model { state | retiredOutputs = retiredOutputs, menu = menu }, [] )
