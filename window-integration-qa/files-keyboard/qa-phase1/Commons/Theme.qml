pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Io

// Palette + structural tokens. Reads the active Omarchy theme's colors.toml
// (live, watched) and falls back to Tokyo Night. In a packaged plugin this
// file would be replaced by `qs.Commons.Color` / `Style` from the shell.
QtObject {
  id: root; objectName:"Theme.root"
  readonly property string home: Quickshell.env("HOME")
  readonly property string themeFile: home + "/.local/state/omarchy/current/theme/colors.toml"

  property var raw: ({})
  function c(key, fb) { var v = raw[key]; return (typeof v === "string" && v.length) ? v : fb }

  readonly property color accent: c("accent", "#7aa2f7")
  readonly property color bg: c("background", "#1a1b26")
  readonly property color bgDark: c("dark_background", "#13141c")
  readonly property color bgDarker: c("darker_background", "#0e0e14")
  readonly property color bgLight: c("lighter_background", "#24283b")
  readonly property color fg: c("foreground", "#a9b1d6")
  readonly property color fgBright: c("bright_foreground", "#c0caf5")
  readonly property color fgDim: c("dark_foreground", "#565f89")
  readonly property color muted: c("muted", "#414868")
  readonly property color selection: c("selection", "#292e42")
  readonly property color red: c("red", "#f7768e")
  readonly property color green: c("green", "#9ece6a")
  readonly property color yellow: c("yellow", "#e0af68")
  readonly property color orange: c("orange", "#eb927b")
  readonly property color cyan: c("bright_cyan", c("cyan", "#449dab"))
  readonly property color blue: c("blue", "#7aa2f7")
  readonly property color magenta: c("magenta", "#ad8ee6")
  readonly property var palette: [blue, magenta, cyan, green, yellow, orange, red, accent]

  function byKey(k) { return ({ accent: accent, green: green, magenta: magenta, orange: orange, cyan: cyan, yellow: yellow, red: red, blue: blue })[k] || fg }
  function alpha(col, a) { return Qt.rgba(col.r, col.g, col.b, a) }
  readonly property color line: alpha(fg, 0.13)
  readonly property color lineStrong: alpha(fg, 0.28)
  readonly property color hover: alpha(fg, 0.07)

  // Hyprland decoration:rounding (0 on Omarchy = square corners)
  property int radius: 0
  readonly property string font: "JetBrainsMono Nerd Font"
  readonly property int fsBody: 12
  readonly property int fsSmall: 10
  readonly property int fsLabel: 9
  readonly property int fsTitle: 26
  readonly property int fsHead: 15

  readonly property int dFast: 110
  readonly property int dMed: 180

  property FileView _f: FileView {
    path: root.themeFile
    watchChanges: true
    onFileChanged: reload()
    onLoaded: root.parse(text())
  }
  function parse(t) {
    var o = {}
    var lines = String(t).split("\n")
    for (var i = 0; i < lines.length; i++) {
      var m = lines[i].match(/^\s*([A-Za-z_]+)\s*=\s*"?(#[0-9a-fA-F]{3,8})"?/)
      if (m) o[m[1]] = m[2]
    }
    raw = o
  }
}
