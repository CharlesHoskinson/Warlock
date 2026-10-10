module OutcomeAnnouncements exposing (Model, initial, observe, encode)

import Announcement
import Binding
import Catalog
import Desktop
import Effects
import Json.Encode as E
import Launch
import Settings
import Surface
import UInt64 exposing (Counter)

-- One policy in the integration root. Views never infer attention from copy,
-- count changes, rendering, publications or focus. No notification source is
-- admitted without its frozen relevance/DND/urgency permission data.
type Model = Model Counter (Maybe Announcement.Message)

initial : Model
initial = Model UInt64.zero Nothing

launch model = Launch.refusal model.launch
transfer model = model.windows.shell.effects.transaction |> Maybe.andThen (\transaction ->
    case transaction.intent.operation of
        Effects.TransferWorkspace _ -> if transaction.status==Effects.Refused then Just (E.object [("effectProtocol",E.int transaction.effectProtocol),("intent",Effects.encodeIntent transaction.intent)]) else Nothing
        _ -> Nothing)
settings model = model.settings.outcome |> Maybe.andThen (\outcome -> if outcome.result==Settings.Refused then Just outcome.request else Nothing)

observe : Desktop.Model -> Desktop.Model -> Model -> Model
observe before after ((Model sequence _) as prior) =
    let correlated kind value text = {correlation=E.encode 0 (E.object [("outcome",E.string kind),("binding",after.windows.shell.binding |> Maybe.map Binding.encode |> Maybe.withDefault E.null),("identity",value)]),text=text}
        candidate =
            if launch before/=launch after then launch after |> Maybe.map (\refusal ->
                let label=after.applications |> Maybe.andThen (Catalog.lookup refusal.entry) |> Maybe.map .name |> Maybe.withDefault refusal.entry
                in correlated "launch-refused" refusal.intent ("Launch refused for "++String.left 512 label++". Refresh applications, then choose again."))
            else if transfer before/=transfer after then transfer after |> Maybe.map (\intent -> correlated "transfer-refused" intent (Surface.windowNotice after))
            else if settings before/=settings after then settings after |> Maybe.map (\request -> correlated "settings-refused" (E.string (UInt64.string request)) after.settings.notice)
            else Nothing
    in case (candidate,UInt64.next sequence) of
        (Just event,Just next) -> Model next (Just {sequence=next,correlation=event.correlation,text=event.text})
        _ -> prior

encode : Model -> E.Value
encode (Model _ current) = current |> Maybe.map Announcement.encodeMessage |> Maybe.withDefault E.null
