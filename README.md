# gaming

halcyon's gaming packages — Fedora 44 (+45) RPMs built on
[Copr](https://copr.fedorainfracloud.org/coprs/aahsnr-work/gaming/).

- **protonplus** — the [ProtonPlus](https://github.com/Vysp3r/ProtonPlus)
  compatibility tools manager, built from upstream's release tags.
- **heroic-games-launcher** — the
  [Heroic Games Launcher](https://heroicgameslauncher.com/), repackaged from
  upstream's official release RPM (x86_64 only).

```
install -Dm644 repo/gaming.repo /etc/yum.repos.d/
dnf install protonplus heroic-games-launcher
```

(or `dnf copr enable aahsnr-work/gaming fedora-44`.)

To leave again: `rm /etc/yum.repos.d/gaming.repo`.

A sibling repo of the six halcyon group repositories: base-pkgs · cli-tools ·
applications · fonts · texlive-packages · linux-p03.

## CI

- `copr-build.yml` — a push to `main` rebuilds changed packages plus every
  higher batch, wave-by-wave. Gated on the `CASCADE_ENABLED` repository
  variable (kill-switch; `workflow_dispatch` bypasses it). PRs validate
  only.
- `update.yml` — the daily version sweep (04:17 UTC, plus manual dispatch)
  moves protonplus and heroic-games-launcher to their newest GitHub
  releases, commits the bump to `main` and dispatches `copr-build.yml` for
  the bumped packages.
- `builder-docker.yml` — builds this repo's own CI job image and pushes it
  to `ghcr.io/halcyon-linux/gaming-builder:f44` (consumed by this repo's
  build and sweep jobs).
- `repoclosure.yml` — nightly (05:43 UTC) + post-cascade closure check of
  the published Copr repo against Fedora 44/45.

## Running and cancelling workflows

### Run a workflow manually

In the GitHub UI: **Actions** → the workflow → **Run workflow** → branch `main` →
fill the inputs → **Run workflow**. From the CLI:

```bash
gh workflow run <file> -R halcyon-linux/gaming --ref main -f <input>=<value>
```

Inputs (leave empty for the default):

- `copr-build.yml` — `only`: space-separated packages to build (empty = all), e.g. `-f only="<pkg> <pkg>"`. Bypasses the `CASCADE_ENABLED` gate.
- `update.yml` — `mode`: `commit` or `pr`; `pkg`: space-separated packages to sweep (empty = all).
- `repoclosure.yml`, `builder-docker.yml` — no inputs.

### Force-cancel a workflow run

1. Find the run ID: `gh run list -R halcyon-linux/gaming --workflow <file>`.
2. Cancel it: `gh run cancel <run-id> -R halcyon-linux/gaming`, or **Cancel workflow**
   on the run page.
3. If it stays in *Cancelling* because a job or runner is hung, use **Force cancel**
   on the run page, or:

   ```bash
   gh api -X POST repos/halcyon-linux/gaming/actions/runs/<run-id>/force-cancel
   ```

A force cancel ends the run without waiting for its jobs. It does not stop Copr
builds that were already submitted; cancel those on the Copr project page.

**Caution:** if a `update.yml` run is cancelled after it has pushed a bump, that bump can be left without a `copr-build` run. Dispatch `copr-build.yml` with `only` set to the bumped packages.

## Layout

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
   cascade gate). 
