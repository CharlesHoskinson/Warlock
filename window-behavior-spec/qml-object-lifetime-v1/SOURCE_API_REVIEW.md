# Primary API review and limits

Installed /usr/include/qt6/QtQml/qqmlengine.h provides the QQmlEngine constructor, contextForObject and singletonInstance<QObject*> by URI/type. /usr/include/qt6/QtQml/qqml.h declares qmlEngine(const QObject*). The singleton registration callback receives its actual engine; this is the proposed source of engine identity. The [Qt QQmlEngine documentation](https://doc.qt.io/qt-6/qqmlengine.html) describes the public singleton/context APIs. Documentation version currently resolves to 6.12; the proposal relies on the inspected installed declarations, without assuming later API additions.

Installed QtCore/qpointer.h provides guarded QObject pointers. The [Qt QPointer documentation](https://doc.qt.io/qt-6/qpointer.html) explains that destruction clears a guarded pointer; this supports weak lifetime observation, not an owning lock or atomic guarantee through arbitrary reentrant calls.

Installed Quickshell core.qmltypes names the actual exported QuickshellGlobal singleton, constant processId and reloadCompleted/reloadFailed. The proposal obtains that actual singleton through the engine, rather than accepting a QObject supplied by QML as a fake signal source. Metadata availability does not prove its installed reload internals. No reload-start signal is exposed here; this is an explicit unresolved observation limit.

Installed bits/dlfcn.h defines RTLD_NOLOAD/RTLD_NODELETE. The [Linux dlopen manual](https://man7.org/linux/man-pages/man3/dlopen.3.html) describes pinning already-loaded objects and preventing unload/reset of static data. Actual CPU DSO tests and exact image/mapping/dependency guards remain required before accepting this proposed persistent registry design. No provider runtime has been implemented or loaded.
