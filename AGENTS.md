# AGENTS.md

RPM source repo for **halcyon gaming snapshots** — currently mesa-git, the
mesa main-branch tip for Intel + AMD. A sibling of the six halcyon group
repositories (base-pkgs, cli-tools, applications, fonts, texlive-packages,
linux-p03); its own GitHub repo under
[halcyon-linux](https://github.com/orgs/halcyon-linux/repositories) and its
own Copr project under `aahsnr-work`. Built on Fedora Copr
([aahsnr-work/gaming](https://copr.fedorainfracloud.org/coprs/aahsnr-work/gaming/),
chroots fedora-44/45 × x86_64 + i386) in CI. The repo carries only specs,
the registry, the version sweeper and the workflows; Copr owns the build
farm, the GPG signing and the repo hosting. Consumers:

```
install -Dm644 repo/gaming.repo /etc/yum.repos.d/
```

Fedora 44 is the target; the fc45 chroot exists so closure and build
breakage surfaces one release early. The i386 chroots are the Steam/Proton
multilib half — mesa-git is consumed as `mesa-*.i686` too.

**Markdown discipline**: do NOT read, use, or act on `TODO.md`, `notes/` or
any other markdown file unless the user explicitly instructs you to utilize
that particular markdown file for the task at hand. Code, the registry
(`ci/packages.toml`), and the workflows are the source of truth.

## Commands

There is no test suite; verification = the Copr build going green.

```bash
# registry consistency + build plan (what CI's validate job runs)
python3 ci/matrix.py --list
python3 ci/matrix.py --list --since <sha>   # what a push would rebuild

# submit the package to Copr (what copr-build.yml's submit0 does;
# rpmbuild/spectool/copr-cli: run inside the CI image or a fedora:44 container)
spectool -g -C _srpms/mesa-git pkgs/mesa-git/mesa-git.spec
rpmbuild -bs --define "_sourcedir $PWD/_srpms/mesa-git" \
         --define "_srcrpmdir $PWD/_srpms" \
         --define "_specdir $PWD/pkgs/mesa-git" pkgs/mesa-git/mesa-git.spec
copr-cli build --nowait gaming _srpms/mesa-git-*.src.rpm

# the version sweep (update.yml) — no token needed: the mesa feed talks to
# GitLab, and update.yml passes GITHUB_TOKEN only for the standard feeds
python3 ci/sweep/sweep.py [--pkg mesa-git]

# a mock buildroot identical to Copr's, for debugging a failed build locally
copr-cli mock-config aahsnr-work/gaming fedora-44-x86_64 > /tmp/copr.cfg
mock -r /tmp/copr.cfg <srpm>
```

## Non-obvious rules

- **A package without a `ci/packages.toml` entry is never built** — the
  registry is the build selection AND the sweep-feed config. Adding a
  package = 2 files: `pkgs/<pkg>/<pkg>.spec` (start from
  `templates/*.spec.tmpl`) and the registry entry (`batch` +
  `[pkg.updates]` feed).
- **Batches are dependency levels**: a package's `batch` must be >= 1 + the
  highest batch of anything it BuildRequires. Packages within one batch
  submit in parallel and must never depend on each other. `copr-build.yml`
  submits wave-by-wave — each successful build is immediately visible to
  the project repo, which is how batch N+1 installs batch N's output as
  BuildRequires. `ci/matrix.py` enforces the invariant (the validate job
  runs it).
- **A push to `main` rebuilds changed packages plus every higher batch**
  (wave-submitted). Push cascades are additionally gated on the
  CASCADE_ENABLED repository variable (kill-switch — set it to `false` to
  stop automatic cascades; `workflow_dispatch` bypasses it). PRs run
  validation only.
- copr-build.yml carries exactly one wave pair — batch 0, where mesa-git
  sits. A package at a NEW batch level needs its submitN/waitN pair added
  first (copy the previous pair, renumber, chain it) or the manifest would
  emit a wave with no job to submit it.
- Touching `ci/**` or `.github/builder/**` makes `ci/matrix.py` rebuild
  _every_ package in this repo (`INFRA_PREFIXES`).
- **Version bumps are automatic** (`update.yml`, weekly Monday floor +
  `workflow_dispatch`; deliberately NO workflow_run chain here — mesa main
  moves all day and sweep-after-every-build would chase the tip in a
  perpetual rebuild loop). `custom_mesa_git` in `ci/sweep/custom.py` edits
  the four spec globals (`commit`, `commit_date`, `mesa_base`, `bumpver`) in
  place; review the feed's version string: it reports the raw Version line,
  so the before/after look identical for macro-driven versions (same as
  hyprland-git).
- **mesa-git specifics**:
  - The binary packages keep Fedora's `mesa-*` names — that is the point
    (drop-in replacement; the consumer drop-in sets priority=1). The
    SRPM/git name is mesa-git only. Do not rename the subpackages.
  - Version is `<VERSION base>^<bumpver>.git<shortcommit>`: the caret keeps
    a snapshot sorting above upstream's own release of the same base; the
    base moves when main's VERSION file moves (27.0.0-devel ->
    27.1.0-devel), which resets bumpver to 1. Don't hand-edit those four
    globals — run the sweeper.
  - Driver scope is hardcoded (Intel + AMD, x86_64 + i686): adding/removing
    a driver = the meson `-Dgallium-drivers`/`-Dvulkan-drivers` list +
    `%files` + BuildRequires. Validate against the upstream tree first —
    mesa main drops options and layers between Fedora rebases (the anti-lag
    layer, present in Fedora's 26.2.4 spec, is gone from main; RADV absorbed
    it).
  - The kmsro `*_dri.so` entries in `%files` are symlinks onto the
    `libdril_dri.so` megadriver — they exist whenever zink is built, and
    `apple_dri.so` (installed unconditionally) is removed in `%install`.
  - Codecs: mesa's default `all_free` set — no h264/h265 decode (Copr
    policy). Codec-enabled VA-API is RPM Fusion's `mesa-freeworld`; it
    conflicts with this repo's priority=1 and that trade-off is documented
    in `repo/gaming.repo`.
  - Build optimization: Fedora's hardened `-O2` CFLAGS (the meson macro
    pins the plain buildtype — passing a buildtype argument breaks the
    build: meson rejects the duplicate and the macro cannot be overridden)
    plus `-Db_ndebug=true` for asserts off. LTO stays off (the spec comment
    links the bug).
  - No performance patches on top of upstream: the 2026-10 research found
    no gaming distro applying mesa performance patches today — "optimized"
    here means Fedora's hardened CFLAGS, asserts off, and the codec/driver
    choices.
- **Spec conventions** (terra-style, differ from Fedora defaults):
  - full URLs in `Source*` entries — the submit job's `spectool -g`
    fetches them before `rpmbuild -bs`; keep downloads out of `%prep`.
  - `Source2` vendors venus-protocol (its wrap would git-fetch the subproject
    at configure time, impossible offline). Keep the pin level with
    `subprojects/venus-protocol.wrap` — mesa checks version == 1.1.3, and a
    mesa bump that moves the wrap fails loudly at configure: bump the Source2
    URL and the `%prep` mv target together.
  - explicit `Release: N%{?dist}` + a written `%changelog` — no
    rpmautospec/`%autorelease`.
  - **never mention macros textually in comments** — rpm expands macros
    inside comments too.
  - _no debug packages_ — every spec carries the debug_package nil define;
    nothing in the halcyon image consumes debug packages.
  - never use forgeautosetup/forgemeta without defining the forgemeta
    state — the archive dir name derives wrong. Use plain
    `%autosetup -n <archive-dir>` (here `mesa-<full commit>`, the GitLab
    archive's root directory).
  - validate a spec against the UPSTREAM tarball, not from memory: release
    layouts drift (this spec's `%files` was verified against the main
    tarball at the pinned commit).
- `repo/` carries this project's consumer drop-in — repoclosure installs it
  and checks THIS repo's project against Fedora, exactly what a halcyon-image
  consumer sees. The i386 stanza is part of the drop-in; Copr publishes
  i386-chroot results in their own tree, so multilib needs it.
- **CI authentication**: the `COPR_CLICONF` GitHub secret drives every
  copr-cli step. The Copr API token expires — a wave of 401s in
  copr-build.yml means: regenerate at
  <https://copr.fedorainfracloud.org/api/>, re-set the secret, re-run.
- **The CI job image** (`.github/builder/Dockerfile`): fedora-minimal 44 +
  copr-cli, python3, rpm-build, rpmdevtools, git, gh, jq, mock. Built by
  `builder-docker.yml` and pulled (privately, via container credentials) by
  this repo's build steps only. Changing it requires a builder-image run
  before CI jobs work (copr-build.yml's validate job waits for it
  automatically).
