"""Truthful aggregate cleanup gate, including actual supervised activation proof."""
def cleanup_passed(evidence):
 return (not any(evidence.get(k) for k in ('cleanupErrors','unexpectedInnerDescendants','remainingDescendants','privateActivationCleanupError','privateActivationPostRetirementError'))
  and evidence.get('runtimeGone') is True and evidence.get('privateActivationCleanupPassed') is True
  and type(evidence.get('privateActivationPostRetirement')) is dict and evidence['privateActivationPostRetirement'].get('passed') is True)
