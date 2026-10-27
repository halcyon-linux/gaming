# CLAUDE.md

RPM source repo for halcyon's gaming packages, built on Fedora Copr
(`aahsnr-work/gaming`, chroots fedora-44/45 × x86_64 + i386). The repo holds
only specs, the registry, the version sweeper and the workflows; Copr owns the
build farm, GPG signing and repo hosting. GitHub: `halcyon-linux/gaming`.

Packages:

- `protonplus` — Vala/GTK4 build from upstream release tags (meson).
- `heroic-games-launcher` — rewrap of upstream's vendor RPM (x86_64 only).

## Ground rules

- **Never build or install locally** (no podman/mock/rpmbuild/dnf test runs).
  Copr is where packages are built and verified; CI submits to it.
- Don't commit, push or touch the Copr project unless asked.
- Code, `ci/packages.toml` and the workflows are the source of truth.

## Files to ignore

Do not read, edit or act on these unless the user explicitly names them:

- `README.md`, `TODO.md`, `notes/` and any other markdown — context only
- `_srpms/`, `tmp/` — local build scratch (gitignored)
- `__pycache__/`, `*.rpm`, `*.src.rpm`, `*.tar.gz`, `*.tar.bz2`, `*.zst` —
  artefacts (gitignored)
- `renovate.json` — dependency-bot config, unrelated to packaging
- `AGENTS.md` — removed; do not recreate it

## Commands

```bash
python3 ci/matrix.py --list                # registry check + build plan
python3 ci/matrix.py --list --since <sha>  # what a push would rebuild
python3 ci/sweep/sweep.py [--pkg NAME]     # version sweep; edits specs in place
python3 -m py_compile ci/*.py ci/sweep/*.py
copr-cli list-packages aahsnr-work/gaming
copr-cli list-builds aahsnr-work/gaming
```

There is no test suite; verification = the Copr build going green on all
four chroots and `dnf install` working from the published repo.

## Layout

- `pkgs/<name>/<name>.spec` — one dir per package
- `ci/packages.toml` — registry: `batch` + `[pkg.updates]` feed. **A package
  without an entry is never built or swept.**
- `ci/matrix.py` — build selection; `ci/sweep/` — version sweeper
  (`custom.py` holds the `custom_<name>()` feeds)
- `repo/gaming.repo` — consumer drop-in; its `includepkgs` must list every
  package this repo ships
- `templates/source-build.spec.tmpl` — starting point for a new spec
- `.github/workflows/` — `copr-build` (submit + wait), `update` (daily sweep),
  `repoclosure` (nightly dependency check), `builder-docker` (CI image)

## Rules

- Adding a package = spec + registry entry (+ `includepkgs` in
  `repo/gaming.repo`). Removing one = all of those, plus
  `copr-cli delete-package`.
- Batches are dependency levels: a package's `batch` must be ≥ 1 + the
  highest batch of anything it BuildRequires. `copr-build.yml` carries one
  submit/wait pair per batch; a new batch level needs its pair added first.
- Touching `ci/**` or `.github/builder/**` rebuilds every package.
- Updates are automatic: `update.yml` runs daily, sweeps every package with
  an `[pkg.updates]` table, commits `bump: <date> (<pkgs>)` to main and
  dispatches `copr-build.yml` for the bumped packages (a `GITHUB_TOKEN` push
  does not trigger workflows by itself). A new package needs a feed entry or
  it will never update.
- `COPR_CLICONF` secret drives copr-cli in CI; a wave of 401s means the Copr
  API token expired — regenerate and re-set it.

## Spec conventions

- Full URLs in `Source*` (CI runs `spectool -g` before `rpmbuild -bs`); no
  downloads in `%prep`.
- Explicit `Release: N%{?dist}` and a written `%changelog`; no rpmautospec.
- No debug packages: every spec has the `debug_package` nil define.
- Never mention macros textually in comments — rpm expands them there too.
- The sweeper edits `Version` and `%global` pins by regex: keep them as
  plain `Version:` / `%global name value` lines.
- Don't use forgeautosetup/forgemeta; use `%autosetup -n <archive-dir>`.

## heroic-games-launcher specifics

- Vendor RPM is unpacked with `rpm2cpio` and kept byte-identical (strip,
  mangle and build-id steps disabled); adds `/usr/bin` launchers, consolidates
  licenses, sets SUID on `chrome-sandbox`.
- `ExclusiveArch: x86_64`: Copr marks the i386 chroots `skipped` and the
  build still reports `succeeded` — expected, not a failure.
- The sweep follows the newest GitHub *release* tag and re-pins the four
  bundled-binary globals (legendary, gogdl, nile, comet) from
  `meta/downloadHelperBinaries.ts`.

## protonplus specifics

- Follows GitHub *releases*, not tags (main already carries the next
  version).
- Build needs `sdl3` ≥ 3.2 and `libadwaita-1` ≥ 1.6; `%check` runs
  `meson_test`.
