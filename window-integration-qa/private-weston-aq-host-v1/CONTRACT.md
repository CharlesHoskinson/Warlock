# Private host with negotiated Aquamarine globals

This adapter retains signed/private hostV2 and its1728 recorded dependencies
unchanged. It verifies that base manifest and a separate frozen private
Aquamarine build. Only the explicit `/usr/bin/Hyprland` child receives the
additional private library directory. Weston, private bus, original main env
and fixtures keep their prior environment; no system library is replaced.
The same context API, scope/runtime/socket/Xwayland guards and client-first
teardown are inherited. A changed compatibility artifact refuses launch.

The actual child maps must contain the exact frozen private Aquamarine path/hash
and exclude the installed Aquamarine path. The official server advertisement
remains unchanged. Required protocol refusal and real hardware renderer/DMA-BUF
are separate gates. Actual foundation acceptance remains unproved until the
new private run passes all checks and complete cleanup/main preservation.
