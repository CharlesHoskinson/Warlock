# GTK sibling and reparent fixture

Extend held canonical GTK fixture244 for the original GTK05 sibling/reparent
obligation in plan234. Preserve A/B/C/D/P input, resource and draft journals,
canonical runtime checks, callback lifetime guards and both group profiles.
Add a sixth role E: an actual modal GtkWindow initially transient for A, which
can be explicitly reparented to live A or B. Never substitute independent C
for a modal sibling. Actual Wayland/native parent and input qualification remain
required; requested GTK state alone does not prove compositor behavior.

Retire descendants before their owner using actual current GTK transient
relationships. Closing B retires E only while E belongs to B; E under A and
independent C survive. Closing A retires its popup and all transient descendants;
quit retires all six roles. Preserve original command sequence and failure rules.
Compile the real fixture and exercise parser/callback/lifecycle controls before
source hold. No native or full GTK01–08 acceptance is inferred from CPU evidence.
