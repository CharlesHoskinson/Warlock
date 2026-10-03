# WindowAccessibility

Quickshell 0.3.1 constructs a temporary QCoreApplication, deletes it, then
constructs its lasting QGuiApplication. Qt 6.11.2's post-routine clears the
constructor-installed accessibility factories when that first application is
destroyed. QQuickWindow and QQuickItem consequently have no accessible interfaces.

The native probe in `~/window-integration-qa/accessibility-probe/native.cpp`
reports one accessible application child with ordinary startup, and no window
interface/zero children with the recreated application sequence.

This QML extension reinstalls Qt Quick's factory dispatch after lasting GUI
application startup. It uses Qt's existing window/item/text implementations;
actions are ordinary Accessible attached properties in the actual UI. V2 adds
Qt's standard ShowMenu action for items that implement `accessibleShowMenu()`;
the handler is the same context-menu path used by the mouse/keyboard.

Sources:
- https://github.com/qt/qtbase/blob/v6.11.2/src/gui/accessible/qaccessible.cpp
- https://github.com/qt/qtdeclarative/blob/v6.11.2/src/quick/util/qquickglobal.cpp
- https://github.com/quickshell-mirror/quickshell/blob/v0.3.1/src/launch/launch.cpp
- https://github.com/qt/qtdeclarative/blob/v6.11.2/src/quick/accessible/qquickaccessiblefactory.cpp

Build with `cmake -S . -B build-make -G 'Unix Makefiles'
-DWINDOW_ACCESSIBILITY_MODULE_DIR=/path/to/fresh/module` and
`cmake --build build-make -j 2`. Copy qmldir and update imports for that directory.
**Never rebuild over a loaded library:** stop all importing processes or change
the output/module directory first. Current consumers: hypr-window-controls uses
the retained V1 artifact; the main shell taskbar and Task View use V2.

Private Qt headers tie this library to Qt 6.11.2. The registerTypes guard skips
factory installation if the runtime Qt version differs; rebuild and repeat
`python3 ~/window-integration-qa/live_accessible_controls.py` after a Qt update.
Qt's existing interface semantics and event bridge remain in use.
