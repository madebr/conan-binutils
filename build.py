#!/usr/bin/env python
#  -*- coding: utf-8 -*-

from bincrafters import build_template_installer
from conans.client.tools.oss import detected_os


if __name__ == "__main__":
    builder = build_template_installer.get_builder()


    for arch_target in ("x86", "x86_64", ):
        if detected_os() == "Linux":
            builder.add(settings={"arch_target": arch_target, "os_target": "Linux",})
        builder.add(settings={"arch_target": arch_target, "os_target": "Windows",})
    for os_target in ("Linux", "Arduino", ):
        builder.add(settings={"arch_target": "armv7", "os_target": os_target,})
        builder.add(settings={"arch_target": "armv8", "os_target": os_target,})
        builder.add(settings={"arch_target": "mips", "os_target": os_target,})
        builder.add(settings={"arch_target": "mips64", "os_target": os_target,})
    builder.add(settings={"arch_target": "avr", "os_target": "Arduino",})

    builder.run()
