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

Requires:       gcc pkgconfig pcre2-devel gc
Requires:       gmp-devel openssl-devel libxml2-devel
Requires:       libyaml-devel zlib-devel
Requires:       llvm-libs libffi

%description
Crystal is a programming language with the following goals:
- Have a syntax similar to Ruby (but compatibility with it is not a goal)
- Statically type-checked but without having to specify the type of variables or method arguments
- Be able to call C code by writing bindings to it in Crystal
- Have compile-time evaluation and generation of code, to avoid boilerplate code
- Compile to efficient native code

%prep
# Set up libgc
mkdir %{_builddir}/libgc
cd %{_builddir}/libgc
git clone --depth=1 --single-branch --branch=v%{getenv:gc_version} https://github.com/ivmai/bdwgc.git .
./autogen.sh

# Set up Crystal
mkdir %{_builddir}/crystal
cd %{_builddir}/crystal
git clone --depth=1 --single-branch --branch=%{version} https://github.com/crystal-lang/crystal.git .

# Set up Shards
mkdir %{_builddir}/shards
cd %{_builddir}/shards
git clone --depth=1 --single-branch --branch=v%{getenv:shards_version} https://github.com/crystal-lang/shards.git .

%build
# Build libgc
cd %{_builddir}/libgc
./configure --disable-debug --disable-shared --enable-large-config --prefix=%{_prefix} --libdir=%{_libdir} --disable-dependency-tracking
make -j$(nproc)

# Build Crystal
cd %{_builddir}/crystal
make crystal release=1 interpreter=1 LDFLAGS="%{build_ldflags}" CRYSTAL_CONFIG_LIBRARY_PATH=%{_libdir}/crystal

# Build Shards
cd %{_builddir}/shards
make release=1 FLAGS="--link-flags=\"%{build_ldflags}\""

%install
# Install libgc
cd %{_builddir}/libgc
make install DESTDIR=%{buildroot}

# Install Crystal
cd %{_builddir}/crystal
make install DESTDIR=%{buildroot} PREFIX=%{_prefix}

# Install Shards
cd %{_builddir}/shards
make install DESTDIR=%{buildroot} PREFIX=%{_prefix}

# Copy libgc.a to crystal lib dir
mkdir -p %{buildroot}%{_libdir}/crystal/
cp %{buildroot}%{_libdir}/libgc.a %{buildroot}%{_libdir}/crystal/

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
%{_libdir}/crystal

%changelog
* Tue Apr 15 2025 84codes <contact@84codes.com> - %{version}-1
- Updated to Crystal %{version}
