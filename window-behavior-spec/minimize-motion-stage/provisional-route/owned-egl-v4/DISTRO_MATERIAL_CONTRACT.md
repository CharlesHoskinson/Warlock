# Exact Arch Mesa material compatibility (before code change)

Executed owned-EGL v2 refuses the runtime backend before snapshot upload or
readiness. This candidate preserves that evidence and adds diagnostic strings
before rejection. It supports the exact audited release token `Mesa 26.2.2`
and the exact Arch build token `Mesa 26.2.2-arch1.1`; each must end or be followed
by whitespace metadata. Numeric/development/other Arch suffixes remain refused,
as do software/swrast/llvmpipe/softpipe/SWR and Zink renderers.

Official Arch tag1-26.2.2-1 resolves to commit51128a667749367aa02787609346a82f034bc24d.
Its PKGBUILD SHA998b28c8d7435aa826404348fb47a23d7d7f1351f1198d9f105edbc2f59ef86a
matches the cached same-build split package's BUILDINFO exactly. Its upstream
archive checksum eeb29ca7e56cfaa8e8a79538dcf834e3b18e501c31bef5145e959ea437cc4216
matches the retained official Mesa26.2.2 archive. The source array contains that
archive/signature and Rust crate archives, with no patch entries. prepare has a
dormant patch loop and changes only VERSION to26.2.2-arch1.1. Therefore the
reviewed src/egl/drivers/dri2/platform_wayland.c commit path is unchanged by the
Arch package recipe. Installed pacman integrity reports127files/0altered.

The producer must also verify the exact installed gallium and Mesa-EGL hashes
and their actual mapped device/inode/buildID identity through same-domain kernel queries (see MAPPED_MATERIAL_CONTRACT.md) before backend readiness. A path
string or version string alone is insufficient. These checks occur once at
owned context initialization, never per animation frame. Diagnostics report
actual vendor/renderer/version and material success without native authority.
No GL connection or native display was used to prepare this provenance.
