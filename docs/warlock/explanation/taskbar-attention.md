# Active windows and attention requests

Warlock derives taskbar indicators from native window observations. A window that requests attention gets an amber top edge and an Attention label while it is inactive. The active window gets a blue bottom edge and an Active label. Attention alone leaves the current keyboard recipient unchanged.

Taskbar entries represent application families. Eligible transient/modal members contribute attention to their root family; the entry appears once. Active state takes precedence when a family is active. Grouping and control identity use native incarnations and application identity, while the native observation and coherent frontend projection determine the displayed state.

The visible distinction also reaches accessibility consumers. The taskbar exports named toggle buttons under its toolbar: the active entry is pressed/current, and the inactive attention entry is unpressed with an Attention label. These exported states let a reader distinguish the entries without relying on colour. Clicking an inactive entry uses the ordinary activation path; resulting native focus and urgency observations update the indicator.

The current [UX-009 evidence](../../../implementation/warlock/qa/evidence/attention-native-composed-20261030/LIMITS.md) includes an isolated native recording, actual AT-SPI nodes, a physical activation and real keyboard recipient. Independent review accepts the original indicator scenario on its recorded tuple. The native recording uses one scale-1 output and two single-family GTK applications. Modal aggregation has separate production replay coverage; this recording does not qualify every family/theme/output combination or full accessibility behaviour.

The fixture also illustrates why evidence ownership matters. An older check assumed a 48px bar, while the actual shared host and CSS both allocate/reserve 56px. The corrected check binds full controls to the configure-qualified viewport, action scrollport and screenshot. A separate inherited click helper required an exact publication/control stamp; supplying a bare point failed before input. Both failures remain retained, and the repaired fixture preserves the original visibility and current-identity requirements.

See [ownership and lifetimes](ownership-and-lifetimes.md), [status and evidence](../reference/status-and-evidence.md), and [verification](../how-to/verify-selected-change.md) for the boundaries between observed state, commands and original acceptance.
