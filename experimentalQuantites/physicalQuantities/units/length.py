# -*- coding: utf-8 -*-
"""
Definitions of units regarding TODO

@author: d0cod3r
"""

from ..quantities import Unit, Representation, NumberDict, FullName

m = meter = meters = Unit(
        None,
        FullName("meter", "m", "m"))

km = kilometer = Unit(
        Representation(NumberDict({m: 1}), 1000),
        FullName("kilometer", "km", "km"))

dm = decimeter = Unit(
        Representation(NumberDict({m: 1}), 1/10),
        FullName("decimeter", "dm", "dm"))

cm = centimeter = Unit(
        Representation(NumberDict({m: 1}), 1/100),
        FullName("centimeter", "cm", "cm"))

mm = millimeter = Unit(
        Representation(NumberDict({m: 1}), 1/1000),
        FullName("millimeter", "mm", "mm"))

um = micrometer = Unit(
        Representation(NumberDict({mm: 1}), 1/1000),
        FullName("micrometer", "um", "\mu m"))

nm = nanometer = Unit(
        Representation(NumberDict({um: 1}), 1/1000),
        FullName("nanometer", "nm", "nm"))

del Unit, Representation, NumberDict, FullName