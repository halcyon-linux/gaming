# gaming

halcyon's gaming snapshot packages — Fedora 44 (+45) RPMs built on
[Copr](https://copr.fedorainfracloud.org/coprs/aahsnr-work/gaming/).

Currently **mesa-git** — the tip of upstream
[mesa](https://gitlab.freedesktop.org/mesa/mesa) main, Intel + AMD only,
built as a drop-in replacement for Fedora's mesa — **protonplus**, the
[ProtonPlus](https://github.com/Vysp3r/ProtonPlus) compatibility tools
manager built from its release tags, and **heroic-games-launcher**, the
[Heroic Games Launcher](https://heroicgameslauncher.com/) repackaged from
upstream's official release RPM. The mesa binary packages keep the
`mesa-*` names, so enabling this repo with priority=1 upgrades Fedora's
mesa in place:

```
install -Dm644 repo/gaming.repo /etc/yum.repos.d/
dnf upgrade
```

(or `dnf copr enable aahsnr-work/gaming fedora-44`, then merge the
`priority=1` line and the i386 stanza from `repo/gaming.repo` into the
generated file — the copr plugin sets neither.)

To leave again: `rm /etc/yum.repos.d/gaming.repo && dnf distro-sync`.

A sibling repo of the six halcyon group repositories: base-pkgs · cli-tools ·
applications · fonts · texlive-packages · linux-p03.

## What mesa-git is

- Upstream `main` tracking: the weekly sweep (or a manual dispatch) re-pins
  the newest main commit; `Version` runs `27.0.0^N.git<shortcommit>`, and the
  caret keeps every snapshot sorting above upstream's own release of that
  base version.
- A Fedora-flags build with the gaming knobs the macro cannot express:
  asserts off (`b_ndebug=true`), LTO off (LTO breaks games — the spec comment
  links the bug).
- Intel + AMD: radeonsi/RADV, iris/ANV + hasvk, crocus, i915, zink,
  llvmpipe/lavapipe, virgl/venus, VA-API — plus the 32-bit half in the i386
  chroot for Steam/Proton multilib.
- Codecs stay at mesa's default `all_free` set (no h264/h265 decode) — Copr
  policy. Codec-enabled VA-API is RPM Fusion's `mesa-freeworld`, and mixing
  it with this repo's priority=1 does not work (see `repo/gaming.repo`).

## CI

- `copr-build.yml` — a push to `main` rebuilds changed packages plus every
  higher batch, wave-by-wave. Gated on the `CASCADE_ENABLED` repository
  variable (kill-switch; `workflow_dispatch` bypasses it). PRs validate
  only.
- `update.yml` — the weekly version sweep (Monday 04:17 UTC, plus manual
  dispatch) re-pins mesa-git to the newest main commit and protonplus +
  heroic-games-launcher to their newest GitHub releases. Deliberately no
  workflow_run chain: mesa main moves all day and sweeping after every build
  would chase the tip forever.
- `builder-docker.yml` — builds this repo's own CI job image and pushes it
  to `ghcr.io/halcyon-linux/gaming-builder:f44` (consumed by this repo's
  build and sweep jobs).
- `repoclosure.yml` — nightly (05:43 UTC) + post-cascade closure check of
  the published Copr repo against Fedora 44/45.

## Layout

- `pkgs/mesa-git/` — the spec (+ the MLAA license email it ships as doc)
- `pkgs/protonplus/` — the spec (release-tag tracking)
- `pkgs/heroic-games-launcher/` — the spec (vendor-RPM rewrap: release-tag
  tracking + bundled-binary pins)
- `ci/packages.toml` — the registry: batch + sweep feed. A package without
  an entry is never built.
- `ci/matrix.py` — build selection; `ci/sweep/` — the version sweeper
- `repo/gaming.repo` — the consumer drop-in (priority=1, both stanzas)
- `.github/` — the workflows + the CI job image

## Bringing this repo online (one-time)

1. **GitHub**: create `halcyon-linux/gaming` and push this tree. Let the
   `builder-image` workflow run once to publish
   `ghcr.io/halcyon-linux/gaming-builder:f44`.
2. **Copr**: create project `aahsnr-work/gaming` with four chroots. No
   external repos are needed in any chroot:

   ```bash
   copr-cli create --chroot fedora-44-x86_64 --chroot fedora-44-i386 \
                   --chroot fedora-45-x86_64 --chroot fedora-45-i386 gaming
   ```
3. **Secrets/vars**: set the repository secret `COPR_CLICONF` (Copr API
   token) and — when ready — the repository variable `CASCADE_ENABLED=true`
   (leave it unset until the first green build). Optional: `UPDATE_MODE=pr`
   to review bumps instead of auto-committing them.
4. **First build**: Actions → copr-build → Run workflow (bypasses the
   cascade gate). Source0 is ~130 MB and the four-chroot build is hours.
