Name: bacon
Version: 1
Release: 1
Summary: bacon that shouts 'eggs!' from time to time
License: MIT
Requires: systemd

%build
pyinstaller --onefile %{_sourcedir}/spam.py

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_unitdir}
install -m 755 dist/spam %{buildroot}%{_bindir}/bacon
install -m 755 %{_sourcedir}/bacon.service %{buildroot}%{_unitdir}/bacon.service
install -m 755 %{_sourcedir}/bacon.timer %{buildroot}%{_unitdir}/bacon.timer

%files
%{_bindir}/bacon
%{_unitdir}/bacon.service
%{_unitdir}/bacon.timer