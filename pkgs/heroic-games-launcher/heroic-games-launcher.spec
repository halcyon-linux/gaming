# heroic-games-launcher — repackaged from Heroic's official release RPM
# (Heroic-<version>-linux-x86_64.rpm) on the applications repo's ferdium
# pattern (2026-10-19). The vendor payload already carries the desktop file
# and the full hicolor icon set, so the rewrap is thin:
#   * /usr/bin/heroic launcher added + a heroic-games-launcher symlink; the
#     vendor Exec line rewritten to the system launcher
#   * Electron/Chromium license texts move to /usr/share/licenses, the app's
#     own GPL-3.0 text rides in as Source1
#   * chrome-sandbox gets the SUID bit Electron wants for the setuid sandbox
#     path
#   * vendor Requires mapped to Fedora package names; python3 runs the
#     bundled legendary/gogdl zipapps, alsa-lib the Electron audio path
# Version tracks the newest GitHub release tag; the custom sweep also re-pins
# the bundled-binary globals from that tag's meta/downloadHelperBinaries.ts
# (ci/sweep/custom.py). x86_64 only: the payload is an amd64 Electron build,
# so Copr marks the i386 chroots skipped (ExclusiveArch).

%global legendary_version 0.21.1
%global gogdl_version 1.3.0
%global nile_version 1.2.0
%global comet_version 0.2.0

Name:           heroic-games-launcher
Version:        2.22.4
Release:        1%{?dist}
Summary:        An Open Source Launcher for GOG, Epic Games and Amazon Games
License:        GPL-3.0-only AND MIT AND BSD-3-Clause
URL:            https://heroicgameslauncher.com/
Source0:        https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/releases/download/v%{version}/Heroic-%{version}-linux-x86_64.rpm
Source1:        https://raw.githubusercontent.com/Heroic-Games-Launcher/HeroicGamesLauncher/v%{version}/COPYING

ExclusiveArch:  x86_64

# the automatic check stage validates the packaged .desktop files
BuildRequires:  desktop-file-utils
BuildRequires:  cpio

# vendor Requires, alternates resolved to Fedora package names; python3 runs
# the bundled legendary/gogdl zipapps, alsa-lib the Electron audio path
Requires:       gtk3
Requires:       nss
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       libuuid
Requires:       at-spi2-core
Requires:       libnotify
Requires:       xdg-utils
Requires:       alsa-lib
Requires:       python3

Provides:       bundled(comet) = %{comet_version}
Provides:       bundled(gogdl) = %{gogdl_version}
Provides:       bundled(legendary) = %{legendary_version}
Provides:       bundled(nile) = %{nile_version}

%define debug_package %{nil}
%global _build_id_links none
%global __os_install_post %{nil}
# the payload must stay byte-identical to the vendor blob
%global __brp_strip %{nil}
%global __brp_strip_comment_note %{nil}
%global __brp_mangle_shebangs %{nil}

%description
Heroic is an Open Source game launcher for GOG, Amazon Games and Epic
Games. Repackaged from the vendor RPM with system launchers in /usr/bin and
the license texts consolidated under /usr/share/licenses/heroic-games-launcher.

%prep
%setup -q -c -T
rpm2cpio %{_sourcedir}/Heroic-%{version}-linux-x86_64.rpm | cpio -idmu

%install
install -dm755 %{buildroot}/opt %{buildroot}%{_bindir} \
    %{buildroot}%{_datadir}/applications %{buildroot}%{_licensedir}/%{name}
cp -a opt/Heroic %{buildroot}/opt/
cp -a usr/share/icons %{buildroot}%{_datadir}/icons

# point the vendor desktop file at the system launcher
sed -i 's|^Exec=.*|Exec=/usr/bin/heroic %U|' \
    usr/share/applications/heroic.desktop
install -pm644 usr/share/applications/heroic.desktop \
    %{buildroot}%{_datadir}/applications/heroic.desktop

# system launcher (and the package-name alias)
cat > %{buildroot}%{_bindir}/heroic <<'EOF'
#!/bin/sh
exec /opt/Heroic/heroic "$@"
EOF
chmod 755 %{buildroot}%{_bindir}/heroic
ln -s heroic %{buildroot}%{_bindir}/heroic-games-launcher

# license texts under /usr/share/licenses/heroic-games-launcher
install -pm644 %{SOURCE1} %{buildroot}%{_licensedir}/%{name}/COPYING
mv %{buildroot}/opt/Heroic/LICENSE.electron.txt \
    %{buildroot}%{_licensedir}/%{name}/LICENSE.electron.txt
mv %{buildroot}/opt/Heroic/LICENSES.chromium.html \
    %{buildroot}%{_licensedir}/%{name}/LICENSES.chromium.html

# SUID chrome-sandbox for the setuid sandbox path
chmod 4755 %{buildroot}/opt/Heroic/chrome-sandbox

%files
/opt/Heroic/
%{_bindir}/heroic
%{_bindir}/heroic-games-launcher
%{_datadir}/applications/heroic.desktop
%{_datadir}/icons/hicolor/*/apps/heroic.png
%{_licensedir}/%{name}/

%changelog
* Mon Oct 19 2026 halcyon-autoupdate <aahsnr041@proton.me> - 2.22.4-1
- initial package: vendor RPM rewrap on the ferdium pattern
- /usr/bin launchers, SUID chrome-sandbox, license consolidation,
  bundled-binary Provides
