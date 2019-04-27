# -*- coding: utf-8 -*-

from conans import ConanFile, MSBuild, AutoToolsBuildEnvironment, tools
import os


class OpusFileConan(ConanFile):
    name = "opusfile"
    version = "0.10"
    description = "stand-alone decoder library for .opus streams"
    topics = ("conan", "opus", "opusfile", "audio", "decoder", "decoding", "multimedia", "sound")
    url = "https://github.com/bincrafters/conan-opusfile"
    homepage = "https://github.com/original_author/original_lib"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "BSD-3-Clause"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    generators = ["pkg_config"]
    requires = (
        "opus/1.2.1@bincrafters/stable",
        "ogg/1.3.3@bincrafters/stable",
        "OpenSSL/1.0.2r@conan/stable"
    )

    def configure(self):
        del self.settings.compiler.libcxx

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def source(self):
        source_url = "https://github.com/xiph/opusfile"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version),
                  sha256="bd9c246cf18d27e9a0815e432731d82f0978717fe2dc2b1e1dce09c184132239")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build_vs(self):
        includedir = os.path.abspath(os.path.join(self._source_subfolder, "include"))
        with tools.chdir(os.path.join(self._source_subfolder, "win32", "VS2015")):
            msbuild = MSBuild(self)
            msbuild.build_env.include_paths.append(includedir)
            msbuild.build(project_file="opusfile.sln", targets=["opusfile"],
                          platforms={"x86": "Win32"})

    def build_configure(self):
        with tools.chdir(self._source_subfolder):
            args = []
            if self.options.shared:
                args.extend(["--disable-static", "--enable-shared"])
            else:
                args.extend(["--disable-shared", "--enable-static"])
            self.run("./autogen.sh", win_bash=tools.os_info.is_windows)
            env_build = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            env_build.configure(args=args)
            env_build.make()
            env_build.install()

    def build(self):
        if self._is_msvc:
            self.build_vs()
        else:
            self.build_configure()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            include_folder = os.path.join(self._source_subfolder, "include")
            self.copy(pattern="*", dst=os.path.join("include", "opus"), src=include_folder)
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["opusfile"]
        self.cpp_info.includedirs.append(os.path.join("include", "opus"))
