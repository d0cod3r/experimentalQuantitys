# -*- coding: utf-8 -*-
"""
Definitions of units regarding angles.

@author: d0cod3r
"""

from ..quantities import Unit, Representation, NumberDict, FullName
from math import pi

rad = radians = Unit(
    Representation(NumberDict(), 1),
    FullName("radians", "rad", "rad"))

deg = degrees = Unit(
    Representation(NumberDict({radians: 1}), pi/180),
    FullName("degrees", "deg", "^{°}"))

turns = Unit(
    Representation(NumberDict({radians: 1}), 2*pi),
    FullName("turns", "turns", "turns"))

del Unit, Representation, NumberDict, FullName
del pi