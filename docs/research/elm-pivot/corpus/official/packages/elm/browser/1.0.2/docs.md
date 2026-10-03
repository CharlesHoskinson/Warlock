# official/packages/elm/browser/1.0.2/docs.json
Source: https://package.elm-lang.org/packages/elm/browser/1.0.2/docs.json

# Browser

 This module helps you set up an Elm `Program` with functions like
[`sandbox`](#sandbox) and [`document`](#document).


# Sandboxes

@docs sandbox


# Elements

@docs element


# Documents

@docs document, Document


# Applications

@docs application, UrlRequest



## Document

```elm
type alias Document msg =
    { title : String.String, body : List.List (Html.Html msg) }
```

 This data specifies the `<title>` and all of the nodes that should go in
the `<body>`. This means you can update the title as your application changes.
Maybe your "single-page app" navigates to a "different page", maybe a calendar
app shows an accurate date in the title, etc.

> **Note about CSS:** This looks similar to an `<html>` document, but this is
> not the place to manage CSS assets. If you want to work with CSS, there are
> a couple ways:
>
> 1.  Packages like [`rtfeldman/elm-css`][elm-css] give all of the features
>     of CSS without any CSS files. You can add all the styles you need in your
>     `view` function, and there is no need to worry about class names matching.
>
> 2.  Compile your Elm code to JavaScript with `elm make --output=elm.js` and
>     then make your own HTML file that loads `elm.js` and the CSS file you want.
>     With this approach, it does not matter where the CSS comes from. Write it
>     by hand. Generate it. Whatever you want to do.
>
> 3.  If you need to change `<link>` tags dynamically, you can send messages
>     out a port to do it in JavaScript.
>
> The bigger point here is that loading assets involves touching the `<head>`
> as an implementation detail of browsers, but that does not mean it should be
> the responsibility of the `view` function in Elm. So we do it differently!

[elm-css]: /packages/rtfeldman/elm-css/latest/



## UrlRequest

```elm
type UrlRequest
    = Internal (Url.Url)
    | External (String.String)
```

 All links in an [`application`](#application) create a `UrlRequest`. So
when you click `<a href="/home">Home</a>`, it does not just navigate! It
notifies `onUrlRequest` that the user wants to change the `Url`.


### `Internal` vs `External`

Imagine we are browsing `https://example.com`. An `Internal` link would be
like:

  - `settings#privacy`
  - `/home`
  - `https://example.com/home`
  - `//example.com/home`

All of these links exist under the `https://example.com` domain. An `External`
link would be like:

  - `https://elm-lang.org/examples`
  - `https://other.example.com/home`
  - `http://example.com/home`

Anything that changes the domain. Notice that changing the protocol from
`https` to `http` is considered a different domain! (And vice versa!)


### Purpose

Having a `UrlRequest` requires a case in your `update` like this:

    import Browser exposing (..)
    import Browser.Navigation as Nav
    import Url

    type Msg
        = ClickedLink UrlRequest

    update : Msg -> Model -> ( Model, Cmd msg )
    update msg model =
        case msg of
            ClickedLink urlRequest ->
                case urlRequest of
                    Internal url ->
                        ( model
                        , Nav.pushUrl model.key (Url.toString url)
                        )

                    External url ->
                        ( model
                        , Nav.load url
                        )

This is useful because it gives you a chance to customize the behavior in each
case. Maybe on some `Internal` links you save the scroll position with
[`Browser.Dom.getViewport`](Browser-Dom#getViewport) so you can restore it
later. Maybe on `External` links you persist parts of the `Model` on your
servers before leaving. Whatever you need to do!

**Note:** Knowing the scroll position is not enough to restore it! What if the
browser dimensions change? The scroll position will not correlate with
&ldquo;what was on screen&rdquo; anymore. So it may be better to remember
&ldquo;what was on screen&rdquo; and recreate the position based on that. For
example, in a Wikipedia article, remember the header that they were looking at
most recently. [`Browser.Dom.getElement`](Browser-Dom#getElement) is designed
for figuring that out!



## application

```elm
application : { init : flags -> Url.Url -> Browser.Navigation.Key -> ( model, Platform.Cmd.Cmd msg ), view : model -> Browser.Document msg, update : msg -> model -> ( model, Platform.Cmd.Cmd msg ), subscriptions : model -> Platform.Sub.Sub msg, onUrlRequest : Browser.UrlRequest -> msg, onUrlChange : Url.Url -> msg } -> Platform.Program flags model msg
```

 Create an application that manages [`Url`][url] changes.

**When the application starts**, `init` gets the initial `Url`. You can show
different things depending on the `Url`!

**When someone clicks a link**, like `<a href="/home">Home</a>`, it always goes
through `onUrlRequest`. The resulting message goes to your `update` function,
giving you a chance to save scroll position or persist data before changing
the URL yourself with [`pushUrl`][bnp] or [`load`][bnl]. More info on this in
the [`UrlRequest`](#UrlRequest) docs!

**When the URL changes**, the new `Url` goes through `onUrlChange`. The
resulting message goes to `update` where you can decide what to show next.

Applications always use the [`Browser.Navigation`][bn] module for precise
control over `Url` changes.

**More Info:** Here are some example usages of `application` programs:

  - [RealWorld example app](https://github.com/rtfeldman/elm-spa-example)
  - [Elm’s package website](https://github.com/elm/package.elm-lang.org)

These are quite advanced Elm programs, so be sure to go through [the guide][g]
first to get a solid conceptual foundation before diving in! If you start
reading a calculus book from page 314, it might seem confusing. Same here!

**Note:** Can an [`element`](#element) manage the URL too? Read [this]!

[g]: https://guide.elm-lang.org/
[bn]: Browser-Navigation
[bnp]: Browser-Navigation#pushUrl
[bnl]: Browser-Navigation#load
[url]: /packages/elm/url/latest/Url#Url
[this]: https://github.com/elm/browser/blob/1.0.2/notes/navigation-in-elements.md



## document

```elm
document : { init : flags -> ( model, Platform.Cmd.Cmd msg ), view : model -> Browser.Document msg, update : msg -> model -> ( model, Platform.Cmd.Cmd msg ), subscriptions : model -> Platform.Sub.Sub msg } -> Platform.Program flags model msg
```

 Create an HTML document managed by Elm. This expands upon what `element`
can do in that `view` now gives you control over the `<title>` and `<body>`.


## element

```elm
element : { init : flags -> ( model, Platform.Cmd.Cmd msg ), view : model -> Html.Html msg, update : msg -> model -> ( model, Platform.Cmd.Cmd msg ), subscriptions : model -> Platform.Sub.Sub msg } -> Platform.Program flags model msg
```

 Create an HTML element managed by Elm. The resulting elements are easy to
embed in larger JavaScript projects, and lots of companies that use Elm
started with this approach! Try it out on something small. If it works, great,
do more! If not, revert, no big deal.

Unlike a [`sandbox`](#sandbox), an `element` can talk to the outside world in
a couple ways:

  - `Cmd` &mdash; you can “command” the Elm runtime to do stuff, like HTTP.
  - `Sub` &mdash; you can “subscribe” to event sources, like clock ticks.
  - `flags` &mdash; JavaScript can pass in data when starting the Elm program
  - `ports` &mdash; set up a client-server relationship with JavaScript

As you read [the guide][guide] you will run into a bunch of examples of `element`
in [this section][fx]. You can learn more about flags and ports in [the interop
section][interop].

[guide]: https://guide.elm-lang.org/
[fx]: https://guide.elm-lang.org/effects/
[interop]: https://guide.elm-lang.org/interop/



## sandbox

```elm
sandbox : { init : model, view : model -> Html.Html msg, update : msg -> model -> model } -> Platform.Program () model msg
```

 Create a “sandboxed” program that cannot communicate with the outside
world.

This is great for learning the basics of [The Elm Architecture][tea]. You can
see sandboxes in action in the following examples:

  - [Buttons](https://guide.elm-lang.org/architecture/buttons.html)
  - [Text Fields](https://guide.elm-lang.org/architecture/text_fields.html)
  - [Forms](https://guide.elm-lang.org/architecture/forms.html)

Those are nice, but **I very highly recommend reading [this guide][guide]
straight through** to really learn how Elm works. Understanding the
fundamentals actually pays off in this language!

[tea]: https://guide.elm-lang.org/architecture/
[guide]: https://guide.elm-lang.org/



# Browser.Dom

 This module allows you to manipulate the DOM in various ways. It covers:

  - Focus and blur input elements.
  - Get the `width` and `height` of elements.
  - Get the `x` and `y` coordinates of elements.
  - Figure out the scroll position.
  - Change the scroll position!

We use different terminology than JavaScript though...


# Terminology

Have you ever thought about how &ldquo;scrolling&rdquo; is a metaphor about
scrolls? Like hanging scrolls of caligraphy made during the Han Dynasty
in China?

This metaphor falls apart almost immediately though. For example, many scrolls
read horizontally! Like a [Sefer Torah][torah] or [Chinese Handscrolls][hand].
The two sides move independently, sometimes kept in place with stones. What is
a scroll bar in this world? And [hanging scrolls][hang] (which _are_ displayed
vertically) do not &ldquo;scroll&rdquo; at all! They hang!

So in JavaScript, we start with a badly stretched metaphor and add a bunch of
DOM details like padding, borders, and margins. How do those relate to scrolls?
For example, JavaScript has `clientWidth`. Client like a feudal state that pays
tribute to the emperor? And `offsetHeight`. Can an offset even have height? And
what has that got to do with scrolls?

So instead of inheriting this metaphorical hodge-podge, we use terminology from
3D graphics. You have a **scene** containing all your elements and a **viewport**
into the scene. I think it ends up being a lot clearer, but you can evaluate
for yourself when you see the diagrams later!

**Note:** For more scroll facts, I recommend [A Day on the Grand Canal with
the Emperor of China or: Surface Is Illusion But So Is Depth][doc] where David
Hockney explores the history of _perspective_ in art. Really interesting!

[torah]: https://en.wikipedia.org/wiki/Sefer_Torah
[hand]: https://www.metmuseum.org/toah/hd/chhs/hd_chhs.htm
[hang]: https://en.wikipedia.org/wiki/Hanging_scroll
[doc]: https://www.imdb.com/title/tt0164525/


# Focus

@docs focus, blur, Error


# Get Viewport

@docs getViewport, Viewport, getViewportOf


# Set Viewport

@docs setViewport, setViewportOf


# Position

@docs getElement, Element



## Element

```elm
type alias Element =
    { scene : { width : Basics.Float, height : Basics.Float }, viewport : { x : Basics.Float, y : Basics.Float, width : Basics.Float, height : Basics.Float }, element : { x : Basics.Float, y : Basics.Float, width : Basics.Float, height : Basics.Float } }
```

 A bunch of information about the position and size of an element relative
to the overall scene.

![getElement](https://elm.github.io/browser/v1/getElement.svg)



## Viewport

```elm
type alias Viewport =
    { scene : { width : Basics.Float, height : Basics.Float }, viewport : { x : Basics.Float, y : Basics.Float, width : Basics.Float, height : Basics.Float } }
```

 All the information about the current viewport.

![getViewport](https://elm.github.io/browser/v1/getViewport.svg)



## Error

```elm
type Error
    = NotFound (String.String)
```

 Many functions in this module look up DOM nodes up by their `id`. If you
ask for an `id` that is not in the DOM, you will get this error.


## blur

```elm
blur : String.String -> Task.Task Browser.Dom.Error ()
```

 Find a DOM node by `id` and make it lose focus. So if you wanted a node
like `<input type="text" id="search-box">` to lose focus you could say:

    import Browser.Dom as Dom
    import Task

    type Msg
        = NoOp

    unfocusSearchBox : Cmd Msg
    unfocusSearchBox =
        Task.attempt (\_ -> NoOp) (Dom.blur "search-box")

Notice that this code ignores the possibility that `search-box` is not used
as an `id` by any node, failing silently in that case. It would be better to
log the failure with whatever error reporting system you use.



## focus

```elm
focus : String.String -> Task.Task Browser.Dom.Error ()
```

 Find a DOM node by `id` and focus on it. So if you wanted to focus a node
like `<input type="text" id="search-box">` you could say:

    import Browser.Dom as Dom
    import Task

    type Msg
        = NoOp

    focusSearchBox : Cmd Msg
    focusSearchBox =
        Task.attempt (\_ -> NoOp) (Dom.focus "search-box")

Notice that this code ignores the possibility that `search-box` is not used
as an `id` by any node, failing silently in that case. It would be better to
log the failure with whatever error reporting system you use.



## getElement

```elm
getElement : String.String -> Task.Task Browser.Dom.Error Browser.Dom.Element
```

 Get position information about specific elements. Say we put
`id "jesting-aside"` on the seventh paragraph of the text. When we call
`getElement "jesting-aside"` we would get the following information:

![getElement](https://elm.github.io/browser/v1/getElement.svg)

This can be useful for:

  - **Scrolling** &mdash; Pair this information with `setViewport` to scroll
    specific elements into view. This gives you a lot of control over where exactly
    the element would be after the viewport moved.

  - **Drag and Drop** &mdash; As of this writing, `touchmove` events do not tell
    you which element you are currently above. To figure out if you have dragged
    something over the target, you could see if the `pageX` and `pageY` of the
    touch are inside the `x`, `y`, `width`, and `height` of the target element.

**Note:** This corresponds to JavaScript&rsquo;s [`getBoundingClientRect`][gbcr],
so **the element&rsquo;s margins are included in its `width` and `height`**.
With scrolling, maybe you want to include the margins. With drag-and-drop, you
probably do not, so some folks set the margins to zero and put the target
element in a `<div>` that adds the spacing. Just something to be aware of!

[gbcr]: https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect



## getViewport

```elm
getViewport : Task.Task x Browser.Dom.Viewport
```

 Get information on the current viewport of the browser.

![getViewport](https://elm.github.io/browser/v1/getViewport.svg)

If you want to move the viewport around (i.e. change the scroll position) you
can use [`setViewport`](#setViewport) which change the `x` and `y` of the
viewport.



## getViewportOf

```elm
getViewportOf : String.String -> Task.Task Browser.Dom.Error Browser.Dom.Viewport
```

 Just like `getViewport`, but for any scrollable DOM node. Say we have an
application with a chat box in the bottow right corner like this:

![chat](https://elm.github.io/browser/v1/chat.svg)

There are probably a whole bunch of messages that are not being shown. You
could scroll up to see them all. Well, we can think of that chat box is a
viewport into a scene!

![getViewportOf](https://elm.github.io/browser/v1/getViewportOf.svg)

This can be useful with [`setViewportOf`](#setViewportOf) to make sure new
messages always appear on the bottom.

The viewport size _does not_ include the border or margins.

**Note:** This data is collected from specific fields in JavaScript, so it
may be helpful to know that:

  - `scene.width` = [`scrollWidth`][sw]
  - `scene.height` = [`scrollHeight`][sh]
  - `viewport.x` = [`scrollLeft`][sl]
  - `viewport.y` = [`scrollTop`][st]
  - `viewport.width` = [`clientWidth`][cw]
  - `viewport.height` = [`clientHeight`][ch]

Neither [`offsetWidth`][ow] nor [`offsetHeight`][oh] are available. The theory
is that (1) the information can always be obtained by using `getElement` on a
node without margins, (2) no cases came to mind where you actually care in the
first place, and (3) it is available through ports if it is really needed.
If you have a case that really needs it though, please share your specific
scenario in an issue! Nicely presented case studies are the raw ingredients for
API improvements!

[sw]: https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollWidth
[sh]: https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollHeight
[st]: https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollTop
[sl]: https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollLeft
[cw]: https://developer.mozilla.org/en-US/docs/Web/API/Element/clientWidth
[ch]: https://developer.mozilla.org/en-US/docs/Web/API/Element/clientHeight
[ow]: https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/offsetWidth
[oh]: https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/offsetHeight



## setViewport

```elm
setViewport : Basics.Float -> Basics.Float -> Task.Task x ()
```

 Change the `x` and `y` offset of the browser viewport immediately. For
example, you could make a command to jump to the top of the page:

    import Browser.Dom as Dom
    import Task

    type Msg
        = NoOp

    resetViewport : Cmd Msg
    resetViewport =
        Task.perform (\_ -> NoOp) (Dom.setViewport 0 0)

This sets the viewport offset to zero.

This could be useful with `Browser.application` where you may want to reset
the viewport when the URL changes. Maybe you go to a &ldquo;new page&rdquo;
and want people to start at the top!



## setViewportOf

```elm
setViewportOf : String.String -> Basics.Float -> Basics.Float -> Task.Task Browser.Dom.Error ()
```

 Change the `x` and `y` offset of a DOM node&rsquo;s viewport by ID. This
is common in text messaging and chat rooms, where once the messages fill the
screen, you want to always be at the very bottom of the message chain. This
way the latest message is always on screen! You could do this:

    import Browser.Dom as Dom
    import Task

    type Msg
        = NoOp

    jumpToBottom : String -> Cmd Msg
    jumpToBottom id =
        Dom.getViewportOf id
            |> Task.andThen (\info -> Dom.setViewportOf id 0 info.scene.height)
            |> Task.attempt (\_ -> NoOp)

So you could call `jumpToBottom "chat-box"` whenever you add a new message.

**Note 1:** What happens if the viewport is placed out of bounds? Where there
is no `scene` to show? To avoid this question, the `x` and `y` offsets are
clamped such that the viewport is always fully within the `scene`. So when
`jumpToBottom` sets the `y` offset of the viewport to the `height` of the
`scene` (i.e. too far!) it relies on this clamping behavior to put the viewport
back in bounds.

**Note 2:** The example ignores when the element ID is not found, but it would
be great to log that information. It means there may be a bug or a dead link
somewhere!



# Browser.Events

 In JavaScript, information about the root of an HTML document is held in
the `document` and `window` objects. This module lets you create event
listeners on those objects for the following topics: [animation](#animation),
[keyboard](#keyboard), [mouse](#mouse), and [window](#window).

If there is something else you need, use [ports] to do it in JavaScript!

[ports]: https://guide.elm-lang.org/interop/ports.html


# Animation

@docs onAnimationFrame, onAnimationFrameDelta


# Keyboard

@docs onKeyPress, onKeyDown, onKeyUp


# Mouse

@docs onClick, onMouseMove, onMouseDown, onMouseUp


# Window

@docs onResize, onVisibilityChange, Visibility



## Visibility

```elm
type Visibility
    = Visible
    | Hidden
```

 Value describing whether the page is hidden or visible.


## onAnimationFrame

```elm
onAnimationFrame : (Time.Posix -> msg) -> Platform.Sub.Sub msg
```

 An animation frame triggers about 60 times per second. Get the POSIX time
on each frame. (See [`elm/time`](/packages/elm/time/latest) for more info on
POSIX times.)

**Note:** Browsers have their own render loop, repainting things as fast as
possible. If you want smooth animations in your application, it is helpful to
sync up with the browsers natural refresh rate. This hooks into JavaScript's
`requestAnimationFrame` function.



## onAnimationFrameDelta

```elm
onAnimationFrameDelta : (Basics.Float -> msg) -> Platform.Sub.Sub msg
```

 Just like `onAnimationFrame`, except message is the time in milliseconds
since the previous frame. So you should get a sequence of values all around
`1000 / 60` which is nice for stepping animations by a time delta.


## onClick

```elm
onClick : Json.Decode.Decoder msg -> Platform.Sub.Sub msg
```

 Subscribe to mouse clicks anywhere on screen. Maybe you need to create a
custom drop down. You could listen for clicks when it is open, letting you know
if someone clicked out of it:

    import Browser.Events as Events
    import Json.Decode as D

    type Msg
       = ClickOut

    subscriptions : Model -> Sub Msg
    subscriptions model =
      case model.dropDown of
        Closed _ ->
          Sub.none

        Open _ ->
          Events.onClick (D.succeed ClickOut)



## onKeyDown

```elm
onKeyDown : Json.Decode.Decoder msg -> Platform.Sub.Sub msg
```

 Subscribe to get codes whenever a key goes down. This can be useful for
creating games. Maybe you want to know if people are pressing `w`, `a`, `s`,
or `d` at any given time.

**Note:** Check out [this advice][note] to learn more about decoding key codes.
It is more complicated than it should be.

[note]: https://github.com/elm/browser/blob/1.0.2/notes/keyboard.md



## onKeyPress

```elm
onKeyPress : Json.Decode.Decoder msg -> Platform.Sub.Sub msg
```

 Subscribe to key presses that normally produce characters. So you should
not rely on this for arrow keys.

**Note:** Check out [this advice][note] to learn more about decoding key codes.
It is more complicated than it should be.

[note]: https://github.com/elm/browser/blob/1.0.2/notes/keyboard.md



## onKeyUp

```elm
onKeyUp : Json.Decode.Decoder msg -> Platform.Sub.Sub msg
```

 Subscribe to get codes whenever a key goes up. Often used in combination
with [`onVisibilityChange`](#onVisibilityChange) to be sure keys do not appear
to down and never come back up.


## onMouseDown

```elm
onMouseDown : Json.Decode.Decoder msg -> Platform.Sub.Sub msg
```

 Subscribe to get mouse information whenever the mouse button goes down.


## onMouseMove

```elm
onMouseMove : Json.Decode.Decoder msg -> Platform.Sub.Sub msg
```

 Subscribe to mouse moves anywhere on screen.

You could use this to implement resizable panels like in Elm's online code
editor. Check out the example imprementation [here][drag].

[drag]: https://github.com/elm/browser/blob/1.0.2/examples/src/Drag.elm

**Note:** Unsubscribe if you do not need these events! Running code on every
single mouse movement can be very costly, and it is recommended to only
subscribe when absolutely necessary.



## onMouseUp

```elm
onMouseUp : Json.Decode.Decoder msg -> Platform.Sub.Sub msg
```

 Subscribe to get mouse information whenever the mouse button goes up.
Often used in combination with [`onVisibilityChange`](#onVisibilityChange)
to be sure keys do not appear to down and never come back up.


## onResize

```elm
onResize : (Basics.Int -> Basics.Int -> msg) -> Platform.Sub.Sub msg
```

 Subscribe to any changes in window size.

For example, you could track the current width by saying:

    import Browser.Events as E

    type Msg
      = GotNewWidth Int

    subscriptions : model -> Cmd Msg
    subscriptions _ =
      E.onResize (\w h -> GotNewWidth w)

**Note:** This is equivalent to getting events from [`window.onresize`][resize].

[resize]: https://developer.mozilla.org/en-US/docs/Web/API/GlobalEventHandlers/onresize



## onVisibilityChange

```elm
onVisibilityChange : (Browser.Events.Visibility -> msg) -> Platform.Sub.Sub msg
```

 Subscribe to any visibility changes, like if the user switches to a
different tab or window. When the user looks away, you may want to:

- Pause a timer.
- Pause an animation.
- Pause video or audio.
- Pause an image carousel.
- Stop polling a server for new information.
- Stop waiting for an [`onKeyUp`](#onKeyUp) event.



# Browser.Navigation

 This module helps you manage the browser’s URL yourself. This is the
crucial trick when using [`Browser.application`](Browser#application).

The most important function is [`pushUrl`](#pushUrl) which changes the
address bar _without_ starting a page load.


## What is a page load?

1.  Request a new HTML document. The page goes blank.
2.  As the HTML loads, request any `<script>` or `<link>` resources.
3.  A `<script>` may mutate the document, so these tags block rendering.
4.  When _all_ of the assets are loaded, actually render the page.

That means the page will go blank for at least two round-trips to the servers!
You may have 90% of the data you need and be blocked on a font that is taking
a long time. Still blank!


## How does `pushUrl` help?

The `pushUrl` function changes the URL, but lets you keep the current HTML.
This means the page _never_ goes blank. Instead of making two round-trips to
the server, you load whatever assets you want from within Elm. Maybe you do
not need any round-trips! Meanwhile, you retain full control over the UI, so
you can show a loading bar, show information as it loads, etc. Whatever you
want!


# Navigate within Page

@docs Key, pushUrl, replaceUrl, back, forward


# Navigate to other Pages

@docs load, reload, reloadAndSkipCache



## Key

```elm
-- Opaque type: Key (constructors not exposed)
```

 A navigation `Key` is needed to create navigation commands that change the
URL. That includes [`pushUrl`](#pushUrl), [`replaceUrl`](#replaceUrl),
[`back`](#back), and [`forward`](#forward).

You only get access to a `Key` when you create your program with
[`Browser.application`](Browser#application), guaranteeing that your program is
equipped to detect these URL changes. If `Key` values were available in other
kinds of programs, unsuspecting programmers would be sure to run into some
[annoying bugs][bugs] and learn a bunch of techniques the hard way!

[bugs]: https://github.com/elm/browser/blob/1.0.2/notes/navigation-in-elements.md



## back

```elm
back : Browser.Navigation.Key -> Basics.Int -> Platform.Cmd.Cmd msg
```

 Go back some number of pages. So `back 1` goes back one page, and `back 2`
goes back two pages.

**Note:** You only manage the browser history that _you_ created. Think of this
library as letting you have access to a small part of the overall history. So
if you go back farther than the history you own, you will just go back to some
other website!



## forward

```elm
forward : Browser.Navigation.Key -> Basics.Int -> Platform.Cmd.Cmd msg
```

 Go forward some number of pages. So `forward 1` goes forward one page, and
`forward 2` goes forward two pages. If there are no more pages in the future,
this will do nothing.

**Note:** You only manage the browser history that _you_ created. Think of this
library as letting you have access to a small part of the overall history. So
if you go forward farther than the history you own, the user will end up on
whatever website they visited next!



## load

```elm
load : String.String -> Platform.Cmd.Cmd msg
```

 Leave the current page and load the given URL. **This always results in a
page load**, even if the provided URL is the same as the current one.

    gotoElmWebsite : Cmd msg
    gotoElmWebsite =
        load "https://elm-lang.org"

Check out the [`elm/url`][url] package for help building URLs. The
[`Url.absolute`][abs] and [`Url.relative`][rel] functions can be particularly
handy!

[url]: /packages/elm/url/latest
[abs]: /packages/elm/url/latest/Url#absolute
[rel]: /packages/elm/url/latest/Url#relative



## pushUrl

```elm
pushUrl : Browser.Navigation.Key -> String.String -> Platform.Cmd.Cmd msg
```

 Change the URL, but do not trigger a page load.

This will add a new entry to the browser history.

Check out the [`elm/url`][url] package for help building URLs. The
[`Url.Builder.absolute`][abs] and [`Url.Builder.relative`][rel] functions can
be particularly handy!

[url]: /packages/elm/url/latest
[abs]: /packages/elm/url/latest/Url-Builder#absolute
[rel]: /packages/elm/url/latest/Url-Builder#relative

**Note:** If the user has gone `back` a few pages, there will be &ldquo;future
pages&rdquo; that the user can go `forward` to. Adding a new URL in that
scenario will clear out any future pages. It is like going back in time and
making a different choice.



## reload

```elm
reload : Platform.Cmd.Cmd msg
```

 Reload the current page. **This always results in a page load!**
This may grab resources from the browser cache, so use
[`reloadAndSkipCache`](#reloadAndSkipCache)
if you want to be sure that you are not loading any cached resources.


## reloadAndSkipCache

```elm
reloadAndSkipCache : Platform.Cmd.Cmd msg
```

 Reload the current page without using the browser cache. **This always
results in a page load!** It is more common to want [`reload`](#reload).


## replaceUrl

```elm
replaceUrl : Browser.Navigation.Key -> String.String -> Platform.Cmd.Cmd msg
```

 Change the URL, but do not trigger a page load.

This _will not_ add a new entry to the browser history.

This can be useful if you have search box and you want the `?search=hats` in
the URL to match without adding a history entry for every single key stroke.
Imagine how annoying it would be to click `back` thirty times and still be on
the same page!

**Note:** Browsers may rate-limit this function by throwing an exception. The
discussion [here](https://bugs.webkit.org/show_bug.cgi?id=156115) suggests
that the limit is 100 calls per 30 second interval in Safari in 2016. It also
suggests techniques for people changing the URL based on scroll position.


