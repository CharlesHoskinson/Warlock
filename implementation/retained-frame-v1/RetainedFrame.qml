pragma ComponentBehavior: Bound
import QtQuick
import Quickshell.Wayland

// Client-only bounded research component. No native window state changes.
Item {
    id: root
    width: 300
    height: 180
    property var source: null
    // Caller must provide stableId + pid + generation, never address alone.
    property string sourceIdentity: ""
    property int generation: 0
    property int maxNativePixels: 8294400
    property int maxSnapshotPixels: 54000
    readonly property bool ready: phase === "retained"
    readonly property string fidelity: "client surfaces; no server decorations"
    property string phase: "idle"
    property string retainedIdentity: ""
    property int retainedGeneration: -1
    signal snapshotReady(string identity, int generation)
    signal refused(string reason)

    function reset() {
        phase = "idle"
        snapshot.active = false
        capture.captureSource = null
        retainedIdentity = ""
        retainedGeneration = -1
    }
    function acquire() {
        reset()
        if (!source || !/^[^:]+:[1-9][0-9]*:[0-9]+$/.test(sourceIdentity)
                || sourceIdentity.split(":")[2] !== String(generation) || width <= 0 || height <= 0
                || width * height > maxSnapshotPixels) {
            refused("source identity or snapshot budget invalid")
            return
        }
        retainedIdentity = sourceIdentity
        retainedGeneration = generation
        phase = "capturing"
        capture.captureSource = source
    }
    function freeze() {
        if (phase !== "capturing" || !capture.hasContent) return
        if (capture.sourceSize.width <= 0 || capture.sourceSize.height <= 0
                || capture.sourceSize.width * capture.sourceSize.height > maxNativePixels) {
            reset()
            refused("native source exceeds budget")
            return
        }
        phase = "freezing"
        snapshot.active = true
    }
    onSourceIdentityChanged: reset()
    onGenerationChanged: reset()
    onSourceChanged: {
        // A destroyed source may become null: retain the independent snapshot.
        if (phase !== "retained" || source !== null) reset()
    }
    onWidthChanged: reset()
    onHeightChanged: reset()

    ScreencopyView {
        id: capture
        width: root.width
        height: root.height
        live: false
        paintCursor: false
        onHasContentChanged: {
            if (hasContent) root.freeze()
            else if (root.phase === "freezing") {
                root.reset()
                root.refused("source stopped before snapshot completion")
            }
        }
    }
    Loader {
        id: snapshot
        anchors.fill: parent
        active: false
        sourceComponent: ShaderEffectSource {
            id: retainedTexture
            Component.onCompleted: {
                if (root.phase === "freezing") retainedTexture.scheduleUpdate()
            }
            sourceItem: capture
            live: false
            hideSource: true
            textureSize: Qt.size(root.width, root.height)
            width: root.width
            height: root.height
            recursive: false
            onScheduledUpdateCompleted: {
                if (root.phase !== "freezing" || root.retainedIdentity !== root.sourceIdentity
                        || root.retainedGeneration !== root.generation) return
                root.phase = "retained"
                // Frozen offscreen texture has its own lifetime. Do not reschedule
                // it after the capture source clears. This signal is not proof
                // that the snapshot was presented on a physical output.
                capture.captureSource = null
                root.snapshotReady(root.retainedIdentity, root.retainedGeneration)
            }
        }
    }
}
