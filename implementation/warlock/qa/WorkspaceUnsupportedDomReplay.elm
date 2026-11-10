port module WorkspaceUnsupportedDomReplay exposing (main)

{- Synthetic view-only fixture; emitted values are captured locally, never sent to a host. -}
import Browser
import Desktop
import Html exposing (Html, div, text)
import Json.Decode as D
import Json.Encode as E
import OutputController as Outputs
import OutputRetirementReplay as Fixture
import Surface
import SurfaceRenderer as Renderer
import SurfaceSnapshot
import UInt64

port outgoing : E.Value -> Cmd msg
port probe : (D.Value -> msg) -> Sub msg

type Msg = Tap E.Value | Probe D.Value

type alias Model = { desktop : Desktop.Model, snapshot : Result String Renderer.Snapshot }

one = UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero
ids = [ "overview:workspace-create", "overview:workspace-delete", "overview:workspace-rename" ]
wire id = E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("surface",E.string "popup"),("publication",E.string "1"),("lease",E.string "1"),("id",E.string id)]

init : () -> ( Model, Cmd Msg )
init _ =
    let ready = Fixture.base [("1",Fixture.left)]
        (opened,_) = Desktop.capture (Fixture.desktop ready) |> Maybe.map (\stamp -> Outputs.update (Outputs.Interaction (Desktop.OpenOverview stamp)) ready) |> Maybe.withDefault (ready,[])
        desktop = Fixture.desktop opened
        packet = Surface.packet one one desktop
    in ( { desktop=desktop,snapshot=Renderer.decode packet }, Cmd.none )

view : Model -> Html Msg
view model =
    case model.snapshot of
        Ok snapshot -> Renderer.view True Tap snapshot
        Err reason -> div [] [text ("snapshot-error: " ++ reason)]

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        Tap action -> ( model, outgoing (E.object [("kind",E.string "tap"),("action",action)]) )
        Probe _ ->
            let snapshotChecks = case model.snapshot of
                    Ok snapshot ->
                        SurfaceSnapshot.mode snapshot=="overview"
                            && List.all (\id -> SurfaceSnapshot.action True id snapshot==Nothing) ids
                            && SurfaceSnapshot.action True "control:close" snapshot/=Nothing
                    Err _ -> False
                sourceChecks = model.desktop.overview && List.all (\id -> Surface.resolve one one (wire id) model.desktop==Nothing) ids
                    && Surface.resolve one one (wire "control:close") model.desktop/=Nothing
                rowChecks = case model.snapshot of
                    Err _ -> False
                    Ok snapshot ->
                        let rows = (SurfaceSnapshot.details snapshot).popup
                            summary = rows |> List.filter (\row -> List.member row.identity ids) |> List.map (\row -> (row.identity,(row.label,row.ariaLabel),(row.detail,row.enabled,row.focusOnly)))
                            expected =
                                [ ("overview:workspace-create",("Create workspace","Create workspace; unavailable"),("Not supported",False,False))
                                , ("overview:workspace-delete",("Delete workspace","Delete workspace; unavailable"),("Not supported",False,False))
                                , ("overview:workspace-rename",("Rename workspace","Rename workspace; unavailable"),("Not supported",False,False)) ]
                            order = rows |> List.filter (\row -> List.member row.identity ("control:close" :: "overview:all" :: ids)) |> List.map .identity
                            close = rows |> List.filter (\row -> row.identity=="control:close")
                        in summary==expected && order==["control:close","overview:all","overview:workspace-create","overview:workspace-delete","overview:workspace-rename"]
                            && (close |> List.map (\row -> (row.label,row.enabled,row.focusOnly)))==[("Close Task View",True,False)]
                staleWire = E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("surface",E.string "popup"),("publication",E.string "2"),("lease",E.string "1"),("id",E.string "control:close")]
                staleChecks = Surface.resolve one one staleWire model.desktop==Nothing
                    && Surface.resolve one one (wire "control:close") model.desktop/=Nothing
            in (model,outgoing (E.object [("kind",E.string "probe"),("snapshotChecks",E.bool snapshotChecks),("sourceChecks",E.bool sourceChecks),("rowChecks",E.bool rowChecks),("staleChecks",E.bool staleChecks)]))

main : Program () Model Msg
main = Browser.element {init=init,view=view,update=update,subscriptions=\_ -> probe Probe}
