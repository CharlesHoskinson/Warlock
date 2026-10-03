# elm-ui 1.1.8
Source: https://package.elm-lang.org/packages/mdgriffith/elm-ui/1.1.8/docs.json

# Element




# Basic Elements

@docs Element, none, text, el


# Rows and Columns

When we want more than one child on an element, we want to be _specific_ about how they will be laid out.

So, the common ways to do that would be `row` and `column`.

@docs row, wrappedRow, column


# Text Layout

Text layout needs some specific considerations.

@docs paragraph, textColumn


# Data Table

@docs Column, table, IndexedColumn, indexedTable


# Size

@docs Attribute, width, height, Length, px, shrink, fill, fillPortion, maximum, minimum


# Debugging

@docs explain


# Padding and Spacing

There's no concept of margin in `elm-ui`, instead we have padding and spacing.

Padding is the distance between the outer edge and the content, and spacing is the space between children.

So, if we have the following row, with some padding and spacing.

    Element.row [ padding 10, spacing 7 ]
        [ Element.el [] none
        , Element.el [] none
        , Element.el [] none
        ]

Here's what we can expect:

![Three boxes spaced 7 pixels apart. There's a 10 pixel distance from the edge of the parent to the boxes.](https://mdgriffith.gitbooks.io/style-elements/content/assets/spacing-400.png)

**Note** `spacing` set on a `paragraph`, will set the pixel spacing between lines.

@docs padding, paddingXY, paddingEach

@docs spacing, spacingXY, spaceEvenly


# Alignment

Alignment can be used to align an `Element` within another `Element`.

    Element.el [ centerX, alignTop ] (text "I'm centered and aligned top!")

If alignment is set on elements in a layout such as `row`, then the element will push the other elements in that direction. Here's an example.

    Element.row []
        [ Element.el [] Element.none
        , Element.el [ alignLeft ] Element.none
        , Element.el [ centerX ] Element.none
        , Element.el [ alignRight ] Element.none
        ]

will result in a layout like

    |-|-|    |-|    |-|

Where there are two elements on the left, one on the right, and one in the center of the space between the elements on the left and right.

**Note** For text alignment, check out `Element.Font`!

@docs centerX, centerY, alignLeft, alignRight, alignTop, alignBottom


# Transparency

@docs transparent, alpha, pointer


# Adjustment

@docs moveUp, moveDown, moveRight, moveLeft, rotate, scale


# Clipping and Scrollbars

Clip the content if it overflows.

@docs clip, clipX, clipY

Add a scrollbar if the content is larger than the element.

@docs scrollbars, scrollbarX, scrollbarY


# Rendering

@docs layout, layoutWith, Option, noStaticStyleSheet, forceHover, noHover, focusStyle, FocusStyle


# Links

@docs link, newTabLink, download, downloadAs


# Images

@docs image


# Color

In order to use attributes like `Font.color` and `Background.color`, you'll need to make some colors!

@docs Color, rgba, rgb, rgb255, rgba255, fromRgb, fromRgb255, toRgb


# Nearby Elements

Let's say we want a dropdown menu. Essentially we want to say: _put this element below this other element, but don't affect the layout when you do_.

    Element.row []
        [ Element.el
            [ Element.below (Element.text "I'm below!")
            ]
            (Element.text "I'm normal!")
        ]

This will result in

    |- I'm normal! -|
       I'm below

Where `"I'm Below"` doesn't change the size of `Element.row`.

This is very useful for things like dropdown menus or tooltips.

@docs above, below, onRight, onLeft, inFront, behindContent


# Temporary Styling

@docs Attr, Decoration, mouseOver, mouseDown, focused


# Responsiveness

The main technique for responsiveness is to store window size information in your model.

Install the `Browser` package, and set up a subscription for [`Browser.Events.onResize`](https://package.elm-lang.org/packages/elm/browser/latest/Browser-Events#onResize).

You'll also need to retrieve the initial window size. You can either use [`Browser.Dom.getViewport`](https://package.elm-lang.org/packages/elm/browser/latest/Browser-Dom#getViewport) or pass in `window.innerWidth` and `window.innerHeight` as flags to your program, which is the preferred way. This requires minor setup on the JS side, but allows you to avoid the state where you don't have window info.

@docs Device, DeviceClass, Orientation, classifyDevice


# Scaling

@docs modular


## Mapping

@docs map, mapAttribute


## Compatibility

@docs html, htmlAttribute



## Attr

```elm
type alias Attr decorative msg =
    Internal.Model.Attribute decorative msg
```

 This is a special attribute that counts as both a `Attribute msg` and a `Decoration`.


## Attribute

```elm
type alias Attribute msg =
    Internal.Model.Attribute () msg
```

 An attribute that can be attached to an `Element`


## Color

```elm
type alias Color =
    Internal.Model.Color
```

 

## Column

```elm
type alias Column record msg =
    { header : Element.Element msg, width : Element.Length, view : record -> Element.Element msg }
```

 

## Decoration

```elm
type alias Decoration =
    Internal.Model.Attribute Basics.Never Basics.Never
```

 Only decorations


## Device

```elm
type alias Device =
    { class : Element.DeviceClass, orientation : Element.Orientation }
```

 

## Element

```elm
type alias Element msg =
    Internal.Model.Element msg
```

 The basic building block of your layout.

    howdy : Element msg
    howdy =
        Element.el [] (Element.text "Howdy!")



## FocusStyle

```elm
type alias FocusStyle =
    { borderColor : Maybe.Maybe Element.Color, backgroundColor : Maybe.Maybe Element.Color, shadow : Maybe.Maybe { color : Element.Color, offset : ( Basics.Int, Basics.Int ), blur : Basics.Int, size : Basics.Int } }
```

 

## IndexedColumn

```elm
type alias IndexedColumn record msg =
    { header : Element.Element msg, width : Element.Length, view : Basics.Int -> record -> Element.Element msg }
```

 

## Length

```elm
type alias Length =
    Internal.Model.Length
```

 

## Option

```elm
type alias Option =
    Internal.Model.Option
```

 

## DeviceClass

```elm
type DeviceClass
    = Phone
    | Tablet
    | Desktop
    | BigDesktop
```

 

## Orientation

```elm
type Orientation
    = Portrait
    | Landscape
```

 

## above

```elm
above : Element.Element msg -> Element.Attribute msg
```

 

## alignBottom

```elm
alignBottom : Element.Attribute msg
```

 

## alignLeft

```elm
alignLeft : Element.Attribute msg
```

 

## alignRight

```elm
alignRight : Element.Attribute msg
```

 

## alignTop

```elm
alignTop : Element.Attribute msg
```

 

## alpha

```elm
alpha : Basics.Float -> Element.Attr decorative msg
```

 A capped value between 0.0 and 1.0, where 0.0 is transparent and 1.0 is fully opaque.

Semantically equivalent to html opacity.



## behindContent

```elm
behindContent : Element.Element msg -> Element.Attribute msg
```

 This will place an element between the background and the content of an element.


## below

```elm
below : Element.Element msg -> Element.Attribute msg
```

 

## centerX

```elm
centerX : Element.Attribute msg
```

 

## centerY

```elm
centerY : Element.Attribute msg
```

 

## classifyDevice

```elm
classifyDevice : { window | height : Basics.Int, width : Basics.Int } -> Element.Device
```

 Takes in a Window.Size and returns a device profile which can be used for responsiveness.

If you have more detailed concerns around responsiveness, it probably makes sense to copy this function into your codebase and modify as needed.



## clip

```elm
clip : Element.Attribute msg
```

 

## clipX

```elm
clipX : Element.Attribute msg
```

 

## clipY

```elm
clipY : Element.Attribute msg
```

 

## column

```elm
column : List.List (Element.Attribute msg) -> List.List (Element.Element msg) -> Element.Element msg
```

 

## download

```elm
download : List.List (Element.Attribute msg) -> { url : String.String, label : Element.Element msg } -> Element.Element msg
```

 A link to download a file.


## downloadAs

```elm
downloadAs : List.List (Element.Attribute msg) -> { label : Element.Element msg, filename : String.String, url : String.String } -> Element.Element msg
```

 A link to download a file, but you can specify the filename.


## el

```elm
el : List.List (Element.Attribute msg) -> Element.Element msg -> Element.Element msg
```

 The basic building block of your layout.

You can think of an `el` as a `div`, but it can only have one child.

If you want multiple children, you'll need to use something like `row` or `column`

    import Element exposing (Element, rgb)
    import Element.Background as Background
    import Element.Border as Border

    myElement : Element msg
    myElement =
        Element.el
            [ Background.color (rgb 0 0.5 0)
            , Border.color (rgb 0 0.7 0)
            ]
            (Element.text "You've made a stylish element!")



## explain

```elm
explain : Element.Todo -> Element.Attribute msg
```

 Highlight the borders of an element and it's children below. This can really help if you're running into some issue with your layout!

**Note** This attribute needs to be handed `Debug.todo` in order to work, even though it won't do anything with it. This is a safety measure so you don't accidently ship code with `explain` in it, as Elm won't compile with `--optimize` if you still have a `Debug` statement in your code.

    el
        [ Element.explain Debug.todo
        ]
        (text "Help, I'm being debugged!")



## fill

```elm
fill : Element.Length
```

 Fill the available space. The available space will be split evenly between elements that have `width fill`.


## fillPortion

```elm
fillPortion : Basics.Int -> Element.Length
```

 Sometimes you may not want to split available space evenly. In this case you can use `fillPortion` to define which elements should have what portion of the available space.

So, two elements, one with `width (fillPortion 2)` and one with `width (fillPortion 3)`. The first would get 2 portions of the available space, while the second would get 3.

**Also:** `fill == fillPortion 1`



## focusStyle

```elm
focusStyle : Element.FocusStyle -> Element.Option
```

 

## focused

```elm
focused : List.List Element.Decoration -> Element.Attribute msg
```

 

## forceHover

```elm
forceHover : Element.Option
```

 Any `hover` styles, aka attributes with `mouseOver` in the name, will be always turned on.

This is useful for when you're targeting a platform that has no mouse, such as mobile.



## fromRgb

```elm
fromRgb : { red : Basics.Float, green : Basics.Float, blue : Basics.Float, alpha : Basics.Float } -> Element.Color
```

 Create a color from an RGB record.


## fromRgb255

```elm
fromRgb255 : { red : Basics.Int, green : Basics.Int, blue : Basics.Int, alpha : Basics.Float } -> Element.Color
```

 

## height

```elm
height : Element.Length -> Element.Attribute msg
```

 

## html

```elm
html : Html.Html msg -> Element.Element msg
```

 

## htmlAttribute

```elm
htmlAttribute : Html.Attribute msg -> Element.Attribute msg
```

 

## image

```elm
image : List.List (Element.Attribute msg) -> { src : String.String, description : String.String } -> Element.Element msg
```

 Both a source and a description are required for images.

The description is used for people using screen readers.

Leaving the description blank will cause the image to be ignored by assistive technology. This can make sense for images that are purely decorative and add no additional information.

So, take a moment to describe your image as you would to someone who has a harder time seeing.



## inFront

```elm
inFront : Element.Element msg -> Element.Attribute msg
```

 This will place an element in front of another.

**Note:** If you use this on a `layout` element, it will place the element as fixed to the viewport which can be useful for modals and overlays.



## indexedTable

```elm
indexedTable : List.List (Element.Attribute msg) -> { data : List.List records, columns : List.List (Element.IndexedColumn records msg) } -> Element.Element msg
```

 Same as `Element.table` except the `view` for each column will also receive the row index as well as the record.


## layout

```elm
layout : List.List (Element.Attribute msg) -> Element.Element msg -> Html.Html msg
```

 This is your top level node where you can turn `Element` into `Html`.


## layoutWith

```elm
layoutWith : { options : List.List Element.Option } -> List.List (Element.Attribute msg) -> Element.Element msg -> Html.Html msg
```

 

## link

```elm
link : List.List (Element.Attribute msg) -> { url : String.String, label : Element.Element msg } -> Element.Element msg
```



    link []
        { url = "http://fruits.com"
        , label = text "A link to my favorite fruit provider."
        }



## map

```elm
map : (msg -> msg1) -> Element.Element msg -> Element.Element msg1
```

 

## mapAttribute

```elm
mapAttribute : (msg -> msg1) -> Element.Attribute msg -> Element.Attribute msg1
```

 

## maximum

```elm
maximum : Basics.Int -> Element.Length -> Element.Length
```

 Add a maximum to a length.

    el
        [ height
            (fill
                |> maximum 300
            )
        ]
        (text "I will stop at 300px")



## minimum

```elm
minimum : Basics.Int -> Element.Length -> Element.Length
```

 Similarly you can set a minimum boundary.

     el
        [ height
            (fill
                |> maximum 300
                |> minimum 30
            )

        ]
        (text "I will stop at 300px")



## modular

```elm
modular : Basics.Float -> Basics.Float -> Basics.Int -> Basics.Float
```

 When designing it's nice to use a modular scale to set spacial rythms.

    scaled =
        Element.modular 16 1.25

A modular scale starts with a number, and multiplies it by a ratio a number of times.
Then, when setting font sizes you can use:

    Font.size (scaled 1) -- results in 16

    Font.size (scaled 2) -- 16 * 1.25 results in 20

    Font.size (scaled 4) -- 16 * 1.25 ^ (4 - 1) results in 31.25

We can also provide negative numbers to scale below 16px.

    Font.size (scaled -1) -- 16 * 1.25 ^ (-1) results in 12.8



## mouseDown

```elm
mouseDown : List.List Element.Decoration -> Element.Attribute msg
```

 

## mouseOver

```elm
mouseOver : List.List Element.Decoration -> Element.Attribute msg
```

 

## moveDown

```elm
moveDown : Basics.Float -> Element.Attr decorative msg
```

 

## moveLeft

```elm
moveLeft : Basics.Float -> Element.Attr decorative msg
```

 

## moveRight

```elm
moveRight : Basics.Float -> Element.Attr decorative msg
```

 

## moveUp

```elm
moveUp : Basics.Float -> Element.Attr decorative msg
```

 

## newTabLink

```elm
newTabLink : List.List (Element.Attribute msg) -> { url : String.String, label : Element.Element msg } -> Element.Element msg
```

 

## noHover

```elm
noHover : Element.Option
```

 Disable all `mouseOver` styles.


## noStaticStyleSheet

```elm
noStaticStyleSheet : Element.Option
```

 Elm UI embeds two StyleSheets, one that is constant, and one that changes dynamically based on styles collected from the elements being rendered.

This option will stop the static/constant stylesheet from rendering.

If you're embedding multiple elm-ui `layout` elements, you need to guarantee that only one is rendering the static style sheet and that it's above all the others in the DOM tree.



## none

```elm
none : Element.Element msg
```

 When you want to render exactly nothing.


## onLeft

```elm
onLeft : Element.Element msg -> Element.Attribute msg
```

 

## onRight

```elm
onRight : Element.Element msg -> Element.Attribute msg
```

 

## padding

```elm
padding : Basics.Int -> Element.Attribute msg
```

 

## paddingEach

```elm
paddingEach : { top : Basics.Int, right : Basics.Int, bottom : Basics.Int, left : Basics.Int } -> Element.Attribute msg
```

 If you find yourself defining unique paddings all the time, you might consider defining

    edges =
        { top = 0
        , right = 0
        , bottom = 0
        , left = 0
        }

And then just do

    paddingEach { edges | right = 5 }



## paddingXY

```elm
paddingXY : Basics.Int -> Basics.Int -> Element.Attribute msg
```

 Set horizontal and vertical padding.


## paragraph

```elm
paragraph : List.List (Element.Attribute msg) -> List.List (Element.Element msg) -> Element.Element msg
```

 A paragraph will layout all children as wrapped, inline elements.

    import Element exposing (el, paragraph, text)
    import Element.Font as Font

    view =
        paragraph []
            [ text "lots of text ...."
            , el [ Font.bold ] (text "this is bold")
            , text "lots of text ...."
            ]

This is really useful when you want to markup text by having some parts be bold, or some be links, or whatever you so desire.

Also, if a child element has `alignLeft` or `alignRight`, then it will be moved to that side and the text will flow around it, (ah yes, `float` behavior).

This makes it particularly easy to do something like a [dropped capital](https://en.wikipedia.org/wiki/Initial).

    import Element exposing (alignLeft, el, padding, paragraph, text)
    import Element.Font as Font

    view =
        paragraph []
            [ el
                [ alignLeft
                , padding 5
                ]
                (text "S")
            , text "o much text ...."
            ]

Which will look something like

![A paragraph where the first letter is twice the height of the others](https://mdgriffith.gitbooks.io/style-elements/content/assets/Screen%20Shot%202017-08-25%20at%209.41.52%20PM.png)

**Note** `spacing` on a paragraph will set the pixel spacing between lines.



## pointer

```elm
pointer : Element.Attribute msg
```

 Set the cursor to be a pointing hand when it's hovering over this element.


## px

```elm
px : Basics.Int -> Element.Length
```

 

## rgb

```elm
rgb : Basics.Float -> Basics.Float -> Basics.Float -> Element.Color
```

 Provide the red, green, and blue channels for the color.

Each channel takes a value between 0 and 1.



## rgb255

```elm
rgb255 : Basics.Int -> Basics.Int -> Basics.Int -> Element.Color
```

 Provide the red, green, and blue channels for the color.

Each channel takes a value between 0 and 255.



## rgba

```elm
rgba : Basics.Float -> Basics.Float -> Basics.Float -> Basics.Float -> Element.Color
```

 

## rgba255

```elm
rgba255 : Basics.Int -> Basics.Int -> Basics.Int -> Basics.Float -> Element.Color
```

 

## rotate

```elm
rotate : Basics.Float -> Element.Attr decorative msg
```

 Angle is given in radians. [Here are some conversion functions if you want to use another unit.](https://package.elm-lang.org/packages/elm/core/latest/Basics#degrees)


## row

```elm
row : List.List (Element.Attribute msg) -> List.List (Element.Element msg) -> Element.Element msg
```

 

## scale

```elm
scale : Basics.Float -> Element.Attr decorative msg
```

 

## scrollbarX

```elm
scrollbarX : Element.Attribute msg
```

 

## scrollbarY

```elm
scrollbarY : Element.Attribute msg
```

 

## scrollbars

```elm
scrollbars : Element.Attribute msg
```

 

## shrink

```elm
shrink : Element.Length
```

 Shrink an element to fit its contents.


## spaceEvenly

```elm
spaceEvenly : Element.Attribute msg
```

 

## spacing

```elm
spacing : Basics.Int -> Element.Attribute msg
```

 

## spacingXY

```elm
spacingXY : Basics.Int -> Basics.Int -> Element.Attribute msg
```

 In the majority of cases you'll just need to use `spacing`, which will work as intended.

However for some layouts, like `textColumn`, you may want to set a different spacing for the x axis compared to the y axis.



## table

```elm
table : List.List (Element.Attribute msg) -> { data : List.List records, columns : List.List (Element.Column records msg) } -> Element.Element msg
```

 Show some tabular data.

Start with a list of records and specify how each column should be rendered.

So, if we have a list of `persons`:

    type alias Person =
        { firstName : String
        , lastName : String
        }

    persons : List Person
    persons =
        [ { firstName = "David"
          , lastName = "Bowie"
          }
        , { firstName = "Florence"
          , lastName = "Welch"
          }
        ]

We could render it using

    Element.table []
        { data = persons
        , columns =
            [ { header = Element.text "First Name"
              , width = fill
              , view =
                    \person ->
                        Element.text person.firstName
              }
            , { header = Element.text "Last Name"
              , width = fill
              , view =
                    \person ->
                        Element.text person.lastName
              }
            ]
        }

**Note:** Sometimes you might not have a list of records directly in your model. In this case it can be really nice to write a function that transforms some part of your model into a list of records before feeding it into `Element.table`.



## text

```elm
text : String.String -> Element.Element msg
```

 Create some plain text.

    text "Hello, you stylish developer!"

**Note** text does not wrap by default. In order to get text to wrap, check out `paragraph`!



## textColumn

```elm
textColumn : List.List (Element.Attribute msg) -> List.List (Element.Element msg) -> Element.Element msg
```

 Now that we have a paragraph, we need some way to attach a bunch of paragraph's together.

To do that we can use a `textColumn`.

The main difference between a `column` and a `textColumn` is that `textColumn` will flow the text around elements that have `alignRight` or `alignLeft`, just like we just saw with paragraph.

In the following example, we have a `textColumn` where one child has `alignLeft`.

    Element.textColumn [ spacing 10, padding 10 ]
        [ paragraph [] [ text "lots of text ...." ]
        , el [ alignLeft ] none
        , paragraph [] [ text "lots of text ...." ]
        ]

Which will result in something like:

![A text layout where an image is on the left.](https://mdgriffith.gitbooks.io/style-elements/content/assets/Screen%20Shot%202017-08-25%20at%208.42.39%20PM.png)



## toRgb

```elm
toRgb : Element.Color -> { red : Basics.Float, green : Basics.Float, blue : Basics.Float, alpha : Basics.Float }
```

 Deconstruct a `Color` into its rgb channels.


## transparent

```elm
transparent : Basics.Bool -> Element.Attr decorative msg
```

 Make an element transparent and have it ignore any mouse or touch events, though it will stil take up space.


## width

```elm
width : Element.Length -> Element.Attribute msg
```

 

## wrappedRow

```elm
wrappedRow : List.List (Element.Attribute msg) -> List.List (Element.Element msg) -> Element.Element msg
```

 Same as `row`, but will wrap if it takes up too much horizontal space.


# Element.Background



@docs color, gradient


# Images

@docs image, uncropped, tiled, tiledX, tiledY

**Note** if you want more control over a background image than is provided here, you should try just using a normal `Element.image` with something like `Element.behindContent`.



## color

```elm
color : Element.Color -> Element.Attr decorative msg
```

 

## gradient

```elm
gradient : { angle : Basics.Float, steps : List.List Element.Color } -> Element.Attr decorative msg
```

 A linear gradient.

First you need to specify what direction the gradient is going by providing an angle in radians. `0` is up and `pi` is down.

The colors will be evenly spaced.



## image

```elm
image : String.String -> Element.Attribute msg
```

 Resize the image to fit the containing element while maintaining proportions and cropping the overflow.


## tiled

```elm
tiled : String.String -> Element.Attribute msg
```

 Tile an image in the x and y axes.


## tiledX

```elm
tiledX : String.String -> Element.Attribute msg
```

 Tile an image in the x axis.


## tiledY

```elm
tiledY : String.String -> Element.Attribute msg
```

 Tile an image in the y axis.


## uncropped

```elm
uncropped : String.String -> Element.Attribute msg
```

 A centered background image that keeps its natural proportions, but scales to fit the space.


# Element.Border



@docs color


## Border Widths

@docs width, widthXY, widthEach


## Border Styles

@docs solid, dashed, dotted


## Rounded Corners

@docs rounded, roundEach


## Shadows

@docs glow, innerGlow, shadow, innerShadow



## color

```elm
color : Element.Color -> Element.Attr decorative msg
```

 

## dashed

```elm
dashed : Element.Attribute msg
```

 

## dotted

```elm
dotted : Element.Attribute msg
```

 

## glow

```elm
glow : Element.Color -> Basics.Float -> Element.Attr decorative msg
```

 A simple glow by specifying the color and size.


## innerGlow

```elm
innerGlow : Element.Color -> Basics.Float -> Element.Attr decorative msg
```

 

## innerShadow

```elm
innerShadow : { offset : ( Basics.Float, Basics.Float ), size : Basics.Float, blur : Basics.Float, color : Element.Color } -> Element.Attr decorative msg
```

 

## roundEach

```elm
roundEach : { topLeft : Basics.Int, topRight : Basics.Int, bottomLeft : Basics.Int, bottomRight : Basics.Int } -> Element.Attribute msg
```

 

## rounded

```elm
rounded : Basics.Int -> Element.Attribute msg
```

 Round all corners.


## shadow

```elm
shadow : { offset : ( Basics.Float, Basics.Float ), size : Basics.Float, blur : Basics.Float, color : Element.Color } -> Element.Attr decorative msg
```

 

## solid

```elm
solid : Element.Attribute msg
```

 

## width

```elm
width : Basics.Int -> Element.Attribute msg
```

 

## widthEach

```elm
widthEach : { bottom : Basics.Int, left : Basics.Int, right : Basics.Int, top : Basics.Int } -> Element.Attribute msg
```

 

## widthXY

```elm
widthXY : Basics.Int -> Basics.Int -> Element.Attribute msg
```

 Set horizontal and vertical borders.


# Element.Events




## Mouse Events

@docs onClick, onDoubleClick, onMouseDown, onMouseUp, onMouseEnter, onMouseLeave, onMouseMove


## Focus Events

@docs onFocus, onLoseFocus



## onClick

```elm
onClick : msg -> Element.Attribute msg
```

 

## onDoubleClick

```elm
onDoubleClick : msg -> Element.Attribute msg
```

 

## onFocus

```elm
onFocus : msg -> Element.Attribute msg
```

 

## onLoseFocus

```elm
onLoseFocus : msg -> Element.Attribute msg
```

 

## onMouseDown

```elm
onMouseDown : msg -> Element.Attribute msg
```

 

## onMouseEnter

```elm
onMouseEnter : msg -> Element.Attribute msg
```

 

## onMouseLeave

```elm
onMouseLeave : msg -> Element.Attribute msg
```

 

## onMouseMove

```elm
onMouseMove : msg -> Element.Attribute msg
```

 

## onMouseUp

```elm
onMouseUp : msg -> Element.Attribute msg
```

 

# Element.Font



    import Element
    import Element.Font as Font

    view =
        Element.el
            [ Font.color (Element.rgb 0 0 1)
            , Font.size 18
            , Font.family
                [ Font.typeface "Open Sans"
                , Font.sansSerif
                ]
            ]
            (Element.text "Woohoo, I'm stylish text")

**Note:** `Font.color`, `Font.size`, and `Font.family` are inherited, meaning you can set them at the top of your view and all subsequent nodes will have that value.

**Other Note:** If you're looking for something like `line-height`, it's handled by `Element.spacing` on a `paragraph`.

@docs color, size


## Typefaces

@docs family, Font, typeface, serif, sansSerif, monospace

@docs external


## Alignment and Spacing

@docs alignLeft, alignRight, center, justify, letterSpacing, wordSpacing


## Font Styles

@docs underline, strike, italic, unitalicized


## Font Weight

@docs heavy, extraBold, bold, semiBold, medium, regular, light, extraLight, hairline


## Variants

@docs Variant, variant, variantList, smallCaps, slashedZero, ligatures, ordinal, tabularNumbers, stackedFractions, diagonalFractions, swash, feature, indexed


## Shadows

@docs glow, shadow



## Font

```elm
type alias Font =
    Internal.Model.Font
```

 

## Variant

```elm
type alias Variant =
    Internal.Model.Variant
```

 

## alignLeft

```elm
alignLeft : Element.Attribute msg
```

 Align the font to the left.


## alignRight

```elm
alignRight : Element.Attribute msg
```

 Align the font to the right.


## bold

```elm
bold : Element.Attribute msg
```

 

## center

```elm
center : Element.Attribute msg
```

 Center align the font.


## color

```elm
color : Element.Color -> Element.Attr decorative msg
```

 

## diagonalFractions

```elm
diagonalFractions : Element.Font.Variant
```

 Render fractions


## external

```elm
external : { url : String.String, name : String.String } -> Element.Font.Font
```

 **Note** it's likely that `Font.external` will cause a flash on your page on loading.

To bypass this, import your fonts using a separate stylesheet and just use `Font.typeface`.

It's likely that `Font.external` will be removed or redesigned in the future to avoid the flashing.

`Font.external` can be used to import font files. Let's say you found a neat font on <http://fonts.google.com>:

    import Element
    import Element.Font as Font

    view =
        Element.el
            [ Font.family
                [ Font.external
                    { name = "Roboto"
                    , url = "https://fonts.googleapis.com/css?family=Roboto"
                    }
                , Font.sansSerif
                ]
            ]
            (Element.text "Woohoo, I'm stylish text")



## extraBold

```elm
extraBold : Element.Attribute msg
```

 

## extraLight

```elm
extraLight : Element.Attribute msg
```

 

## family

```elm
family : List.List Element.Font.Font -> Element.Attribute msg
```



    import Element
    import Element.Font as Font

    myElement =
        Element.el
            [ Font.family
                [ Font.typeface "Helvetica"
                , Font.sansSerif
                ]
            ]
            (text "")



## feature

```elm
feature : String.String -> Basics.Bool -> Element.Font.Variant
```

 Set a feature by name and whether it should be on or off.

Feature names are four-letter names as defined in the [OpenType specification](https://docs.microsoft.com/en-us/typography/opentype/spec/featurelist).



## glow

```elm
glow : Element.Color -> Basics.Float -> Element.Attr decorative msg
```

 A glow is just a simplified shadow.


## hairline

```elm
hairline : Element.Attribute msg
```

 

## heavy

```elm
heavy : Element.Attribute msg
```

 

## indexed

```elm
indexed : String.String -> Basics.Int -> Element.Font.Variant
```

 A font variant might have multiple versions within the font.

In these cases we need to specify the index of the version we want.



## italic

```elm
italic : Element.Attribute msg
```

 

## justify

```elm
justify : Element.Attribute msg
```

 

## letterSpacing

```elm
letterSpacing : Basics.Float -> Element.Attribute msg
```

 In `px`.


## ligatures

```elm
ligatures : Element.Font.Variant
```

 

## light

```elm
light : Element.Attribute msg
```

 

## medium

```elm
medium : Element.Attribute msg
```

 

## monospace

```elm
monospace : Element.Font.Font
```

 

## ordinal

```elm
ordinal : Element.Font.Variant
```

 Oridinal markers like `1st` and `2nd` will receive special glyphs.


## regular

```elm
regular : Element.Attribute msg
```

 

## sansSerif

```elm
sansSerif : Element.Font.Font
```

 

## semiBold

```elm
semiBold : Element.Attribute msg
```

 

## serif

```elm
serif : Element.Font.Font
```

 

## shadow

```elm
shadow : { offset : ( Basics.Float, Basics.Float ), blur : Basics.Float, color : Element.Color } -> Element.Attr decorative msg
```

 

## size

```elm
size : Basics.Int -> Element.Attr decorative msg
```

 Font sizes are always given as `px`.


## slashedZero

```elm
slashedZero : Element.Font.Variant
```

 Add a slash when rendering `0`


## smallCaps

```elm
smallCaps : Element.Font.Variant
```

 [Small caps](https://en.wikipedia.org/wiki/Small_caps) are rendered using uppercase glyphs, but at the size of lowercase glyphs.


## stackedFractions

```elm
stackedFractions : Element.Font.Variant
```

 Render fractions with the numerator stacked on top of the denominator.


## strike

```elm
strike : Element.Attribute msg
```

 

## swash

```elm
swash : Basics.Int -> Element.Font.Variant
```

 

## tabularNumbers

```elm
tabularNumbers : Element.Font.Variant
```

 Number figures will each take up the same space, allowing them to be easily aligned, such as in tables.


## typeface

```elm
typeface : String.String -> Element.Font.Font
```

 

## underline

```elm
underline : Element.Attribute msg
```

 

## unitalicized

```elm
unitalicized : Element.Attribute msg
```

 This will reset bold and italic.


## variant

```elm
variant : Element.Font.Variant -> Element.Attribute msg
```

 You can use this to set a single variant on an element itself such as:

    el
        [ Font.variant Font.smallCaps
        ]
        (text "rendered with smallCaps")

**Note** These will **not** stack. If you want multiple variants, you should use `Font.variantList`.



## variantList

```elm
variantList : List.List Element.Font.Variant -> Element.Attribute msg
```

 

## wordSpacing

```elm
wordSpacing : Basics.Float -> Element.Attribute msg
```

 In `px`.


# Element.Input

 Input elements have a lot of constraints!

We want all of our input elements to:

  - _Always be accessible_
  - _Behave intuitively_
  - _Be completely restyleable_

While these three goals may seem pretty obvious, Html and CSS have made it surprisingly difficult to achieve!

And incredibly difficult for developers to remember all the tricks necessary to make things work. If you've every tried to make a `<textarea>` be the height of it's content or restyle a radio button while maintaining accessibility, you may be familiar.

This module is intended to be accessible by default. You shouldn't have to wade through docs, articles, and books to find out [exactly how accessible your html actually is](https://www.powermapper.com/tests/screen-readers/aria/index.html).


# Focus Styling

All Elements can be styled on focus by using [`Element.focusStyle`](Element#focusStyle) to set a global focus style or [`Element.focused`](Element#focused) to set a focus style individually for an element.

@docs focusedOnLoad


# Buttons

@docs button


# Checkboxes

A checkbox requires you to store a `Bool` in your model.

This is also the first input element that has a [`required label`](#Label).

    import Element exposing (text)
    import Element.Input as Input

    type Msg
        = GuacamoleChecked Bool

    view model =
        Input.checkbox []
            { onChange = GuacamoleChecked
            , icon = Input.defaultCheckbox
            , checked = model.guacamole
            , label =
                Input.labelRight []
                    (text "Do you want Guacamole?")
            }

@docs checkbox, defaultCheckbox


# Text

@docs text, multiline

@docs Placeholder, placeholder


## Text with autofill

If we want to play nicely with a browser's ability to autofill a form, we need to be able to give it a hint about what we're expecting.

The following inputs are very similar to `Input.text`, but they give the browser a hint to allow autofill to work correctly.

@docs username, newPassword, currentPassword, email, search, spellChecked


# Sliders

A slider is great for choosing between a range of numerical values.

  - **thumb** - The icon that you click and drag to change the value.
  - **track** - The line behind the thumb denoting where you can slide to.

@docs slider, Thumb, thumb, defaultThumb


# Radio Selection

The fact that we still call this a radio selection is fascinating. I can't remember the last time I actually used an honest-to-goodness button on a radio. Chalk it up along with the floppy disk save icon or the word [Dashboard](https://en.wikipedia.org/wiki/Dashboard).

Perhaps a better name would be `Input.chooseOne`, because this allows you to select one of a set of options!

Nevertheless, here we are. Here's how you put one together

    Input.radio
        [ padding 10
        , spacing 20
        ]
        { onChange = ChooseLunch
        , selected = Just model.lunch
        , label = Input.labelAbove [] (text "Lunch")
        , options =
            [ Input.option Burrito (text "Burrito")
            , Input.option Taco (text "Taco!")
            , Input.option Gyro (text "Gyro")
            ]
        }

**Note** we're using `Input.option`, which will render the default radio icon you're probably used to. If you want compeltely custom styling, use `Input.optionWith`!

@docs radio, radioRow, Option, option, optionWith, OptionState


# Labels

Every input has a required `Label`.

@docs Label, labelAbove, labelBelow, labelLeft, labelRight, labelHidden


# Form Elements

You might be wondering where something like `<form>` is.

What I've found is that most people who want `<form>` usually want it for the [implicit submission behavior](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#implicit-submission) or to be clearer, they want to do something when the `Enter` key is pressed.

Instead of implicit submission behavior, [try making an `onEnter` event handler like in this Ellie Example](https://ellie-app.com/5X6jBKtxzdpa1). Then everything is explicit!

And no one has to look up obtuse html documentation to understand the behavior of their code :).


# File Inputs

Presently, elm-ui does not expose a replacement for `<input type="file">`; in the meantime, an `Input.button` and `elm/file`'s `File.Select` may meet your needs.


# Disabling Inputs

You also might be wondering how to disable an input.

Disabled inputs can be a little problematic for user experience, and doubly so for accessibility. This is because it's now your priority to inform the user _why_ some field is disabled.

If an input is truly disabled, meaning it's not focusable or doesn't send off a `Msg`, you actually lose your ability to help the user out! For those wary about accessibility [this is a big problem.](https://ux.stackexchange.com/questions/103239/should-disabled-elements-be-focusable-for-accessibility-purposes)

Here are some alternatives to think about that don't involve explicitly disabling an input.

**Disabled Buttons** - Change the `Msg` it fires, the text that is rendered, and optionally set a `Region.description` which will be available to screen readers.

    import Element.Input as Input
    import Element.Region as Region

    myButton ready =
        if ready then
            Input.button
                [ Background.color blue
                ]
                { onPress =
                    Just SaveButtonPressed
                , label =
                    text "Save blog post"
                }

        else
            Input.button
                [ Background.color grey
                , Region.description
                    "A publish date is required before saving a blogpost."
                ]
                { onPress =
                    Just DisabledSaveButtonPressed
                , label =
                    text "Save Blog "
                }

Consider showing a hint if `DisabledSaveButtonPressed` is sent.

For other inputs such as `Input.text`, consider simply rendering it in a normal `paragraph` or `el` if it's not editable.

Alternatively, see if it's reasonable to _not_ display an input if you'd normally disable it. Is there an option where it's only visible when it's editable?



## Label

```elm
type Label msg
    = 
```

 

## Option

```elm
type Option value msg
    = 
```

 

## OptionState

```elm
type OptionState
    = Idle
    | Focused
    | Selected
```

 

## Placeholder

```elm
type Placeholder msg
    = 
```

 

## Thumb

```elm
type Thumb
    = 
```

 

## button

```elm
button : List.List (Element.Attribute msg) -> { onPress : Maybe.Maybe msg, label : Element.Element msg } -> Element.Element msg
```

 A standard button.

The `onPress` handler will be fired either `onClick` or when the element is focused and the `Enter` key has been pressed.

    import Element exposing (rgb255, text)
    import Element.Background as Background
    import Element.Input as Input

    blue =
        Element.rgb255 238 238 238

    myButton =
        Input.button
            [ Background.color blue
            , Element.focused
                [ Background.color purple ]
            ]
            { onPress = Just ClickMsg
            , label = text "My Button"
            }

**Note** If you have an icon button but want it to be accessible, consider adding a [`Region.description`](Element-Region#description), which will describe the button to screen readers.



## checkbox

```elm
checkbox : List.List (Element.Attribute msg) -> { onChange : Basics.Bool -> msg, icon : Basics.Bool -> Element.Element msg, checked : Basics.Bool, label : Element.Input.Label msg } -> Element.Element msg
```



  - **onChange** - The `Msg` to send.
  - **icon** - The checkbox icon to show. This can be whatever you'd like, but `Input.defaultCheckbox` is included to get you started.
  - **checked** - The current checked state.
  - **label** - The [`Label`](#Label) for this checkbox



## currentPassword

```elm
currentPassword : List.List (Element.Attribute msg) -> { onChange : String.String -> msg, text : String.String, placeholder : Maybe.Maybe (Element.Input.Placeholder msg), label : Element.Input.Label msg, show : Basics.Bool } -> Element.Element msg
```

 

## defaultCheckbox

```elm
defaultCheckbox : Basics.Bool -> Element.Element msg
```

 The blue default checked box icon.

You'll likely want to make your own checkbox at some point that fits your design.



## defaultThumb

```elm
defaultThumb : Element.Input.Thumb
```

 

## email

```elm
email : List.List (Element.Attribute msg) -> { onChange : String.String -> msg, text : String.String, placeholder : Maybe.Maybe (Element.Input.Placeholder msg), label : Element.Input.Label msg } -> Element.Element msg
```

 

## focusedOnLoad

```elm
focusedOnLoad : Element.Attribute msg
```

 Attach this attribute to any `Input` that you would like to be automatically focused when the page loads.

You should only have a maximum of one per page.



## labelAbove

```elm
labelAbove : List.List (Element.Attribute msg) -> Element.Element msg -> Element.Input.Label msg
```

 

## labelBelow

```elm
labelBelow : List.List (Element.Attribute msg) -> Element.Element msg -> Element.Input.Label msg
```

 

## labelHidden

```elm
labelHidden : String.String -> Element.Input.Label msg
```

 Sometimes you may need to have a label which is not visible, but is still accessible to screen readers.

Seriously consider a visible label before using this.

The situations where a hidden label makes sense:

  - A searchbar with a `search` button right next to it.
  - A `table` of inputs where the header gives the label.

Basically, a hidden label works when there are other contextual clues that sighted people can pick up on.



## labelLeft

```elm
labelLeft : List.List (Element.Attribute msg) -> Element.Element msg -> Element.Input.Label msg
```

 

## labelRight

```elm
labelRight : List.List (Element.Attribute msg) -> Element.Element msg -> Element.Input.Label msg
```

 

## multiline

```elm
multiline : List.List (Element.Attribute msg) -> { onChange : String.String -> msg, text : String.String, placeholder : Maybe.Maybe (Element.Input.Placeholder msg), label : Element.Input.Label msg, spellcheck : Basics.Bool } -> Element.Element msg
```

 A multiline text input.

By default it will have a minimum height of one line and resize based on it's contents.



## newPassword

```elm
newPassword : List.List (Element.Attribute msg) -> { onChange : String.String -> msg, text : String.String, placeholder : Maybe.Maybe (Element.Input.Placeholder msg), label : Element.Input.Label msg, show : Basics.Bool } -> Element.Element msg
```

 A password input that allows the browser to autofill.

It's `newPassword` instead of just `password` because it gives the browser a hint on what type of password input it is.

A password takes all the arguments a normal `Input.text` would, and also **show**, which will remove the password mask (e.g. `****` vs `pass1234`)



## option

```elm
option : value -> Element.Element msg -> Element.Input.Option value msg
```

 Add a choice to your radio element. This will be rendered with the default radio icon.


## optionWith

```elm
optionWith : value -> (Element.Input.OptionState -> Element.Element msg) -> Element.Input.Option value msg
```

 Customize exactly what your radio option should look like in different states.


## placeholder

```elm
placeholder : List.List (Element.Attribute msg) -> Element.Element msg -> Element.Input.Placeholder msg
```

 

## radio

```elm
radio : List.List (Element.Attribute msg) -> { onChange : option -> msg, options : List.List (Element.Input.Option option msg), selected : Maybe.Maybe option, label : Element.Input.Label msg } -> Element.Element msg
```

 

## radioRow

```elm
radioRow : List.List (Element.Attribute msg) -> { onChange : option -> msg, options : List.List (Element.Input.Option option msg), selected : Maybe.Maybe option, label : Element.Input.Label msg } -> Element.Element msg
```

 Same as radio, but displayed as a row


## search

```elm
search : List.List (Element.Attribute msg) -> { onChange : String.String -> msg, text : String.String, placeholder : Maybe.Maybe (Element.Input.Placeholder msg), label : Element.Input.Label msg } -> Element.Element msg
```

 

## slider

```elm
slider : List.List (Element.Attribute msg) -> { onChange : Basics.Float -> msg, label : Element.Input.Label msg, min : Basics.Float, max : Basics.Float, value : Basics.Float, thumb : Element.Input.Thumb, step : Maybe.Maybe Basics.Float } -> Element.Element msg
```

 A slider input, good for capturing float values.

    Input.slider
        [ Element.height (Element.px 30)

        -- Here is where we're creating/styling the "track"
        , Element.behindContent
            (Element.el
                [ Element.width Element.fill
                , Element.height (Element.px 2)
                , Element.centerY
                , Background.color grey
                , Border.rounded 2
                ]
                Element.none
            )
        ]
        { onChange = AdjustValue
        , label =
            Input.labelAbove []
                (text "My Slider Value")
        , min = 0
        , max = 75
        , step = Nothing
        , value = model.sliderValue
        , thumb =
            Input.defaultThumb
        }

`Element.behindContent` is used to render the track of the slider. Without it, no track would be rendered. The `thumb` is the icon that you can move around.

The slider can be vertical or horizontal depending on the width/height of the slider.

  - `height fill` and `width (px someWidth)` will cause the slider to be vertical.
  - `height (px someHeight)` and `width (px someWidth)` where `someHeight` > `someWidth` will also do it.
  - otherwise, the slider will be horizontal.

**Note** If you want a slider for an `Int` value:

  - set `step` to be `Just 1`, or some other whole value
  - `value = toFloat model.myInt`
  - And finally, round the value before making a message `onChange = round >> AdjustValue`



## spellChecked

```elm
spellChecked : List.List (Element.Attribute msg) -> { onChange : String.String -> msg, text : String.String, placeholder : Maybe.Maybe (Element.Input.Placeholder msg), label : Element.Input.Label msg } -> Element.Element msg
```

 If spell checking is available, this input will be spellchecked.


## text

```elm
text : List.List (Element.Attribute msg) -> { onChange : String.String -> msg, text : String.String, placeholder : Maybe.Maybe (Element.Input.Placeholder msg), label : Element.Input.Label msg } -> Element.Element msg
```

 

## thumb

```elm
thumb : List.List (Element.Attribute Basics.Never) -> Element.Input.Thumb
```

 

## username

```elm
username : List.List (Element.Attribute msg) -> { onChange : String.String -> msg, text : String.String, placeholder : Maybe.Maybe (Element.Input.Placeholder msg), label : Element.Input.Label msg } -> Element.Element msg
```

 

# Element.Keyed

 Notes from the `Html.Keyed` on how keyed works:

---

A keyed node helps optimize cases where children are getting added, moved, removed, etc. Common examples include:

  - The user can delete items from a list.
  - The user can create new items in a list.
  - You can sort a list based on name or date or whatever.

When you use a keyed node, every child is paired with a string identifier. This makes it possible for the underlying diffing algorithm to reuse nodes more efficiently.

This means if a key is changed between renders, then the diffing step will be skipped and the node will be forced to rerender.

---

@docs el, column, row



## column

```elm
column : List.List (Element.Attribute msg) -> List.List ( String.String, Element.Element msg ) -> Element.Element msg
```

 

## el

```elm
el : List.List (Element.Attribute msg) -> ( String.String, Element.Element msg ) -> Element.Element msg
```

 

## row

```elm
row : List.List (Element.Attribute msg) -> List.List ( String.String, Element.Element msg ) -> Element.Element msg
```

 

# Element.Lazy

 Same as `Html.lazy`. In case you're unfamiliar, here's a note from the `Html` library!

---

Since all Elm functions are pure we have a guarantee that the same input
will always result in the same output. This module gives us tools to be lazy
about building `Html` that utilize this fact.

Rather than immediately applying functions to their arguments, the `lazy`
functions just bundle the function and arguments up for later. When diffing
the old and new virtual DOM, it checks to see if all the arguments are equal
by reference. If so, it skips calling the function!

This is a really cheap test and often makes things a lot faster, but definitely
benchmark to be sure!

---

@docs lazy, lazy2, lazy3, lazy4, lazy5



## lazy

```elm
lazy : (a -> Internal.Model.Element msg) -> a -> Internal.Model.Element msg
```

 

## lazy2

```elm
lazy2 : (a -> b -> Internal.Model.Element msg) -> a -> b -> Internal.Model.Element msg
```

 

## lazy3

```elm
lazy3 : (a -> b -> c -> Internal.Model.Element msg) -> a -> b -> c -> Internal.Model.Element msg
```

 

## lazy4

```elm
lazy4 : (a -> b -> c -> d -> Internal.Model.Element msg) -> a -> b -> c -> d -> Internal.Model.Element msg
```

 

## lazy5

```elm
lazy5 : (a -> b -> c -> d -> e -> Internal.Model.Element msg) -> a -> b -> c -> d -> e -> Internal.Model.Element msg
```

 

# Element.Region

 This module is meant to make accessibility easy!

These are sign posts that accessibility software like screen readers can use to navigate your app.

All you have to do is add them to elements in your app where you see fit.

Here's an example of annotating your navigation region:

    import Element.Region as Region

    myNavigation =
        Element.row [ Region.navigation ]
            [-- ..your navigation links
            ]

@docs mainContent, navigation, heading, aside, footer

@docs description

@docs announce, announceUrgently



## announce

```elm
announce : Element.Attribute msg
```

 Screen readers will announce when changes to this element are made.


## announceUrgently

```elm
announceUrgently : Element.Attribute msg
```

 Screen readers will announce changes to this element and potentially interrupt any other announcement.


## aside

```elm
aside : Element.Attribute msg
```

 

## description

```elm
description : String.String -> Element.Attribute msg
```

 Adds an `aria-label`, which is used by accessibility software to identity otherwise unlabeled elements.

A common use for this would be to label buttons that only have an icon.



## footer

```elm
footer : Element.Attribute msg
```

 

## heading

```elm
heading : Basics.Int -> Element.Attribute msg
```

 This will mark an element as `h1`, `h2`, etc where possible.

Though it's also smart enough to not conflict with existing nodes.

So, this code

    link [ Region.heading 1 ]
        { url = "http://fruits.com"
        , label = text "Best site ever"
        }

will generate

    <a href="http://fruits.com">
        <h1>Best site ever</h1>
    </a>



## mainContent

```elm
mainContent : Element.Attribute msg
```

 

## navigation

```elm
navigation : Element.Attribute msg
```

 
