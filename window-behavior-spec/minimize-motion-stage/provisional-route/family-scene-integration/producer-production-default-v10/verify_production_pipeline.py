"""Exact launch-role observation gate. Never grants pixels or native authority."""
ROLES={
    'production-default':(False,False,True,True),
    'diagnostic-default':(True,False,True,True),
    'diagnostic-over-experiment':(True,True,True,True),
    'diagnostic-manual-experiment':(True,True,True,False),
}


def verify_selection(events,role):
    if role not in ROLES:raise ValueError('explicit expected launch role required')
    raster,experiment,manual,over=ROLES[role]
    expected={'event':'renderPipelineSelected','role':role,'explicitExperiment':experiment,
        'rasterDiagnostic':raster,'manualSampling':manual,'quantizedOver':over,
        'nativeAuthority':False,'pixelProof':False}
    observed=[event for event in events if event.get('event')=='renderPipelineSelected']
    if len(observed)!=1 or set(observed[0])!=set(expected) or any(observed[0][key]!=value or type(observed[0][key]) is not type(value) for key,value in expected.items()):
        raise ValueError('actual immutable default/experiment launch role differs')
    return {'launchRole':role,'repairedDefault':not experiment,'actualModeSelectionGate':True,'pixelProof':False,'nativeAuthority':False}
