// The model is the only source of components, connections and flow steps.
export function adapt(model) {
  const nodes = new Map(model.nodes.map(node => [node.id, node]));
  function match(step) {
    const candidates = model.edges.map((edge, index) => ({edge, index})).filter(({edge}) => edge.from === step.from && edge.to === step.to);
    if (candidates.length === 1) return candidates[0];
    const matching = candidates.filter(({edge}) => edge.messages.some(message => step.message.includes(message) || message.includes(step.message)));
    if (matching.length === 1) return matching[0];
    // The supplied flows follow the ordinary runtime, not cancellationOptIn.
    const ordinary = matching.filter(({edge}) => !edge.channel.includes('cancellationOptIn'));
    return ordinary.length === 1 ? ordinary[0] : null;
  }
  return {model, nodes, match};
}
