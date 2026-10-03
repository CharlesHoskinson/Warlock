# official/packages/elm/html/1.0.1/docs.json
Source: https://package.elm-lang.org/packages/elm/html/1.0.1/docs.json

# Html

 This file is organized roughly in order of popularity. The tags which you'd
expect to use frequently will be closer to the top.

# Primitives
@docs Html, Attribute, text, node, map

# Tags

## Headers
@docs h1, h2, h3, h4, h5, h6

## Grouping Content
@docs div, p, hr, pre, blockquote

## Text
@docs span, a, code, em, strong, i, b, u, sub, sup, br

## Lists
@docs ol, ul, li, dl, dt, dd

## Embedded Content
@docs img, iframe, canvas, math

## Inputs
@docs form, input, textarea, button, select, option

## Sections
@docs section, nav, article, aside, header, footer, address, main_

## Figures
@docs figure, figcaption

## Tables
@docs table, caption, colgroup, col, tbody, thead, tfoot, tr, td, th


## Less Common Elements

### Less Common Inputs
@docs fieldset, legend, label, datalist, optgroup, output, progress, meter

### Audio and Video
@docs audio, video, source, track

### Embedded Objects
@docs embed, object, param

### Text Edits
@docs ins, del

### Semantic Text
@docs small, cite, dfn, abbr, time, var, samp, kbd, s, q

### Less Common Text Tags
@docs mark, ruby, rt, rp, bdi, bdo, wbr

## Interactive Elements
@docs details, summary, menuitem, menu



## Attribute

```elm
type alias Attribute msg =
    VirtualDom.Attribute msg
```

 Set attributes on your `Html`. Learn more in the
[`Html.Attributes`](Html-Attributes) module.


## Html

```elm
type alias Html msg =
    VirtualDom.Node msg
```

 The core building block used to build up HTML. Here we create an `Html`
value with no attributes and one child:

    hello : Html msg
    hello =
      div [] [ text "Hello!" ]


## a

```elm
a : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a hyperlink, linking to another resource. 

## abbr

```elm
abbr : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents an abbreviation or an acronym; the expansion of the
abbreviation can be represented in the title attribute.


## address

```elm
address : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines a section containing contact information. 

## article

```elm
article : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines self-contained content that could exist independently of the rest
of the content.


## aside

```elm
aside : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines some content loosely related to the page content. If it is removed,
the remaining content still makes sense.


## audio

```elm
audio : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a sound or audio stream. 

## b

```elm
b : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a text which to which attention is drawn for utilitarian
purposes. It doesn't convey extra importance and doesn't imply an alternate
voice.


## bdi

```elm
bdi : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents text that must be isolated from its surrounding for
bidirectional text formatting. It allows embedding a span of text with a
different, or unknown, directionality.


## bdo

```elm
bdo : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents the directionality of its children, in order to explicitly
override the Unicode bidirectional algorithm.


## blockquote

```elm
blockquote : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a content that is quoted from another source. 

## br

```elm
br : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a line break. 

## button

```elm
button : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a button. 

## canvas

```elm
canvas : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a bitmap area for graphics rendering. 

## caption

```elm
caption : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents the title of a table. 

## cite

```elm
cite : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents the title of a work. 

## code

```elm
code : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents computer code. 

## col

```elm
col : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a column of a table. 

## colgroup

```elm
colgroup : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a set of one or more columns of a table. 

## datalist

```elm
datalist : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a set of predefined options for other controls. 

## dd

```elm
dd : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents the definition of the terms immediately listed before it. 

## del

```elm
del : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines a removal from the document. 

## details

```elm
details : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a widget from which the user can obtain additional information
or controls.


## dfn

```elm
dfn : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a term whose definition is contained in its nearest ancestor
content.


## div

```elm
div : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a generic container with no special meaning. 

## dl

```elm
dl : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines a definition list, that is, a list of terms and their associated
definitions.


## dt

```elm
dt : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a term defined by the next `dd`. 

## em

```elm
em : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents emphasized text, like a stress accent. 

## embed

```elm
embed : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a integration point for an external, often non-HTML,
application or interactive content.


## fieldset

```elm
fieldset : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a set of controls. 

## figcaption

```elm
figcaption : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents the legend of a figure. 

## figure

```elm
figure : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a figure illustrated as part of the document. 

## footer

```elm
footer : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines the footer for a page or section. It often contains a copyright
notice, some links to legal information, or addresses to give feedback.


## form

```elm
form : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a form, consisting of controls, that can be submitted to a
server for processing.


## h1

```elm
h1 : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```



## h2

```elm
h2 : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```



## h3

```elm
h3 : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```



## h4

```elm
h4 : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```



## h5

```elm
h5 : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```



## h6

```elm
h6 : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```



## header

```elm
header : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines the header of a page or section. It often contains a logo, the
title of the web site, and a navigational table of content.


## hr

```elm
hr : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a thematic break between paragraphs of a section or article or
any longer content.


## i

```elm
i : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents some text in an alternate voice or mood, or at least of
different quality, such as a taxonomic designation, a technical term, an
idiomatic phrase, a thought, or a ship name.


## iframe

```elm
iframe : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Embedded an HTML document. 

## img

```elm
img : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents an image. 

## input

```elm
input : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a typed data field allowing the user to edit the data. 

## ins

```elm
ins : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines an addition to the document. 

## kbd

```elm
kbd : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents user input, often from the keyboard, but not necessarily; it
may represent other input, like transcribed voice commands.


## label

```elm
label : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents the caption of a form control. 

## legend

```elm
legend : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents the caption for a `fieldset`. 

## li

```elm
li : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines a item of an enumeration list. 

## main_

```elm
main_ : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines the main or important content in the document. There is only one
`main` element in the document.


## map

```elm
map : (a -> msg) -> Html.Html a -> Html.Html msg
```

 Transform the messages produced by some `Html`. In the following example,
we have `viewButton` that produces `()` messages, and we transform those values
into `Msg` values in `view`.

    type Msg = Left | Right

    view : model -> Html Msg
    view model =
      div []
        [ map (\_ -> Left) (viewButton "Left")
        , map (\_ -> Right) (viewButton "Right")
        ]

    viewButton : String -> Html ()
    viewButton name =
      button [ onClick () ] [ text name ]

If you are growing your project as recommended in [the official
guide](https://guide.elm-lang.org/), this should not come in handy in most
projects. Usually it is easier to just pass things in as arguments.

**Note:** Some folks have tried to use this to make “components” in their
projects, but they run into the fact that components are objects. Both are
local mutable state with methods. Elm is not an object-oriented language, so
you run into all sorts of friction if you try to use it like one. I definitely
recommend against going down that path! Instead, make the simplest function
possible and repeat.


## mark

```elm
mark : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents text highlighted for reference purposes, that is for its
relevance in another context.


## math

```elm
math : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines a mathematical formula. 

## menu

```elm
menu : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a list of commands. 

## menuitem

```elm
menuitem : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a command that the user can invoke. 

## meter

```elm
meter : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a scalar measurement (or a fractional value), within a known
range.


## nav

```elm
nav : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines a section that contains only navigation links.


## node

```elm
node : String.String -> List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 General way to create HTML nodes. It is used to define all of the helper
functions in this library.

    div : List (Attribute msg) -> List (Html msg) -> Html msg
    div attributes children =
        node "div" attributes children

You can use this to create custom nodes if you need to create something that
is not covered by the helper functions in this library.


## object

```elm
object : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents an external resource, which is treated as an image, an HTML
sub-document, or an external resource to be processed by a plug-in.


## ol

```elm
ol : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines an ordered list of items. 

## optgroup

```elm
optgroup : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a set of options, logically grouped. 

## option

```elm
option : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents an option in a `select` element or a suggestion of a `datalist`
element.


## output

```elm
output : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents the result of a calculation. 

## p

```elm
p : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines a portion that should be displayed as a paragraph. 

## param

```elm
param : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines parameters for use by plug-ins invoked by `object` elements. 

## pre

```elm
pre : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Indicates that its content is preformatted and that this format must be
preserved.


## progress

```elm
progress : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents the completion progress of a task. 

## q

```elm
q : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents an inline quotation. 

## rp

```elm
rp : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents parenthesis around a ruby annotation, used to display the
annotation in an alternate way by browsers not supporting the standard display
for annotations.


## rt

```elm
rt : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents the text of a ruby annotation. 

## ruby

```elm
ruby : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents content to be marked with ruby annotations, short runs of text
presented alongside the text. This is often used in conjunction with East Asian
language where the annotations act as a guide for pronunciation, like the
Japanese furigana.


## s

```elm
s : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents content that is no longer accurate or relevant. 

## samp

```elm
samp : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents the output of a program or a computer. 

## section

```elm
section : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines a section in a document.


## select

```elm
select : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a control allowing selection among a set of options. 

## small

```elm
small : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a side comment, that is, text like a disclaimer or a
copyright, which is not essential to the comprehension of the document.


## source

```elm
source : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Allows authors to specify alternative media resources for media elements
like `video` or `audio`.


## span

```elm
span : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents text with no specific meaning. This has to be used when no other
text-semantic element conveys an adequate meaning, which, in this case, is
often brought by global attributes like `class`, `lang`, or `dir`.


## strong

```elm
strong : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents especially important text. 

## sub

```elm
sub : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represent a subscript. 

## summary

```elm
summary : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a summary, caption, or legend for a given `details`. 

## sup

```elm
sup : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represent a superscript. 

## table

```elm
table : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents data with more than one dimension. 

## tbody

```elm
tbody : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents the block of rows that describes the concrete data of a table.


## td

```elm
td : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a data cell in a table. 

## text

```elm
text : String.String -> Html.Html msg
```

 Just put plain text in the DOM. It will escape the string so that it appears
exactly as you specify.

    text "Hello World!"


## textarea

```elm
textarea : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a multiline text edit control. 

## tfoot

```elm
tfoot : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents the block of rows that describes the column summaries of a table.


## th

```elm
th : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a header cell in a table. 

## thead

```elm
thead : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents the block of rows that describes the column labels of a table.


## time

```elm
time : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a date and time value; the machine-readable equivalent can be
represented in the datetime attribute.


## tr

```elm
tr : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a row of cells in a table. 

## track

```elm
track : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Allows authors to specify timed text track for media elements like `video`
or `audio`.


## u

```elm
u : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a non-textual annotation for which the conventional
presentation is underlining, such labeling the text as being misspelt or
labeling a proper name in Chinese text.


## ul

```elm
ul : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Defines an unordered list of items. 

## var

```elm
var : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a variable. Specific cases where it should be used include an
actual mathematical expression or programming context, an identifier
representing a constant, a symbol identifying a physical quantity, a function
parameter, or a mere placeholder in prose.


## video

```elm
video : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a video, the associated audio and captions, and controls. 

## wbr

```elm
wbr : List.List (Html.Attribute msg) -> List.List (Html.Html msg) -> Html.Html msg
```

 Represents a line break opportunity, that is a suggested point for
wrapping text in order to improve readability of text split on several lines.


# Html.Attributes

 Helper functions for HTML attributes. They are organized roughly by
category. Each attribute is labeled with the HTML tags it can be used with, so
just search the page for `video` if you want video stuff.

# Primitives
@docs style, property, attribute, map

# Super Common Attributes
@docs class, classList, id, title, hidden

# Inputs
@docs type_, value, checked, placeholder, selected

## Input Helpers
@docs accept, acceptCharset, action, autocomplete, autofocus,
    disabled, enctype, list, maxlength, minlength, method, multiple,
    name, novalidate, pattern, readonly, required, size, for, form

## Input Ranges
@docs max, min, step

## Input Text Areas
@docs cols, rows, wrap


# Links and Areas
@docs href, target, download, hreflang, media, ping, rel

## Maps
@docs ismap, usemap, shape, coords


# Embedded Content
@docs src, height, width, alt

## Audio and Video
@docs autoplay, controls, loop, preload, poster, default, kind, srclang

## iframes
@docs sandbox

# Ordered Lists
@docs reversed, start

# Tables
@docs align, colspan, rowspan, headers, scope

# Less Common Global Attributes
Attributes that can be attached to any HTML tag but are less commonly used.
@docs accesskey, contenteditable, contextmenu, dir, draggable, dropzone,
      itemprop, lang, spellcheck, tabindex

# Miscellaneous
@docs cite, datetime, pubdate, manifest

# Deprecated
@docs srcdoc



## accept

```elm
accept : String.String -> Html.Attribute msg
```

 List of types the server accepts, typically a file type.
For `form` and `input`.


## acceptCharset

```elm
acceptCharset : String.String -> Html.Attribute msg
```

 List of supported charsets in a `form`.


## accesskey

```elm
accesskey : Char.Char -> Html.Attribute msg
```

 Defines a keyboard shortcut to activate or add focus to the element. 

## action

```elm
action : String.String -> Html.Attribute msg
```

 The URI of a program that processes the information submitted via a `form`.


## align

```elm
align : String.String -> Html.Attribute msg
```

 Specifies the horizontal alignment of a `caption`, `col`, `colgroup`,
`hr`, `iframe`, `img`, `table`, `tbody`,  `td`,  `tfoot`, `th`, `thead`, or
`tr`.


## alt

```elm
alt : String.String -> Html.Attribute msg
```

 Alternative text in case an image can't be displayed. Works with `img`,
`area`, and `input`.


## attribute

```elm
attribute : String.String -> String.String -> Html.Attribute msg
```

 Create *attributes*, like saying `domNode.setAttribute('class', 'greeting')`
in JavaScript.

    class : String -> Attribute msg
    class name =
      attribute "class" name

Read more about the difference between properties and attributes [here][].

[here]: https://github.com/elm/html/blob/master/properties-vs-attributes.md


## autocomplete

```elm
autocomplete : Basics.Bool -> Html.Attribute msg
```

 Indicates whether a `form` or an `input` can have their values automatically
completed by the browser.


## autofocus

```elm
autofocus : Basics.Bool -> Html.Attribute msg
```

 The element should be automatically focused after the page loaded.
For `button`, `input`, `select`, and `textarea`.


## autoplay

```elm
autoplay : Basics.Bool -> Html.Attribute msg
```

 The `audio` or `video` should play as soon as possible. 

## checked

```elm
checked : Basics.Bool -> Html.Attribute msg
```

 Indicates whether an `input` of type checkbox is checked. 

## cite

```elm
cite : String.String -> Html.Attribute msg
```

 Contains a URI which points to the source of the quote or change in a
`blockquote`, `del`, `ins`, or `q`.


## class

```elm
class : String.String -> Html.Attribute msg
```

 Often used with CSS to style elements with common properties.

**Note:** You can have as many `class` and `classList` attributes as you want.
They all get applied, so if you say `[ class "notice", class "notice-seen" ]`
you will get both classes!


## classList

```elm
classList : List.List ( String.String, Basics.Bool ) -> Html.Attribute msg
```

 This function makes it easier to build a space-separated class attribute.
Each class can easily be added and removed depending on the boolean value it
is paired with. For example, maybe we want a way to view notices:

    viewNotice : Notice -> Html msg
    viewNotice notice =
      div
        [ classList
            [ ("notice", True)
            , ("notice-important", notice.isImportant)
            , ("notice-seen", notice.isSeen)
            ]
        ]
        [ text notice.content ]

**Note:** You can have as many `class` and `classList` attributes as you want.
They all get applied, so if you say `[ class "notice", class "notice-seen" ]`
you will get both classes!


## cols

```elm
cols : Basics.Int -> Html.Attribute msg
```

 Defines the number of columns in a `textarea`. 

## colspan

```elm
colspan : Basics.Int -> Html.Attribute msg
```

 The colspan attribute defines the number of columns a cell should span.
For `td` and `th`.


## contenteditable

```elm
contenteditable : Basics.Bool -> Html.Attribute msg
```

 Indicates whether the element's content is editable. 

## contextmenu

```elm
contextmenu : String.String -> Html.Attribute msg
```

 Defines the ID of a `menu` element which will serve as the element's
context menu.


## controls

```elm
controls : Basics.Bool -> Html.Attribute msg
```

 Indicates whether the browser should show playback controls for the `audio`
or `video`.


## coords

```elm
coords : String.String -> Html.Attribute msg
```

 A set of values specifying the coordinates of the hot-spot region in an
`area`. Needs to be paired with a `shape` attribute to be meaningful.


## datetime

```elm
datetime : String.String -> Html.Attribute msg
```

 Indicates the date and time associated with the element.
For `del`, `ins`, `time`.


## default

```elm
default : Basics.Bool -> Html.Attribute msg
```

 Indicates that the `track` should be enabled unless the user's preferences
indicate something different.


## dir

```elm
dir : String.String -> Html.Attribute msg
```

 Defines the text direction. Allowed values are ltr (Left-To-Right) or rtl
(Right-To-Left).


## disabled

```elm
disabled : Basics.Bool -> Html.Attribute msg
```

 Indicates whether the user can interact with a `button`, `fieldset`,
`input`, `optgroup`, `option`, `select` or `textarea`.


## download

```elm
download : String.String -> Html.Attribute msg
```

 Indicates that clicking an `a` and `area` will download the resource
directly. The `String` argument determins the name of the downloaded file.
Say the file you are serving is named `hats.json`.

    download ""               -- hats.json
    download "my-hats.json"   -- my-hats.json
    download "snakes.json"    -- snakes.json

The empty `String` says to just name it whatever it was called on the server.


## draggable

```elm
draggable : String.String -> Html.Attribute msg
```

 Defines whether the element can be dragged. 

## dropzone

```elm
dropzone : String.String -> Html.Attribute msg
```

 Indicates that the element accept the dropping of content on it. 

## enctype

```elm
enctype : String.String -> Html.Attribute msg
```

 How `form` data should be encoded when submitted with the POST method.
Options include: application/x-www-form-urlencoded, multipart/form-data, and
text/plain.


## for

```elm
for : String.String -> Html.Attribute msg
```

 The element ID described by this `label` or the element IDs that are used
for an `output`.


## form

```elm
form : String.String -> Html.Attribute msg
```

 Indicates the element ID of the `form` that owns this particular `button`,
`fieldset`, `input`, `label`, `meter`, `object`, `output`, `progress`,
`select`, or `textarea`.


## headers

```elm
headers : String.String -> Html.Attribute msg
```

 A space separated list of element IDs indicating which `th` elements are
headers for this cell. For `td` and `th`.


## height

```elm
height : Basics.Int -> Html.Attribute msg
```

 Declare the height of a `canvas`, `embed`, `iframe`, `img`, `input`,
`object`, or `video`.


## hidden

```elm
hidden : Basics.Bool -> Html.Attribute msg
```

 Indicates the relevance of an element. 

## href

```elm
href : String.String -> Html.Attribute msg
```

 The URL of a linked resource, such as `a`, `area`, `base`, or `link`. 

## hreflang

```elm
hreflang : String.String -> Html.Attribute msg
```

 Two-letter language code of the linked resource of an `a`, `area`, or `link`.


## id

```elm
id : String.String -> Html.Attribute msg
```

 Often used with CSS to style a specific element. The value of this
attribute must be unique.


## ismap

```elm
ismap : Basics.Bool -> Html.Attribute msg
```

 When an `img` is a descendant of an `a` tag, the `ismap` attribute
indicates that the click location should be added to the parent `a`'s href as
a query string.


## itemprop

```elm
itemprop : String.String -> Html.Attribute msg
```



## kind

```elm
kind : String.String -> Html.Attribute msg
```

 Specifies the kind of text `track`. 

## lang

```elm
lang : String.String -> Html.Attribute msg
```

 Defines the language used in the element. 

## list

```elm
list : String.String -> Html.Attribute msg
```

 Associates an `input` with a `datalist` tag. The datalist gives some
pre-defined options to suggest to the user as they interact with an input.
The value of the list attribute must match the id of a `datalist` node.
For `input`.


## loop

```elm
loop : Basics.Bool -> Html.Attribute msg
```

 Indicates whether the `audio` or `video` should start playing from the
start when it's finished.


## manifest

```elm
manifest : String.String -> Html.Attribute msg
```

 Specifies the URL of the cache manifest for an `html` tag. 

## map

```elm
map : (a -> msg) -> Html.Attribute a -> Html.Attribute msg
```

 Transform the messages produced by an `Attribute`.


## max

```elm
max : String.String -> Html.Attribute msg
```

 Indicates the maximum value allowed. When using an input of type number or
date, the max value must be a number or date. For `input`, `meter`, and `progress`.


## maxlength

```elm
maxlength : Basics.Int -> Html.Attribute msg
```

 Defines the maximum number of characters allowed in an `input` or
`textarea`.


## media

```elm
media : String.String -> Html.Attribute msg
```

 Specifies a hint of the target media of a `a`, `area`, `link`, `source`,
or `style`.


## method

```elm
method : String.String -> Html.Attribute msg
```

 Defines which HTTP method to use when submitting a `form`. Can be GET
(default) or POST.


## min

```elm
min : String.String -> Html.Attribute msg
```

 Indicates the minimum value allowed. When using an input of type number or
date, the min value must be a number or date. For `input` and `meter`.


## minlength

```elm
minlength : Basics.Int -> Html.Attribute msg
```

 Defines the minimum number of characters allowed in an `input` or
`textarea`.


## multiple

```elm
multiple : Basics.Bool -> Html.Attribute msg
```

 Indicates whether multiple values can be entered in an `input` of type
email or file. Can also indicate that you can `select` many options.


## name

```elm
name : String.String -> Html.Attribute msg
```

 Name of the element. For example used by the server to identify the fields
in form submits. For `button`, `form`, `fieldset`, `iframe`, `input`,
`object`, `output`, `select`, `textarea`, `map`, `meta`, and `param`.


## novalidate

```elm
novalidate : Basics.Bool -> Html.Attribute msg
```

 This attribute indicates that a `form` shouldn't be validated when
submitted.


## pattern

```elm
pattern : String.String -> Html.Attribute msg
```

 Defines a regular expression which an `input`'s value will be validated
against.


## ping

```elm
ping : String.String -> Html.Attribute msg
```

 Specify a URL to send a short POST request to when the user clicks on an
`a` or `area`. Useful for monitoring and tracking.


## placeholder

```elm
placeholder : String.String -> Html.Attribute msg
```

 Provides a hint to the user of what can be entered into an `input` or
`textarea`.


## poster

```elm
poster : String.String -> Html.Attribute msg
```

 A URL indicating a poster frame to show until the user plays or seeks the
`video`.


## preload

```elm
preload : String.String -> Html.Attribute msg
```

 Control how much of an `audio` or `video` resource should be preloaded. 

## property

```elm
property : String.String -> Json.Encode.Value -> Html.Attribute msg
```

 Create *properties*, like saying `domNode.className = 'greeting'` in
JavaScript.

    import Json.Encode as Encode

    class : String -> Attribute msg
    class name =
      property "className" (Encode.string name)

Read more about the difference between properties and attributes [here][].

[here]: https://github.com/elm/html/blob/master/properties-vs-attributes.md


## pubdate

```elm
pubdate : String.String -> Html.Attribute msg
```

 Indicates whether this date and time is the date of the nearest `article`
ancestor element. For `time`.


## readonly

```elm
readonly : Basics.Bool -> Html.Attribute msg
```

 Indicates whether an `input` or `textarea` can be edited. 

## rel

```elm
rel : String.String -> Html.Attribute msg
```

 Specifies the relationship of the target object to the link object.
For `a`, `area`, `link`.


## required

```elm
required : Basics.Bool -> Html.Attribute msg
```

 Indicates whether this element is required to fill out or not.
For `input`, `select`, and `textarea`.


## reversed

```elm
reversed : Basics.Bool -> Html.Attribute msg
```

 Indicates whether an ordered list `ol` should be displayed in a descending
order instead of a ascending.


## rows

```elm
rows : Basics.Int -> Html.Attribute msg
```

 Defines the number of rows in a `textarea`. 

## rowspan

```elm
rowspan : Basics.Int -> Html.Attribute msg
```

 Defines the number of rows a table cell should span over.
For `td` and `th`.


## sandbox

```elm
sandbox : String.String -> Html.Attribute msg
```

 A space separated list of security restrictions you'd like to lift for an
`iframe`.


## scope

```elm
scope : String.String -> Html.Attribute msg
```

 Specifies the scope of a header cell `th`. Possible values are: col, row,
colgroup, rowgroup.


## selected

```elm
selected : Basics.Bool -> Html.Attribute msg
```

 Defines which `option` will be selected on page load. 

## shape

```elm
shape : String.String -> Html.Attribute msg
```

 Declare the shape of the clickable area in an `a` or `area`. Valid values
include: default, rect, circle, poly. This attribute can be paired with
`coords` to create more particular shapes.


## size

```elm
size : Basics.Int -> Html.Attribute msg
```

 For `input` specifies the width of an input in characters.

For `select` specifies the number of visible options in a drop-down list.


## spellcheck

```elm
spellcheck : Basics.Bool -> Html.Attribute msg
```

 Indicates whether spell checking is allowed for the element. 

## src

```elm
src : String.String -> Html.Attribute msg
```

 The URL of the embeddable content. For `audio`, `embed`, `iframe`, `img`,
`input`, `script`, `source`, `track`, and `video`.


## srcdoc

```elm
srcdoc : String.String -> Html.Attribute msg
```

 **DEPRECATED.** We would like to remove this in a future release. Please
prefer web components in cases where this might be useful.


## srclang

```elm
srclang : String.String -> Html.Attribute msg
```

 A two letter language code indicating the language of the `track` text data.


## start

```elm
start : Basics.Int -> Html.Attribute msg
```

 Defines the first number of an ordered list if you want it to be something
besides 1.


## step

```elm
step : String.String -> Html.Attribute msg
```

 Add a step size to an `input`. Use `step "any"` to allow any floating-point
number to be used in the input.


## style

```elm
style : String.String -> String.String -> Html.Attribute msg
```

 Specify a style.

    greeting : Node msg
    greeting =
      div
        [ style "background-color" "red"
        , style "height" "90px"
        , style "width" "100%"
        ]
        [ text "Hello!"
        ]

There is no `Html.Styles` module because best practices for working with HTML
suggest that this should primarily be specified in CSS files. So the general
recommendation is to use this function lightly.


## tabindex

```elm
tabindex : Basics.Int -> Html.Attribute msg
```

 Overrides the browser's default tab order and follows the one specified
instead.


## target

```elm
target : String.String -> Html.Attribute msg
```

 Specify where the results of clicking an `a`, `area`, `base`, or `form`
should appear. Possible special values include:

  * _blank &mdash; a new window or tab
  * _self &mdash; the same frame (this is default)
  * _parent &mdash; the parent frame
  * _top &mdash; the full body of the window

You can also give the name of any `frame` you have created.


## title

```elm
title : String.String -> Html.Attribute msg
```

 Text to be displayed in a tooltip when hovering over the element. 

## type_

```elm
type_ : String.String -> Html.Attribute msg
```

 Defines the type of a `button`, `checkbox`, `input`, `embed`, `menu`,
`object`, `script`, `source`, or `style`.


## usemap

```elm
usemap : String.String -> Html.Attribute msg
```

 Specify the hash name reference of a `map` that should be used for an `img`
or `object`. A hash name reference is a hash symbol followed by the element's name or id.
E.g. `"#planet-map"`.


## value

```elm
value : String.String -> Html.Attribute msg
```

 Defines a default value which will be displayed in a `button`, `option`,
`input`, `li`, `meter`, `progress`, or `param`.


## width

```elm
width : Basics.Int -> Html.Attribute msg
```

 Declare the width of a `canvas`, `embed`, `iframe`, `img`, `input`,
`object`, or `video`.


## wrap

```elm
wrap : String.String -> Html.Attribute msg
```

 Indicates whether the text should be wrapped in a `textarea`. Possible
values are "hard" and "soft".


# Html.Events


It is often helpful to create an [Custom Type][] so you can have many different kinds
of events as seen in the [TodoMVC][] example.

[Custom Type]: https://guide.elm-lang.org/types/custom_types.html
[TodoMVC]: https://github.com/evancz/elm-todomvc/blob/master/Todo.elm

# Mouse
@docs onClick, onDoubleClick,
      onMouseDown, onMouseUp,
      onMouseEnter, onMouseLeave,
      onMouseOver, onMouseOut

# Forms
@docs onInput, onCheck, onSubmit

# Focus
@docs onBlur, onFocus

# Custom
@docs on, stopPropagationOn, preventDefaultOn, custom

## Custom Decoders
@docs targetValue, targetChecked, keyCode


## custom

```elm
custom : String.String -> Json.Decode.Decoder { message : msg, stopPropagation : Basics.Bool, preventDefault : Basics.Bool } -> Html.Attribute msg
```

 Create an event listener that may [`stopPropagation`][stop] or
[`preventDefault`][prevent].

[stop]: https://developer.mozilla.org/en-US/docs/Web/API/Event/stopPropagation
[prevent]: https://developer.mozilla.org/en-US/docs/Web/API/Event/preventDefault
[handler]: https://package.elm-lang.org/packages/elm/virtual-dom/latest/VirtualDom#Handler

**Note:** Check out the lower-level event API in `elm/virtual-dom` for more
information on exactly how events work, especially the [`Handler`][handler]
docs.


## keyCode

```elm
keyCode : Json.Decode.Decoder Basics.Int
```

 A `Json.Decoder` for grabbing `event.keyCode`. This helps you define
keyboard listeners like this:

    import Json.Decode as Json

    onKeyUp : (Int -> msg) -> Attribute msg
    onKeyUp tagger =
      on "keyup" (Json.map tagger keyCode)

**Note:** It looks like the spec is moving away from `event.keyCode` and
towards `event.key`. Once this is supported in more browsers, we may add
helpers here for `onKeyUp`, `onKeyDown`, `onKeyPress`, etc.


## on

```elm
on : String.String -> Json.Decode.Decoder msg -> Html.Attribute msg
```

 Create a custom event listener. Normally this will not be necessary, but
you have the power! Here is how `onClick` is defined for example:

    import Json.Decode as Decode

    onClick : msg -> Attribute msg
    onClick message =
      on "click" (Decode.succeed message)

The first argument is the event name in the same format as with JavaScript's
[`addEventListener`][aEL] function.

The second argument is a JSON decoder. Read more about these [here][decoder].
When an event occurs, the decoder tries to turn the event object into an Elm
value. If successful, the value is routed to your `update` function. In the
case of `onClick` we always just succeed with the given `message`.

If this is confusing, work through the [Elm Architecture Tutorial][tutorial].
It really helps!

[aEL]: https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener
[decoder]: /packages/elm/json/latest/Json-Decode
[tutorial]: https://github.com/evancz/elm-architecture-tutorial/

**Note:** This creates a [passive][] event listener, enabling optimizations for
touch, scroll, and wheel events in some browsers.

[passive]: https://github.com/WICG/EventListenerOptions/blob/gh-pages/explainer.md


## onBlur

```elm
onBlur : msg -> Html.Attribute msg
```



## onCheck

```elm
onCheck : (Basics.Bool -> msg) -> Html.Attribute msg
```

 Detect [change](https://developer.mozilla.org/en-US/docs/Web/Events/change)
events on checkboxes. It will grab the boolean value from `event.target.checked`
on any input event.

Check out [`targetChecked`](#targetChecked) for more details on how this works.


## onClick

```elm
onClick : msg -> Html.Attribute msg
```



## onDoubleClick

```elm
onDoubleClick : msg -> Html.Attribute msg
```



## onFocus

```elm
onFocus : msg -> Html.Attribute msg
```



## onInput

```elm
onInput : (String.String -> msg) -> Html.Attribute msg
```

 Detect [input](https://developer.mozilla.org/en-US/docs/Web/Events/input)
events for things like text fields or text areas.

For more details on how `onInput` works, check out [`targetValue`](#targetValue).

**Note 1:** It grabs the **string** value at `event.target.value`, so it will
not work if you need some other information. For example, if you want to track
inputs on a range slider, make a custom handler with [`on`](#on).

**Note 2:** It uses `stopPropagationOn` internally to always stop propagation
of the event. This is important for complicated reasons explained [here][1] and
[here][2].

[1]: /packages/elm/virtual-dom/latest/VirtualDom#Handler
[2]: https://github.com/elm/virtual-dom/issues/125


## onMouseDown

```elm
onMouseDown : msg -> Html.Attribute msg
```



## onMouseEnter

```elm
onMouseEnter : msg -> Html.Attribute msg
```



## onMouseLeave

```elm
onMouseLeave : msg -> Html.Attribute msg
```



## onMouseOut

```elm
onMouseOut : msg -> Html.Attribute msg
```



## onMouseOver

```elm
onMouseOver : msg -> Html.Attribute msg
```



## onMouseUp

```elm
onMouseUp : msg -> Html.Attribute msg
```



## onSubmit

```elm
onSubmit : msg -> Html.Attribute msg
```

 Detect a [submit](https://developer.mozilla.org/en-US/docs/Web/Events/submit)
event with [`preventDefault`](https://developer.mozilla.org/en-US/docs/Web/API/Event/preventDefault)
in order to prevent the form from changing the page’s location. If you need
different behavior, create a custom event handler.


## preventDefaultOn

```elm
preventDefaultOn : String.String -> Json.Decode.Decoder ( msg, Basics.Bool ) -> Html.Attribute msg
```

 Create an event listener that may [`preventDefault`][prevent]. Your decoder
must produce a message and a `Bool` that decides if `preventDefault` should
be called.

For example, the `onSubmit` function in this library *always* prevents the
default behavior:

[prevent]: https://developer.mozilla.org/en-US/docs/Web/API/Event/preventDefault

    onSubmit : msg -> Attribute msg
    onSubmit msg =
      preventDefaultOn "submit" (Json.map alwaysPreventDefault (Json.succeed msg))

    alwaysPreventDefault : msg -> ( msg, Bool )
    alwaysPreventDefault msg =
      ( msg, True )


## stopPropagationOn

```elm
stopPropagationOn : String.String -> Json.Decode.Decoder ( msg, Basics.Bool ) -> Html.Attribute msg
```

 Create an event listener that may [`stopPropagation`][stop]. Your decoder
must produce a message and a `Bool` that decides if `stopPropagation` should
be called.

[stop]: https://developer.mozilla.org/en-US/docs/Web/API/Event/stopPropagation

**Note:** This creates a [passive][] event listener, enabling optimizations for
touch, scroll, and wheel events in some browsers.

[passive]: https://github.com/WICG/EventListenerOptions/blob/gh-pages/explainer.md


## targetChecked

```elm
targetChecked : Json.Decode.Decoder Basics.Bool
```

 A `Json.Decoder` for grabbing `event.target.checked`. We use this to define
`onCheck` as follows:

    import Json.Decode as Json

    onCheck : (Bool -> msg) -> Attribute msg
    onCheck tagger =
      on "input" (Json.map tagger targetChecked)


## targetValue

```elm
targetValue : Json.Decode.Decoder String.String
```

 A `Json.Decoder` for grabbing `event.target.value`. We use this to define
`onInput` as follows:

    import Json.Decode as Json

    onInput : (String -> msg) -> Attribute msg
    onInput tagger =
      stopPropagationOn "input" <|
        Json.map alwaysStop (Json.map tagger targetValue)

    alwaysStop : a -> (a, Bool)
    alwaysStop x =
      (x, True)

You probably will never need this, but hopefully it gives some insights into
how to make custom event handlers.


# Html.Keyed

 A keyed node helps optimize cases where children are getting added, moved,
removed, etc. Common examples include:

  - The user can delete items from a list.
  - The user can create new items in a list.
  - You can sort a list based on name or date or whatever.

When you use a keyed node, every child is paired with a string identifier. This
makes it possible for the underlying diffing algorithm to reuse nodes more
efficiently.

# Keyed Nodes
@docs node

# Commonly Keyed Nodes
@docs ol, ul


## node

```elm
node : String.String -> List.List (Html.Attribute msg) -> List.List ( String.String, Html.Html msg ) -> Html.Html msg
```

 Works just like `Html.node`, but you add a unique identifier to each child
node. You want this when you have a list of nodes that is changing: adding
nodes, removing nodes, etc. In these cases, the unique identifiers help make
the DOM modifications more efficient.


## ol

```elm
ol : List.List (Html.Attribute msg) -> List.List ( String.String, Html.Html msg ) -> Html.Html msg
```



## ul

```elm
ul : List.List (Html.Attribute msg) -> List.List ( String.String, Html.Html msg ) -> Html.Html msg
```



# Html.Lazy

 Since all Elm functions are pure we have a guarantee that the same input
will always result in the same output. This module gives us tools to be lazy
about building `Html` that utilize this fact.

Rather than immediately applying functions to their arguments, the `lazy`
functions just bundle the function and arguments up for later. When diffing
the old and new virtual DOM, it checks to see if all the arguments are equal
by reference. If so, it skips calling the function!

This is a really cheap test and often makes things a lot faster, but definitely
benchmark to be sure!

@docs lazy, lazy2, lazy3, lazy4, lazy5, lazy6, lazy7, lazy8



## lazy

```elm
lazy : (a -> Html.Html msg) -> a -> Html.Html msg
```

 A performance optimization that delays the building of virtual DOM nodes.

Calling `(view model)` will definitely build some virtual DOM, perhaps a lot of
it. Calling `(lazy view model)` delays the call until later. During diffing, we
can check to see if `model` is referentially equal to the previous value used,
and if so, we just stop. No need to build up the tree structure and diff it,
we know if the input to `view` is the same, the output must be the same!


## lazy2

```elm
lazy2 : (a -> b -> Html.Html msg) -> a -> b -> Html.Html msg
```

 Same as `lazy` but checks on two arguments.


## lazy3

```elm
lazy3 : (a -> b -> c -> Html.Html msg) -> a -> b -> c -> Html.Html msg
```

 Same as `lazy` but checks on three arguments.


## lazy4

```elm
lazy4 : (a -> b -> c -> d -> Html.Html msg) -> a -> b -> c -> d -> Html.Html msg
```

 Same as `lazy` but checks on four arguments.


## lazy5

```elm
lazy5 : (a -> b -> c -> d -> e -> Html.Html msg) -> a -> b -> c -> d -> e -> Html.Html msg
```

 Same as `lazy` but checks on five arguments.


## lazy6

```elm
lazy6 : (a -> b -> c -> d -> e -> f -> Html.Html msg) -> a -> b -> c -> d -> e -> f -> Html.Html msg
```

 Same as `lazy` but checks on six arguments.


## lazy7

```elm
lazy7 : (a -> b -> c -> d -> e -> f -> g -> Html.Html msg) -> a -> b -> c -> d -> e -> f -> g -> Html.Html msg
```

 Same as `lazy` but checks on seven arguments.


## lazy8

```elm
lazy8 : (a -> b -> c -> d -> e -> f -> g -> h -> Html.Html msg) -> a -> b -> c -> d -> e -> f -> g -> h -> Html.Html msg
```

 Same as `lazy` but checks on eight arguments.

