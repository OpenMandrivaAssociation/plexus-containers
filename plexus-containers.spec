# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'

%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

%define section     free

%define parent plexus
%define namedversion 1.0-alpha-30

Name:           plexus-containers
Version:        1.0
Release:        %mkrel 0.a30.1.0.1
Epoch:          0
Summary:        Default Plexus Container
License:        Apache Software License 2.0
Group:          Development/Java
URL:            http://plexus.codehaus.org/
Source0:        plexus-containers-%{namedversion}-src.tar.gz
# svn export http://svn.codehaus.org/plexus/plexus-containers/tags/plexus-containers-1.0-alpha-30/

Source1:        plexus-container-default-build.xml
Source2:        plexus-component-api-build.xml
Source3:        plexus-containers-settings.xml
Source4:        plexus-containers-1.0-jpp-depmap.xml


Patch0:         plexus-containers-javadoc-junit-link.patch
Patch1:         plugin-containers-no-mojo-shade-plugin.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

%if ! %{gcj_support}
BuildArch:      noarch
%endif

BuildRequires:  jpackage-utils >= 0:1.7.3
BuildRequires: java-rpmbuild
BuildRequires:  ant >= 0:1.6.5
BuildRequires:  ant-junit
BuildRequires:  junit
%if %{with_maven}
BuildRequires:  maven2 >= 2.0.4-10jpp
BuildRequires:  maven2-plugin-compiler
BuildRequires:  maven2-plugin-install
BuildRequires:  maven2-plugin-jar
BuildRequires:  maven2-plugin-javadoc
BuildRequires:  maven2-plugin-release
BuildRequires:  maven2-plugin-resources
BuildRequires:  maven2-plugin-surefire
%endif
BuildRequires:  plexus-classworlds
BuildRequires:  plexus-utils 
%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
%endif

Requires:  plexus-classworlds
Requires:  plexus-utils 
Requires(post):    jpackage-utils >= 0:1.7.2
Requires(postun):  jpackage-utils >= 0:1.7.2

%description
The Plexus project seeks to create end-to-end developer tools for 
writing applications. At the core is the container, which can be 
embedded or for a full scale application server. There are many 
reusable components for hibernate, form processing, jndi, i18n, 
velocity, etc. Plexus also includes an application server which 
is like a J2EE application server, without all the baggage.


%package component-api
Summary:        Component API from %{name}
Group:          Development/Java
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       plexus-classworlds

%description component-api
%{summary}.

%package container-default
Summary:        Default Container from %{name}
Group:          Development/Java
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:       plexus-classworlds
Requires:       plexus-containers-component-api
Requires:       plexus-utils

%description container-default
%{summary}.

%package component-api-javadoc
Summary:        Javadoc for plexus-component-api
Group:          Development/Documentation

%description component-api-javadoc
%{summary}.

%package container-default-javadoc
Summary:        Javadoc for plexus-container-default
Group:          Development/Documentation

%description container-default-javadoc
%{summary}.

%prep
%setup -q -n plexus-containers-%{namedversion}
for j in $(find . -name "*.jar"); do
        mv $j $j.no
done
cp %{SOURCE1} plexus-container-default/build.xml
cp %{SOURCE2} plexus-component-api/build.xml
cp %{SOURCE3} settings.xml

%patch0 -b .sav0
%patch1 -b .sav1

%build
sed -i -e "s|<url>__JPP_URL_PLACEHOLDER__</url>|<url>file://`pwd`/.m2/repository</url>|g" settings.xml
sed -i -e "s|<url>__JAVADIR_PLACEHOLDER__</url>|<url>file://`pwd`/external_repo</url>|g" settings.xml
sed -i -e "s|<url>__MAVENREPO_DIR_PLACEHOLDER__</url>|<url>file://`pwd`/.m2/repository</url>|g" settings.xml
sed -i -e "s|<url>__MAVENDIR_PLUGIN_PLACEHOLDER__</url>|<url>file:///usr/share/maven2/plugins</url>|g" settings.xml
sed -i -e "s|<url>__ECLIPSEDIR_PLUGIN_PLACEHOLDER__</url>|<url>file:///usr/share/eclipse/plugins</url>|g" settings.xml

export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mkdir -p $MAVEN_REPO_LOCAL

mkdir external_repo
ln -s %{_javadir} external_repo/JPP

%if %{with_maven}
    mvn-jpp \
        -e \
        -s $(pwd)/settings.xml \
        -Dmaven2.jpp.depmap.file=%{SOURCE4} \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        -Dmaven.test.failure.ignore=true \
        install javadoc:javadoc

%else
export OPT_JAR_LIST="ant/ant-junit junit"
pushd plexus-component-api
export CLASSPATH=$(build-classpath \
plexus/classworlds \
)
%ant -Dbuild.sysclasspath=only jar javadoc
popd
pushd plexus-container-default
rm src/test/java/org/codehaus/plexus/hierarchy/PlexusHierarchyTest.java
CLASSPATH=$CLASSPATH:$(build-classpath \
plexus/utils \
)
CLASSPATH=$CLASSPATH:../plexus-component-api/target/plexus-component-api-%{namedversion}.jar
CLASSPATH=$CLASSPATH:target/classes:target/test-classes
%ant -Dbuild.sysclasspath=only jar javadoc
popd
%endif

%install
rm -rf $RPM_BUILD_ROOT
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/plexus
install -pm 644 %{parent}-component-api/target/%{parent}-component-api-%{namedversion}.jar \
  $RPM_BUILD_ROOT%{_javadir}/plexus/containers-component-api-%{version}.jar
install -pm 644 %{parent}-container-default/target/%{parent}-container-default-%{namedversion}.jar \
  $RPM_BUILD_ROOT%{_javadir}/plexus/containers-container-default-%{version}.jar

%add_to_maven_depmap org.codehaus.plexus %{parent}-component-api %{version} JPP/%{parent} containers-component-api
%add_to_maven_depmap org.codehaus.plexus %{parent}-containers-container-default %{version} JPP/%{parent} containers-container-default

(cd $RPM_BUILD_ROOT%{_javadir}/plexus && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

# poms
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -pm 644 pom.xml \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{parent}-containers.pom
install -pm 644 plexus-component-api/pom.xml \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{parent}-containers-component-api.pom
install -pm 644 plexus-container-default/pom.xml \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{parent}-containers-container-default.pom

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{parent}-containers-component-api-%{version}
cp -pr plexus-component-api/target/site/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{parent}-containers-component-api-%{version}
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{parent}-containers-container-default-%{version}
cp -pr plexus-container-default/target/site/apidocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{parent}-containers-container-default-%{version}
ln -s %{parent}-containers-component-api-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{parent}-containers-component-api # ghost symlink
ln -s %{parent}-containers-container-default-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{parent}-containers-container-default # ghost symlink

%{gcj_compile}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_maven_depmap

%postun
%update_maven_depmap

%if %{gcj_support}
%post component-api
%{update_gcjdb}
%endif

%if %{gcj_support}
%postun component-api
%{clean_gcjdb}
%endif

%if %{gcj_support}
%post container-default
%{update_gcjdb}
%endif

%if %{gcj_support}
%postun container-default
%{clean_gcjdb}
%endif

%files
%defattr(-,root,root,-)
%{_datadir}/maven2/poms/*
%{_mavendepmapfragdir}

%files component-api
%defattr(-,root,root,-)
%{_javadir}/%{parent}/containers-component-api*
%if %{gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/containers-component-api*-%{version}.jar.*
%endif

%files container-default
%defattr(-,root,root,-)
%{_javadir}/%{parent}/containers-container-default*
%if %{gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/containers-container-default*-%{version}.jar.*
%endif

%files component-api-javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/plexus-containers-component-api-%{version}
%doc %{_javadocdir}/plexus-containers-component-api

%files container-default-javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/plexus-containers-container-default-%{version}
%doc %{_javadocdir}/plexus-containers-container-default
