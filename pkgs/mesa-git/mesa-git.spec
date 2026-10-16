# mesa-git — the mesa main-branch tip for Intel + AMD, a drop-in replacement
# for Fedora's mesa (binary packages keep the mesa-* names, so enabling this
# repo with priority=1 upgrades Fedora's mesa in place).
#
# Ported from Fedora's mesa.spec (26.2.4, 2026-10-01) with the on-top-of-main
# deltas of this snapshot applied: no Rust crate sources (no NVK/rusticl
# toolchain), no teflon/d3d12/OpenCL subpackages, no anti-lag layer (absorbed
# into RADV upstream), plus the zink VA driver main has gained.
#
# Driver scope (Intel + AMD only, x86_64 + i686): radeonsi, iris, crocus,
# i915, zink, llvmpipe, virgl and the kmsro display stubs (gallium); amd,
# intel, intel_hasvk, swrast and virtio/venus (vulkan). Dropped from Fedora's
# set: nouveau/NVK, rusticl (OpenCL), r300/r600, all ARM/embedded GPU drivers,
# d3d12, teflon, svga.
#
# Codecs stay at mesa's default all_free set (no h264/h265 decode) — Copr
# policy; RPM Fusion's mesa-freeworld remains the codec route.

%global mesa_base 27.0.0
%global commit 626e78b034ee57b77a26ea8cbcc3901b6914c30c
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commit_date Fri Oct 16 14:09:17 2026
%global bumpver 2

%ifarch %{valgrind_arches}
%bcond_without valgrind
%else
%bcond_with valgrind
%endif

# We've gotten a report that enabling LTO for mesa breaks some games. See
# https://bugzilla.redhat.com/show_bug.cgi?id=1862771 for details.
# Disable LTO for now
%global _lto_cflags %nil

Name:           mesa-git
Version:        %{mesa_base}%{?bumpver:^%{bumpver}.git%{shortcommit}}
Release:        1%{?dist}
%define debug_package %{nil}
Summary:        Mesa graphics libraries
License:        MIT AND BSD-3-Clause AND SGI-B-2.0
URL:            https://gitlab.freedesktop.org/mesa/mesa

Source0:        %{url}/-/archive/%{commit}/mesa-%{commit}.tar.gz
# src/gallium/auxiliary/postprocess/pp_mlaa* have an ... interestingly worded license.
# Source1 contains email correspondence clarifying the license terms.
# We opt to ignore the optional part of clause 2 and treat that code as 2-clause BSD.
Source1:        Mesa-MLAA-License-Clarification-Email.txt
# venus (Vulkan on virtio-gpu) builds against the venus-protocol subproject,
# which its wrap would fetch from git at configure time; that cannot work in
# an offline build, so vendor the pinned revision. Keep the pin level with
# subprojects/venus-protocol.wrap: mesa checks version == 1.1.3 and fails
# loudly at configure when they drift.
Source2:        https://gitlab.freedesktop.org/virgl/venus-protocol/-/archive/v1.1.3/venus-protocol-v1.1.3.tar.gz

BuildRequires:  meson >= 1.3.0
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  libstdc++-static
BuildRequires:  gettext
BuildRequires:  kernel-headers
BuildRequires:  systemd-devel
# We only check for the minimum version of pkgconfig(libdrm) needed so that the
# SRPMs for each arch still have the same build dependencies. See:
# https://bugzilla.redhat.com/show_bug.cgi?id=1859515
BuildRequires:  pkgconfig(libdrm) >= 2.4.133
BuildRequires:  pkgconfig(libunwind)
BuildRequires:  pkgconfig(expat)
BuildRequires:  pkgconfig(zlib) >= 1.2.3
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.41
BuildRequires:  pkgconfig(wayland-client) >= 1.11
BuildRequires:  pkgconfig(wayland-server) >= 1.11
BuildRequires:  pkgconfig(wayland-egl-backend) >= 3
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xext)
BuildRequires:  pkgconfig(xdamage) >= 1.1
BuildRequires:  pkgconfig(xfixes)
BuildRequires:  pkgconfig(xcb-glx) >= 1.8.1
BuildRequires:  pkgconfig(xxf86vm)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(x11-xcb)
BuildRequires:  pkgconfig(xcb-dri2) >= 1.8
BuildRequires:  pkgconfig(xcb-dri3)
BuildRequires:  pkgconfig(xcb-present)
BuildRequires:  pkgconfig(xcb-sync)
BuildRequires:  pkgconfig(xshmfence) >= 1.1
BuildRequires:  pkgconfig(dri2proto) >= 2.8
BuildRequires:  pkgconfig(glproto) >= 1.4.14
BuildRequires:  pkgconfig(xcb-xfixes)
BuildRequires:  pkgconfig(xcb-randr)
BuildRequires:  pkgconfig(xrandr) >= 1.3
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  lm_sensors-devel
BuildRequires:  pkgconfig(libva) >= 0.38.0
BuildRequires:  pkgconfig(libelf)
BuildRequires:  pkgconfig(libglvnd) >= 1.3.2
BuildRequires:  llvm-devel >= 7.0.0
# mesa main's Intel drivers build through the CLC compiler path, which needs
# the clang libraries plus the SPIR-V translator matching the LLVM version
BuildRequires:  clang-devel
BuildRequires:  pkgconfig(LLVMSPIRVLib)
BuildRequires:  pkgconfig(SPIRV-Tools)
BuildRequires:  python3-devel
BuildRequires:  python3-mako
BuildRequires:  python3-pycparser
BuildRequires:  python3-pyyaml
BuildRequires:  vulkan-headers
BuildRequires:  glslang
BuildRequires:  pkgconfig(vulkan)
%if %{with valgrind}
BuildRequires:  pkgconfig(valgrind)
%endif

%description
%{summary}.

%package -n mesa-filesystem
Summary:        Mesa driver filesystem
Provides:       mesa-dri-filesystem = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      mesa-omx-drivers < %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      mesa-libd3d < %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      mesa-libd3d-devel < %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      mesa-vdpau-drivers < %{?epoch:%{epoch}:}%{version}-%{release}

%description -n mesa-filesystem
%{summary}.

%package -n mesa-libGL
Summary:        Mesa libGL runtime libraries
Requires:       libglvnd-glx%{?_isa} >= 1:1.3.2
Requires:       mesa-dri-drivers%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      mesa-libOSMesa < 25.1.0~rc2-1

%description -n mesa-libGL
%{summary}.

%package -n mesa-libGL-devel
Summary:        Mesa libGL development package
Requires:       (mesa-libGL%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release} if mesa-libGL%{?_isa})
Requires:       libglvnd-devel%{?_isa} >= 1:1.3.2
Provides:       libGL-devel = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       libGL-devel%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Recommends:     gl-manpages
Obsoletes:      mesa-libOSMesa-devel < 25.1.0~rc2-1

%description -n mesa-libGL-devel
%{summary}.

%package -n mesa-libEGL
Summary:        Mesa libEGL runtime libraries
Requires:       libglvnd-egl%{?_isa} >= 1:1.3.2
Requires:       mesa-libgbm%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       mesa-dri-drivers%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description -n mesa-libEGL
%{summary}.

%package -n mesa-libEGL-devel
Summary:        Mesa libEGL development package
Requires:       (mesa-libEGL%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release} if mesa-libEGL%{?_isa})
Requires:       libglvnd-devel%{?_isa} >= 1:1.3.2
Requires:       mesa-khr-devel%{?_isa}
Provides:       libEGL-devel = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       libEGL-devel%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description -n mesa-libEGL-devel
%{summary}.

%package -n mesa-dri-drivers
Summary:        Mesa-based DRI drivers
Requires:       mesa-filesystem%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       mesa-libgbm%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      mesa-libglapi < 25.0.0~rc2-1
Obsoletes:      mesa-va-drivers < 26.0.0-5
Provides:       mesa-va-drivers = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       mesa-va-drivers%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      mesa-vaapi-drivers < 22.2.0-5

%description -n mesa-dri-drivers
%{summary}.

%package -n mesa-libgbm
Summary:        Mesa gbm runtime library
Provides:       libgbm = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       libgbm%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Recommends:     mesa-dri-drivers%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
# If mesa-dri-drivers are installed, they must match in version. This is here to prevent using
# older mesa-dri-drivers together with a newer mesa-libgbm and its dependants.
# See https://bugzilla.redhat.com/show_bug.cgi?id=2193135 .
Requires:       (mesa-dri-drivers%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release} if mesa-dri-drivers%{?_isa})

%description -n mesa-libgbm
%{summary}.

%package -n mesa-libgbm-devel
Summary:        Mesa libgbm development package
Requires:       mesa-libgbm%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       libgbm-devel = %{?epoch:%{epoch}:}%{version}-%{release}
Provides:       libgbm-devel%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

%description -n mesa-libgbm-devel
%{summary}.

%package -n mesa-vulkan-drivers
Summary:        Mesa Vulkan drivers
Requires:       vulkan%{_isa}
Requires:       mesa-filesystem%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      mesa-vulkan-devel < %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      VK_hdr_layer < 1

%description -n mesa-vulkan-drivers
The drivers with support for the Vulkan API.

%prep
%autosetup -n mesa-%{commit}
cp %{SOURCE1} docs/

# the venus-protocol.wrap declares directory = venus-protocol-1.1.3; meson
# uses a present subproject directory instead of downloading it
tar -xzf %{SOURCE2} -C subprojects/
mv subprojects/venus-protocol-v1.1.3 subprojects/venus-protocol-1.1.3

%build
# No buildtype argument: Fedora's meson macro pins plain on purpose (the
# distro -O2 + hardening CFLAGS are the optimization policy), and meson
# rejects a duplicate; b_ndebug=true switches mesa's own runtime asserts off.
%meson \
  -Db_ndebug=true \
  -Dplatforms=x11,wayland \
  -Dgallium-drivers=llvmpipe,virgl,crocus,i915,iris,radeonsi,zink \
  -Dgallium-va=enabled \
  -Dgallium-mediafoundation=disabled \
  -Dvulkan-drivers=swrast,amd,intel,intel_hasvk,virtio \
  -Dvulkan-layers=device-select \
  -Dgles1=enabled \
  -Dgles2=enabled \
  -Dopengl=true \
  -Dgbm=enabled \
  -Dglx=dri \
  -Degl=enabled \
  -Dglvnd=enabled \
%ifarch x86_64
  -Dintel-rt=enabled \
%else
  -Dintel-rt=disabled \
%endif
  -Dmicrosoft-clc=disabled \
  -Dllvm=enabled \
  -Dshared-llvm=enabled \
  -Dvalgrind=%{?with_valgrind:enabled}%{!?with_valgrind:disabled} \
  -Dbuild-tests=false \
  -Dandroid-libbacktrace=disabled \
%ifarch %{ix86}
  -Dglx-read-only-text=true \
%endif
  -Dspirv-tools=enabled \
  %{nil}
%meson_build

%install
%meson_install

# likewise glvnd
rm -vf %{buildroot}%{_libdir}/libGLX_mesa.so
rm -vf %{buildroot}%{_libdir}/libEGL_mesa.so
# XXX can we just not build this
rm -vf %{buildroot}%{_libdir}/libGLES*

# The dril megadriver installs this stub whenever any kmsro driver is built;
# it is a dangling symlink without the asahi driver, so drop it
rm -vf %{buildroot}%{_libdir}/dri/apple_dri.so

# glvnd needs a default provider for indirect rendering where it cannot
# determine the vendor
ln -s libGLX_mesa.so.0 %{buildroot}%{_libdir}/libGLX_system.so.0

%files -n mesa-filesystem
%doc docs/Mesa-MLAA-License-Clarification-Email.txt
%dir %{_libdir}/dri
%dir %{_datadir}/drirc.d

%files -n mesa-libGL
%{_libdir}/libGLX_mesa.so.0*
%{_libdir}/libGLX_system.so.0*

%files -n mesa-libGL-devel
%dir %{_includedir}/GL
%dir %{_includedir}/GL/internal
%{_includedir}/GL/internal/dri_interface.h
%{_libdir}/pkgconfig/dri.pc

%files -n mesa-libEGL
%{_datadir}/glvnd/egl_vendor.d/50_mesa.json
%{_libdir}/libEGL_mesa.so.0*

%files -n mesa-libEGL-devel
%dir %{_includedir}/EGL
%{_includedir}/EGL/eglext_angle.h
%{_includedir}/EGL/eglmesaext.h

%files -n mesa-libgbm
%{_libdir}/libgbm.so.1
%{_libdir}/libgbm.so.1.*

%files -n mesa-libgbm-devel
%{_libdir}/libgbm.so
%{_includedir}/gbm.h
%{_includedir}/gbm_backend_abi.h
%{_libdir}/pkgconfig/gbm.pc

%files -n mesa-dri-drivers
%{_datadir}/drirc.d/00-mesa-defaults.conf
%{_libdir}/libgallium-*.so
%{_libdir}/gbm/dri_gbm.so
%{_libdir}/dri/kms_swrast_dri.so
%{_libdir}/dri/libdril_dri.so
%{_libdir}/dri/swrast_dri.so
%{_libdir}/dri/virtio_gpu_dri.so
%{_datadir}/drirc.d/00-virtio_gpu-defaults.conf
%{_libdir}/dri/radeonsi_dri.so
%{_datadir}/drirc.d/00-radeonsi-defaults.conf
%ifarch %{ix86} x86_64
%{_libdir}/dri/crocus_dri.so
%{_datadir}/drirc.d/00-crocus-defaults.conf
%{_libdir}/dri/iris_dri.so
%{_datadir}/drirc.d/00-iris-defaults.conf
%{_libdir}/dri/i915_dri.so
%endif
%{_libdir}/dri/zink_dri.so
%{_datadir}/drirc.d/00-zink-defaults.conf
# kmsro display-only stubs (symlinks onto the dril megadriver)
%{_libdir}/dri/armada-drm_dri.so
%{_libdir}/dri/exynos_dri.so
%{_libdir}/dri/gm12u320_dri.so
%{_libdir}/dri/hdlcd_dri.so
%{_libdir}/dri/hx8357d_dri.so
%{_libdir}/dri/ili9163_dri.so
%{_libdir}/dri/ili9225_dri.so
%{_libdir}/dri/ili9341_dri.so
%{_libdir}/dri/ili9486_dri.so
%{_libdir}/dri/imx-dcss_dri.so
%{_libdir}/dri/imx-drm_dri.so
%{_libdir}/dri/imx-lcdif_dri.so
%{_libdir}/dri/ingenic-drm_dri.so
%{_libdir}/dri/kirin_dri.so
%{_libdir}/dri/komeda_dri.so
%{_libdir}/dri/mali-dp_dri.so
%{_libdir}/dri/mcde_dri.so
%{_libdir}/dri/mediatek_dri.so
%{_libdir}/dri/meson_dri.so
%{_libdir}/dri/mi0283qt_dri.so
%{_libdir}/dri/mxsfb-drm_dri.so
%{_libdir}/dri/panel-mipi-dbi_dri.so
%{_libdir}/dri/pl111_dri.so
%{_libdir}/dri/rcar-du_dri.so
%{_libdir}/dri/repaper_dri.so
%{_libdir}/dri/rockchip_dri.so
%{_libdir}/dri/rzg2l-du_dri.so
%{_libdir}/dri/ssd130x_dri.so
%{_libdir}/dri/st7586_dri.so
%{_libdir}/dri/st7735r_dri.so
%{_libdir}/dri/sti_dri.so
%{_libdir}/dri/stm_dri.so
%{_libdir}/dri/sun4i-drm_dri.so
%{_libdir}/dri/udl_dri.so
%{_libdir}/dri/vkms_dri.so
%{_libdir}/dri/zynqmp-dpsub_dri.so
%{_libdir}/dri/radeonsi_drv_video.so
%{_libdir}/dri/virtio_gpu_drv_video.so
%{_libdir}/dri/zink_drv_video.so

%files -n mesa-vulkan-drivers
%{_libdir}/libvulkan_lvp.so
%{_datadir}/vulkan/icd.d/lvp_icd.*.json
%{_datadir}/drirc.d/00-lavapipe-defaults.conf
%{_libdir}/libVkLayer_MESA_device_select.so
%{_datadir}/vulkan/implicit_layer.d/VkLayer_MESA_device_select.json
%{_libdir}/libvulkan_virtio.so
%{_datadir}/vulkan/icd.d/virtio_icd.*.json
%{_datadir}/drirc.d/00-venus-defaults.conf
%{_libdir}/libvulkan_radeon.so
%{_datadir}/drirc.d/00-radv-defaults.conf
%{_datadir}/drirc.d/01-radv-performance.conf
%{_datadir}/vulkan/icd.d/radeon_icd.*.json
%ifarch %{ix86} x86_64
%{_libdir}/libvulkan_intel.so
%{_datadir}/vulkan/icd.d/intel_icd.*.json
%{_datadir}/drirc.d/00-anv-defaults.conf
%{_libdir}/libvulkan_intel_hasvk.so
%{_datadir}/vulkan/icd.d/intel_hasvk_icd.*.json
%{_datadir}/drirc.d/00-hasvk-defaults.conf
%endif

%changelog
* Fri Oct 16 2026 halcyon-autoupdate <aahsnr041@proton.me> - 27.0.0^1.git25947cfd-1
- initial snapshot of mesa main (commit 25947cfdf2dd54e26fb99815ef4638cba48ce238); Fedora spec
  base trimmed to Intel + AMD, asserts off, no LTO
