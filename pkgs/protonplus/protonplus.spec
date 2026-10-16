# protonplus — the ProtonPlus compatibility tools manager: Vala + GTK4/
# libadwaita, built from upstream's GitHub release tags. The weekly sweep
# re-pins Version to the newest upstream release (0.6.8 at the time of
# writing); the source archive follows the version, so both move together.

%global appid com.vysp3r.ProtonPlus

Name:           protonplus
Version:        0.6.8
Release:        1%{?dist}
%define debug_package %{nil}
Summary:        A modern compatibility tools manager

License:        GPL-3.0-or-later
URL:            https://github.com/Vysp3r/ProtonPlus
Source0:        %{url}/archive/refs/tags/v%{version}/ProtonPlus-%{version}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  vala
BuildRequires:  gettext
BuildRequires:  desktop-file-utils
BuildRequires:  python3
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(libadwaita-1) >= 1.6
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libsoup-3.0)
BuildRequires:  pkgconfig(gee-0.8)
BuildRequires:  pkgconfig(libarchive)
BuildRequires:  pkgconfig(libnotify)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(appstream)
BuildRequires:  pkgconfig(sdl3) >= 3.2.0

Requires:       hicolor-icon-theme

%description
ProtonPlus is a modern compatibility tools manager for Linux. It manages
Proton, Wine, DXVK and VKD3D builds across Steam, Lutris, Heroic, Bottles
and other launchers.

%prep
%autosetup -n ProtonPlus-%{version}

%build
%meson
%meson_build

%install
%meson_install
%find_lang %{appid}

%check
%meson_test

%files -f %{appid}.lang
%license LICENSE.md
%doc README.md
%{_bindir}/protonplus
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/glib-2.0/schemas/%{appid}.gschema.xml
%{_datadir}/icons/hicolor/*/apps/%{appid}.png
%{_datadir}/metainfo/%{appid}.metainfo.xml

%changelog
* Sat Oct 17 2026 halcyon-autoupdate <aahsnr041@proton.me> - 0.6.8-1
- initial package (upstream release 0.6.8); release-tag tracking, Vala/GTK4 build
