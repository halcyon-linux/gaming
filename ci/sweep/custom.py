"""Custom version feeds for packages whose version logic does not fit the
standard github-release / github-tag feeds in ci/packages.toml. Each
`[pkg.updates] feed = "custom"` entry resolves to custom_<name>() here."""

from __future__ import annotations

from pathlib import Path

import feeds
from spec import SpecFile


def custom_heroic_games_launcher(spec: SpecFile, pkg_dir: Path) -> None:
    # port of Terra's update.rhai with one deliberate deviation: the rhai
    # keyed the version off package.json on main, but the gaming repo
    # rewraps the released vendor RPM, so this keys off the newest GitHub
    # *release* tag instead - the release assets must exist to rewrap
    # (package.json can lead the tag). Like the rhai's rpm.changed() guard,
    # the bundled-binary globals re-pin only when the version actually
    # moved; they feed the bundled(...) Provides (legendary and gogdl are
    # python zipapps).
    tag = feeds.github_release_tag("Heroic-Games-Launcher/HeroicGamesLauncher")
    if not spec.set_version(tag):
        return
    ts = feeds.fetch_text(
        "https://raw.githubusercontent.com/Heroic-Games-Launcher/"
        f"HeroicGamesLauncher/{tag}/meta/downloadHelperBinaries.ts")
    for name, pattern in (
        ("legendary_version", r"legendary: '([\d.]+)'"),
        ("gogdl_version", r"gogdl: 'v([\d.]+)'"),
        ("nile_version", r"nile: 'v([\d.]+)'"),
        ("comet_version", r"comet: 'v([\d.]+)'"),
    ):
        spec.set_global(name, feeds.find_group(pattern, ts))
