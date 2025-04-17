Name:           crystal
Version:        %{getenv:crystal_version}
Release:        1%{?dist}
Summary:        A general-purpose, object-oriented programming language
License:        Apache-2.0
URL:            https://crystal-lang.org
Packager:       84codes <contact@84codes.com>

%define _unpackaged_files_terminate_build 0

BuildRequires:  git gcc gcc-c++ make gc-devel
BuildRequires:  llvm-devel
BuildRequires:  pcre2-devel libxml2-devel libyaml-devel libffi-devel
BuildRequires:  openssl-devel zlib-devel gmp-devel autoconf automake libtool

Requires:       gcc pkgconfig pcre2-devel gc-devel
Requires:       gmp-devel openssl-devel libxml2-devel
Requires:       libyaml-devel zlib-devel
Requires:       llvm-libs libffi

Source0: crystal.tar.gz
Source1: shards.tar.gz

%description
Crystal is a programming language with the following goals:
- Have a syntax similar to Ruby (but compatibility with it is not a goal)
- Statically type-checked but without having to specify the type of variables or method arguments
- Be able to call C code by writing bindings to it in Crystal
- Have compile-time evaluation and generation of code, to avoid boilerplate code
- Compile to efficient native code

%prep
%setup -q -b 1

%build
# Build Crystal
cd ../crystal-%{getenv:crystal_version}
make crystal interpreter=1 LDFLAGS="%{build_ldflags}" CRYSTAL_CONFIG_LIBRARY_PATH=%{_libdir}/crystal

# Build Shards
cd ../shards-%{getenv:shards_version}
make FLAGS="--link-flags=\"%{build_ldflags}\""

%install
# Install Crystal
cd ../crystal-%{getenv:crystal_version}
make install DESTDIR=%{buildroot} PREFIX=%{_prefix}

# Install Shards
cd ../shards-%{getenv:shards_version}
make install DESTDIR=%{buildroot} PREFIX=%{_prefix}

%files
%license %{_datadir}/licenses/crystal/LICENSE
%{_bindir}/crystal
%{_bindir}/shards
%{_datadir}/crystal
%{_datadir}/zsh/site-functions/_crystal
%{_datadir}/bash-completion/completions/crystal
%{_datadir}/fish/vendor_completions.d/crystal.fish
%{_mandir}/man1/crystal.1.gz
%{_mandir}/man1/shards.1.gz
%{_mandir}/man5/shard.yml.5.gz

%changelog
* Tue Apr 15 2025 84codes <contact@84codes.com> - %{version}-1
- Updated to Crystal %{version}
