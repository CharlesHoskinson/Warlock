module SiteMain exposing
    ( AppearanceTheme(..)
    , CueFacts
    , Model
    , MotionMode(..)
    , Msg(..)
    , OutcomeSample(..)
    , SurfaceCategory(..)
    , SurfaceId(..)
    , init
    , main
    , update
    , view
    , viewDocument
    )

import Browser
import Browser.Dom as Dom
import Html exposing (Html)
import Html.Attributes as Attr
import Html.Events as Events
import Json.Decode as Decode
import Task


main : Program () Model Msg
main =
    Browser.element
        { init = init
        , view = view
        , update = update
        , subscriptions = \_ -> Sub.none
        }



-- MODEL


type AppearanceTheme
    = ThemeNight
    | ThemeDawn
    | ThemeHighContrast


type MotionMode
    = MotionStandard
    | MotionReduced


type SurfaceId
    = SurfaceTaskbar
    | SurfaceLauncher
    | SurfaceSwitcher
    | SurfaceTaskView
    | SurfaceSnap
    | SurfaceNotifications
    | SurfaceSettings
    | SurfaceFiles


type SurfaceCategory
    = CategoryAll
    | CategoryWindows
    | CategoryAppsFiles
    | CategorySystem


type OutcomeSample
    = SampleObserved
    | SamplePending
    | SampleUnknown
    | SampleRefused


type alias CueFacts =
    { windowFocused : Bool
    , activeApplication : Bool
    , switcherCandidate : Bool
    }


type alias Model =
    { theme : AppearanceTheme
    , motion : MotionMode
    , mobileNavOpen : Bool
    , spotlight : SurfaceId
    , tabFocusSeq : Int
    , lastTabFocusMiss : Maybe String
    , category : SurfaceCategory
    , cues : CueFacts
    , outcomeSample : OutcomeSample
    }


type Msg
    = SelectTheme AppearanceTheme
    | ToggleMotion
    | ToggleMobileNav
    | CloseMobileNav
    | SelectSpotlight SurfaceId
    | StepSpotlight Int
    | KeyboardStepSpotlight Int
    | KeyboardJumpSpotlight SurfaceId
    | TabFocusSettled Int SurfaceId (Result Dom.Error ())
    | SelectCategory SurfaceCategory
    | ToggleWindowFocused
    | ToggleActiveApplication
    | ToggleSwitcherCandidate
    | SelectOutcomeSample OutcomeSample


init : () -> ( Model, Cmd Msg )
init _ =
    ( { theme = ThemeNight
      , motion = MotionStandard
      , mobileNavOpen = False
      , spotlight = SurfaceTaskbar
      , tabFocusSeq = 0
      , lastTabFocusMiss = Nothing
      , category = CategoryAll
      , cues =
            { windowFocused = True
            , activeApplication = True
            , switcherCandidate = False
            }
      , outcomeSample = SampleObserved
      }
    , Cmd.none
    )


update : Msg -> Model -> ( Model, Cmd Msg )
update msg currentModel =
    case msg of
        SelectTheme chosenTheme ->
            ( { currentModel | theme = chosenTheme }, Cmd.none )

        ToggleMotion ->
            let
                nextMotion =
                    case currentModel.motion of
                        MotionStandard ->
                            MotionReduced

                        MotionReduced ->
                            MotionStandard
            in
            ( { currentModel | motion = nextMotion }, Cmd.none )

        ToggleMobileNav ->
            ( { currentModel | mobileNavOpen = not currentModel.mobileNavOpen }, Cmd.none )

        CloseMobileNav ->
            ( { currentModel | mobileNavOpen = False }, Cmd.none )

        SelectSpotlight surfaceId ->
            ( { currentModel | spotlight = surfaceId, lastTabFocusMiss = Nothing }, Cmd.none )

        StepSpotlight delta ->
            ( { currentModel
                | spotlight = stepSurface delta currentModel.spotlight
                , lastTabFocusMiss = Nothing
              }
            , Cmd.none
            )

        KeyboardStepSpotlight delta ->
            let
                targetSurface =
                    stepSurface delta currentModel.spotlight

                nextSeq =
                    currentModel.tabFocusSeq + 1
            in
            ( { currentModel
                | spotlight = targetSurface
                , tabFocusSeq = nextSeq
                , lastTabFocusMiss = Nothing
              }
            , Task.attempt
                (TabFocusSettled nextSeq targetSurface)
                (Dom.focus (surfaceTabDomId targetSurface))
            )

        KeyboardJumpSpotlight targetSurface ->
            let
                nextSeq =
                    currentModel.tabFocusSeq + 1
            in
            ( { currentModel
                | spotlight = targetSurface
                , tabFocusSeq = nextSeq
                , lastTabFocusMiss = Nothing
              }
            , Task.attempt
                (TabFocusSettled nextSeq targetSurface)
                (Dom.focus (surfaceTabDomId targetSurface))
            )

        TabFocusSettled seq targetSurface focusOutcome ->
            if seq /= currentModel.tabFocusSeq || targetSurface /= currentModel.spotlight then
                ( currentModel, Cmd.none )

            else
                case focusOutcome of
                    Ok () ->
                        ( { currentModel | lastTabFocusMiss = Nothing }, Cmd.none )

                    Err (Dom.NotFound missingDomId) ->
                        ( { currentModel | lastTabFocusMiss = Just missingDomId }, Cmd.none )

        SelectCategory chosenCategory ->
            ( { currentModel | category = chosenCategory }, Cmd.none )

        ToggleWindowFocused ->
            let
                prior =
                    currentModel.cues
            in
            ( { currentModel | cues = { prior | windowFocused = not prior.windowFocused } }
            , Cmd.none
            )

        ToggleActiveApplication ->
            let
                prior =
                    currentModel.cues
            in
            ( { currentModel | cues = { prior | activeApplication = not prior.activeApplication } }
            , Cmd.none
            )

        ToggleSwitcherCandidate ->
            let
                prior =
                    currentModel.cues
            in
            ( { currentModel | cues = { prior | switcherCandidate = not prior.switcherCandidate } }
            , Cmd.none
            )

        SelectOutcomeSample sample ->
            ( { currentModel | outcomeSample = sample }, Cmd.none )



-- STRUCTURED CATALOG & SITE DATA


type alias SurfaceSpec =
    { surfaceId : SurfaceId
    , anchorId : String
    , label : String
    , heading : String
    , chord : String
    , category : SurfaceCategory
    , imageSrc : String
    , imageWidth : Int
    , imageHeight : Int
    , imageAlt : String
    , summary : String
    , elmAuthority : String
    , hostObservation : String
    , scenarioHref : String
    , scenarioCta : String
    , specHref : String
    }


type alias CardSpec =
    { eyebrow : String
    , title : String
    , body : String
    , detail : String
    }


type alias NavCardSpec =
    { title : String
    , body : String
    , href : String
    }


type alias DirectoryGroup =
    { heading : String
    , links : List ( String, String )
    }


taskbarSurface : SurfaceSpec
taskbarSurface =
    { surfaceId = SurfaceTaskbar
    , anchorId = "taskbar"
    , label = "Taskbar"
    , heading = "Your apps, one bar away"
    , chord = "Super + 1-9"
    , category = CategoryWindows
    , imageSrc = "./assets/site/feature-taskbar.png"
    , imageWidth = 1600
    , imageHeight = 330
    , imageAlt = "The Warlock taskbar across the top of the desktop with pinned applications, Start, Task View and the tray"
    , summary = "Pinned and running applications share the top bar. A neutral pill marks running apps and turns lacquer red for the active application alongside Start, Task View, Alt-Tab, notifications, Files, System, and Settings."
    , elmAuthority = "Group ordering, primary action routing (activate, minimize, restore, or picker), active indicator projection, and accessible status text."
    , hostObservation = "Observed window families, per-output focus and minimized state, CAS pin-store revisions, and effect completion receipts."
    , scenarioHref = "./test-drive/index.html?scenario=taskbar"
    , scenarioCta = "Try the taskbar"
    , specHref = "./components/taskbar/index.html"
    }


allSurfaces : List SurfaceSpec
allSurfaces =
    [ taskbarSurface
    , { surfaceId = SurfaceLauncher
      , anchorId = "launcher"
      , label = "Launcher"
      , heading = "Search, then launch"
      , chord = "Super + Alt + Space"
      , category = CategoryAppsFiles
      , imageSrc = "./assets/site/feature-launcher.png"
      , imageWidth = 1000
      , imageHeight = 620
      , imageAlt = "The Start-style launcher with its search field, application actions and launch tiles"
      , summary = "Open Applications, type a query with IME composition safety, and launch the matching entry. The top result exposes application actions and recent items while pinned apps reorder cleanly."
      , elmAuthority = "IME-safe search composition, deterministic ranking, bounded paging, compact metadata disclosure, and pin causality guards."
      , hostObservation = "Haskell catalog snapshots, durable pin-store revisions, and Submitted, Refused, or Unknown launch receipts distinct from window mapping."
      , scenarioHref = "./test-drive/index.html?scenario=launcher"
      , scenarioCta = "Try the launcher"
      , specHref = "./components/launcher/index.html"
      }
    , { surfaceId = SurfaceSwitcher
      , anchorId = "switcher"
      , label = "Alt-Tab"
      , heading = "Switch windows the way you expect"
      , chord = "Alt + Tab"
      , category = CategoryWindows
      , imageSrc = "./assets/site/feature-switcher.png"
      , imageWidth = 1000
      , imageHeight = 620
      , imageAlt = "The Alt-Tab window switcher with the selected window highlighted"
      , summary = "Hold Alt and tap Tab to step through open windows. Corner candidate brackets mark the prospective window before you commit, and Escape leaves focus untouched."
      , elmAuthority = "Candidate traversal order, ARIA selection state, commit vs cancel transitions, and steady card geometry across live or fallback previews."
      , hostObservation = "Window incarnation identities, preview stream grants or fallbacks, and verified Hyprland focus change after commit."
      , scenarioHref = "./test-drive/index.html?scenario=switcher"
      , scenarioCta = "Try Alt-Tab"
      , specHref = "./components/window-switcher/index.html"
      }
    , { surfaceId = SurfaceTaskView
      , anchorId = "task-view"
      , label = "Task View"
      , heading = "Every desktop at a glance"
      , chord = "Task View"
      , category = CategoryWindows
      , imageSrc = "./assets/site/feature-task-view.png"
      , imageWidth = 1000
      , imageHeight = 620
      , imageAlt = "Task View showing workspaces with their windows"
      , summary = "Inspect workspaces and their windows side by side, transfer a window to another desktop, or switch straight to an empty or populated workspace."
      , elmAuthority = "Workspace filter toggles, transfer destination selection, and generation-bound navigation intents."
      , hostObservation = "Observed workspace topology, monitor ownership, and post-command workspace or transfer verification."
      , scenarioHref = "./test-drive/index.html?scenario=task-view"
      , scenarioCta = "Try Task View"
      , specHref = "./components/task-view/index.html"
      }
    , { surfaceId = SurfaceSnap
      , anchorId = "snap"
      , label = "Snap layouts"
      , heading = "Snap into place"
      , chord = "Snap chooser"
      , category = CategoryWindows
      , imageSrc = "./assets/site/feature-snap.png"
      , imageWidth = 1000
      , imageHeight = 620
      , imageAlt = "The snap layout chooser with half and quarter screen regions"
      , summary = "Choose a half or quarter of the screen from the snap chooser and apply deliberately. Warlock asks Hyprland to place the window and retains pre-snap bounds for clean restore."
      , elmAuthority = "Region selection state, explicit Apply confirmation, and separation of snapped state from maximized restore."
      , hostObservation = "Floating window eligibility checks, observed work-area geometry, and post-placement bounds confirmation."
      , scenarioHref = "./test-drive/index.html?scenario=snap"
      , scenarioCta = "Try snap layouts"
      , specHref = "./components/snap-layouts/index.html"
      }
    , { surfaceId = SurfaceNotifications
      , anchorId = "notifications"
      , label = "Notifications"
      , heading = "Stay in the loop"
      , chord = "Tray · Bell"
      , category = CategorySystem
      , imageSrc = "./assets/site/feature-notifications.png"
      , imageWidth = 1000
      , imageHeight = 620
      , imageAlt = "The notification center with live notifications, their actions and do not disturb"
      , summary = "Live notifications preserve their producer actions, bounded history keeps what you missed, and Do Not Disturb holds interruptions while you focus."
      , elmAuthority = "History presentation, Do Not Disturb toggle state, and single-surface accessible announcement routing."
      , hostObservation = "Desktop notification service snapshots, action invocation receipts, and dismissal settlements."
      , scenarioHref = "./test-drive/index.html?scenario=notifications"
      , scenarioCta = "Try notifications"
      , specHref = "./components/notifications/index.html"
      }
    , { surfaceId = SurfaceSettings
      , anchorId = "settings"
      , label = "Settings"
      , heading = "Make it yours"
      , chord = "Explicit Save"
      , category = CategorySystem
      , imageSrc = "./assets/site/feature-settings.png"
      , imageWidth = 1000
      , imageHeight = 620
      , imageAlt = "Warlock Settings with theme, text size, motion and effects choices"
      , summary = "Review Night, Dawn, or High contrast, 100-200% text size, reduced motion, and portal effect tiers as a draft, then commit atomically with Save."
      , elmAuthority = "Draft vs committed appearance state, revision-bound Save proposals, and immediate reduced-motion precedence."
      , hostObservation = "Atomic preference writes, storage revision receipts, and system reduced-motion observations."
      , scenarioHref = "./test-drive/index.html?scenario=settings"
      , scenarioCta = "Try Settings"
      , specHref = "./components/appearance-settings/index.html"
      }
    , { surfaceId = SurfaceFiles
      , anchorId = "files"
      , label = "Files"
      , heading = "Your folders, one click away"
      , chord = "Tray · Files"
      , category = CategoryAppsFiles
      , imageSrc = "./assets/site/feature-files.png"
      , imageWidth = 1000
      , imageHeight = 620
      , imageAlt = "Files with quick-access tiles for Home, Recent and the collections"
      , summary = "Open Home, Recent, Downloads, Documents, or collections from quick-access tiles, or submit a folder path for checked handoff to Omarchy's Files application."
      , elmAuthority = "Quick-access tile controls, path input state, and non-replaying outcome feedback when a path is refused or unconfirmed."
      , hostObservation = "Quint-specified file operation checks, validated path resolution, and peer launch receipts."
      , scenarioHref = "./test-drive/index.html?scenario=files"
      , scenarioCta = "Try Files"
      , specHref = "./components/files/index.html"
      }
    ]


scopeCards : List CardSpec
scopeCards =
    [ { eyebrow = "Browser test drive · Simulated stage"
      , title = "Interactive Elm interface on fixture desktop state"
      , body = "The browser test drive runs Warlock's compiled Elm surfaces (Main, Bar, and Popup) over a deterministic simulated stage. Window interiors are browser fixtures, not Linux processes, Wayland surfaces, or native acceptance proof."
      , detail = "Route: ./test-drive/index.html (16 seeded scenarios)"
      }
    , { eyebrow = "Beta MVP · Active integration"
      , title = "Elm GUI + Haskell runtime custody"
      , body = "Authored production code uses Elm and Haskell only, with every GUI element in Elm. Private UI origin, strict CSP, and WebKit engine hardening gates (ELM-ARC-024 and ELM-DEL-014) remain OPEN in active verification."
      , detail = "Source: implementation/warlock/ (no Python runtime ships)"
      }
    , { eyebrow = "Native release gate · 242 requirements / 417 scenarios"
      , title = "Full release and native parity remain incomplete"
      , body = "Warlock preserves all 242 original requirements, 417 scenarios, literal latency deadlines, and frozen failure records. Fifteen whole original requirements hold source-bound historical acceptance in the canonical ledger (retaining their recorded scope), while full release and native parity obligations remain incomplete."
      , detail = "Historical verdicts retain recorded source scope; browser demos never imply native acceptance"
      }
    , { eyebrow = "Documentation website · Outside desktop runtime"
      , title = "Elm homepage source with shared Lacquer tokens"
      , body = "This homepage is authored in Elm (Browser.element, zero new authored JavaScript) consuming shared site/assets/shared/ tokens and styles. Standalone HTML publication runs through Root's protected compiler."
      , detail = "Contract: site/src/SiteMain.elm + site/elm.json"
      }
    ]


principleCards : List ( String, String )
principleCards =
    [ ( "Show what is known", "Keep intent, host receipt, and observed window state distinct." )
    , ( "Keep targets steady", "Preserve control identity and geometry while asynchronous facts arrive." )
    , ( "Separate attention", "Give window focus, active app, and switcher candidate distinct cues." )
    , ( "Use color economically", "Let neutral lacquer surfaces carry content and purposeful color carry meaning." )
    , ( "Preserve access", "Keep every action reachable by keyboard, 200% enlarged text, and reduced motion." )
    ]


guideCards : List NavCardSpec
guideCards =
    [ { title = "Foundations", body = "Principles, accessibility, keyboard interaction, and layered windows.", href = "./foundations/index.html" }
    , { title = "Styles", body = "Lacquer color, typography, shape, elevation, motion, icons, and portal effects.", href = "./styles/index.html" }
    , { title = "Components", body = "Specifications, anatomy, states, and specimens for all 19 desktop surfaces.", href = "./components/index.html" }
    , { title = "Architecture", body = "Follow Elm policy authority, Haskell services, and compositor boundaries.", href = "./architecture/index.html" }
    , { title = "Get started", body = "Design tokens, Elm + Haskell workflow, contributor rules, and licenses.", href = "./get-started/index.html" }
    , { title = "Search & frozen catalog", body = "Search documentation routes or inspect the frozen v6 reference catalog.", href = "./search/index.html" }
    ]


directoryGroups : List DirectoryGroup
directoryGroups =
    [ { heading = "Foundations & styles"
      , links =
            [ ( "Design principles", "./foundations/principles/index.html" )
            , ( "Accessibility", "./foundations/accessibility/index.html" )
            , ( "Interaction", "./foundations/interaction/index.html" )
            , ( "Layered windows", "./foundations/layered-windows/index.html" )
            , ( "Color", "./styles/color/index.html" )
            , ( "Typography", "./styles/typography/index.html" )
            , ( "Shape & elevation", "./styles/shape/index.html" )
            , ( "Elevation & glow", "./styles/elevation-glow/index.html" )
            , ( "Motion", "./styles/motion/index.html" )
            , ( "Effects", "./styles/effects/index.html" )
            , ( "Iconography", "./styles/iconography/index.html" )
            , ( "CSS architecture", "./styles/css-architecture/index.html" )
            ]
      }
    , { heading = "Core desktop components"
      , links =
            [ ( "Taskbar", "./components/taskbar/index.html" )
            , ( "Application groups", "./components/application-groups/index.html" )
            , ( "Launcher", "./components/launcher/index.html" )
            , ( "Window picker", "./components/window-picker/index.html" )
            , ( "Window switcher", "./components/window-switcher/index.html" )
            , ( "Task View", "./components/task-view/index.html" )
            , ( "Workspace transfer", "./components/workspace-transfer/index.html" )
            , ( "Previews", "./components/previews/index.html" )
            , ( "Popup surfaces", "./components/popup-surfaces/index.html" )
            , ( "Window menu", "./components/window-menu/index.html" )
            ]
      }
    , { heading = "System, files & reference"
      , links =
            [ ( "Snap layouts", "./components/snap-layouts/index.html" )
            , ( "Application actions", "./components/application-actions/index.html" )
            , ( "Notifications", "./components/notifications/index.html" )
            , ( "Appearance settings", "./components/appearance-settings/index.html" )
            , ( "Motion & shortcuts help", "./components/motion-shortcuts-help/index.html" )
            , ( "Files", "./components/files/index.html" )
            , ( "System menu", "./components/system-menu/index.html" )
            , ( "Dialogs", "./components/dialogs/index.html" )
            , ( "Status & recovery", "./components/status-recovery/index.html" )
            , ( "Contributing", "./get-started/contributing/index.html" )
            , ( "Licenses & attribution", "./get-started/licenses/index.html" )
            , ( "Frozen catalog v6", "./reference/catalog/v6/index.html" )
            ]
      }
    ]


primaryNavLinks : List ( String, String )
primaryNavLinks =
    [ ( "Try the desktop", "./test-drive/index.html" )
    , ( "Components", "./components/index.html" )
    , ( "Foundations", "./foundations/index.html" )
    , ( "Styles", "./styles/index.html" )
    , ( "Architecture", "./architecture/index.html" )
    , ( "Get started", "./get-started/index.html" )
    , ( "Search", "./search/index.html" )
    ]



-- PURE HELPERS & KEYBOARD DECODERS


orderedSurfaceIds : List SurfaceId
orderedSurfaceIds =
    List.map .surfaceId allSurfaces


stepSurface : Int -> SurfaceId -> SurfaceId
stepSurface delta currentId =
    let
        total =
            List.length orderedSurfaceIds

        currentIdx =
            findSurfaceIndex 0 currentId orderedSurfaceIds

        nextIdx =
            modBy ( Basics.max 1 total ) (currentIdx + delta)
    in
    surfaceAt nextIdx orderedSurfaceIds


findSurfaceIndex : Int -> SurfaceId -> List SurfaceId -> Int
findSurfaceIndex idx target remaining =
    case remaining of
        [] ->
            0

        first :: rest ->
            if first == target then
                idx

            else
                findSurfaceIndex (idx + 1) target rest


surfaceAt : Int -> List SurfaceId -> SurfaceId
surfaceAt idx remaining =
    case remaining of
        [] ->
            SurfaceTaskbar

        first :: rest ->
            if idx <= 0 then
                first

            else
                surfaceAt (idx - 1) rest


findSurfaceSpec : SurfaceId -> SurfaceSpec
findSurfaceSpec target =
    let
        pick items =
            case items of
                [] ->
                    taskbarSurface

                first :: rest ->
                    if first.surfaceId == target then
                        first

                    else
                        pick rest
    in
    pick allSurfaces


matchesCategory : SurfaceCategory -> SurfaceSpec -> Bool
matchesCategory chosenCategory spec =
    case chosenCategory of
        CategoryAll ->
            True

        _ ->
            spec.category == chosenCategory


countInCategory : SurfaceCategory -> Int
countInCategory chosenCategory =
    List.length (List.filter (matchesCategory chosenCategory) allSurfaces)


themeSlug : AppearanceTheme -> String
themeSlug chosenTheme =
    case chosenTheme of
        ThemeNight ->
            "night"

        ThemeDawn ->
            "dawn"

        ThemeHighContrast ->
            "high-contrast"


motionSlug : MotionMode -> String
motionSlug chosenMotion =
    case chosenMotion of
        MotionStandard ->
            "standard"

        MotionReduced ->
            "reduced"


boolToken : Bool -> String
boolToken flag =
    if flag then
        "true"

    else
        "false"


decodeEscapeKey : Msg -> Decode.Decoder Msg
decodeEscapeKey escapeMsg =
    Decode.field "key" Decode.string
        |> Decode.andThen
            (\keyName ->
                if keyName == "Escape" || keyName == "Esc" then
                    Decode.succeed escapeMsg

                else
                    Decode.fail "not escape"
            )


surfaceTabDomId : SurfaceId -> String
surfaceTabDomId target =
    "wl-tab-" ++ (findSurfaceSpec target).anchorId


decodeWorkbenchTabKey : Decode.Decoder ( Msg, Bool )
decodeWorkbenchTabKey =
    Decode.field "key" Decode.string
        |> Decode.andThen
            (\keyName ->
                case keyName of
                    "ArrowRight" ->
                        Decode.succeed ( KeyboardStepSpotlight 1, True )

                    "ArrowDown" ->
                        Decode.succeed ( KeyboardStepSpotlight 1, True )

                    "ArrowLeft" ->
                        Decode.succeed ( KeyboardStepSpotlight -1, True )

                    "ArrowUp" ->
                        Decode.succeed ( KeyboardStepSpotlight -1, True )

                    "Home" ->
                        Decode.succeed ( KeyboardJumpSpotlight SurfaceTaskbar, True )

                    "End" ->
                        Decode.succeed ( KeyboardJumpSpotlight SurfaceFiles, True )

                    _ ->
                        Decode.fail "unhandled tab key"
            )



-- DOCUMENT & VIEW


viewDocument : Model -> Browser.Document Msg
viewDocument currentModel =
    { title = "Warlock · Windows-style Elm + Haskell desktop for Omarchy & Hyprland"
    , body = [ view currentModel ]
    }


view : Model -> Html Msg
view currentModel =
    Html.div
        [ Attr.class "wl-home-root"
        , Attr.attribute "data-theme" (themeSlug currentModel.theme)
        , Attr.attribute "data-motion" (motionSlug currentModel.motion)
        , Attr.attribute "data-nav-open" (boolToken currentModel.mobileNavOpen)
        ]
        (sharedHeadLinks
            ++ [ Html.node "style" [] [ Html.text supplementalCss ]
               , Html.a [ Attr.class "wl-doc-skip", Attr.href "#main" ] [ Html.text "Skip to content" ]
               , viewHeader currentModel
               , Html.main_
                    [ Attr.id "main"
                    , Attr.tabindex -1
                    , Attr.class "wl-landing"
                    ]
                    [ viewHero
                    , viewScopeSection
                    , viewWorkbenchSection currentModel
                    , viewFeaturesSection currentModel
                    , viewPrinciplesSection currentModel
                    , viewArchitectureSection
                    , viewGuideSection
                    ]
               , viewFooter
               ]
        )


sharedHeadLinks : List (Html msg)
sharedHeadLinks =
    let
        stylesheet path =
            Html.node "link"
                [ Attr.attribute "rel" "stylesheet"
                , Attr.href path
                ]
                []
    in
    [ Html.node "link"
        [ Attr.attribute "rel" "icon"
        , Attr.href "./assets/brand/identity/warlock-mark-mono.svg"
        ]
        []
    , stylesheet "./assets/shared/layers.css"
    , stylesheet "./assets/shared/tokens.css"
    , stylesheet "./assets/shared/fonts.css"
    , stylesheet "./assets/shared/site.css"
    , stylesheet "./assets/shared/glyphs.css"
    , stylesheet "./assets/shared/landing.css"
    , stylesheet "./assets/shared/effects.css"
    ]



-- HEADER & RESPONSIVE NAVIGATION


viewHeader : Model -> Html Msg
viewHeader currentModel =
    Html.header
        [ Attr.class "wl-doc-header wl-home-header"
        , Events.on "keydown" (decodeEscapeKey CloseMobileNav)
        ]
        [ Html.div [ Attr.class "wl-home-bar" ]
            [ Html.a
                [ Attr.class "wl-doc-brand"
                , Attr.href "./index.html"
                , Attr.attribute "aria-current" "page"
                , Attr.attribute "aria-label" "Warlock home"
                ]
                [ Html.img
                    [ Attr.src "./assets/brand/identity/warlock-mark.svg"
                    , Attr.alt ""
                    , Attr.width 32
                    , Attr.height 32
                    ]
                    []
                , Html.span [] [ Html.text "WARLOCK" ]
                ]
            , Html.div [ Attr.class "wl-home-mobile-actions" ]
                [ Html.a
                    [ Attr.class "wl-doc-button wl-doc-button-primary wl-home-mobile-cta"
                    , Attr.href "./test-drive/index.html"
                    ]
                    [ Html.text "Test drive" ]
                , Html.button
                    [ Attr.type_ "button"
                    , Attr.class "wl-doc-button wl-home-nav-toggle"
                    , Attr.attribute "aria-expanded" (boolToken currentModel.mobileNavOpen)
                    , Attr.attribute "aria-controls" "wl-home-nav-drawer"
                    , Events.onClick ToggleMobileNav
                    ]
                    [ Html.text
                        (if currentModel.mobileNavOpen then
                            "Close menu"

                         else
                            "Menu"
                        )
                    ]
                ]
            ]
        , Html.div
            [ Attr.id "wl-home-nav-drawer"
            , Attr.class "wl-home-drawer"
            ]
            [ Html.nav
                [ Attr.class "wl-home-nav"
                , Attr.attribute "aria-label" "Primary"
                ]
                (List.map
                    (\( linkLabel, linkHref ) ->
                        Html.a
                            [ Attr.href linkHref
                            , Events.onClick CloseMobileNav
                            ]
                            [ Html.text linkLabel ]
                    )
                    primaryNavLinks
                )
            , Html.div
                [ Attr.class "wl-home-appearance"
                , Attr.attribute "role" "group"
                , Attr.attribute "aria-label" "Page preview appearance"
                ]
                [ viewToggleChip (currentModel.theme == ThemeNight) (SelectTheme ThemeNight) "Night"
                , viewToggleChip (currentModel.theme == ThemeDawn) (SelectTheme ThemeDawn) "Dawn"
                , viewToggleChip (currentModel.theme == ThemeHighContrast) (SelectTheme ThemeHighContrast) "High contrast"
                , viewToggleChip (currentModel.motion == MotionReduced) ToggleMotion "Reduced motion"
                ]
            ]
        ]


viewToggleChip : Bool -> Msg -> String -> Html Msg
viewToggleChip isPressed clickMsg chipLabel =
    Html.button
        [ Attr.type_ "button"
        , Attr.class
            (if isPressed then
                "wl-doc-button wl-home-chip is-pressed"

             else
                "wl-doc-button wl-home-chip"
            )
        , Attr.attribute "aria-pressed" (boolToken isPressed)
        , Events.onClick clickMsg
        ]
        [ Html.text chipLabel ]



-- HERO


viewHero : Html Msg
viewHero =
    Html.section
        [ Attr.class "wl-hero"
        , Attr.attribute "aria-labelledby" "hero-title"
        ]
        [ Html.div [ Attr.class "wl-hero-copy" ]
            [ Html.p [ Attr.class "wl-hero-eyebrow" ]
                [ Html.img
                    [ Attr.src "./assets/brand/identity/warlock-mark.svg"
                    , Attr.width 28
                    , Attr.height 22
                    , Attr.alt ""
                    ]
                    []
                , Html.text "Warlock for Omarchy · Beta MVP in active integration"
                ]
            , Html.h1 [ Attr.id "hero-title" ]
                [ Html.text "A Windows-style desktop for Hyprland" ]
            , Html.p [ Attr.class "wl-hero-lead" ]
                [ Html.text "Warlock gives Omarchy a taskbar, a Start-style launcher, Alt-Tab, Task View, snap layouts, notifications, Files quick access, and Settings. Hyprland keeps its tiling, input, and speed; one Elm interface and Haskell runtime keep every desktop surface honest." ]
            , Html.div [ Attr.class "wl-hero-actions" ]
                [ Html.a
                    [ Attr.class "wl-doc-button wl-doc-button-primary"
                    , Attr.href "./test-drive/index.html"
                    ]
                    [ Html.text "Open browser test drive (simulated)" ]
                , Html.a
                    [ Attr.class "wl-doc-button"
                    , Attr.href "#workbench"
                    ]
                    [ Html.text "Inspect surfaces" ]
                , Html.a
                    [ Attr.class "wl-doc-button"
                    , Attr.href "#scope"
                    ]
                    [ Html.text "Current beta & native status" ]
                ]
            , Html.p [ Attr.class "wl-hero-note" ]
                [ Html.text "Honest scope: the browser test drive runs Warlock's compiled Elm surfaces over a simulated desktop with fixture client interiors. Full Omarchy/Hyprland release parity across the preserved 242 requirements / 417 scenarios remains incomplete (15 whole original requirements hold source-bound historical acceptance), and private-origin security gates (ELM-ARC-024 / ELM-DEL-014) remain OPEN." ]
            ]
        , Html.figure [ Attr.class "wl-hero-shot" ]
            [ Html.img
                [ Attr.src "./assets/site/hero-desktop.png"
                , Attr.width 1600
                , Attr.height 903
                , Attr.alt "The Warlock desktop: a frosted taskbar across the top and Task View open with three workspace columns, over a black and red lacquer wallpaper"
                ]
                []
            ]
        ]



-- HONEST SCOPE & DELIVERY STATUS


viewScopeSection : Html msg
viewScopeSection =
    Html.section
        [ Attr.id "scope"
        , Attr.class "wl-band"
        , Attr.attribute "aria-labelledby" "scope-title"
        ]
        [ Html.div [ Attr.class "wl-section-head" ]
            [ Html.p [ Attr.class "wl-doc-eyebrow" ] [ Html.text "Honest delivery boundaries" ]
            , Html.h2 [ Attr.id "scope-title" ] [ Html.text "What runs in the browser vs on the native desktop" ]
            , Html.p []
                [ Html.text "Warlock keeps simulated browser demonstrations, CPU contract checks, Quint formal models, and native compositor acceptance strictly separate. Header appearance buttons above preview Lacquer tokens on this page only." ]
            ]
        , Html.div [ Attr.class "wl-doc-grid wl-home-scope-grid" ]
            (List.map viewScopeCard scopeCards)
        ]


viewScopeCard : CardSpec -> Html msg
viewScopeCard item =
    Html.article [ Attr.class "wl-doc-card wl-home-card-stack" ]
        [ Html.p [ Attr.class "wl-doc-eyebrow" ] [ Html.text item.eyebrow ]
        , Html.h3 [] [ Html.text item.title ]
        , Html.p [] [ Html.text item.body ]
        , Html.p [ Attr.class "wl-home-detail" ] [ Html.code [] [ Html.text item.detail ] ]
        ]



-- INTERACTIVE 8-SURFACE WORKBENCH (ARIA TABLIST + ARROW KEYS)


viewWorkbenchSection : Model -> Html Msg
viewWorkbenchSection currentModel =
    let
        activeSpec =
            findSurfaceSpec currentModel.spotlight
    in
    Html.section
        [ Attr.id "workbench"
        , Attr.class "wl-band"
        , Attr.attribute "aria-labelledby" "workbench-title"
        ]
        [ Html.div [ Attr.class "wl-section-head" ]
            [ Html.p [ Attr.class "wl-doc-eyebrow" ] [ Html.text "Interactive surface workbench" ]
            , Html.h2 [ Attr.id "workbench-title" ] [ Html.text "Inspect Elm policy authority vs observed host facts" ]
            , Html.p []
                [ Html.text "Select any desktop surface below (or press Left and Right arrow keys on the tab strip) to inspect what Elm decides locally, what the Haskell/Hyprland host reports back, and jump to its simulated scenario or specification." ]
            ]
        , Html.div [ Attr.class "wl-doc-card wl-home-workbench" ]
            [ Html.div [ Attr.class "wl-home-workbench-bar" ]
                [ Html.div
                    [ Attr.class "wl-home-tabs"
                    , Attr.attribute "role" "tablist"
                    , Attr.attribute "aria-label" "Desktop surfaces"
                    ]
                    (List.map (viewWorkbenchTab currentModel.spotlight) allSurfaces)
                , Html.div [ Attr.class "wl-home-step-group" ]
                    [ Html.button
                        [ Attr.type_ "button"
                        , Attr.class "wl-doc-button wl-home-chip"
                        , Events.onClick (StepSpotlight -1)
                        ]
                        [ Html.text "Previous" ]
                    , Html.button
                        [ Attr.type_ "button"
                        , Attr.class "wl-doc-button wl-home-chip"
                        , Events.onClick (StepSpotlight 1)
                        ]
                        [ Html.text "Next" ]
                    ]
                ]
            , Html.div
                [ Attr.id "wl-workbench-panel"
                , Attr.class "wl-home-split"
                , Attr.attribute "role" "tabpanel"
                , Attr.attribute "aria-labelledby" (surfaceTabDomId activeSpec.surfaceId)
                , Attr.tabindex 0
                ]
                [ Html.figure [ Attr.class "wl-feature-shot" ]
                    [ Html.img
                        [ Attr.src activeSpec.imageSrc
                        , Attr.width activeSpec.imageWidth
                        , Attr.height activeSpec.imageHeight
                        , Attr.alt activeSpec.imageAlt
                        ]
                        []
                    ]
                , Html.div [ Attr.class "wl-home-card-stack" ]
                    [ Html.div [ Attr.class "wl-home-badges" ]
                        [ Html.span [ Attr.class "wl-doc-eyebrow" ] [ Html.text activeSpec.label ]
                        , Html.kbd [ Attr.class "wl-home-kbd" ] [ Html.text activeSpec.chord ]
                        ]
                    , Html.h3 [] [ Html.text activeSpec.heading ]
                    , Html.p [] [ Html.text activeSpec.summary ]
                    , Html.dl [ Attr.class "wl-home-dl" ]
                        [ Html.div []
                            [ Html.dt [] [ Html.text "Elm GUI policy authority" ]
                            , Html.dd [] [ Html.text activeSpec.elmAuthority ]
                            ]
                        , Html.div []
                            [ Html.dt [] [ Html.text "Haskell / compositor observations" ]
                            , Html.dd [] [ Html.text activeSpec.hostObservation ]
                            ]
                        ]
                    , Html.div [ Attr.class "wl-home-actions-row" ]
                        [ Html.a
                            [ Attr.class "wl-doc-button wl-doc-button-primary"
                            , Attr.href activeSpec.scenarioHref
                            ]
                            [ Html.text (activeSpec.scenarioCta ++ " (simulated)") ]
                        , Html.a
                            [ Attr.class "wl-doc-button"
                            , Attr.href activeSpec.specHref
                            ]
                            [ Html.text ("Read " ++ activeSpec.label ++ " spec") ]
                        ]
                    ]
                ]
            ]
        ]


viewWorkbenchTab : SurfaceId -> SurfaceSpec -> Html Msg
viewWorkbenchTab activeId spec =
    let
        isSelected =
            activeId == spec.surfaceId
    in
    Html.button
        [ Attr.type_ "button"
        , Attr.id (surfaceTabDomId spec.surfaceId)
        , Attr.class
            (if isSelected then
                "wl-doc-button wl-home-chip is-pressed"

             else
                "wl-doc-button wl-home-chip"
            )
        , Attr.attribute "role" "tab"
        , Attr.attribute "aria-selected" (boolToken isSelected)
        , Attr.attribute "aria-controls" "wl-workbench-panel"
        , Attr.tabindex
            (if isSelected then
                0

             else
                -1
            )
        , Events.onClick (SelectSpotlight spec.surfaceId)
        , Events.preventDefaultOn "keydown" decodeWorkbenchTabKey
        ]
        [ Html.text spec.label ]



-- EDITORIAL FEATURES SECTION WITH AREA FILTER


viewFeaturesSection : Model -> Html Msg
viewFeaturesSection currentModel =
    let
        visibleSurfaces =
            List.filter (matchesCategory currentModel.category) allSurfaces

        shownCount =
            List.length visibleSurfaces

        totalCount =
            List.length allSurfaces
    in
    Html.section
        [ Attr.id "features"
        , Attr.class "wl-features"
        , Attr.attribute "aria-labelledby" "features-title"
        ]
        ([ Html.div [ Attr.class "wl-section-head" ]
            [ Html.p [ Attr.class "wl-doc-eyebrow" ] [ Html.text "What it does" ]
            , Html.h2 [ Attr.id "features-title" ] [ Html.text "The desktop you know, on the compositor you love" ]
            , Html.p []
                [ Html.text "Filter by workflow area or browse all eight desktop surfaces." ]
            ]
         , Html.div [ Attr.class "wl-home-filter-bar" ]
            [ Html.div
                [ Attr.class "wl-home-tabs"
                , Attr.attribute "role" "group"
                , Attr.attribute "aria-label" "Filter desktop surfaces by area"
                ]
                [ viewCategoryButton currentModel.category CategoryAll "All surfaces"
                , viewCategoryButton currentModel.category CategoryWindows "Windows & workspaces"
                , viewCategoryButton currentModel.category CategoryAppsFiles "Apps & files"
                , viewCategoryButton currentModel.category CategorySystem "System & tray"
                ]
            , Html.p
                [ Attr.class "wl-home-detail"
                , Attr.attribute "aria-live" "polite"
                ]
                [ Html.text
                    ("Showing "
                        ++ String.fromInt shownCount
                        ++ " of "
                        ++ String.fromInt totalCount
                        ++ " desktop surfaces."
                    )
                ]
            ]
         ]
            ++ List.map viewFeatureArticle visibleSurfaces
        )


viewCategoryButton : SurfaceCategory -> SurfaceCategory -> String -> Html Msg
viewCategoryButton activeCategory targetCategory labelText =
    let
        countLabel =
            labelText ++ " (" ++ String.fromInt (countInCategory targetCategory) ++ ")"
    in
    viewToggleChip (activeCategory == targetCategory) (SelectCategory targetCategory) countLabel


viewFeatureArticle : SurfaceSpec -> Html msg
viewFeatureArticle spec =
    Html.article
        [ Attr.class "wl-feature"
        , Attr.id spec.anchorId
        ]
        [ Html.figure [ Attr.class "wl-feature-shot" ]
            [ Html.img
                [ Attr.src spec.imageSrc
                , Attr.width spec.imageWidth
                , Attr.height spec.imageHeight
                , Attr.attribute "loading" "lazy"
                , Attr.alt spec.imageAlt
                ]
                []
            ]
        , Html.div [ Attr.class "wl-feature-copy" ]
            [ Html.p [ Attr.class "wl-doc-eyebrow" ] [ Html.text spec.label ]
            , Html.h3 [] [ Html.text spec.heading ]
            , Html.p [] [ Html.text spec.summary ]
            , Html.div [ Attr.class "wl-home-actions-row" ]
                [ Html.a
                    [ Attr.class "wl-feature-link"
                    , Attr.href spec.scenarioHref
                    ]
                    [ Html.text (spec.scenarioCta ++ " (simulated)") ]
                , Html.a
                    [ Attr.class "wl-feature-link"
                    , Attr.href spec.specHref
                    ]
                    [ Html.text (spec.label ++ " specification") ]
                ]
            ]
        ]



-- PRINCIPLES + INTERACTIVE ATTENTION & CAUSALITY SPECIMEN


viewPrinciplesSection : Model -> Html Msg
viewPrinciplesSection currentModel =
    Html.section
        [ Attr.id "principles"
        , Attr.class "wl-band"
        , Attr.attribute "aria-labelledby" "principles-title"
        ]
        [ Html.div [ Attr.class "wl-section-head" ]
            [ Html.p [ Attr.class "wl-doc-eyebrow" ] [ Html.text "Built on Elm" ]
            , Html.h2 [ Attr.id "principles-title" ] [ Html.text "Honest about every window" ]
            , Html.p []
                [ Html.text "Warlock asks Hyprland to act and shows what Hyprland reports. One Elm policy authority drives every surface, so the taskbar, the launcher, and the switcher never contradict one another." ]
            ]
        , Html.div [ Attr.class "wl-doc-grid" ]
            (List.map
                (\( titleText, bodyText ) ->
                    Html.div [ Attr.class "wl-doc-card wl-home-card-stack" ]
                        [ Html.h3 [] [ Html.text titleText ]
                        , Html.p [] [ Html.text bodyText ]
                        ]
                )
                principleCards
            )
        , Html.div [ Attr.class "wl-home-split wl-home-specimen-grid" ]
            [ viewCueLabCard currentModel.cues
            , viewOutcomeLabCard currentModel.outcomeSample
            ]
        ]


viewCueLabCard : CueFacts -> Html Msg
viewCueLabCard cueState =
    Html.div [ Attr.class "wl-doc-card wl-home-card-stack" ]
        [ Html.p [ Attr.class "wl-doc-eyebrow" ] [ Html.text "Interactive cue check · Separate attention" ]
        , Html.h3 [] [ Html.text "Window focus, active app, and switcher candidate stay distinct" ]
        , Html.p []
            [ Html.text "Toggle each independent fact below to verify how Lacquer separates compositor window focus (bright border), active taskbar group (lacquer pill), and uncommitted Alt-Tab candidate selection (corner brackets)." ]
        , Html.div
            [ Attr.class "wl-home-tabs"
            , Attr.attribute "role" "group"
            , Attr.attribute "aria-label" "Toggle attention cues"
            ]
            [ viewToggleChip cueState.windowFocused ToggleWindowFocused "Window focused"
            , viewToggleChip cueState.activeApplication ToggleActiveApplication "Active app on bar"
            , viewToggleChip cueState.switcherCandidate ToggleSwitcherCandidate "Alt-Tab candidate"
            ]
        , Html.div
            [ Attr.class
                ("wl-home-window"
                    ++ (if cueState.windowFocused then
                            " is-focused"

                        else
                            ""
                       )
                    ++ (if cueState.switcherCandidate then
                            " is-candidate"

                        else
                            ""
                       )
                )
            , Attr.attribute "aria-live" "polite"
            ]
            [ Html.div [ Attr.class "wl-home-badges" ]
                [ Html.span
                    [ Attr.class
                        (if cueState.activeApplication then
                            "wl-home-pill is-active"

                         else
                            "wl-home-pill"
                        )
                    ]
                    [ Html.text
                        (if cueState.activeApplication then
                            "Taskbar: active lacquer pill"

                         else
                            "Taskbar: neutral running pill"
                        )
                    ]
                , Html.code []
                    [ Html.text
                        ("Focus: "
                            ++ (if cueState.windowFocused then
                                    "focused edge"

                                else
                                    "unfocused edge"
                               )
                            ++ " · Candidate: "
                            ++ (if cueState.switcherCandidate then
                                    "selected (uncommitted)"

                                else
                                    "none"
                               )
                        )
                    ]
                ]
            ]
        ]


viewOutcomeLabCard : OutcomeSample -> Html Msg
viewOutcomeLabCard currentSample =
    let
        ( statusTitle, statusExplanation, statusHref ) =
            case currentSample of
                SampleObserved ->
                    ( "Observed result: Hyprland reported window mapped on Workspace 2"
                    , "Only after an observed compositor snapshot arrives does Elm advance active window and workspace indicators."
                    , "./test-drive/index.html?scenario=taskbar"
                    )

                SamplePending ->
                    ( "Submitted receipt: launch accepted, awaiting observed window"
                    , "Elm shows non-blocking pending feedback without fabricating a focused window or reordering taskbar groups early."
                    , "./test-drive/index.html?scenario=launcher"
                    )

                SampleUnknown ->
                    ( "Unknown outcome: bridge timed out without confirming failure"
                    , "Ambiguous outcomes are never silently retried when side effects could duplicate launches or move the wrong window."
                    , "./test-drive/index.html?scenario=status-recovery"
                    )

                SampleRefused ->
                    ( "Refused receipt: validation or compositor check rejected request"
                    , "Explicit refusal preserves user draft input in place and explains why the action did not run."
                    , "./components/status-recovery/index.html"
                    )
    in
    Html.div [ Attr.class "wl-doc-card wl-home-card-stack" ]
        [ Html.p [ Attr.class "wl-doc-eyebrow" ] [ Html.text "Interactive causality check · Show what is known" ]
        , Html.h3 [] [ Html.text "Intent, receipt, and observed outcome never collapse into one boolean" ]
        , Html.div
            [ Attr.class "wl-home-tabs"
            , Attr.attribute "role" "group"
            , Attr.attribute "aria-label" "Select host receipt state"
            ]
            [ viewToggleChip (currentSample == SampleObserved) (SelectOutcomeSample SampleObserved) "Observed"
            , viewToggleChip (currentSample == SamplePending) (SelectOutcomeSample SamplePending) "Submitted"
            , viewToggleChip (currentSample == SampleUnknown) (SelectOutcomeSample SampleUnknown) "Unknown"
            , viewToggleChip (currentSample == SampleRefused) (SelectOutcomeSample SampleRefused) "Refused"
            ]
        , Html.div
            [ Attr.class "wl-home-window is-focused"
            , Attr.attribute "aria-live" "polite"
            ]
            [ Html.p [] [ Html.strong [] [ Html.text statusTitle ] ]
            , Html.p [ Attr.class "wl-home-detail" ] [ Html.text statusExplanation ]
            , Html.a [ Attr.class "wl-feature-link", Attr.href statusHref ]
                [ Html.text "Inspect status & recovery behavior" ]
            ]
        ]



-- PRODUCTION ARCHITECTURE SECTION


viewArchitectureSection : Html msg
viewArchitectureSection =
    Html.section
        [ Attr.id "architecture"
        , Attr.class "wl-band"
        , Attr.attribute "aria-labelledby" "architecture-title"
        ]
        [ Html.div [ Attr.class "wl-section-head" ]
            [ Html.p [ Attr.class "wl-doc-eyebrow" ] [ Html.text "Elm + Haskell architecture" ]
            , Html.h2 [ Attr.id "architecture-title" ] [ Html.text "One policy authority per decision" ]
            , Html.p []
                [ Html.text "Warlock-authored production code uses Elm and Haskell only. Elm owns every GUI element and interaction transition; Haskell owns system integration, Hyprland IPC, atomic storage, and reviewed native WebKit custody." ]
            ]
        , Html.div [ Attr.class "wl-home-split" ]
            [ Html.figure [ Attr.class "wl-feature-shot" ]
                [ Html.img
                    [ Attr.src "./assets/brand/readme/elm-architecture.png"
                    , Attr.width 1200
                    , Attr.height 800
                    , Attr.attribute "loading" "lazy"
                    , Attr.alt "Diagram of Warlock's Elm policy engine connected through typed message contracts to Haskell runtime services and Hyprland observations"
                    ]
                    []
                ]
            , Html.div [ Attr.class "wl-doc-card wl-home-card-stack" ]
                [ Html.p [ Attr.class "wl-doc-eyebrow" ] [ Html.text "Verified 35-node / 68-edge model" ]
                , Html.h3 [] [ Html.text "Strict boundary between UI intent and compositor truth" ]
                , Html.p []
                    [ Html.text "Quint specifications model workspace navigation, file operations, settings CAS revisions, and effect lifecycles. Fuzz and property checks test opaque boundary contracts while ELM-ARC-024 and ELM-DEL-014 govern private UI origin and WebKit engine isolation." ]
                , Html.div [ Attr.class "wl-home-actions-row" ]
                    [ Html.a [ Attr.class "wl-doc-button wl-doc-button-primary", Attr.href "./architecture/index.html" ]
                        [ Html.text "Explore interactive architecture" ]
                    , Html.a [ Attr.class "wl-doc-button", Attr.href "./get-started/index.html" ]
                        [ Html.text "Read Elm + Haskell guide" ]
                    ]
                ]
            ]
        ]



-- DESIGN LANGUAGE & FULL SITE DIRECTORY


viewGuideSection : Html msg
viewGuideSection =
    Html.section
        [ Attr.id "guide"
        , Attr.class "wl-band"
        , Attr.attribute "aria-labelledby" "guide-title"
        ]
        [ Html.div [ Attr.class "wl-section-head" ]
            [ Html.p [ Attr.class "wl-doc-eyebrow" ] [ Html.text "The design language" ]
            , Html.h2 [ Attr.id "guide-title" ] [ Html.text "Lacquer, in detail" ]
            , Html.p []
                [ Html.text "Explore foundations, token-driven styles, all 19 component specifications, and the preserved v6 reference catalog." ]
            ]
        , Html.div [ Attr.class "wl-doc-grid" ]
            (List.map
                (\card ->
                    Html.a [ Attr.class "wl-doc-card wl-home-card-stack", Attr.href card.href ]
                        [ Html.h3 [] [ Html.text card.title ]
                        , Html.p [] [ Html.text card.body ]
                        ]
                )
                guideCards
            )
        , Html.div [ Attr.class "wl-home-directory" ]
            (List.map viewDirectoryGroup directoryGroups)
        ]


viewDirectoryGroup : DirectoryGroup -> Html msg
viewDirectoryGroup grp =
    Html.nav
        [ Attr.class "wl-home-card-stack"
        , Attr.attribute "aria-label" grp.heading
        ]
        [ Html.h3 [] [ Html.text grp.heading ]
        , Html.ul [ Attr.class "wl-home-links" ]
            (List.map
                (\( linkText, linkHref ) ->
                    Html.li [] [ Html.a [ Attr.href linkHref ] [ Html.text linkText ] ]
                )
                grp.links
            )
        ]



-- FOOTER


viewFooter : Html msg
viewFooter =
    Html.footer [ Attr.class "wl-doc-footer wl-home-footer" ]
        [ Html.p [] [ Html.text "Warlock · Windows-style Elm + Haskell desktop for Omarchy and Hyprland." ]
        , Html.a [ Attr.href "./test-drive/index.html" ] [ Html.text "Browser test drive (simulated)" ]
        , Html.a [ Attr.href "./reference/catalog/v6/index.html" ] [ Html.text "Frozen catalog v6" ]
        , Html.a [ Attr.href "./get-started/contributing/index.html" ] [ Html.text "Contribute" ]
        , Html.a [ Attr.href "./get-started/licenses/index.html" ] [ Html.text "Licenses and attribution" ]
        , Html.p [] [ Html.text "Apache License 2.0" ]
        ]



-- MINIMAL SUPPLEMENTAL LAYOUT CSS (CONSUMES SHARED TOKENS.CSS + SITE.CSS + LANDING.CSS)


supplementalCss : String
supplementalCss =
    """
@layer base {
  .wl-home-root {
    min-height: 100vh;
    overflow-x: clip;
    color: var(--wl-sys-color-text, #F6EFE8);
    background: var(--wl-sys-color-canvas, #100E0E);
    font-family: var(--wl-sys-font-body, Inter, sans-serif);
    line-height: 1.5;
  }
  .wl-home-root :where(*, *::before, *::after) { box-sizing: border-box; }
  .wl-home-root :where(h1, h2, h3, p, ul, dl) { margin: 0; }
  .wl-home-root img { max-width: 100%; height: auto; }
  .wl-home-root a { color: inherit; text-underline-offset: 0.18em; }
  .wl-home-root :where(button) { font: inherit; }
  .wl-home-root :focus-visible {
    outline: 2px solid var(--wl-sys-color-focus, #8EC8FF);
    outline-offset: 3px;
    box-shadow: 0 0 0 2px var(--wl-sys-color-focus-gap, #191516);
  }
}

@layer components {
  .wl-home-root[data-theme="dawn"] .wl-hero {
    background: linear-gradient(90deg, var(--wl-sys-color-canvas) 0%, color-mix(in srgb, var(--wl-sys-color-canvas) 70%, transparent) 42%, transparent 75%),
                url("./test-drive/stage/assets/wallpaper-dawn.svg") center/cover no-repeat, var(--wl-sys-color-canvas);
  }
  .wl-home-root[data-theme="high-contrast"] .wl-hero {
    background: var(--wl-sys-color-canvas, #000000);
  }
  .wl-home-header { gap: 12px 20px; justify-content: space-between; }
  .wl-home-bar { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
  .wl-home-mobile-actions { display: none; align-items: center; gap: 8px; margin-left: auto; }
  .wl-home-drawer { display: flex; align-items: center; flex-wrap: wrap; gap: 12px 18px; flex: 1 1 auto; justify-content: flex-end; min-width: 0; }
  .wl-home-nav { display: flex; align-items: center; flex-wrap: wrap; gap: 8px 16px; min-width: 0; }
  .wl-home-nav a { padding: 4px 2px; overflow-wrap: anywhere; }
  .wl-home-appearance, .wl-home-tabs, .wl-home-step-group, .wl-home-actions-row, .wl-home-badges {
    display: flex; flex-wrap: wrap; align-items: center; gap: 8px; min-width: 0;
  }
  .wl-home-chip { text-decoration: none; font-size: 0.875rem; min-height: 2.25rem; padding: 6px 12px; }
  .wl-home-chip.is-pressed {
    background: var(--wl-sys-color-surface-selected, #331C1E);
    border-color: var(--wl-sys-color-brand-text, #FCA399);
    box-shadow: inset 0 -3px 0 0 var(--wl-sys-color-brand-text, #FCA399);
    font-weight: 700;
  }
  .wl-home-scope-grid { grid-template-columns: repeat(auto-fit, minmax(min(100%, 250px), 1fr)); }
  .wl-home-card-stack { display: grid; align-content: start; gap: 10px; min-width: 0; overflow-wrap: anywhere; }
  .wl-home-detail { font-size: 0.875rem; color: var(--wl-sys-color-text-secondary, #BDB2AF); margin: 0; }
  .wl-home-workbench { display: grid; gap: 24px; }
  .wl-home-workbench-bar, .wl-home-filter-bar {
    display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px;
    padding-bottom: 16px; margin-bottom: 24px; border-bottom: 1px solid color-mix(in srgb, var(--wl-sys-color-text, #F6EFE8) 12%, transparent);
  }
  .wl-home-workbench .wl-home-workbench-bar { margin-bottom: 0; }
  .wl-home-split { display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); gap: clamp(20px, 3vw, 40px); align-items: start; min-width: 0; }
  .wl-home-specimen-grid { grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); margin-top: 24px; }
  .wl-home-kbd { padding: 2px 8px; border-radius: 6px; border: 1px solid var(--wl-sys-color-border-essential, #9E9290); font-size: 0.75rem; }
  .wl-home-dl { display: grid; gap: 10px; margin: 4px 0; padding: 12px; border-radius: 8px; background: var(--wl-sys-color-surface-recessed, #141112); border: 1px solid color-mix(in srgb, var(--wl-sys-color-text, #F6EFE8) 10%, transparent); }
  .wl-home-dl dt { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--wl-sys-color-brand-text, #FCA399); }
  .wl-home-dl dd { margin: 2px 0 0; font-size: 0.9rem; color: var(--wl-sys-color-text-secondary, #BDB2AF); }
  .wl-home-window {
    padding: 16px; border-radius: var(--wl-sys-radius-window, 8px);
    background: var(--wl-sys-color-surface-recessed, #141112);
    border: 2px solid var(--wl-sys-color-window-edge-unfocused, #707078);
    display: grid; gap: 8px;
  }
  .wl-home-window.is-focused { border-color: var(--wl-sys-color-window-edge-focused, #F6EFE8); }
  .wl-home-window.is-candidate { outline: 2px dashed var(--wl-sys-color-focus, #8EC8FF); outline-offset: 4px; }
  .wl-home-pill { padding: 4px 10px; border-radius: 999px; border: 1px solid var(--wl-sys-color-border-essential, #9E9290); font-size: 0.8125rem; font-weight: 600; }
  .wl-home-pill.is-active { background: var(--wl-sys-color-action-fill, #B02026); color: var(--wl-sys-color-on-action, #FFF8F5); border-color: var(--wl-sys-color-on-action, #FFF8F5); }
  .wl-home-directory {
    margin-top: 32px; padding-top: 28px; border-top: 1px solid color-mix(in srgb, var(--wl-sys-color-text, #F6EFE8) 12%, transparent);
    display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr)); gap: 24px;
  }
  .wl-home-links { list-style: none; padding: 0; margin: 0; display: grid; gap: 6px; font-size: 0.9rem; }
  .wl-home-footer { align-items: center; }

  @media (max-width: 900px) {
    .wl-home-bar { width: 100%; justify-content: space-between; }
    .wl-home-mobile-actions { display: inline-flex; }
    .wl-home-root[data-nav-open="false"] .wl-home-drawer { display: none; }
    .wl-home-root[data-nav-open="true"] .wl-home-drawer {
      display: grid; width: 100%; justify-content: stretch; gap: 14px;
      padding-top: 12px; border-top: 1px solid var(--wl-sys-color-border-essential, #9E9290);
    }
    .wl-home-split { grid-template-columns: minmax(0, 1fr); }
    .wl-home-root[data-theme="dawn"] .wl-hero {
      background: linear-gradient(180deg, color-mix(in srgb, var(--wl-sys-color-canvas) 30%, transparent), var(--wl-sys-color-canvas) 92%),
                  url("./test-drive/stage/assets/wallpaper-dawn.svg") center/cover no-repeat, var(--wl-sys-color-canvas);
    }
  }
}

@layer states {
  .wl-home-chip.is-pressed:hover { background: var(--wl-sys-color-surface-selected-hover, #3A252A); }
  .wl-home-chip.is-pressed:active { background: var(--wl-sys-color-surface-selected-pressed, #423035); }
}

@layer accessibility {
  .wl-home-root[data-motion="reduced"] *, .wl-home-root[data-motion="reduced"] *::before, .wl-home-root[data-motion="reduced"] *::after {
    transition-duration: 0ms !important;
    animation-duration: 0ms !important;
  }
  .wl-home-root[data-motion="reduced"] .wl-hero-shot img { transform: none; }
  @media (forced-colors: active) {
    .wl-home-chip.is-pressed { outline: 2px solid Highlight; outline-offset: -2px; text-decoration: underline; }
    .wl-home-window.is-focused { border-color: Highlight; }
  }
}
"""
