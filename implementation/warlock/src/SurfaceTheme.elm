module SurfaceTheme exposing
    ( ControlSpec
    , barActionsStyles
    , barRootStyles
    , barStatusInnerStyles
    , barStatusStyles
    , checkboxIndicator
    , controlDetailStyles
    , controlLabelStyles
    , controlStyles
    , notificationTextStyles
    , overviewWorkspaceStyles
    , popupControlsStyles
    , popupHeadingStyles
    , popupRootStyles
    , popupStatusStyles
    , searchFieldStyles
    , searchLabelStyles
    , settingsSaveCaptionStyles
    , settingsSaveGroupStyles
    , switcherActionsStyles
    , switcherListboxStyles
    )

import Html exposing (Html, span, text)
import Html.Attributes exposing (attribute, style)
import Settings


type alias Palette =
    { colorScheme : String
    , canvas : String
    , surfaceRecessed : String
    , surface : String
    , surfaceUtility : String
    , surfaceRaised : String
    , surfaceSelected : String
    , surfaceAttention : String
    , textPrimary : String
    , textSecondary : String
    , textDisabled : String
    , brandAccent : String
    , actionFill : String
    , onAction : String
    , borderSubtle : String
    , borderControl : String
    , borderEssential : String
    , borderDisabled : String
    , focusRing : String
    , activeContour : String
    , warningContour : String
    , dangerAccent : String
    , cardShadow : String
    , snapShadow : String
    , snapSelectedShadow : String
    , inputInsetShadow : String
    , highContrast : Bool
    }


type alias ControlSpec =
    { popup : Bool
    , surfaceMode : String
    , identity : String
    , kind : String
    , windowState : String
    , isEnabled : Bool
    , isFocusOnly : Bool
    , isCurrent : Bool
    , checked : Maybe Bool
    , isMenuCheckbox : Bool
    , appearance : Settings.Values
    , motion : String
    }


paletteFor : Settings.Theme -> Palette
paletteFor selectedTheme =
    case selectedTheme of
        Settings.Night ->
            { colorScheme = "dark"
            , canvas = "#100e0e"
            , surfaceRecessed = "#131011"
            , surface = "#191516"
            , surfaceUtility = "#1e191b"
            , surfaceRaised = "#262022"
            , surfaceSelected = "#351c1f"
            , surfaceAttention = "#2f2314"
            , textPrimary = "#f6efe8"
            , textSecondary = "#c6bab7"
            , textDisabled = "#9a8e8b"
            , brandAccent = "#fca399"
            , actionFill = "#b02026"
            , onAction = "#fff8f5"
            , borderSubtle = "#3b3335"
            , borderControl = "#786c6e"
            , borderEssential = "#a89b99"
            , borderDisabled = "#4d4446"
            , focusRing = "#8ec8ff"
            , activeContour = "#fca399"
            , warningContour = "#f2c172"
            , dangerAccent = "#ff9eb0"
            , cardShadow = "inset 0 1px 0 #ffffff10, 0 1px 2px #00000040"
            , snapShadow = "0 4px 12px #00000045, inset 0 1px 0 #ffffff12"
            , snapSelectedShadow = "inset 2px 0 0 #fca399, 0 0 0 1px #fca399, 0 6px 16px #00000055"
            , inputInsetShadow = "inset 0 1px 2px #00000055"
            , highContrast = False
            }

        Settings.Dawn ->
            { colorScheme = "light"
            , canvas = "#f6f1ea"
            , surfaceRecessed = "#eae3d9"
            , surface = "#fffdf9"
            , surfaceUtility = "#f5efe7"
            , surfaceRaised = "#ffffff"
            , surfaceSelected = "#fce8e4"
            , surfaceAttention = "#fdf1dc"
            , textPrimary = "#181314"
            , textSecondary = "#524846"
            , textDisabled = "#5f5451"
            , brandAccent = "#a11d22"
            , actionFill = "#a11d22"
            , onAction = "#fffdf9"
            , borderSubtle = "#d4cac0"
            , borderControl = "#6e625f"
            , borderEssential = "#544a48"
            , borderDisabled = "#8f837e"
            , focusRing = "#14539a"
            , activeContour = "#a11d22"
            , warningContour = "#8c4e00"
            , dangerAccent = "#9b1b3b"
            , cardShadow = "0 1px 2px #18131412"
            , snapShadow = "0 4px 12px #1813141a, inset 0 1px 0 #ffffffcc"
            , snapSelectedShadow = "inset 2px 0 0 #a11d22, 0 0 0 1px #a11d22, 0 6px 14px #a11d2224"
            , inputInsetShadow = "inset 0 1px 2px #18131414"
            , highContrast = False
            }

        Settings.HighContrast ->
            { colorScheme = "dark"
            , canvas = "#000000"
            , surfaceRecessed = "#000000"
            , surface = "#000000"
            , surfaceUtility = "#000000"
            , surfaceRaised = "#000000"
            , surfaceSelected = "#000000"
            , surfaceAttention = "#000000"
            , textPrimary = "#ffffff"
            , textSecondary = "#ffffff"
            , textDisabled = "#bfbfbf"
            , brandAccent = "#ffffff"
            , actionFill = "#ffffff"
            , onAction = "#000000"
            , borderSubtle = "#ffffff"
            , borderControl = "#ffffff"
            , borderEssential = "#ffffff"
            , borderDisabled = "#8c8c8c"
            , focusRing = "#ffff00"
            , activeContour = "#00ffff"
            , warningContour = "#ffcc00"
            , dangerAccent = "#ff9eb0"
            , cardShadow = "none"
            , snapShadow = "none"
            , snapSelectedShadow = "none"
            , inputInsetShadow = "none"
            , highContrast = True
            }


bodyFontStack : String
bodyFontStack =
    "Inter, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif"


headingFontStack : String
headingFontStack =
    "\"Space Grotesk\", Inter, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif"


monoFontStack : String
monoFontStack =
    "\"JetBrains Mono\", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"


scaledRootFontSize : Int -> String
scaledRootFontSize textScale =
    let
        pixelSize =
            case textScale of
                125 ->
                    "20px"

                150 ->
                    "24px"

                200 ->
                    "32px"

                _ ->
                    "16px"
    in
    "max(1rem, " ++ pixelSize ++ ")"


motionStyles : String -> List (Html.Attribute msg)
motionStyles motionProfile =
    if motionProfile == "reduced" then
        [ style "animation" "none"
        , style "transition" "none"
        , style "scroll-behavior" "auto"
        ]

    else
        [ style "animation" "none" ]


softEffectsEnabled : Settings.Values -> Palette -> Bool
softEffectsEnabled appearance palette =
    not appearance.effectsOff && not palette.highContrast


statusStripeColor : Palette -> String -> String
statusStripeColor palette statusText =
    let
        lowerStatus =
            String.toLower statusText
    in
    if String.startsWith "applications connected" lowerStatus || String.startsWith "search applications" lowerStatus then
        palette.brandAccent

    else if String.contains "refused" lowerStatus || String.contains "unavailable" lowerStatus then
        palette.dangerAccent

    else if
        String.contains "not confirmed" lowerStatus
            || String.contains "check your windows" lowerStatus
            || String.contains "confirm or cancel" lowerStatus
    then
        palette.warningContour

    else
        palette.focusRing


isPrimaryCommitIdentity : String -> String -> Bool
isPrimaryCommitIdentity surfaceMode controlIdentity =
    (surfaceMode == "settings"
        && List.member controlIdentity
            [ "settings:save"
            , "settings:motion:save"
            , "settings:shortcuts:save"
            ]
    )
        || (surfaceMode == "snap" && controlIdentity == "snap:apply")
        || (surfaceMode == "files" && controlIdentity == "files:open-path")


isDestructiveConfirmIdentity : String -> String -> Bool
isDestructiveConfirmIdentity surfaceMode controlIdentity =
    surfaceMode == "system" && controlIdentity == "system:confirm"


barRootStyles : Settings.Values -> String -> List (Html.Attribute msg)
barRootStyles appearance motionProfile =
    let
        palette =
            paletteFor appearance.theme

        backdropShadow =
            if softEffectsEnabled appearance palette then
                "inset 0 -1px 0 " ++ palette.borderSubtle ++ ", 0 1px 0 " ++ palette.borderControl ++ ", 0 100vh 0 100vh " ++ palette.canvas

            else
                "none"
    in
    -- Avoid layout-consuming top/bottom borders on .surface-bar so .surface-actions
    -- stays anchored at y=0 and 3px outer focus contours never clip in narrow viewports.
    [ style "box-sizing" "border-box"
    , style "display" "flex"
    , style "align-items" "center"
    , style "flex-wrap" "nowrap"
    , style "width" "100%"
    , style "height" "calc(3em + 8px)"
    , style "overflow" "hidden"
    , style "background-color" palette.surface
    , style "color" palette.textPrimary
    , style "color-scheme" palette.colorScheme
    , style "font-family" bodyFontStack
    , style "font-size" (scaledRootFontSize appearance.textScale)
    , style "line-height" "1.25"
    , style "opacity" "1"
    , style "backdrop-filter" "none"
    , style "box-shadow" backdropShadow
    , style "text-shadow" "none"
    ]
        ++ motionStyles motionProfile


barActionsStyles : List (Html.Attribute msg)
barActionsStyles =
    [ style "box-sizing" "border-box"
    , style "display" "flex"
    , style "align-items" "center"
    , style "flex" "1 1 auto"
    , style "min-width" "0"
    , style "height" "calc(3em + 8px)"
    , style "padding" "0 3px"
    , style "overflow-x" "auto"
    , style "overflow-y" "hidden"
    , style "flex-wrap" "nowrap"
    ]


barStatusStyles : Settings.Values -> Bool -> String -> List (Html.Attribute msg)
barStatusStyles appearance isIdle statusText =
    let
        palette =
            paletteFor appearance.theme

        stripeColor =
            statusStripeColor palette statusText

        statusAccent =
            if softEffectsEnabled appearance palette then
                "inset 3px 0 0 " ++ stripeColor

            else
                "none"
    in
    if isIdle then
        [ style "display" "none"
        , style "align-items" "flex-start"
        ]

    else
        -- Omit inline position, width, height, padding, border, and clip-path on
        -- the [role=status] element so legacy baseline.css regression checks can
        -- still observe 1x1 clipped geometry when shell.css is disabled; stretch
        -- the inner reachable scrollport so long 200% recovery notices never crop.
        [ style "display" "flex"
        , style "align-items" "stretch"
        , style "align-self" "stretch"
        , style "flex" "0 0 clamp(180px, 40vw, 360px)"
        , style "overflow" "hidden"
        , style "background-color" palette.surfaceRecessed
        , style "color" palette.textPrimary
        , style "box-shadow" statusAccent
        , style "font-size" "0.75em"
        , style "line-height" "1.2"
        , style "white-space" "normal"
        , style "overflow-wrap" "anywhere"
        ]


barStatusInnerStyles : Settings.Values -> String -> List (Html.Attribute msg)
barStatusInnerStyles appearance motionProfile =
    let
        palette =
            paletteFor appearance.theme
    in
    [ style "display" "block"
    , style "box-sizing" "border-box"
    , style "width" "100%"
    , style "height" "100%"
    , style "min-height" "0"
    , style "max-height" "100%"
    , style "padding" "3px 6px 3px 9px"
    , style "overflow-y" "auto"
    , style "overflow-x" "hidden"
    , style "overscroll-behavior" "contain"
    , style "scrollbar-width" "thin"
    , style "white-space" "normal"
    , style "overflow-wrap" "anywhere"
    , style "outline-width" "2px"
    , style "outline-color" palette.focusRing
    , style "outline-offset" "-2px"
    ]
        ++ motionStyles motionProfile


popupRootStyles : Settings.Values -> String -> List (Html.Attribute msg)
popupRootStyles appearance motionProfile =
    let
        palette =
            paletteFor appearance.theme
    in
    [ style "box-sizing" "border-box"
    , style "width" "100%"
    , style "height" "100vh"
    , style "min-height" "100vh"
    , style "margin" "0"
    , style "padding" "8px 10px"
    , style "overflow-y" "auto"
    , style "overflow-x" "hidden"
    , style "background-color" palette.canvas
    , style "color" palette.textPrimary
    , style "color-scheme" palette.colorScheme
    , style "font-family" bodyFontStack
    , style "font-size" (scaledRootFontSize appearance.textScale)
    , style "line-height" "1.4"
    , style "opacity" "1"
    , style "backdrop-filter" "none"
    , style "box-shadow" "none"
    , style "text-shadow" "none"
    ]
        ++ motionStyles motionProfile


popupHeadingStyles : Settings.Values -> List (Html.Attribute msg)
popupHeadingStyles appearance =
    let
        palette =
            paletteFor appearance.theme

        ruleWidth =
            if palette.highContrast then
                "2px"

            else
                "1px"
    in
    [ style "box-sizing" "border-box"
    , style "margin" "0 0 6px 0"
    , style "padding" "1px 0 6px 10px"
    , style "border-left" ("3px solid " ++ palette.brandAccent)
    , style "border-bottom" (ruleWidth ++ " solid " ++ palette.borderSubtle)
    , style "font-family" headingFontStack
    , style "font-size" "1.2em"
    , style "font-weight" "700"
    , style "line-height" "1.25"
    , style "letter-spacing" "-0.015em"
    , style "color" palette.textPrimary
    , style "white-space" "nowrap"
    , style "overflow" "hidden"
    , style "text-overflow" "ellipsis"
    ]


popupStatusStyles : Settings.Values -> String -> List (Html.Attribute msg)
popupStatusStyles appearance statusText =
    let
        palette =
            paletteFor appearance.theme

        stripeColor =
            statusStripeColor palette statusText

        borderWidth =
            if palette.highContrast then
                "2px"

            else
                "1px"
    in
    [ style "box-sizing" "border-box"
    , style "margin" "0 0 8px 0"
    , style "padding" "7px 11px"
    , style "background-color" palette.surfaceRecessed
    , style "color" palette.textPrimary
    , style "border-top" (borderWidth ++ " solid " ++ palette.borderSubtle)
    , style "border-right" (borderWidth ++ " solid " ++ palette.borderSubtle)
    , style "border-bottom" (borderWidth ++ " solid " ++ palette.borderSubtle)
    , style "border-left" ("3px solid " ++ stripeColor)
    , style "border-radius" "6px"
    , style "font-size" "0.875em"
    , style "line-height" "1.35"
    , style "white-space" "normal"
    , style "overflow-wrap" "anywhere"
    ]


popupControlsStyles : String -> List (Html.Attribute msg)
popupControlsStyles surfaceMode =
    if surfaceMode == "applications" then
        [ style "box-sizing" "border-box"
        , style "display" "grid"
        , style "grid-template-columns" "repeat(6, minmax(0, 1fr))"
        , style "gap" "8px"
        , style "padding" "4px"
        , style "width" "100%"
        , style "align-items" "stretch"
        ]

    else if surfaceMode == "snap" then
        [ style "box-sizing" "border-box"
        , style "display" "grid"
        , style "grid-template-columns" "repeat(2, minmax(0, 1fr))"
        , style "gap" "10px"
        , style "padding" "4px"
        , style "width" "100%"
        ]

    else
        [ style "box-sizing" "border-box"
        , style "display" "flex"
        , style "flex-direction" "column"
        , style "gap" "6px"
        , style "padding" "4px"
        , style "width" "100%"
        ]


searchLabelStyles : Settings.Values -> String -> List (Html.Attribute msg)
searchLabelStyles appearance surfaceMode =
    let
        palette =
            paletteFor appearance.theme

        gridPlacement =
            if surfaceMode == "applications" then
                [ style "grid-column" "1 / -1" ]

            else
                []
    in
    [ style "display" "block"
    , style "box-sizing" "border-box"
    , style "margin" "2px 0 0 0"
    , style "padding" "0 2px"
    , style "color" palette.textSecondary
    , style "font-size" "0.8125em"
    , style "font-weight" "600"
    , style "letter-spacing" "0.01em"
    , style "line-height" "1.3"
    ]
        ++ gridPlacement


searchFieldStyles : Settings.Values -> Bool -> String -> String -> List (Html.Attribute msg)
searchFieldStyles appearance fieldEnabled surfaceMode motionProfile =
    let
        palette =
            paletteFor appearance.theme

        effectsOn =
            softEffectsEnabled appearance palette

        fieldFont =
            if surfaceMode == "files" then
                monoFontStack

            else
                bodyFontStack

        gridPlacement =
            if surfaceMode == "applications" then
                [ style "grid-column" "1 / -1" ]

            else
                []

        borderColor =
            if fieldEnabled then
                palette.borderEssential

            else
                palette.borderDisabled

        borderStyle =
            if not fieldEnabled then
                "dashed"

            else
                "solid"

        fieldShadow =
            if effectsOn && fieldEnabled then
                palette.inputInsetShadow

            else
                "none"
    in
    [ style "box-sizing" "border-box"
    , style "display" "block"
    , style "width" "100%"
    , style "min-height" "2.75em"
    , style "margin" "0 0 2px 0"
    , style "padding" "9px 12px"
    , style "background-color"
        (if fieldEnabled then
            palette.surface

         else
            palette.surfaceRecessed
        )
    , style "color"
        (if fieldEnabled then
            palette.textPrimary

         else
            palette.textDisabled
        )
    , style "border-width" "2px"
    , style "border-style" borderStyle
    , style "border-color" borderColor
    , style "border-radius" "6px"
    , style "font-family" fieldFont
    , style "font-size" "1em"
    , style "line-height" "1.35"
    , style "outline-width" "3px"
    , style "outline-color" palette.focusRing
    , style "outline-offset"
        (if palette.highContrast then
            "0px"

         else
            "2px"
        )
    , style "scroll-margin" "8px"
    , style "opacity" "1"
    , style "box-shadow" fieldShadow
    ]
        ++ gridPlacement
        ++ motionStyles motionProfile


applicationsGridSpan : Int -> String -> List (Html.Attribute msg)
applicationsGridSpan textScale controlIdentity =
    if controlIdentity == "control:acknowledge" || controlIdentity == "control:page-range" then
        [ style "grid-column" "1 / -1" ]

    else if controlIdentity == "control:page-previous" || controlIdentity == "control:page-next" then
        if textScale >= 200 then
            [ style "grid-column" "1 / -1" ]

        else
            [ style "grid-column" "span 3" ]

    else if String.startsWith "control:" controlIdentity then
        [ style "grid-column" "span 3" ]

    else if String.startsWith "unpin:" controlIdentity then
        if textScale >= 150 then
            [ style "grid-column" "1 / -1" ]

        else
            [ style "grid-column" "span 2" ]

    else if String.startsWith "pin-left:" controlIdentity || String.startsWith "pin-right:" controlIdentity then
        if textScale >= 150 then
            [ style "grid-column" "span 3" ]

        else
            [ style "grid-column" "span 2" ]

    else
        [ style "grid-column" "1 / -1" ]


barControlStyles : ControlSpec -> Palette -> List (Html.Attribute msg)
barControlStyles spec palette =
    let
        effectsOn =
            softEffectsEnabled spec.appearance palette

        baseBorderWidth =
            if palette.highContrast then
                "2px"

            else
                "1px"

        isApplicationsOpener =
            spec.identity == "bar:applications"

        bgColor =
            if not spec.isEnabled then
                palette.surfaceRecessed

            else if spec.kind == "control-group" && spec.windowState == "active" then
                palette.surfaceSelected

            else if spec.kind == "control-group" && spec.windowState == "attention" then
                palette.surfaceAttention

            else if isApplicationsOpener then
                palette.surfaceSelected

            else
                palette.surfaceRaised

        fgColor =
            if not spec.isEnabled then
                palette.textDisabled

            else
                palette.textPrimary

        topBorderColor =
            if not spec.isEnabled then
                palette.borderDisabled

            else if spec.kind == "control-group" && spec.windowState == "attention" then
                palette.warningContour

            else if spec.kind == "control-group" && spec.windowState == "active" then
                palette.activeContour

            else if isApplicationsOpener then
                palette.brandAccent

            else
                palette.borderControl

        bottomBorderColor =
            if not spec.isEnabled then
                palette.borderDisabled

            else if spec.kind == "control-group" && spec.windowState == "active" then
                palette.activeContour

            else if spec.kind == "control-group" && spec.windowState == "attention" then
                palette.warningContour

            else if isApplicationsOpener then
                palette.brandAccent

            else
                palette.borderControl

        leftBorderColor =
            if not spec.isEnabled then
                palette.borderDisabled

            else if spec.kind == "control-group" && spec.windowState == "active" then
                palette.activeContour

            else if spec.kind == "control-group" && spec.windowState == "attention" then
                palette.warningContour

            else if isApplicationsOpener then
                palette.brandAccent

            else
                palette.borderControl

        rightBorderColor =
            if not spec.isEnabled then
                palette.borderDisabled

            else if spec.kind == "control-group" && spec.windowState == "active" then
                palette.activeContour

            else if spec.kind == "control-group" && spec.windowState == "attention" then
                palette.warningContour

            else if isApplicationsOpener then
                palette.brandAccent

            else
                palette.borderControl

        topWidth =
            if spec.kind == "control-group" && spec.windowState == "attention" then
                "4px"

            else
                baseBorderWidth

        bottomWidth =
            if spec.kind == "control-group" && spec.windowState == "active" then
                "4px"

            else
                baseBorderWidth

        leftWidth =
            if isApplicationsOpener && spec.isEnabled then
                "3px"

            else
                baseBorderWidth

        borderStyle =
            if not spec.isEnabled then
                "dashed"

            else if spec.kind == "control-group" && spec.windowState == "minimized" && not palette.highContrast then
                "dashed"

            else
                "solid"

        shadowValue =
            if not effectsOn || not spec.isEnabled then
                "none"

            else if spec.kind == "control-group" && spec.windowState == "active" then
                "inset 0 -2px 0 " ++ palette.actionFill

            else if spec.kind == "control-group" && spec.windowState == "attention" then
                "inset 0 2px 0 " ++ palette.warningContour

            else if isApplicationsOpener then
                "inset 2px 0 0 " ++ palette.actionFill ++ ", " ++ palette.cardShadow

            else
                palette.cardShadow

        flexSizing =
            if spec.kind == "control-group" then
                [ style "flex" "1 1 8em"
                , style "min-width" "min(7.5em, calc(100% - 6px))"
                , style "max-width" "min(15em, calc(100% - 6px))"
                ]

            else if spec.kind == "control-recovery" then
                [ style "flex" "0 0 7.5em"
                , style "min-width" "0"
                , style "max-width" "min(15em, calc(100% - 6px))"
                ]

            else
                [ style "flex" "0 0 auto"
                , style "min-width" "min(5.25em, calc(100% - 6px))"
                , style "max-width" "min(15em, calc(100% - 6px))"
                ]
    in
    [ style "box-sizing" "border-box"
    , style "display" "flex"
    , style "flex-direction" "column"
    , style "justify-content" "center"
    , style "align-items" "flex-start"
    , style "height" "calc(100% - 6px)"
    , style "min-height" "0"
    , style "max-height" "none"
    , style "margin" "3px"
    , style "padding"
        (if isApplicationsOpener then
            "2px 12px"

         else
            "2px 10px"
        )
    , style "background-color" bgColor
    , style "color" fgColor
    , style "border-style" borderStyle
    , style "border-top-width" topWidth
    , style "border-bottom-width" bottomWidth
    , style "border-left-width" leftWidth
    , style "border-right-width" baseBorderWidth
    , style "border-top-color" topBorderColor
    , style "border-bottom-color" bottomBorderColor
    , style "border-left-color" leftBorderColor
    , style "border-right-color" rightBorderColor
    , style "border-radius" "6px"
    , style "font-family" "inherit"
    , style "font-size" "1em"
    , style "font-weight"
        (if isApplicationsOpener || (spec.kind == "control-group" && spec.windowState == "active") then
            "600"

         else
            "500"
        )
    , style "line-height" "1.125em"
    , style "text-align" "left"
    , style "cursor"
        (if spec.isEnabled then
            "pointer"

         else
            "not-allowed"
        )
    , style "opacity" "1"
    , style "box-shadow" shadowValue
    , style "text-shadow" "none"
    , style "outline-width" "3px"
    , style "outline-color" palette.focusRing
    , style "outline-offset" "0px"
    , style "scroll-margin-inline" "6px"
    , style "overflow" "hidden"
    ]
        ++ flexSizing
        ++ motionStyles spec.motion


popupControlStyles : ControlSpec -> Palette -> List (Html.Attribute msg)
popupControlStyles spec palette =
    let
        effectsOn =
            softEffectsEnabled spec.appearance palette

        isPickerFamily =
            spec.surfaceMode == "picker" && String.startsWith "family:" spec.identity

        isPickerOrMenu =
            spec.surfaceMode == "picker" || spec.surfaceMode == "menu"

        isSnapRegion =
            spec.surfaceMode == "snap" && String.startsWith "snap:region:" spec.identity

        isPrimaryCommit =
            isPrimaryCommitIdentity spec.surfaceMode spec.identity

        isDestructive =
            isDestructiveConfirmIdentity spec.surfaceMode spec.identity

        isPageRange =
            spec.surfaceMode == "applications" && spec.identity == "control:page-range"

        isApplicationsEntry =
            spec.surfaceMode == "applications" && String.startsWith "entry:" spec.identity

        isApplicationsJump =
            spec.surfaceMode == "applications" && String.startsWith "jump:open:" spec.identity

        isApplicationsPinPrimary =
            spec.surfaceMode == "applications" && String.startsWith "pin:" spec.identity

        isApplicationsPinReorder =
            spec.surfaceMode == "applications"
                && (String.startsWith "unpin:" spec.identity
                        || String.startsWith "pin-left:" spec.identity
                        || String.startsWith "pin-right:" spec.identity
                   )

        isUtilityControl =
            String.startsWith "control:" spec.identity && not isPageRange

        selectedLike =
            spec.isCurrent || spec.checked == Just True

        baseBorderWidth =
            if palette.highContrast then
                "2px"

            else
                "1px"

        leftBorderWidth =
            if selectedLike then
                "4px"

            else if (isApplicationsEntry || isApplicationsPinPrimary || isApplicationsJump) && spec.isEnabled then
                "3px"

            else
                baseBorderWidth

        bgColor =
            if isPageRange || spec.isFocusOnly || not spec.isEnabled then
                palette.surfaceRecessed

            else if isPrimaryCommit then
                palette.actionFill

            else if selectedLike then
                palette.surfaceSelected

            else if isUtilityControl || isApplicationsPinReorder then
                palette.surfaceUtility

            else
                palette.surfaceRaised

        fgColor =
            if isPageRange then
                palette.textSecondary

            else if spec.isFocusOnly then
                palette.textPrimary

            else if not spec.isEnabled then
                palette.textDisabled

            else if isPrimaryCommit then
                palette.onAction

            else if isDestructive then
                palette.dangerAccent

            else
                palette.textPrimary

        frameBorderColor =
            if isPageRange then
                palette.borderSubtle

            else if spec.isFocusOnly then
                palette.borderEssential

            else if not spec.isEnabled then
                palette.borderDisabled

            else if isPrimaryCommit then
                palette.actionFill

            else if isDestructive then
                palette.dangerAccent

            else if selectedLike then
                palette.brandAccent

            else
                palette.borderControl

        leftBorderColor =
            if isPageRange then
                palette.borderSubtle

            else if spec.isFocusOnly then
                palette.borderEssential

            else if not spec.isEnabled then
                palette.borderDisabled

            else if isPrimaryCommit then
                palette.actionFill

            else if isDestructive then
                palette.dangerAccent

            else if selectedLike || isApplicationsEntry || isApplicationsPinPrimary then
                palette.brandAccent

            else if isApplicationsJump then
                palette.focusRing

            else
                palette.borderControl

        borderStyle =
            if spec.isFocusOnly then
                "dashed"

            else if not spec.isEnabled && not isPageRange then
                "dashed"

            else
                "solid"

        shadowValue =
            if not effectsOn || not spec.isEnabled || isDestructive then
                "none"

            else if isSnapRegion && selectedLike then
                palette.snapSelectedShadow

            else if isSnapRegion then
                palette.snapShadow

            else if selectedLike then
                "inset 2px 0 0 " ++ palette.brandAccent

            else if isApplicationsEntry || isPrimaryCommit then
                palette.cardShadow

            else
                "none"

        gridSpanAttrs =
            if spec.surfaceMode == "applications" then
                applicationsGridSpan spec.appearance.textScale spec.identity

            else if spec.surfaceMode == "snap" && (spec.identity == "control:close" || spec.identity == "snap:apply") then
                [ style "grid-column" "1 / -1" ]

            else
                []

        layoutAttrs =
            if isPickerFamily then
                -- Preserve exact picker family height & omit inline display/min-height
                -- so legacy preview grid rules and runtime minHeight probes remain intact.
                [ style "width" "calc(100% - 6px)"
                , style "margin" "3px"
                , style "padding" "6px 12px"
                , style "height" "min(calc(7.5em + 14px), calc(100vh - 30px))"
                , style "max-height" "min(calc(7.5em + 14px), calc(100vh - 30px))"
                , style "overflow" "hidden"
                ]

            else if isSnapRegion then
                [ style "display" "flex"
                , style "flex-direction" "column"
                , style "justify-content" "center"
                , style "align-items" "center"
                , style "width" "100%"
                , style "min-height" "5.75em"
                , style "margin" "0"
                , style "padding" "12px"
                , style "text-align" "center"
                ]

            else if spec.surfaceMode == "applications" then
                [ style "display" "flex"
                , style "flex-direction" "column"
                , style "justify-content" "center"
                , style "align-items" "stretch"
                , style "width" "100%"
                , style "min-height"
                    (if isPageRange then
                        "2.25em"

                     else
                        "2.75em"
                    )
                , style "margin" "0"
                , style "padding"
                    (if isApplicationsEntry then
                        "9px 14px"

                     else
                        "8px 12px"
                    )
                ]

            else if spec.isMenuCheckbox then
                [ style "position" "relative"
                , style "display" "block"
                , style "width" "calc(100% - 6px)"
                , style "margin" "2px 3px"
                , style "padding" "9px 12px"
                , style "padding-inline-start" "2.5em"
                ]

            else if isPickerOrMenu then
                -- Omit inline min-height on picker/menu buttons so dense-taskbar-browser.mjs
                -- runtime style.minHeight probes and narrow 320x180 menu viewports stay intact.
                [ style "display" "block"
                , style "width" "calc(100% - 6px)"
                , style "margin" "2px 3px"
                , style "padding" "9px 12px"
                ]

            else
                [ style "display" "flex"
                , style "flex-direction" "column"
                , style "justify-content" "center"
                , style "align-items" "stretch"
                , style "width" "calc(100% - 6px)"
                , style "min-height" "2.75em"
                , style "margin" "2px 3px"
                , style "padding" "8px 12px"
                ]

        cursorValue =
            if spec.isEnabled then
                "pointer"

            else if isPageRange || spec.isFocusOnly then
                "default"

            else
                "not-allowed"
    in
    [ style "box-sizing" "border-box"
    , style "background-color" bgColor
    , style "color" fgColor
    , style "border-style" borderStyle
    , style "border-top-width" baseBorderWidth
    , style "border-right-width" baseBorderWidth
    , style "border-bottom-width" baseBorderWidth
    , style "border-left-width" leftBorderWidth
    , style "border-top-color" frameBorderColor
    , style "border-right-color" frameBorderColor
    , style "border-bottom-color" frameBorderColor
    , style "border-left-color" leftBorderColor
    , style "border-radius" "6px"
    , style "font-family" "inherit"
    , style "font-size" "1em"
    , style "font-weight"
        (if isPrimaryCommit || selectedLike || isApplicationsEntry then
            "600"

         else
            "500"
        )
    , style "line-height" "1.35"
    , style "text-align"
        (if isSnapRegion then
            "center"

         else
            "left"
        )
    , style "cursor" cursorValue
    , style "opacity" "1"
    , style "box-shadow" shadowValue
    , style "text-shadow" "none"
    , style "outline-width" "3px"
    , style "outline-color" palette.focusRing
    , style "outline-offset"
        (if palette.highContrast then
            "0px"

         else
            "1px"
        )
    , style "scroll-margin-block" "8px"
    ]
        ++ gridSpanAttrs
        ++ layoutAttrs
        ++ motionStyles spec.motion


controlStyles : ControlSpec -> List (Html.Attribute msg)
controlStyles spec =
    let
        palette =
            paletteFor spec.appearance.theme
    in
    if spec.popup then
        popupControlStyles spec palette

    else
        barControlStyles spec palette


controlLabelStyles : Bool -> String -> String -> List (Html.Attribute msg)
controlLabelStyles isPopup surfaceMode controlIdentity =
    if not isPopup then
        if controlIdentity == "bar:recovery-refresh" then
            [ style "display" "block"
            , style "width" "100%"
            , style "min-width" "0"
            , style "font-size" "0.85em"
            , style "line-height" "1.1"
            , style "white-space" "normal"
            , style "overflow" "hidden"
            ]

        else
            [ style "display" "block"
            , style "width" "100%"
            , style "min-width" "0"
            , style "overflow" "hidden"
            , style "text-overflow" "ellipsis"
            , style "white-space" "nowrap"
            ]

    else if surfaceMode == "picker" && String.startsWith "family:" controlIdentity then
        [ style "display" "block"
        , style "min-width" "0"
        , style "overflow" "hidden"
        , style "text-overflow" "ellipsis"
        , style "white-space" "nowrap"
        ]

    else if surfaceMode == "applications" then
        [ style "display" "block"
        , style "width" "100%"
        , style "min-width" "0"
        , style "white-space" "normal"
        , style "overflow-wrap" "anywhere"
        , style "line-height" "1.3"
        ]

    else
        [ style "display" "block"
        , style "width" "100%"
        , style "min-width" "0"
        , style "white-space" "normal"
        , style "overflow-wrap" "anywhere"
        ]


controlDetailStyles : ControlSpec -> String -> List (Html.Attribute msg)
controlDetailStyles spec detailText =
    let
        palette =
            paletteFor spec.appearance.theme

        isPrimaryCommit =
            spec.popup && isPrimaryCommitIdentity spec.surfaceMode spec.identity

        isPickerFamily =
            spec.popup && spec.surfaceMode == "picker" && String.startsWith "family:" spec.identity

        detailColor =
            if not spec.isEnabled && not spec.isFocusOnly then
                palette.textDisabled

            else if isPrimaryCommit && spec.isEnabled then
                palette.onAction

            else
                palette.textSecondary
    in
    if String.isEmpty detailText then
        [ style "display" "none" ]

    else if not spec.popup then
        [ style "display" "block"
        , style "width" "100%"
        , style "min-width" "0"
        , style "color" detailColor
        , style "font-size" "0.75em"
        , style "font-weight" "400"
        , style "line-height" "1.05"
        , style "overflow" "hidden"
        , style "text-overflow" "ellipsis"
        , style "white-space" "nowrap"
        ]

    else if isPickerFamily then
        [ style "display" "block"
        , style "min-width" "0"
        , style "margin" "0"
        , style "color" detailColor
        , style "font-size" "0.875em"
        , style "font-weight" "400"
        , style "line-height" "1.2"
        , style "overflow" "hidden"
        , style "text-overflow" "ellipsis"
        , style "white-space" "nowrap"
        ]

    else
        [ style "display" "block"
        , style "width" "100%"
        , style "min-width" "0"
        , style "margin-top" "2px"
        , style "color" detailColor
        , style "font-size" "0.8125em"
        , style "font-weight" "400"
        , style "line-height" "1.25"
        , style "white-space" "normal"
        , style "overflow-wrap" "anywhere"
        ]


checkboxIndicator : Maybe Bool -> Html msg
checkboxIndicator checkedState =
    let
        isChecked =
            checkedState == Just True
    in
    span
        [ attribute "aria-hidden" "true"
        , style "position" "absolute"
        , style "inset-inline-start" "0.8em"
        , style "top" "0.75em"
        , style "width" "1em"
        , style "height" "1em"
        , style "box-sizing" "border-box"
        , style "border" "2px solid currentColor"
        , style "border-radius" "2px"
        , style "pointer-events" "none"
        ]
        (if isChecked then
            [ span
                [ attribute "aria-hidden" "true"
                , style "position" "absolute"
                , style "inset-inline-start" "0.18em"
                , style "top" "0.02em"
                , style "width" "0.35em"
                , style "height" "0.6em"
                , style "border-style" "solid"
                , style "border-color" "currentColor"
                , style "border-width" "0 2px 2px 0"
                , style "transform" "rotate(45deg)"
                ]
                []
            ]

         else
            [ text "" ]
        )


notificationTextStyles : Settings.Values -> List (Html.Attribute msg)
notificationTextStyles appearance =
    let
        palette =
            paletteFor appearance.theme

        borderWidth =
            if palette.highContrast then
                "2px"

            else
                "1px"
    in
    [ style "box-sizing" "border-box"
    , style "margin" "4px 3px"
    , style "padding" "8px 10px"
    , style "background-color" palette.surfaceRecessed
    , style "color" palette.textPrimary
    , style "border-top" (borderWidth ++ " solid " ++ palette.borderSubtle)
    , style "border-right" (borderWidth ++ " solid " ++ palette.borderSubtle)
    , style "border-bottom" (borderWidth ++ " solid " ++ palette.borderSubtle)
    , style "border-left" ("3px solid " ++ palette.borderEssential)
    , style "border-radius" "6px"
    , style "opacity" "1"
    , style "white-space" "normal"
    , style "overflow-wrap" "anywhere"
    ]


settingsSaveGroupStyles : Settings.Values -> List (Html.Attribute msg)
settingsSaveGroupStyles appearance =
    let
        palette =
            paletteFor appearance.theme

        borderWidth =
            if palette.highContrast then
                "2px"

            else
                "1px"
    in
    [ style "box-sizing" "border-box"
    , style "margin" "4px 0"
    , style "padding" "8px"
    , style "background-color" palette.surfaceRecessed
    , style "border" (borderWidth ++ " solid " ++ palette.borderSubtle)
    , style "border-radius" "8px"
    ]


settingsSaveCaptionStyles : Settings.Values -> List (Html.Attribute msg)
settingsSaveCaptionStyles appearance =
    let
        palette =
            paletteFor appearance.theme
    in
    [ style "margin" "6px 4px 0 4px"
    , style "color" palette.textSecondary
    , style "font-size" "0.8125em"
    , style "line-height" "1.35"
    , style "white-space" "normal"
    , style "overflow-wrap" "anywhere"
    ]


overviewWorkspaceStyles : Settings.Values -> List (Html.Attribute msg)
overviewWorkspaceStyles appearance =
    let
        palette =
            paletteFor appearance.theme

        borderWidth =
            if palette.highContrast then
                "2px"

            else
                "1px"
    in
    [ style "box-sizing" "border-box"
    , style "display" "flex"
    , style "flex-direction" "column"
    , style "gap" "6px"
    , style "margin" "2px 0"
    , style "padding" "8px"
    , style "background-color" palette.surfaceRecessed
    , style "border" (borderWidth ++ " solid " ++ palette.borderControl)
    , style "border-radius" "8px"
    ]


switcherListboxStyles : Settings.Values -> List (Html.Attribute msg)
switcherListboxStyles appearance =
    let
        palette =
            paletteFor appearance.theme

        borderWidth =
            if palette.highContrast then
                "2px"

            else
                "1px"
    in
    [ style "box-sizing" "border-box"
    , style "display" "flex"
    , style "flex-direction" "column"
    , style "gap" "6px"
    , style "padding" "6px"
    , style "background-color" palette.surfaceRecessed
    , style "border" (borderWidth ++ " solid " ++ palette.borderControl)
    , style "border-radius" "8px"
    ]


switcherActionsStyles : List (Html.Attribute msg)
switcherActionsStyles =
    [ style "box-sizing" "border-box"
    , style "display" "flex"
    , style "flex-direction" "column"
    , style "gap" "6px"
    ]
