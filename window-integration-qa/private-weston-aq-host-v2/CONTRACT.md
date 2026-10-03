# Private host with negotiated Aquamarine globals

This adapter retains signed/private hostV2 and its1728 recorded dependencies
unchanged. It verifies that base manifest and a separate frozen private
Aquamarine build. Only the explicit `/usr/bin/Hyprland` child receives the
additional private library directory. Weston and the private bus keep their
graphics libraries. This V2 adapter selects the memory GSettings backend for
the private host tree to avoid creating a dconf service which outlives setup.
It copies the supplied environment; the original main env remains unchanged.
No system library is replaced. The V1 adapter and failed run are retained.
The same context API, scope/runtime/socket/Xwayland guards and client-first
teardown are inherited. A changed compatibility artifact refuses launch.

The actual child maps must contain the exact frozen private Aquamarine path/hash
and exclude the installed Aquamarine path. The official server advertisement
remains unchanged. Required protocol refusal and real hardware renderer/DMA-BUF
are separate gates. Actual foundation acceptance remains unproved until the
new private run passes all checks and complete cleanup/main preservation.
