[![](https://img.shields.io/crates/v/wry?style=flat-square)](https://crates.io/crates/wry) [![](https://img.shields.io/docsrs/wry?style=flat-square)](https://docs.rs/wry/)
[![License](https://img.shields.io/badge/License-MIT%20or%20Apache%202-green.svg)](https://opencollective.com/tauri)
[![Chat Server](https://img.shields.io/badge/chat-discord-7289da.svg)](https://discord.gg/SpmNs4S)
[![website](https://img.shields.io/badge/website-tauri.app-purple.svg)](https://tauri.app)
[![https://good-labs.github.io/greater-good-affirmation/assets/images/badge.svg](https://good-labs.github.io/greater-good-affirmation/assets/images/badge.svg)](https://good-labs.github.io/greater-good-affirmation)
[![support](https://img.shields.io/badge/sponsor-Open%20Collective-blue.svg)](https://opencollective.com/tauri)

Wry is a cross-platform WebView rendering library.

The webview requires a running event loop and a window type that implements [`HasWindowHandle`],
or a gtk container widget if you need to support X11 and Wayland.
You can use a windowing library like [`tao`] or [`winit`].

### Examples

This example leverages the [`HasWindowHandle`] and supports Windows, macOS, iOS, Android and Linux (X11 Only).
See the following example using [`winit`]:

```rust
#[derive(Default)]
struct App {
  window: Option
,
  webview: Option
,
}

impl ApplicationHandler for App {
  fn resumed(&mut self, event_loop: &ActiveEventLoop) {
    let window = event_loop.create_window(Window::default_attributes()).unwrap();
    let webview = WebViewBuilder::new()
      .with_url("https://tauri.app")
      .build(&window)
      .unwrap();

    self.window = Some(window);
    self.webview = Some(webview);
  }

  fn window_event(&mut self, _event_loop: &ActiveEventLoop, _window_id: WindowId, event: WindowEvent) {}
}

let event_loop = EventLoop::new().unwrap();
let mut app = App::default();
event_loop.run_app(&mut app).unwrap();
```

If you also want to support Wayland too, then we recommend you use [`WebViewBuilderExtUnix::build_gtk`] on Linux.
See the following example using [`tao`]:

```rust
let event_loop = EventLoop::new();
let window = WindowBuilder::new().build(&event_loop).unwrap();

let builder = WebViewBuilder::new().with_url("https://tauri.app");

#[cfg(not(target_os = "linux"))]
let webview = builder.build(&window).unwrap();
#[cfg(target_os = "linux")]
let webview = builder.build_gtk(window.gtk_window()).unwrap();
```

### Child webviews

You can use [`WebViewBuilder::build_as_child`] to create the webview as a child inside another window. This is supported on
macOS, Windows and Linux (X11 Only).

```rust
#[derive(Default)]
struct App {
  window: Option
,
  webview: Option
,
}

impl ApplicationHandler for App {
  fn resumed(&mut self, event_loop: &ActiveEventLoop) {
    let window = event_loop.create_window(Window::default_attributes()).unwrap();
    let webview = WebViewBuilder::new()
      .with_url("https://tauri.app")
      .with_bounds(Rect {
        position: LogicalPosition::new(100, 100).into(),
        size: LogicalSize::new(200, 200).into(),
      })
      .build_as_child(&window)
      .unwrap();

    self.window = Some(window);
    self.webview = Some(webview);
  }

  fn window_event(&mut self, _event_loop: &ActiveEventLoop, _window_id: WindowId, event: WindowEvent) {}
}

let event_loop = EventLoop::new().unwrap();
let mut app = App::default();
event_loop.run_app(&mut app).unwrap();
```

If you want to support X11 and Wayland at the same time, we recommend using
[`WebViewExtUnix::new_gtk`] or [`WebViewBuilderExtUnix::build_gtk`] with [`gtk::Fixed`].

```rust
let event_loop = EventLoop::new();
let window = WindowBuilder::new().build(&event_loop).unwrap();

let builder = WebViewBuilder::new()
  .with_url("https://tauri.app")
  .with_bounds(Rect {
    position: LogicalPosition::new(100, 100).into(),
    size: LogicalSize::new(200, 200).into(),
  });

#[cfg(not(target_os = "linux"))]
let webview = builder.build_as_child(&window).unwrap();
#[cfg(target_os = "linux")]
let webview = {
  let vbox = window.default_vbox().unwrap(); // tao adds a gtk::Box by default
  let fixed = gtk::Fixed::new();
  fixed.show_all();
  vbox.pack_start(&fixed, true, true, 0);
  builder.build_gtk(&fixed).unwrap()
};
```

### Platform Considerations

Here is the underlying web engine each platform uses, and some dependencies you might need to install.

#### Linux

[WebKitGTK](https://webkitgtk.org/) is used to provide webviews on Linux which requires GTK,
so if the windowing library doesn't support GTK (as in [`winit`])
you'll need to call [`gtk::init`] before creating the webview and then call [`gtk::main_iteration_do`] alongside
your windowing library event loop.

```rust
#[derive(Default)]
struct App {
  webview_window: Option<(Window, WebView)>,
}

impl ApplicationHandler for App {
  fn resumed(&mut self, event_loop: &ActiveEventLoop) {
    let window = event_loop.create_window(Window::default_attributes()).unwrap();
    let webview = WebViewBuilder::new()
      .with_url("https://tauri.app")
      .build(&window)
      .unwrap();

    self.webview_window = Some((window, webview));
  }

  fn window_event(&mut self, _event_loop: &ActiveEventLoop, _window_id: WindowId, event: WindowEvent) {}

  // Advance GTK event loop