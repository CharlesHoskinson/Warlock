import QtQuick
import Quickshell
import "SwitcherState.js" as SwitcherState

Item {
    id: controller
    property string session: Quickshell.env("HYPRLAND_INSTANCE_SIGNATURE")
    property var machine: SwitcherState.create(session, String(Date.now())+"-"+String(Math.random()))
    readonly property bool pending: machine.phase === "pending"
    readonly property bool presentationOpen: machine.phase === "open" && !machine.released
    readonly property int selected: machine.selected
    readonly property var request: machine.request || ({})
    signal restoreRequested(string epoch, int generation, string token)
    function apply(transition) {
        machine=transition.state
        if(transition.effect)restoreRequested(transition.effect.epoch,transition.effect.generation,transition.effect.token)
        return JSON.stringify({accepted:transition.accepted,builder:transition.builder,
            epoch:machine.epoch,generation:machine.generation,token:machine.token})
    }
    function step(session, generation, ordinal, direction) { return apply(SwitcherState.step(machine,session,generation,ordinal,direction)) }
    function barrier(session,generation) {return apply(SwitcherState.barrier(machine,session,generation))}
    function release(session, generation, ordinal) { return apply(SwitcherState.release(machine,session,generation,ordinal)) }
    function ready(epoch, generation, token, payload) {
        var request
        try { request=JSON.parse(payload) } catch(error) { return cancel(generation,token) }
        return apply(SwitcherState.ready(machine,epoch,generation,token,request))
    }
    function cancel(generation,token) { return apply(SwitcherState.cancel(machine,generation,token)) }
    function claim(epoch,generation,token) {
        var result=SwitcherState.claim(machine,epoch,generation,token);machine=result.state
        return JSON.stringify(result.candidate)
    }
    function choose(index) { return apply(SwitcherState.choose(machine,index)) }
    function commitSelection(index) {
        choose(index)
        var ordinals=Object.keys(machine.steps).map(Number)
        if(!ordinals.length)return cancel()
        return release(machine.session,machine.generation,Math.max.apply(Math,ordinals))
    }
    Timer { interval:3000; running:controller.pending; onTriggered:controller.cancel() }
    Timer { interval:30000; running:controller.machine.phase === "open"; onTriggered:controller.cancel() }
}
