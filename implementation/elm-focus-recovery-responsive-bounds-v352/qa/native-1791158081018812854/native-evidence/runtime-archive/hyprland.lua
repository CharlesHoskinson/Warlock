hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="1600x1200@60",position="0x0",scale=2})

-- Crash handoff: X11 is outside this private fixture.
hl.config({ xwayland = { enabled = false } })
