module Settings exposing (Model, Values, Snapshot, Theme(..), initial, defaults, valuesDecoder, decoder, encodeValues, encode, themeName, observe, edit, writable, propose, receive)

import Json.Decode as D
import Json.Encode as E
import UInt64 exposing (Counter)

type Theme = Night | Dawn | HighContrast
type alias Values = { theme : Theme, textScale : Int }
type alias Snapshot = { schema : Int, revision : Counter, values : Values }
type alias Model = { snapshot : Maybe Snapshot, draft : Values, pending : Maybe { request : Counter, values : Values }, notice : String }

defaults : Values
defaults = {theme=Night,textScale=100}
initial : Model
initial = {snapshot=Nothing,draft=defaults,pending=Nothing,notice="Loading settings…"}
strict fields child = D.keyValuePairs D.value |> D.andThen (\pairs -> if List.sort (List.map Tuple.first pairs)==List.sort fields then child else D.fail "Settings fields")
themeName theme = case theme of
    Night -> "night"
    Dawn -> "dawn"
    HighContrast -> "high-contrast"
valuesDecoder : D.Decoder Values
valuesDecoder = strict ["theme","textScale"] (D.map2 Values
    (D.field "theme" (D.string |> D.andThen (\value -> case value of
        "night" -> D.succeed Night
        "dawn" -> D.succeed Dawn
        "high-contrast" -> D.succeed HighContrast
        _ -> D.fail "Theme unavailable")))
    (D.field "textScale" (D.int |> D.andThen (\scale -> if List.member scale [100,125,150,200] then D.succeed scale else D.fail "Text scale unavailable"))))
decoder : D.Decoder Snapshot
decoder = strict ["schema","revision","values"] (D.map3 Snapshot
    (D.field "schema" (D.int |> D.andThen (\version -> if version==1 then D.succeed version else D.fail "Settings schema unavailable")))
    (D.field "revision" (UInt64.decoder |> D.andThen (\revision -> if revision/=UInt64.zero then D.succeed revision else D.fail "Settings revision")))
    (D.field "values" valuesDecoder))
encodeValues values = E.object [("theme",E.string (themeName values.theme)),("textScale",E.int values.textScale)]
encode snapshot = E.object [("schema",E.int snapshot.schema),("revision",E.string (UInt64.string snapshot.revision)),("values",encodeValues snapshot.values)]
observe : Maybe Snapshot -> Model -> Model
observe snapshot model = case snapshot of
    Nothing -> {model | snapshot=Nothing,pending=Nothing,notice="Settings unavailable or from an unsupported version. Refresh to read them again; the stored copy is preserved."}
    Just current ->
        if model.snapshot |> Maybe.map (\old -> UInt64.compare current.revision old.revision==LT) |> Maybe.withDefault False then model else
            {model | snapshot=Just current,draft=current.values,pending=Nothing,notice="Settings loaded."}
writable model = model.snapshot/=Nothing && model.pending==Nothing
edit : Values -> Model -> Model
edit values model = if not (writable model) || not (List.member values.textScale [100,125,150,200]) then model else {model | draft=values,notice="Unsaved changes. Save to apply."}
propose : Counter -> Model -> (Model,Maybe E.Value)
propose request model = case model.snapshot of
    Just current ->
        if not (writable model) || current.values==model.draft then (model,Nothing) else
            ({model | pending=Just {request=request,values=model.draft},notice="Saving settings…"},Just (encode {current | values=model.draft}))
    Nothing -> (model,Nothing)
receive : Counter -> String -> Maybe Snapshot -> Model -> Model
receive request status snapshot model = case model.pending of
    Nothing -> model
    Just pending ->
        if request/=pending.request then model else
        if status=="Saved" && (snapshot |> Maybe.map (\current -> current.values==pending.values && (model.snapshot |> Maybe.map (\old -> UInt64.compare current.revision old.revision==GT) |> Maybe.withDefault False)) |> Maybe.withDefault False) then
            {model | snapshot=snapshot,pending=Nothing,notice="Settings saved."}
        else if status=="Refused" then {model | pending=Nothing,notice="Settings change refused. Refresh, then choose again."}
        else {model | notice="Settings save not confirmed. Refresh to read the stored values; this write will not be repeated."}
