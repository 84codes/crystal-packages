Name:           crystal
Version:        %(echo %{getenv:crystal_version} | tr '-' '.')
Release:        %{getenv:pkg_revision}%{?dist}
Summary:        A general-purpose, object-oriented programming language
License:        Apache-2.0 AND Boehm-GC
URL:            https://crystal-lang.org
Packager:       84codes <contact@84codes.com>

%define _enable_debug_packages 0
# EL's rpmbuild ignores the above and still builds -debuginfo/-debugsource
%global debug_package %{nil}
# libgc is shipped as a static archive that the compiler links into every
# program; LTO bytecode in it would tie programs to this exact gcc version
%define _lto_cflags %{nil}

BuildRequires:  git gcc gcc-c++ make llvm-devel
BuildRequires:  pcre2-devel libyaml-devel libffi-devel
# asciidoctor (for the man pages) isn't packaged in EL, only in EPEL,
# so it's installed as a gem in the Dockerfile instead

Requires:       gcc pkgconfig pcre2-devel
Recommends:     openssl-devel zlib-devel
Recommends:     libyaml-devel libxml2-devel gmp-devel
Recommends:     libevent-devel
# Commonly used by shards
Recommends:     git make

Source0: crystal.tar.gz
Source1: shards.tar.gz
Source2: gc.tar.gz

%description
Crystal is a programming language with the following goals:
- Have a syntax similar to Ruby (but compatibility with it is not a goal)
- Statically type-checked but without having to specify the type of variables or method arguments
- Be able to call C code by writing bindings to it in Crystal
- Have compile-time evaluation and generation of code, to avoid boilerplate code
- Compile to efficient native code

%prep
%setup -q -n crystal-%{getenv:crystal_version} -b 1 -b 2

%build
# Build libgc as a static library, same flags as the other distributions.
# EL9 only ships libgc 8.0.4 (the stdlib needs 8.2) and EL10 doesn't ship
# gc-devel at all, and linking it statically into programs means they
# don't depend on libgc at runtime.
cd ../gc-%{getenv:gc_version}
CFLAGS="%{build_cflags} -fPIC -std=gnu17" ./configure --disable-debug --disable-shared --enable-large-config
%make_build
# Put it on the default linker path so the compiler and shards link it
install -Dm644 .libs/libgc.a %{_libdir}/libgc.a

# Build Crystal
cd ../crystal-%{getenv:crystal_version}
make release=1 interpreter=1 LDFLAGS="%{build_ldflags}" CRYSTAL_CONFIG_LIBRARY_PATH=%{_libdir}/crystal

# Build Shards
cd ../shards-%{getenv:shards_version}
make release=1 FLAGS="--link-flags=\"%{build_ldflags}\""

%install
# Install Crystal
cd ../crystal-%{getenv:crystal_version}
make install DESTDIR=%{buildroot} PREFIX=%{_prefix}

# Install Shards
cd ../shards-%{getenv:shards_version}
make install DESTDIR=%{buildroot} PREFIX=%{_prefix}

# Install libgc where the compiler looks for it (CRYSTAL_CONFIG_LIBRARY_PATH)
cd ../gc-%{getenv:gc_version}
install -Dm644 .libs/libgc.a %{buildroot}%{_libdir}/crystal/libgc.a
install -Dm644 README.md %{buildroot}%{_datadir}/licenses/crystal/LICENSE.libgc

%files
%license %{_datadir}/licenses/crystal/LICENSE
%license %{_datadir}/licenses/crystal/LICENSE.libgc
%{_bindir}/crystal
%{_bindir}/shards
%{_libdir}/crystal/libgc.a
%{_datadir}/crystal
%{_datadir}/zsh/site-functions/_crystal
%{_datadir}/bash-completion/completions/crystal
%{_datadir}/fish/vendor_completions.d/crystal.fish
%{_mandir}/man1/crystal*.1.gz
%{_mandir}/man1/shards.1.gz
%{_mandir}/man5/shard.yml.5.gz

%changelog
* Tue Apr 15 2025 84codes <contact@84codes.com> - %{version}-1
- Updated to Crystal %{version}
