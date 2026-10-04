hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
hl.monitor({output="WAYLAND-2",mode="800x600@60",position="1000x100",scale=1})

-- Crash handoff: X11 is outside this private fixture.
hl.config({ xwayland = { enabled = false } })
