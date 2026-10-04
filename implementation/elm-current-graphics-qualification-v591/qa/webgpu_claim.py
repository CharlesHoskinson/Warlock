"""Separate API/compute claims; never infer hardware or WGSL rendering."""
def classify(body):
    result={'status':'invalid','capabilityRecordValid':False,'computeResultQualified':False,'hardwareQualified':False,'wgslRenderQualified':False}
    if not isinstance(body,dict) or type(body.get('secureContext')) is not bool:return result
    gpu=body.get('webgpu')
    if not isinstance(gpu,dict) or type(gpu.get('exposed')) is not bool:return result
    status=gpu.get('status')
    if status not in ('unavailable','no-adapter','executed','failed'):return result
    if status=='unavailable':valid=not gpu['exposed']
    else:valid=gpu['exposed'] and body['secureContext']
    if status=='executed':valid=valid and isinstance(gpu.get('adapter'),dict) and type(gpu.get('value')) is int and gpu['value']==42 and gpu.get('validation','missing') is None
    result.update(status=status,capabilityRecordValid=valid,computeResultQualified=valid and status=='executed')
    return result
