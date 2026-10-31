// Packets retain the controller's exact binding and request identity.
export const packet = (request, kind, fields) => ({protocolVersion:3, kind, binding:request.binding, requestId:request.requestId, ...fields});
export const clone = value => structuredClone(value);
export const read = (ctx, name, fallback) => clone(ctx.readWorld().services?.[name] ?? fallback);
export const nextRevision = revision => (BigInt(revision) + 1n).toString();
export function registerRead(host, requestKind, responseKind, name, fallback) {
  return host.registerService(requestKind, (request, ctx) => {
    if (!ctx.signal.aborted) ctx.reply(packet(request, responseKind, {snapshot:read(ctx,name,fallback)}));
  });
}
// The transaction checks the revision again inside the host's serialized update.
export function mutate(ctx, name, fallback, revision, change) {
  let result = null;
  const committed = ctx.transact(world => {
    const current = clone(world.services?.[name] ?? fallback);
    if (current.revision !== revision) return world;
    const next = change(current);
    if (!next) return world;
    next.revision = nextRevision(current.revision);
    world.services = {...world.services, [name]:next}; result = clone(next);
    return world;
  });
  return committed && result ? result : null;
}
