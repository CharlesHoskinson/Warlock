hl.config({xwayland={enabled=false},animations={enabled=false},general={border_size=1}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})

-- Crash handoff: X11 is outside this private fixture.
hl.config({ xwayland = { enabled = false } })
