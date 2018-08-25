# -*- coding: utf-8 -*-
"""
Definitions of units regarding TODO

@author: d0cod3r
"""

from ..quantities import Unit, Representation, NumberDict, FullName

kg = kilogramm =Unit(
        None,
        FullName("kilogramm", "kg", "kg"))

g = gramm = Unit(
        Representation(NumberDict({kg: 1}), 1/1000),
        FullName("gramm", "g", "g"))

mg = milligramm = Unit(
        Representation(NumberDict({gramm: 1}), 1/1000),
        FullName("milligramm", "mg", "mg"))

ug = microgramm = Unit(
        Representation(NumberDict({milligramm: 1}), 1/1000),
        FullName("microgramm", "ug", "\mu g"))

ng = nanogramm = Unit(
        Representation(NumberDict({microgramm: 1}), 1/1000),
        FullName("nanogramm", "ng", "ng"))

del Unit, Representation, NumberDict, FullName