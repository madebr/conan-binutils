# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools


class BinutilsInstallerTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def test(self):
        pass
