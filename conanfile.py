# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.client.tools.oss import detected_os
from conans.errors import ConanException
from conans.util.env_reader import get_env
import os
import tempfile


class BinutilsConan(ConanFile):
    name = "binutils"
    version = "2.32"
    description = "The GNU Binutils are a collection of binary tools."
    license = "GPL2"
    url = "https://github.com/bincrafters/conan-binutils"
    author = "Bincrafters <bincrafters@gmail.com>"
    topics = ("conan", "gnu", "binutils", "tools")
    settings = "os_build", "arch_build", "os_target", "arch_target", "compiler"
    no_copy_source = True

    options = {
        "big_endian": [False, True],
    }

    default_options = {
        "big_endian": False,
    }

    _source_subfolder = "sources"

    def build_requirements(self):
        if detected_os() == "Windows":
            self.build_requires("msys2_installer/latest@bincrafters/stable")

    def source(self):
        filename = "{}-{}.tar.gz".format(self.name, self.version)
        url = "https://ftp.gnu.org/gnu/{}/{}".format(self.name, filename)
        sha256 = "9b0d97b3d30df184d302bced12f976aa1e5fbf4b0be696cdebc6cca30411a46e"

        dlfilepath = os.path.join(tempfile.gettempdir(), filename)
        if os.path.exists(dlfilepath) and not get_env("BINUTILS_FORCE_DOWNLOAD", False):
            self.output.info("Skipping download. Using cached {}".format(dlfilepath))
        else:
            tools.download(url, dlfilepath)
        tools.check_sha256(dlfilepath, sha256)
        tools.untargz(dlfilepath)
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    @property
    def _arch_target_triple(self):
        os_target = str(self.settings.os_target)
        if os_target == "Arduino":
            os_target = None
        trans = {
            "x86": "i386",
            "armv6": "arm",
            "armv7": "arm",
            "armv7hf": "arm",
            "armv7s": "arm",
            "armv7k": "arm",
            "armv8": "aarch64",
        }
        binutils_arch = trans.get(str(self.settings.arch_target), str(self.settings.arch_target))
        if binutils_arch in ["i386", "x86_64"]:
            if os_target == "Linux":
                abi = "linux"
            elif os_target == "Windows":
                abi = "pe"
            else:
                raise ConanException("Unsupported os_target")
            return "{}-{}-{}".format(binutils_arch, os_target, abi).lower()
        elif binutils_arch == "aarch64":
            if os_target == "Linux":
                abi = "linux"
            elif os_target is None:
                abi = "elf"
            else:
                raise ConanException("Unsupported os_target")
            return "{}-{}-{}".format(binutils_arch, os_target, abi).lower()
        elif binutils_arch == "arm":
            if os_target == "Linux":
                abi = "elf"
            elif os_target == "Windows":
                abi = "pe"
            elif os_target is None:
                abi = "eabi"
            else:
                raise ConanException("Unsupported os_target")
            return "{}-{}-{}".format(binutils_arch, os_target, abi).lower()
        elif binutils_arch == "mips":
            if os_target == "Linux":
                abi = "linux"
            elif os_target == "FreeBSD":
                abi = "freebsd"
            elif os_target is None:
                abi = "elf"
            else:
                raise ConanException("Unsupported os_target")
            return "{}-{}-{}".format(binutils_arch, os_target, abi).lower()
        elif binutils_arch == "mips64":
            if os_target == "Linux":
                abi = "linux"
            elif os_target == "FreeBSD":
                abi = "freebsd"
            elif os_target is None:
                abi = "elf"
            else:
                raise ConanException("Unsupported os_target")
            return "{}-{}-{}".format(binutils_arch, os_target, abi).lower()
        elif binutils_arch == "avr":
            os_target = "none"
            abi = "none"
            return "{}-{}-{}".format(binutils_arch, os_target, abi).lower()
        raise ConanException("Unsupported arch_target")

    def build(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=detected_os() is "Windows")
        config_args = [
            "--target={}".format(self._arch_target_triple),
            "--enable-gold=yes",
            "--enable-ld=yes",
        ]
        autotools.configure(args=config_args, configure_dir=os.path.join(self.source_folder, self._source_subfolder))
        autotools.make()

    def package(self):
        with tools.chdir(os.path.join(self.build_folder)):
            autotools = AutoToolsBuildEnvironment(self, win_bash=detected_os() is "Windows")
            autotools.install()

    def package_id(self):
        del self.info.settings.compiler

        # alias armv6 and armv7
        if str(self.settings.arch_target).startswith('armv6') or str(self.settings.arch_target).startswith('armv7'):
            self.info.settings.arch_target = 'armv6'

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(bindir))
        self.env_info.PATH.append(bindir)

        target_bindir = os.path.join(self.package_folder, self._arch_target_triple, "bin")
        self.output.info('Appending PATH environment variable: {}'.format(target_bindir))
        self.env_info.PATH.append(target_bindir)
